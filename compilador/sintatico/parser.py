"""Parser descendente recursivo preditivo (LL(1)).

Há uma função por não-terminal da gramática de
``compilador.sintatico.gramatica``. Como a gramática é LL(1), cada função
decide qual produção aplicar olhando **um** token de *lookahead* — sem
retrocesso. A árvore sintática (AST) é construída diretamente durante a
descida.

A linguagem é pós-fixada e ambígua *estruturalmente* entre algumas formas de
mesma aridade (ex.: ``(V MEM)`` escrita vs. ``(N RES)`` histórico — ambas são
"dois operandos sem operador"). Essa distinção é resolvida aqui, ao montar a
AST, conforme a categoria do segundo operando: um identificador nu vira
**destino de escrita**; a palavra ``RES`` vira **referência a resultado**.
Leituras de memória exigem parênteses — ``(MEM)`` —, de modo que um
identificador nu em posição de valor é um erro com mensagem explicativa.
"""

from __future__ import annotations

from dataclasses import dataclass

from compilador.dominio.ast_nodes import (
    Enquanto,
    EscritaMemoria,
    LeituraMemoria,
    LiteralBool,
    LiteralInteiro,
    LiteralReal,
    No,
    OperacaoBinaria,
    OperacaoUnaria,
    Programa,
    ResultadoAnterior,
    Se,
    SeSenao,
)
from compilador.dominio.erros import ErroSintatico
from compilador.dominio.tokens import (
    OPERADORES_ARITMETICOS,
    OPERADORES_RELACIONAIS,
    Token,
)

_BINARIOS = OPERADORES_ARITMETICOS | OPERADORES_RELACIONAIS | {"AND", "OR"}
_INICIO_OPERANDO = {"INTEIRO", "REAL", "TRUE", "FALSE", "IDENT", "RES", "("}


@dataclass
class _IdentNu:
    """Identificador lido como operando, antes de saber seu papel semântico."""

    nome: str
    linha: int
    coluna: int


@dataclass
class _ResNu:
    """Palavra ``RES`` lida como operando, antes de virar ``(N RES)``."""

    linha: int
    coluna: int


