"""Analisador léxico: um Autômato Finito Determinístico (AFD).

Cada estado do autômato é uma **função** (exigência do enunciado). Não se
usa nenhuma forma de expressão regular. A função :func:`tokenizar` percorre
o texto-fonte (já sem comentários) caractere a caractere, mantendo um
contexto mutável compartilhado, e despacha para a função do estado atual.

Estados:

    inicial            ponto de partida; decide a categoria do próximo token
    em_inteiro         acumulando dígitos de um inteiro
    em_real            acumulando dígitos após o ponto decimal
    em_identificador   acumulando letras maiúsculas (ident ou palavra reservada)
    pos_igual          viu '='; espera outro '=' para formar '=='
    pos_exclamacao     viu '!'; espera '=' para formar '!='
    pos_maior          viu '>'; pode virar '>' ou '>='
    pos_menor          viu '<'; pode virar '<' ou '<='

Convenção das funções de estado: recebem ``(caractere, contexto)`` e
devolvem ``(proximo_estado, consumiu)``. Quando ``consumiu`` é ``False``, o
mesmo caractere é reprocessado no novo estado (transição-ε implícita), o que
permite "fechar" um token ao encontrar o delimitador seguinte.
"""

from __future__ import annotations

from compilador.dominio.erros import ErroLexico
from compilador.dominio.tokens import (
    CAT_ABRE,
    CAT_FECHA,
    CAT_FIM,
    CAT_IDENT,
    CAT_INTEIRO,
    CAT_OPERADOR,
    CAT_PALAVRA,
    CAT_REAL,
    PALAVRAS_RESERVADAS,
    Token,
)

_OPERADORES_SIMPLES = "+-*|/%^"


def _e_digito(c: str) -> bool:
    return "0" <= c <= "9"


def _e_maiuscula(c: str) -> bool:
    return "A" <= c <= "Z"


def _e_minuscula(c: str) -> bool:
    return "a" <= c <= "z"


def _emitir(ctx: dict, categoria: str, lexema: str) -> None:
    ctx["tokens"].append(
        Token(
            categoria=categoria,
            lexema=lexema,
            linha=ctx["linha_inicio"],
            coluna=ctx["coluna_inicio"],
        )
    )
    ctx["buffer"] = ""


def _marcar_inicio(ctx: dict) -> None:
    ctx["linha_inicio"] = ctx["linha"]
    ctx["coluna_inicio"] = ctx["coluna"]


# --------------------------------------------------------------------------
# Funções de estado
# --------------------------------------------------------------------------


def _inicial(c: str, ctx: dict) -> tuple[str, bool]:
    if c in (" ", "\t", "\r", "\n"):
        return "inicial", True

    if c == "(":
        _marcar_inicio(ctx)
        _emitir(ctx, CAT_ABRE, "(")
        return "inicial", True
    if c == ")":
        _marcar_inicio(ctx)
        _emitir(ctx, CAT_FECHA, ")")
        return "inicial", True

    if _e_digito(c):
        _marcar_inicio(ctx)
        ctx["buffer"] = c
        return "em_inteiro", True

    if _e_maiuscula(c):
        _marcar_inicio(ctx)
        ctx["buffer"] = c
        return "em_identificador", True

    if c in _OPERADORES_SIMPLES:
        _marcar_inicio(ctx)
        _emitir(ctx, CAT_OPERADOR, c)
        return "inicial", True

    if c == "=":
        _marcar_inicio(ctx)
        return "pos_igual", True
    if c == "!":
        _marcar_inicio(ctx)
        return "pos_exclamacao", True
    if c == ">":
        _marcar_inicio(ctx)
        return "pos_maior", True
    if c == "<":
        _marcar_inicio(ctx)
        return "pos_menor", True

    if c == ".":
        raise ErroLexico(
            "número malformado: ponto decimal sem dígito antes",
            ctx["linha"],
            ctx["coluna"],
        )
    if _e_minuscula(c):
        raise ErroLexico(
            f"caractere minúsculo '{c}' — identificadores usam só letras maiúsculas",
            ctx["linha"],
            ctx["coluna"],
        )

    raise ErroLexico(f"caractere inválido '{c}'", ctx["linha"], ctx["coluna"])


def _em_inteiro(c: str, ctx: dict) -> tuple[str, bool]:
    if _e_digito(c):
        ctx["buffer"] += c
        return "em_inteiro", True
    if c == ".":
        ctx["buffer"] += c
        return "em_real", True
    if _e_maiuscula(c) or _e_minuscula(c):
        raise ErroLexico(
            f"número malformado '{ctx['buffer'] + c}': letra logo após dígitos",
            ctx["linha"],
            ctx["coluna"],
        )
    _emitir(ctx, CAT_INTEIRO, ctx["buffer"])
    return "inicial", False


