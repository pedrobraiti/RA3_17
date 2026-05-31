"""Árvore Sintática Atribuída — enriquece a AST tipada com metadados de código.

Pré-condição: a AST já passou por ``verificarTipos`` (todo nó tem ``tipo``).
Aqui preenchemos ``no.meta`` com a informação que o gerador de Assembly
precisa, **sem** ainda emitir instruções:

* ``categoria``     — papel semântico do nó (literal, leitura, escrita,
  aritmetica, relacional, logica, controle...);
* ``registrador``   — registrador-alvo (sempre ``d0``: todo valor trafega
  como ``double`` IEEE-754 de 64 bits, inclusive ``bool`` como ``0.0``/``1.0``);
* ``rotulos``       — rótulos de salto únicos dos nós de controle (o gerador
  usa exatamente estes, garantindo que árvore e Assembly fiquem coerentes);
* ``rotulo_mem``    — rótulo da variável na seção de dados;
* ``valor_double``  — valor literal já convertido para ``double``.

O nó raiz recebe, em ``meta``, o conjunto de memórias e o número de
instruções de topo — dados globais usados na reserva de memória e no
suporte ao comando ``(N RES)``.
"""

from __future__ import annotations

from compilador.dominio import ast_nodes as ast
from compilador.dominio.tipos import categoria_operador


class _Atribuidor:
    def __init__(self, tabela) -> None:
        self.tabela = tabela
        self._contador = 0
        self.memorias: set[str] = set()

    def _novo_id(self) -> int:
        self._contador += 1
        return self._contador

    def visitar(self, no: ast.No | None) -> None:
        if no is None:
            return
        metodo = getattr(self, f"_attr_{type(no).__name__}", self._attr_generico)
        metodo(no)

    def _attr_generico(self, no: ast.No) -> None:
        for filho in no.filhos():
            self.visitar(filho)

    # -- literais ------------------------------------------------------

    def _attr_LiteralInteiro(self, no: ast.LiteralInteiro) -> None:
        no.meta = {"categoria": "literal", "registrador": "d0", "valor_double": float(no.valor)}

    def _attr_LiteralReal(self, no: ast.LiteralReal) -> None:
        no.meta = {"categoria": "literal", "registrador": "d0", "valor_double": float(no.valor)}

    def _attr_LiteralBool(self, no: ast.LiteralBool) -> None:
        no.meta = {
            "categoria": "literal",
            "registrador": "d0",
            "valor_double": 1.0 if no.valor else 0.0,
        }

    # -- memória / histórico ------------------------------------------

    def _attr_LeituraMemoria(self, no: ast.LeituraMemoria) -> None:
        self.memorias.add(no.nome)
        no.meta = {
            "categoria": "leitura",
            "registrador": "d0",
            "rotulo_mem": f"mem_{no.nome}",
            "simbolo": self._simbolo(no.nome),
        }

    def _attr_EscritaMemoria(self, no: ast.EscritaMemoria) -> None:
        self.visitar(no.valor)
        self.memorias.add(no.nome)
        no.meta = {
            "categoria": "escrita",
            "registrador": "d0",
            "rotulo_mem": f"mem_{no.nome}",
            "simbolo": self._simbolo(no.nome),
        }

    def _attr_ResultadoAnterior(self, no: ast.ResultadoAnterior) -> None:
        no.meta = {"categoria": "historico", "registrador": "d0", "n": no.n}

    # -- operações -----------------------------------------------------

    def _attr_OperacaoBinaria(self, no: ast.OperacaoBinaria) -> None:
        self.visitar(no.esquerda)
        self.visitar(no.direita)
        no.meta = {
            "categoria": categoria_operador(no.operador),
            "registrador": "d0",
            "operador": no.operador,
        }

    def _attr_OperacaoUnaria(self, no: ast.OperacaoUnaria) -> None:
        self.visitar(no.operando)
        no.meta = {"categoria": "logica", "registrador": "d0", "operador": no.operador}

    # -- controle ------------------------------------------------------

    def _attr_Se(self, no: ast.Se) -> None:
        self.visitar(no.condicao)
        self.visitar(no.entao)
        k = self._novo_id()
        no.meta = {"categoria": "controle_se", "registrador": "d0", "rotulos": {"fim": f"L_if_fim_{k}"}}

    def _attr_SeSenao(self, no: ast.SeSenao) -> None:
        self.visitar(no.condicao)
        self.visitar(no.entao)
        self.visitar(no.senao)
        k = self._novo_id()
        no.meta = {
            "categoria": "controle_se_senao",
            "registrador": "d0",
            "rotulos": {"senao": f"L_else_{k}", "fim": f"L_ifelse_fim_{k}"},
        }

    def _attr_Enquanto(self, no: ast.Enquanto) -> None:
        self.visitar(no.condicao)
        self.visitar(no.corpo)
        k = self._novo_id()
        no.meta = {
            "categoria": "controle_enquanto",
            "registrador": "d0",
            "rotulos": {"inicio": f"L_while_ini_{k}", "fim": f"L_while_fim_{k}"},
        }

    # -- auxiliares ----------------------------------------------------

    def _simbolo(self, nome: str) -> dict:
        simbolo = self.tabela.obter(nome)
        if simbolo is None:
            return {"nome": nome, "tipo": "indef"}
        return {"nome": simbolo.nome, "tipo": simbolo.tipo, "linha_definicao": simbolo.linha_definicao}


def gerarArvoreAtribuida(arvore: ast.Programa, tabela) -> ast.Programa:
    """Anota a AST (já tipada) com metadados de geração de código.

    A árvore é alterada no lugar e também devolvida.
    """
    if not isinstance(arvore, ast.Programa):
        return arvore
    atribuidor = _Atribuidor(tabela)
    for instrucao in arvore.instrucoes:
        atribuidor.visitar(instrucao)
    arvore.meta = {
        "memorias": sorted(atribuidor.memorias),
        "n_instrucoes": len(arvore.instrucoes),
    }
    return arvore
