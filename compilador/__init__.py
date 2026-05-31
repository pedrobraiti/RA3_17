"""Compilador da linguagem RPN tipada — Fase 3 (Analisador Semântico).

O pacote está organizado **por etapa de compilação**, e não por tipo
técnico de arquivo, para que cada fronteira do compilador fique explícita:

    compilador/
        dominio/      estruturas compartilhadas (tokens, tipos, nós da árvore)
        lexico/       análise léxica  (AFD + remoção de comentários)
        sintatico/    análise sintática (gramática LL(1) + parser preditivo)
        semantico/    análise semântica (tabela de símbolos, tipos, atribuição)
        codegen/      geração de Assembly ARMv7 (Cpulator DEC1-SOC v16.1)
        pipeline.py   orquestração das fronteiras entre as etapas
        relatorios.py serialização dos artefatos (Markdown / JSON)

As funções exigidas pelo enunciado são reexportadas aqui de forma
**preguiçosa** (PEP 562): elas só são importadas quando realmente acessadas,
o que evita carregar todas as etapas para usar apenas uma.
"""

from __future__ import annotations

__all__ = [
    "prepararEntradaSemantica",
    "construirTabelaSimbolos",
    "verificarTipos",
    "gerarArvoreAtribuida",
    "gerarAssembly",
]

_ORIGEM = {
    "prepararEntradaSemantica": "compilador.pipeline",
    "construirTabelaSimbolos": "compilador.semantico.tabela_simbolos",
    "verificarTipos": "compilador.semantico.verificacao_tipos",
    "gerarArvoreAtribuida": "compilador.semantico.arvore_atribuida",
    "gerarAssembly": "compilador.codegen.armv7",
}


def __getattr__(nome: str):
    modulo = _ORIGEM.get(nome)
    if modulo is None:
        raise AttributeError(f"module 'compilador' has no attribute {nome!r}")
    import importlib

    return getattr(importlib.import_module(modulo), nome)
