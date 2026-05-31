"""Análise semântica: tabela de símbolos, verificação de tipos e atribuição."""

from compilador.semantico.arvore_atribuida import gerarArvoreAtribuida
from compilador.semantico.tabela_simbolos import (
    TabelaSimbolos,
    construirTabelaSimbolos,
)
from compilador.semantico.verificacao_tipos import verificarTipos

__all__ = [
    "TabelaSimbolos",
    "construirTabelaSimbolos",
    "verificarTipos",
    "gerarArvoreAtribuida",
]