def _em_real(c: str, ctx: dict) -> tuple[str, bool]:
    if _e_digito(c):
        ctx["buffer"] += c
        return "em_real", True
    if c == ".":
        raise ErroLexico(
            f"número malformado '{ctx['buffer'] + c}': mais de um ponto decimal",
            ctx["linha"],
            ctx["coluna"],
        )
    if ctx["buffer"].endswith("."):
        raise ErroLexico(
            f"número malformado '{ctx['buffer']}': ponto decimal sem dígito depois",
            ctx["linha"],
            ctx["coluna"],
        )
    if _e_maiuscula(c) or _e_minuscula(c):
        raise ErroLexico(
            f"número malformado '{ctx['buffer'] + c}': letra logo após dígitos",
            ctx["linha"],
            ctx["coluna"],
        )
    _emitir(ctx, CAT_REAL, ctx["buffer"])
    return "inicial", False


def _em_identificador(c: str, ctx: dict) -> tuple[str, bool]:
    if _e_maiuscula(c):
        ctx["buffer"] += c
        return "em_identificador", True
    if _e_minuscula(c):
        raise ErroLexico(
            f"identificador '{ctx['buffer'] + c}' contém letra minúscula",
            ctx["linha"],
            ctx["coluna"],
        )
    if _e_digito(c):
        raise ErroLexico(
            f"identificador '{ctx['buffer'] + c}' contém dígito",
            ctx["linha"],
            ctx["coluna"],
        )
    lexema = ctx["buffer"]
    categoria = CAT_PALAVRA if lexema in PALAVRAS_RESERVADAS else CAT_IDENT
    _emitir(ctx, categoria, lexema)
    return "inicial", False


def _pos_igual(c: str, ctx: dict) -> tuple[str, bool]:
    if c == "=":
        _emitir(ctx, CAT_OPERADOR, "==")
        return "inicial", True
    raise ErroLexico("'=' isolado — use '==' para igualdade", ctx["linha"], ctx["coluna"])


def _pos_exclamacao(c: str, ctx: dict) -> tuple[str, bool]:
    if c == "=":
        _emitir(ctx, CAT_OPERADOR, "!=")
        return "inicial", True
    raise ErroLexico("'!' isolado — use '!=' para diferença", ctx["linha"], ctx["coluna"])


def _pos_maior(c: str, ctx: dict) -> tuple[str, bool]:
    if c == "=":
        _emitir(ctx, CAT_OPERADOR, ">=")
        return "inicial", True
    _emitir(ctx, CAT_OPERADOR, ">")
    return "inicial", False


def _pos_menor(c: str, ctx: dict) -> tuple[str, bool]:
    if c == "=":
        _emitir(ctx, CAT_OPERADOR, "<=")
        return "inicial", True
    _emitir(ctx, CAT_OPERADOR, "<")
    return "inicial", False


_MAQUINA = {
    "inicial": _inicial,
    "em_inteiro": _em_inteiro,
    "em_real": _em_real,
    "em_identificador": _em_identificador,
    "pos_igual": _pos_igual,
    "pos_exclamacao": _pos_exclamacao,
    "pos_maior": _pos_maior,
    "pos_menor": _pos_menor,
}


def tokenizar(fonte_sem_comentarios: str) -> list[Token]:
    """Converte o texto-fonte (já sem comentários) em uma lista de tokens.

    A lista termina sempre com um token sentinela de categoria ``FIM`` (``$``),
    consumido pelo parser. Levanta :class:`ErroLexico` no primeiro caractere
    inválido — o léxico, por construção, não tem como prosseguir sem tokens.
    """
    ctx: dict = {
        "tokens": [],
        "buffer": "",
        "linha": 1,
        "coluna": 1,
        "linha_inicio": 1,
        "coluna_inicio": 1,
    }

    # O '\n' sentinela garante que um token grudado no fim do texto seja
    # fechado pelo seu estado (que então reprocessa o '\n' como separador).
    texto = fonte_sem_comentarios + "\n"
    estado = "inicial"
    indice = 0
    while indice < len(texto):
        c = texto[indice]
        proximo_estado, consumiu = _MAQUINA[estado](c, ctx)
        estado = proximo_estado
        if consumiu:
            if c == "\n":
                ctx["linha"] += 1
                ctx["coluna"] = 1
            else:
                ctx["coluna"] += 1
            indice += 1

    if estado in ("pos_igual", "pos_exclamacao"):
        raise ErroLexico("operador relacional incompleto no fim da entrada", ctx["linha"], ctx["coluna"])

    ctx["tokens"].append(Token(CAT_FIM, "$", ctx["linha"], ctx["coluna"]))
    return ctx["tokens"]
