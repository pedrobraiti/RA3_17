"""Análise sintática: gramática LL(1) e parser preditivo recursivo."""

from compilador.sintatico.gramatica import construir_gramatica
from compilador.sintatico.parser import Parser, parsear

__all__ = ["construir_gramatica", "Parser", "parsear"]
