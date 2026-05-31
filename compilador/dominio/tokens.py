"""Definição dos tokens reconhecidos pelo analisador léxico.

Um *token* é a menor unidade com significado na linguagem. O AFD da etapa
léxica (``compilador.lexico.automato``) produz uma sequência de instâncias
de :class:`Token`, que alimenta o parser LL(1).
"""

from __future__ import annotations

from dataclasses import dataclass


# --------------------------------------------------------------------------
# Categorias léxicas (o atributo ``categoria`` de cada Token)
# --------------------------------------------------------------------------
# Mantemos as categorias como constantes de string em vez de um Enum para que
# os tokens sejam trivialmente serializáveis (o artefato de tokens é salvo em
# texto) e para que a comparação com os terminais da gramática seja direta.

CAT_INTEIRO = "INTEIRO"
CAT_REAL = "REAL"
CAT_IDENT = "IDENT"          # nome de memória (letras maiúsculas)
CAT_PALAVRA = "PALAVRA"      # palavra reservada (START, IF, TRUE, AND, ...)
CAT_OPERADOR = "OPERADOR"    # + - * | / % ^ > < == != >= <=
CAT_ABRE = "ABRE_PAREN"
CAT_FECHA = "FECHA_PAREN"
CAT_FIM = "FIM"              # marcador de fim de entrada ($) usado pelo parser


# Palavras reservadas da linguagem na Fase 3.
# `RES` vem da Fase 1; `START/END/IF/IFELSE/WHILE` da Fase 2;
# `TRUE/FALSE/AND/OR/NOT` são a extensão lógica desta fase.
PALAVRAS_RESERVADAS = frozenset(
    {
        "START",
        "END",
        "RES",
        "IF",
        "IFELSE",
        "WHILE",
        "TRUE",
        "FALSE",
        "AND",
        "OR",
        "NOT",
    }
)

# Operadores aritméticos, relacionais e (não-keyword) da linguagem.
OPERADORES_ARITMETICOS = frozenset({"+", "-", "*", "|", "/", "%", "^"})
OPERADORES_RELACIONAIS = frozenset({">", "<", "==", "!=", ">=", "<="})


@dataclass(frozen=True)
class Token:
    """Unidade léxica com sua posição no arquivo-fonte.

    Atributos
    ---------
    categoria : str
        Uma das constantes ``CAT_*`` deste módulo.
    lexema : str
        O texto exato reconhecido (``"3.14"``, ``"VARA"``, ``">="`` ...).
    linha : int
        Linha (base 1) onde o token começa.
    coluna : int
        Coluna (base 1) onde o token começa.
    """

    categoria: str
    lexema: str
    linha: int
    coluna: int

    def terminal(self) -> str:
        """Nome do *terminal* da gramática correspondente a este token.

        Palavras reservadas e operadores são terminais pelo próprio lexema
        (``IF``, ``+``, ``==`` ...). Números e identificadores são terminais
        pela categoria (``INTEIRO``, ``REAL``, ``IDENT``). Parênteses têm
        nomes simbólicos.
        """
        if self.categoria in (CAT_PALAVRA, CAT_OPERADOR):
            return self.lexema
        if self.categoria == CAT_ABRE:
            return "("
        if self.categoria == CAT_FECHA:
            return ")"
        if self.categoria == CAT_FIM:
            return "$"
        return self.categoria  # INTEIRO, REAL, IDENT

    def __str__(self) -> str:
        return f"{self.categoria}:{self.lexema}@{self.linha}:{self.coluna}"
