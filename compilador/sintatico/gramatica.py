"""Gramática LL(1) da linguagem e sua tabela de análise.

A gramática é livre de ambiguidades e fatorada à esquerda para ser
**LL(1)** — basta 1 símbolo de *lookahead* para escolher cada produção. Este
módulo:

1. declara as produções (forma BNF numerada);
2. calcula os conjuntos **FIRST** e **FOLLOW** por ponto-fixo;
3. constrói a **tabela de análise** ``M[não-terminal, terminal]``;
4. **detecta conflitos** — se alguma célula receber duas produções, a
   gramática não seria LL(1) e :func:`construir_gramatica` levanta erro.

O parser (``compilador.sintatico.parser``) é um descendente recursivo
preditivo guiado por esta mesma gramática; a tabela aqui também serve de
artefato de documentação exigido pelo enunciado.

Convenção: não-terminais em **minúsculas**, terminais em **MAIÚSCULAS** ou
pelo próprio lexema do operador. ``$`` marca o fim da entrada; ``""`` (rhs
vazio) representa ``ε``.
"""

from __future__ import annotations

EPSILON = ""
FIM = "$"

# Não-terminais da gramática.
NAO_TERMINAIS = (
    "programa",
    "corpo",
    "corpo_resto",
    "expr",
    "apos1",
    "apos2",
    "operando",
    "binop",
    "kw2",
)

_OPS_BINARIOS = [
    "+", "-", "*", "|", "/", "%", "^",
    ">", "<", "==", "!=", ">=", "<=",
    "AND", "OR",
]

# Produções na ordem em que são numeradas (#0, #1, ...).
PRODUCOES: list[tuple[str, list[str]]] = [
    ("programa", ["(", "START", ")", "corpo"]),                 # 0
    ("corpo", ["(", "corpo_resto"]),                            # 1
    ("corpo_resto", ["END", ")"]),                              # 2
    ("corpo_resto", ["expr", ")", "corpo"]),                    # 3
    ("expr", ["operando", "apos1"]),                            # 4
    ("apos1", []),                                              # 5  (ε)
    ("apos1", ["NOT"]),                                         # 6
    ("apos1", ["operando", "apos2"]),                           # 7
    ("apos2", []),                                              # 8  (ε)
    ("apos2", ["binop"]),                                       # 9
    ("apos2", ["kw2"]),                                         # 10
    ("apos2", ["operando", "IFELSE"]),                          # 11
    ("operando", ["INTEIRO"]),                                  # 12
    ("operando", ["REAL"]),                                     # 13
    ("operando", ["TRUE"]),                                     # 14
    ("operando", ["FALSE"]),                                    # 15
    ("operando", ["IDENT"]),                                    # 16
    ("operando", ["RES"]),                                      # 17
    ("operando", ["(", "expr", ")"]),                           # 18
]
PRODUCOES += [("binop", [op]) for op in _OPS_BINARIOS]          # 19..33
PRODUCOES += [("kw2", ["IF"]), ("kw2", ["WHILE"])]             # 34, 35


def _e_nao_terminal(simbolo: str) -> bool:
    return simbolo in NAO_TERMINAIS


def _terminais() -> set[str]:
    terminais: set[str] = {FIM}
    for _, rhs in PRODUCOES:
        for simbolo in rhs:
            if not _e_nao_terminal(simbolo):
                terminais.add(simbolo)
    return terminais


def _calcular_first() -> dict[str, set[str]]:
    """FIRST de cada não-terminal, por ponto-fixo.

    ``EPSILON`` participa de FIRST quando o símbolo pode derivar a cadeia
    vazia. FIRST de um terminal é ele próprio (tratado direto nos laços).
    """
    first: dict[str, set[str]] = {nt: set() for nt in NAO_TERMINAIS}

    def first_de_sequencia(seq: list[str]) -> set[str]:
        resultado: set[str] = set()
        for simbolo in seq:
            if not _e_nao_terminal(simbolo):
                resultado.add(simbolo)
                return resultado
            resultado |= first[simbolo] - {EPSILON}
            if EPSILON not in first[simbolo]:
                return resultado
        resultado.add(EPSILON)
        return resultado

    mudou = True
    while mudou:
        mudou = False
        for lhs, rhs in PRODUCOES:
            if not rhs:  # produção ε
                if EPSILON not in first[lhs]:
                    first[lhs].add(EPSILON)
                    mudou = True
                continue
            novos = first_de_sequencia(rhs)
            if not novos <= first[lhs]:
                first[lhs] |= novos
                mudou = True
    return first


def _first_sequencia(seq: list[str], first: dict[str, set[str]]) -> set[str]:
    resultado: set[str] = set()
    for simbolo in seq:
        if not _e_nao_terminal(simbolo):
            resultado.add(simbolo)
            return resultado
        resultado |= first[simbolo] - {EPSILON}
        if EPSILON not in first[simbolo]:
            return resultado
    resultado.add(EPSILON)
    return resultado


def _calcular_follow(first: dict[str, set[str]]) -> dict[str, set[str]]:
    follow: dict[str, set[str]] = {nt: set() for nt in NAO_TERMINAIS}
    follow["programa"].add(FIM)

    mudou = True
    while mudou:
        mudou = False
        for lhs, rhs in PRODUCOES:
            for i, simbolo in enumerate(rhs):
                if not _e_nao_terminal(simbolo):
                    continue
                resto = rhs[i + 1 :]
                first_resto = _first_sequencia(resto, first) if resto else {EPSILON}
                adicionar = first_resto - {EPSILON}
                if EPSILON in first_resto:
                    adicionar |= follow[lhs]
                if not adicionar <= follow[simbolo]:
                    follow[simbolo] |= adicionar
                    mudou = True
    return follow


def _construir_tabela(
    first: dict[str, set[str]], follow: dict[str, set[str]]
) -> dict[tuple[str, str], int]:
    """Tabela ``M[nt, terminal] -> índice da produção``.

    Levanta ``AssertionError`` se houver conflito (gramática não-LL(1)).
    """
    tabela: dict[tuple[str, str], int] = {}

    def inserir(nt: str, terminal: str, indice: int) -> None:
        chave = (nt, terminal)
        if chave in tabela and tabela[chave] != indice:
            raise AssertionError(
                f"conflito LL(1) em M[{nt}, {terminal}]: "
                f"produções #{tabela[chave]} e #{indice}"
            )
        tabela[chave] = indice

    for indice, (lhs, rhs) in enumerate(PRODUCOES):
        first_rhs = _first_sequencia(rhs, first) if rhs else {EPSILON}
        for terminal in first_rhs - {EPSILON}:
            inserir(lhs, terminal, indice)
        if EPSILON in first_rhs:
            for terminal in follow[lhs]:
                inserir(lhs, terminal, indice)
    return tabela


def construir_gramatica() -> dict:
    """Devolve a gramática completa com FIRST, FOLLOW e tabela LL(1).

    A construção da tabela já valida a ausência de conflitos — chamar esta
    função é, em si, a verificação de que a gramática é LL(1).
    """
    first = _calcular_first()
    follow = _calcular_follow(first)
    tabela = _construir_tabela(first, follow)
    return {
        "producoes": PRODUCOES,
        "nao_terminais": NAO_TERMINAIS,
        "terminais": sorted(_terminais()),
        "first": first,
        "follow": follow,
        "tabela": tabela,
    }
