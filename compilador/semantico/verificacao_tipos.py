"""Verificação de tipos — anota cada nó com seu tipo e coleta erros.

As regras formais estão em ``regras_semanticas.md`` (cálculo de sequentes). A
decisão de tipo de cada operador vem de ``compilador.dominio.tipos`` (o mesmo
módulo usado pela inferência da tabela de símbolos), de modo que as duas
etapas são sempre coerentes. **Não há promoção implícita** entre ``int`` e
``real``.

A verificação não aborta no primeiro erro: anota o que conseguir (usando
``indef`` quando necessário) e acumula
:class:`~compilador.dominio.erros.Diagnostico` para um relatório único.
"""

from __future__ import annotations

from compilador.dominio import ast_nodes as ast
from compilador.dominio.erros import Diagnostico
from compilador.dominio.tipos import (
    BOOL,
    INDEF,
    UNIT,
    categoria_operador,
    tipo_de_negacao,
    tipo_de_operacao,
)
from compilador.semantico.tabela_simbolos import TabelaSimbolos


class _Verificador:
    def __init__(self, tabela: TabelaSimbolos) -> None:
        self.tabela = tabela
        self.erros: list[Diagnostico] = []
        self.tipos_instrucoes: list[str] = []  # tipos das instruções de topo, em ordem

    def verificar(self, programa: ast.Programa) -> None:
        for instrucao in programa.instrucoes:
            self.tipos_instrucoes.append(self.tipar(instrucao))

    def _erro(self, mensagem: str, linha: int, categoria: str = "tipo") -> None:
        self.erros.append(Diagnostico(mensagem, linha, categoria))

    def tipar(self, no: ast.No | None) -> str:
        if no is None:
            return INDEF
        metodo = getattr(self, f"_tipar_{type(no).__name__}", None)
        tipo = metodo(no) if metodo else INDEF
        no.tipo = tipo
        return tipo

    # -- literais ------------------------------------------------------

    def _tipar_LiteralInteiro(self, no: ast.LiteralInteiro) -> str:
        return "int"

    def _tipar_LiteralReal(self, no: ast.LiteralReal) -> str:
        return "real"

    def _tipar_LiteralBool(self, no: ast.LiteralBool) -> str:
        return BOOL

    # -- memória / histórico ------------------------------------------

    def _tipar_LeituraMemoria(self, no: ast.LeituraMemoria) -> str:
        # Uso-antes-da-definição já foi reportado pela tabela de símbolos.
        return self.tabela.tipo_de(no.nome)

    def _tipar_EscritaMemoria(self, no: ast.EscritaMemoria) -> str:
        return self.tipar(no.valor)

    def _tipar_ResultadoAnterior(self, no: ast.ResultadoAnterior) -> str:
        if 1 <= no.n <= len(self.tipos_instrucoes):
            return self.tipos_instrucoes[-no.n]
        return INDEF

    # -- operações -----------------------------------------------------

    def _tipar_OperacaoBinaria(self, no: ast.OperacaoBinaria) -> str:
        te = self.tipar(no.esquerda)
        td = self.tipar(no.direita)
        resultado = tipo_de_operacao(no.operador, te, td)
        if resultado == INDEF and INDEF not in (te, td):
            self._erro(self._mensagem_binaria(no.operador, te, td), no.linha)
        return resultado

    def _tipar_OperacaoUnaria(self, no: ast.OperacaoUnaria) -> str:
        t = self.tipar(no.operando)
        resultado = tipo_de_negacao(t)
        if resultado == INDEF and t != INDEF:
            self._erro(
                f"operador lógico 'NOT' exige um operando 'bool', recebeu '{t}'",
                no.linha,
            )
            return BOOL
        return resultado

    # -- controle ------------------------------------------------------

    def _tipar_Se(self, no: ast.Se) -> str:
        self._exigir_bool_condicao(self.tipar(no.condicao), "IF", no.linha)
        return self.tipar(no.entao)

    def _tipar_SeSenao(self, no: ast.SeSenao) -> str:
        self._exigir_bool_condicao(self.tipar(no.condicao), "IFELSE", no.linha)
        t_entao = self.tipar(no.entao)
        t_senao = self.tipar(no.senao)
        if t_entao == t_senao:
            return t_entao
        if INDEF in (t_entao, t_senao):
            return t_entao if t_entao != INDEF else t_senao
        self._erro(
            f"os ramos do IFELSE têm tipos divergentes: 'então' é '{t_entao}' "
            f"e 'senão' é '{t_senao}' (devem ser iguais)",
            no.linha,
        )
        return INDEF

    def _tipar_Enquanto(self, no: ast.Enquanto) -> str:
        self._exigir_bool_condicao(self.tipar(no.condicao), "WHILE", no.linha)
        self.tipar(no.corpo)
        return UNIT

    # -- auxiliares ----------------------------------------------------

    def _exigir_bool_condicao(self, tipo: str, estrutura: str, linha: int) -> None:
        if tipo not in (BOOL, INDEF):
            self._erro(
                f"a condição do {estrutura} deve ser do tipo 'bool', recebeu '{tipo}'",
                linha,
                categoria="controle",
            )

    @staticmethod
    def _mensagem_binaria(operador: str, te: str, td: str) -> str:
        categoria = categoria_operador(operador)
        if categoria == "relacional":
            return (
                f"operador relacional '{operador}' exige dois operandos numéricos "
                f"do mesmo tipo (int ou real), recebeu '{te}' e '{td}'"
            )
        if categoria == "logico":
            return (
                f"operador lógico '{operador}' exige dois operandos 'bool', "
                f"recebeu '{te}' e '{td}'"
            )
        if operador == "|":
            return (
                f"divisão real '|' exige dois operandos 'real', recebeu '{te}' e '{td}'"
            )
        if operador in ("/", "%"):
            return (
                f"operador inteiro '{operador}' exige dois operandos 'int', "
                f"recebeu '{te}' e '{td}'"
            )
        return (
            f"operador '{operador}' exige dois operandos numéricos do mesmo tipo "
            f"(sem promoção implícita), recebeu '{te}' e '{td}'"
        )


def verificarTipos(
    arvore: ast.Programa, tabela: TabelaSimbolos
) -> tuple[ast.Programa, list[Diagnostico]]:
    """Anota a AST com tipos e devolve ``(arvore, erros)``."""
    if not isinstance(arvore, ast.Programa):
        return arvore, []
    verificador = _Verificador(tabela)
    verificador.verificar(arvore)
    return arvore, verificador.erros
