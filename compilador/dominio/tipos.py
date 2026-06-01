"""Sistema de tipos da linguagem.

Os tipos são **estáticos e fortes**: o tipo de cada artefato é fixado no
momento de sua definição e operações entre tipos incompatíveis são erros
semânticos. **Não há promoção implícita** entre ``int`` e ``real`` — essa
decisão está formalizada em ``regras_semanticas.md`` (cálculo de sequentes) e é
aplicada por um único ponto de verdade: :func:`tipo_de_operacao`.
"""

from __future__ import annotations

from compilador.dominio.tokens import (
    OPERADORES_ARITMETICOS,
    OPERADORES_RELACIONAIS,
)

# Tipos da linguagem.
INT = "int"
REAL = "real"
BOOL = "bool"
UNIT = "unit"      # "sem valor" — resultado de um laço WHILE
INDEF = "indef"    # falha de inferência (um erro já foi/será reportado)

TIPOS_NUMERICOS = frozenset({INT, REAL})

# Subconjuntos de operadores por comportamento de tipo.
_ARIT_HOMOGENEOS = frozenset({"+", "-", "*", "^"})  # exigem (τ, τ), τ numérico
_DIV_INTEIRA = frozenset({"/", "%"})                # exigem (int, int)
_DIV_REAL = frozenset({"|"})                        # exige (real, real)
_LOGICOS_BINARIOS = frozenset({"AND", "OR"})        # exigem (bool, bool)


def tipo_de_literal_numerico(lexema: str) -> str:
    """``int`` se o lexema não tem ponto decimal; ``real`` caso contrário."""
    return REAL if "." in lexema else INT


def tipo_de_operacao(operador: str, esquerda: str, direita: str) -> str:
    """Tipo resultante de uma operação binária — ou ``INDEF`` se inválida.

    Esta é a **única** fonte de verdade sobre tipos de operadores binários:
    tanto a verificação de tipos quanto a inferência usada pela tabela de
    símbolos a consultam, garantindo que as duas etapas nunca discordem
    (evitando a clássica armadilha de "uma etapa promove e a outra proíbe").

    Operandos ``INDEF`` propagam o tipo nominal esperado do operador sem
    gerar novos erros — o erro de origem já terá sido reportado.
    """
    # Operandos indefinidos: devolve o tipo nominal do operador para evitar
    # uma avalanche de erros em cascata, sem disparar erro adicional aqui.
    if INDEF in (esquerda, direita):
        return _tipo_nominal(operador)

    if operador in OPERADORES_RELACIONAIS:
        return BOOL if (esquerda == direita and esquerda in TIPOS_NUMERICOS) else INDEF

    if operador in _LOGICOS_BINARIOS:
        return BOOL if (esquerda == BOOL == direita) else INDEF

    if operador in _DIV_REAL:
        return REAL if (esquerda == REAL == direita) else INDEF

    if operador in _DIV_INTEIRA:
        return INT if (esquerda == INT == direita) else INDEF

    if operador in _ARIT_HOMOGENEOS:
        return esquerda if (esquerda == direita and esquerda in TIPOS_NUMERICOS) else INDEF

    return INDEF


def tipo_de_negacao(operando: str) -> str:
    """Tipo do operador unário ``NOT`` — ``bool`` se o operando é ``bool``."""
    if operando == INDEF:
        return BOOL
    return BOOL if operando == BOOL else INDEF


def _tipo_nominal(operador: str) -> str:
    """Tipo que o operador *produz* quando bem-formado (para propagação)."""
    if operador in OPERADORES_RELACIONAIS or operador in _LOGICOS_BINARIOS:
        return BOOL
    if operador in _DIV_REAL:
        return REAL
    if operador in _DIV_INTEIRA:
        return INT
    # +, -, *, ^ : herdam o tipo dos operandos; sem informação, ficam indef.
    return INDEF


def categoria_operador(operador: str) -> str:
    """Classifica o operador em ``aritmetico`` / ``relacional`` / ``logico``."""
    if operador in OPERADORES_RELACIONAIS:
        return "relacional"
    if operador in _LOGICOS_BINARIOS:
        return "logico"
    if operador in OPERADORES_ARITMETICOS:
        return "aritmetico"
    return "desconhecido"
