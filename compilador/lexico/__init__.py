"""Análise léxica: remoção de comentários e tokenização por AFD."""

from compilador.lexico.automato import tokenizar
from compilador.lexico.comentarios import remover_comentarios

__all__ = ["tokenizar", "remover_comentarios"]
