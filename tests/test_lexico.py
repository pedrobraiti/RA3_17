"""Testes do analisador léxico: comentários e tokenização por AFD."""

from __future__ import annotations

import pytest

from compilador.dominio.erros import ErroLexico
from compilador.lexico.automato import tokenizar
from compilador.lexico.comentarios import remover_comentarios
from tests.apoio import tokens_de


def categorias(fonte: str) -> list[tuple[str, str]]:
    return [(t.categoria, t.lexema) for t in tokens_de(fonte) if t.categoria != "FIM"]


# -- comentários -----------------------------------------------------------


def test_comentario_linha_inteira_e_descartado():
    limpo, coments = remover_comentarios("*{ tudo isto some }*\n(10 3 +)")
    assert len(coments) == 1
    assert "10" in limpo and "tudo" not in limpo


def test_comentario_no_fim_da_linha():
    _, coments = remover_comentarios("(10 3 +)   *{ nota }*")
    assert len(coments) == 1


def test_comentario_entre_tokens_preserva_colunas():
    # o '2' deve manter sua coluna original mesmo com comentário no meio
    tokens = tokens_de("(10 *{ x }* 2 +)")
    lexemas = [t.lexema for t in tokens if t.categoria != "FIM"]
    assert lexemas == ["(", "10", "2", "+", ")"]


def test_comentario_multilinha():
    limpo, coments = remover_comentarios("(1\n*{ varias\nlinhas }*\n2 +)")
    assert len(coments) == 1
    assert "varias" not in limpo


def test_comentario_nao_fechado_e_erro():
    with pytest.raises(ErroLexico):
        remover_comentarios("(10 3 +) *{ nunca fecha")


# -- tokenização -----------------------------------------------------------


def test_inteiro_e_real_distintos():
    assert categorias("42 3.14") == [("INTEIRO", "42"), ("REAL", "3.14")]


def test_palavras_reservadas_viram_palavra_e_resto_ident():
    assert categorias("CONTADOR TRUE START AND") == [
        ("IDENT", "CONTADOR"),
        ("PALAVRA", "TRUE"),
        ("PALAVRA", "START"),
        ("PALAVRA", "AND"),
    ]


def test_relacionais_de_dois_caracteres():
    assert categorias(">= <= == != > <") == [
        ("OPERADOR", ">="),
        ("OPERADOR", "<="),
        ("OPERADOR", "=="),
        ("OPERADOR", "!="),
        ("OPERADOR", ">"),
        ("OPERADOR", "<"),
    ]


def test_operadores_aritmeticos():
    assert [c[1] for c in categorias("+ - * | / % ^")] == list("+-*|/%^")


@pytest.mark.parametrize(
    "fonte",
    [
        "3.14.5",      # dois pontos
        ".5",          # ponto sem dígito antes
        "10X",         # letra após número
        "mem",         # minúscula
        "=",           # '=' isolado
        "!",           # '!' isolado
        "&",           # caractere inválido
        "3.",          # ponto sem dígito depois
    ],
)
def test_erros_lexicos(fonte):
    with pytest.raises(ErroLexico):
        tokenizar(fonte)
