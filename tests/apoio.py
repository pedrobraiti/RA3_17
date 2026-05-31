"""Funções de apoio compartilhadas pelos testes."""

from __future__ import annotations

from pathlib import Path

from compilador.dominio.ast_nodes import Programa
from compilador.lexico.automato import tokenizar
from compilador.lexico.comentarios import remover_comentarios
from compilador.semantico.arvore_atribuida import gerarArvoreAtribuida
from compilador.semantico.tabela_simbolos import construirTabelaSimbolos
from compilador.semantico.verificacao_tipos import verificarTipos
from compilador.sintatico.parser import parsear

RAIZ = Path(__file__).resolve().parents[1]


def tokens_de(fonte: str):
    limpo, _ = remover_comentarios(fonte)
    return tokenizar(limpo)


def arvore_de(fonte: str) -> Programa:
    return parsear(tokens_de(fonte))


def analisar(fonte: str):
    """Roda léxico→sintático→semântico e devolve ``(arvore, tabela, erros)``."""
    arvore = arvore_de(fonte)
    tabela, erros_tabela = construirTabelaSimbolos(arvore)
    arvore, erros_tipos = verificarTipos(arvore, tabela)
    gerarArvoreAtribuida(arvore, tabela)
    return arvore, tabela, erros_tabela + erros_tipos


def programa(*linhas: str) -> str:
    """Envolve as linhas dadas entre (START) e (END)."""
    corpo = "\n".join(linhas)
    return f"(START)\n{corpo}\n(END)\n"
