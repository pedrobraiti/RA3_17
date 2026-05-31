"""Orquestração das etapas léxica e sintática (entrada da análise semântica).

``prepararEntradaSemantica`` é o ponto onde a Fase 3 reaproveita as fases
anteriores: lê o arquivo-fonte, remove os comentários, roda o AFD léxico e o
parser LL(1), e devolve tudo o que as etapas semânticas precisam — os tokens,
a árvore sintática inicial e a gramática. Erros léxicos ou sintáticos são
capturados e devolvidos como lista (o orquestrador de alto nível decide
abortar antes da semântica).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from compilador.dominio.ast_nodes import Programa
from compilador.dominio.erros import ErroCompilacao
from compilador.dominio.tokens import Token
from compilador.lexico.comentarios import Comentario, remover_comentarios
from compilador.lexico.automato import tokenizar
from compilador.sintatico.gramatica import construir_gramatica
from compilador.sintatico.parser import parsear


@dataclass
class EntradaSemantica:
    """Resultado de :func:`prepararEntradaSemantica`."""

    caminho: str
    fonte: str = ""
    tokens: list[Token] = field(default_factory=list)
    comentarios: list[Comentario] = field(default_factory=list)
    arvore: Programa | None = None
    gramatica: dict | None = None
    erros_lexsint: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.erros_lexsint and self.arvore is not None


def prepararEntradaSemantica(arquivo: str) -> EntradaSemantica:
    """Lê o arquivo, descarta comentários, tokeniza e parseia.

    Devolve uma :class:`EntradaSemantica`. Em caso de erro léxico ou
    sintático, ``arvore`` fica ``None`` e a mensagem é registrada em
    ``erros_lexsint`` (a análise semântica não deve prosseguir).
    """
    with open(arquivo, encoding="utf-8") as fonte_arquivo:
        fonte = fonte_arquivo.read()

    entrada = EntradaSemantica(caminho=arquivo, fonte=fonte)
    # A gramática é construída sempre (a sua construção valida que é LL(1)) e
    # é útil como artefato mesmo quando a análise aborta adiante.
    entrada.gramatica = construir_gramatica()

    try:
        fonte_limpa, comentarios = remover_comentarios(fonte)
        entrada.comentarios = comentarios
        entrada.tokens = tokenizar(fonte_limpa)
        entrada.arvore = parsear(entrada.tokens)
    except ErroCompilacao as erro:
        entrada.erros_lexsint.append(str(erro))

    return entrada
