"""Testes da análise semântica: tabela de símbolos e verificação de tipos."""

from __future__ import annotations

import pytest

from compilador.dominio.tipos import BOOL, INT, REAL, UNIT
from tests.apoio import analisar, programa


def tem_erro(erros, trecho: str) -> bool:
    return any(trecho in str(e) for e in erros)


# -- tipos básicos e inferência -------------------------------------------


def test_tipos_de_literais_e_operacoes():
    arvore, _, erros = analisar(
        programa("(10 3 +)", "(10.0 3.0 |)", "(10 0 >)", "(TRUE FALSE AND)")
    )
    assert erros == []
    assert [n.tipo for n in arvore.instrucoes] == [INT, REAL, BOOL, BOOL]


def test_potencia_e_divisoes_inteiras():
    _, _, erros = analisar(programa("(2 5 ^)", "(10 3 /)", "(10 3 %)"))
    assert erros == []


# -- sem promoção implícita -----------------------------------------------


def test_sem_promocao_int_real():
    _, _, erros = analisar(programa("(1 2.5 +)"))
    assert tem_erro(erros, "sem promoção")


def test_divisao_real_exige_reais():
    _, _, erros = analisar(programa("(10 3 |)"))
    assert tem_erro(erros, "divisão real")


def test_divisao_inteira_exige_inteiros():
    _, _, erros = analisar(programa("(10.0 3.0 /)"))
    assert tem_erro(erros, "inteiro")


# -- lógicos ---------------------------------------------------------------


def test_and_exige_bool():
    _, _, erros = analisar(programa("(TRUE 1 AND)"))
    assert tem_erro(erros, "lógico")


def test_not_exige_bool():
    _, _, erros = analisar(programa("(10 NOT)"))
    assert tem_erro(erros, "NOT")


# -- variáveis -------------------------------------------------------------


def test_uso_antes_da_definicao():
    _, _, erros = analisar(programa("((X) 1 +)"))
    assert tem_erro(erros, "antes da definição")


def test_redefinicao_incompativel():
    _, _, erros = analisar(programa("(10 X)", "(2.5 X)"))
    assert tem_erro(erros, "incompatível")


def test_redefinicao_mesmo_tipo_ok():
    _, tabela, erros = analisar(programa("(10 X)", "(20 X)"))
    assert erros == []
    assert tabela.tipo_de("X") == INT


def test_variavel_registra_tipo_e_usos():
    _, tabela, _ = analisar(programa("(5 CONT)", "((CONT) 2 *)", "((CONT) 0 >)"))
    simbolo = tabela.obter("CONT")
    assert simbolo.tipo == INT
    assert len(simbolo.linhas_uso) == 2


# -- comandos especiais ----------------------------------------------------


def test_res_fora_de_faixa():
    _, _, erros = analisar(programa("(1 2 +)", "(99 RES)"))
    assert tem_erro(erros, "RES")


def test_res_valido_herda_tipo():
    arvore, _, erros = analisar(programa("(1 2 +)", "(1 RES)"))
    assert erros == []
    assert arvore.instrucoes[1].tipo == INT


# -- controle --------------------------------------------------------------


def test_condicao_if_deve_ser_bool():
    _, _, erros = analisar(programa("((1 2 +) (3 4 +) IF)"))
    assert tem_erro(erros, "condição do IF")


def test_condicao_while_deve_ser_bool():
    _, _, erros = analisar(programa("((5 1 +) (1 2 +) WHILE)"))
    assert tem_erro(erros, "condição do WHILE")


def test_while_tem_tipo_unit():
    arvore, _, erros = analisar(programa("(5 C)", "(((C) 0 >) (((C) 1 -) C) WHILE)"))
    assert erros == []
    assert arvore.instrucoes[1].tipo == UNIT


def test_ifelse_ramos_divergentes():
    _, _, erros = analisar(programa("((1 2 <) (3 4 +) (3.0 4.0 +) IFELSE)"))
    assert tem_erro(erros, "divergentes")


def test_ifelse_ramos_iguais_ok():
    arvore, _, erros = analisar(programa("((1 2 <) (3 X) (4 X) IFELSE)"))
    assert erros == []
    assert arvore.instrucoes[0].tipo == INT