class Parser:
    """Constrói a :class:`Programa` (AST) a partir da lista de tokens."""

    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._pos = 0

    # -- utilitários de fluxo ------------------------------------------

    @property
    def _atual(self) -> Token:
        return self._tokens[self._pos]

    def _terminal(self) -> str:
        return self._atual.terminal()

    def _avancar(self) -> Token:
        token = self._tokens[self._pos]
        if self._pos < len(self._tokens) - 1:
            self._pos += 1
        return token

    def _consumir(self, terminal: str) -> Token:
        if self._terminal() != terminal:
            self._erro(f"esperado '{terminal}', encontrado '{self._atual.lexema}'")
        return self._avancar()

    def _erro(self, mensagem: str) -> None:
        token = self._atual
        raise ErroSintatico(mensagem, token.linha, token.coluna)

    # -- regras da gramática -------------------------------------------

    def analisar(self) -> Programa:
        """``programa -> ( START ) corpo`` e nada após ``(END)``."""
        self._consumir("(")
        self._consumir("START")
        self._consumir(")")
        instrucoes = self._corpo()
        if self._terminal() != "$":
            self._erro(
                f"conteúdo após o (END) do programa: '{self._atual.lexema}'"
            )
        return Programa(linha=1, instrucoes=instrucoes)

    def _corpo(self) -> list[No]:
        """``corpo -> ( corpo_resto`` ; itera até encontrar ``(END)``."""
        instrucoes: list[No] = []
        while True:
            self._consumir("(")
            if self._terminal() == "END":
                self._avancar()
                self._consumir(")")
                return instrucoes
            instrucoes.append(self._expr())
            self._consumir(")")

    def _expr(self) -> No:
        """``expr -> operando apos1`` — resolve a forma pós-fixada."""
        o1 = self._operando()
        terminal = self._terminal()

        if terminal == ")":
            return self._uma_posicao(o1)

        if terminal == "NOT":
            token = self._avancar()
            return OperacaoUnaria(
                linha=token.linha,
                operador="NOT",
                operando=self._como_valor(o1),
            )

        # apos1 -> operando apos2
        o2 = self._operando()
        terminal = self._terminal()

        if terminal == ")":
            return self._duas_posicoes(o1, o2)

        if terminal in _BINARIOS:
            token = self._avancar()
            return OperacaoBinaria(
                linha=token.linha,
                operador=token.lexema,
                esquerda=self._como_valor(o1),
                direita=self._como_valor(o2),
            )

        if terminal == "IF":
            token = self._avancar()
            return Se(
                linha=token.linha,
                condicao=self._como_valor(o1),
                entao=self._como_valor(o2),
            )

        if terminal == "WHILE":
            token = self._avancar()
            return Enquanto(
                linha=token.linha,
                condicao=self._como_valor(o1),
                corpo=self._como_valor(o2),
            )

        # apos2 -> operando IFELSE
        o3 = self._operando()
        token = self._consumir("IFELSE")
        return SeSenao(
            linha=token.linha,
            condicao=self._como_valor(o1),
            entao=self._como_valor(o2),
            senao=self._como_valor(o3),
        )

    def _operando(self):
        """``operando`` — literal, identificador nu, RES nu ou subexpressão."""
        token = self._atual
        terminal = token.terminal()

        if terminal == "INTEIRO":
            self._avancar()
            return LiteralInteiro(linha=token.linha, valor=int(token.lexema))
        if terminal == "REAL":
            self._avancar()
            return LiteralReal(linha=token.linha, valor=float(token.lexema))
        if terminal == "TRUE":
            self._avancar()
            return LiteralBool(linha=token.linha, valor=True)
        if terminal == "FALSE":
            self._avancar()
            return LiteralBool(linha=token.linha, valor=False)
        if terminal == "IDENT":
            self._avancar()
            return _IdentNu(nome=token.lexema, linha=token.linha, coluna=token.coluna)
        if terminal == "RES":
            self._avancar()
            return _ResNu(linha=token.linha, coluna=token.coluna)
        if terminal == "(":
            self._avancar()
            interno = self._expr()
            self._consumir(")")
            return interno

        self._erro(f"esperado um operando, encontrado '{token.lexema}'")

    # -- montagem semântica das formas pós-fixadas ---------------------

    def _uma_posicao(self, o1) -> No:
        """``(operando)`` — leitura de memória, RES inválido ou literal nu."""
        if isinstance(o1, _IdentNu):
            return LeituraMemoria(linha=o1.linha, nome=o1.nome)
        if isinstance(o1, _ResNu):
            raise ErroSintatico("'RES' só é válido na forma (N RES)", o1.linha, o1.coluna)
        return o1

    def _duas_posicoes(self, o1, o2) -> No:
        """``(operando operando)`` sem operador — escrita ou ``(N RES)``."""
        if isinstance(o2, _IdentNu):
            return EscritaMemoria(
                linha=o2.linha, nome=o2.nome, valor=self._como_valor(o1)
            )
        if isinstance(o2, _ResNu):
            valor = self._como_valor(o1)
            if not isinstance(valor, LiteralInteiro):
                raise ErroSintatico(
                    "o N em (N RES) deve ser um inteiro literal", o2.linha, o2.coluna
                )
            return ResultadoAnterior(linha=o2.linha, n=valor.valor)
        linha = getattr(o2, "linha", 0)
        raise ErroSintatico(
            "dois operandos sem operador — faltou um operador, IF/WHILE, "
            "um identificador (escrita) ou RES",
            linha,
        )

    def _como_valor(self, operando) -> No:
        """Converte um operando para um nó de **valor**.

        Identificador nu não é valor (leitura exige parênteses: ``(MEM)``);
        ``RES`` nu não é valor (só vale na forma ``(N RES)``).
        """
        if isinstance(operando, _IdentNu):
            raise ErroSintatico(
                f"para usar a variável '{operando.nome}' como valor escreva "
                f"({operando.nome}); identificador nu só vale como destino de escrita",
                operando.linha,
                operando.coluna,
            )
        if isinstance(operando, _ResNu):
            raise ErroSintatico(
                "'RES' só é válido na forma (N RES)", operando.linha, operando.coluna
            )
        return operando


def parsear(tokens: list[Token]) -> Programa:
    """Atalho: constrói e devolve a AST a partir dos tokens."""
    return Parser(tokens).analisar()
