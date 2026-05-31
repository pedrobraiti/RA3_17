"""Inferência de tipos — ponto único de verdade.

Esta função é consultada **tanto** pela tabela de símbolos (para fixar o
tipo de uma variável no momento da definição) **quanto** pela verificação
de tipos. Como ambas as etapas usam exatamente as mesmas regras
(``compilador.dominio.tipos``), elas nunca discordam — em particular, não
há promoção implícita em lugar algum.

A inferência é *best-effort* e silenciosa: devolve ``INDEF`` quando não
consegue um tipo, sem emitir erros (quem emite mensagens é a verificação
de tipos, que reusa estas mesmas regras).
"""

from __future__ import annotations

from compilador.dominio import ast_nodes as ast
from compilador.dominio.tipos import (
    BOOL,
    INDEF,
    INT,
    REAL,
    UNIT,
    tipo_de_negacao,
    tipo_de_operacao,
)


def inferir(no: ast.No | None, tabela) -> str:
    if no is None:
        return INDEF
    if isinstance(no, ast.LiteralInteiro):
        return INT
    if isinstance(no, ast.LiteralReal):
        return REAL
    if isinstance(no, ast.LiteralBool):
        return BOOL
    if isinstance(no, ast.LeituraMemoria):
        return tabela.tipo_de(no.nome)
    if isinstance(no, ast.EscritaMemoria):
        return inferir(no.valor, tabela)
    if isinstance(no, ast.ResultadoAnterior):
        return INDEF  # depende do contexto; resolvido na verificação de tipos
    if isinstance(no, ast.OperacaoBinaria):
        return tipo_de_operacao(
            no.operador, inferir(no.esquerda, tabela), inferir(no.direita, tabela)
        )
    if isinstance(no, ast.OperacaoUnaria):
        return tipo_de_negacao(inferir(no.operando, tabela))
    if isinstance(no, ast.Se):
        return inferir(no.entao, tabela)
    if isinstance(no, ast.SeSenao):
        t_entao = inferir(no.entao, tabela)
        t_senao = inferir(no.senao, tabela)
        return t_entao if t_entao == t_senao else INDEF
    if isinstance(no, ast.Enquanto):
        return UNIT
    return INDEF
