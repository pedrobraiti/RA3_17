"""Testes do parser LL(1) e da construção da gramática."""

from __future__ import annotations

import pytest

from compilador.dominio import ast_nodes as ast
from compilador.dominio.erros import ErroSintatico
from compilador.sintatico.gramatica import construir_gramatica
from tests.apoio import arvore_de, programa


def test_gramatica_e_ll1_sem_conflitos():
    # A própria construção da tabela levanta erro se houver conflito.
    g = construir_gramatica()
    assert g["tabela"]  # tabela não vazia
    assert "programa" in g["nao_terminais"]


def test_formas_basicas_viram_os_nos_certos():
    arvore = arvore_de(
        programa(
            "(10 3 +)",
            "(5 CONT)",
            "(CONT)",
            "(2 RES)",
            "((10 0 >) NOT)",
            "((10 0 >) (1 X) IF)",
            "((10 0 >) (1 X) (2 X) IFELSE)",
            "((10 0 >) (1 X) WHILE)",
        )
    )
    tipos = [type(n) for n in arvore.instrucoes]
    assert tipos == [
        ast.OperacaoBinaria,
        ast.EscritaMemoria,
        ast.LeituraMemoria,
        ast.ResultadoAnterior,
        ast.OperacaoUnaria,
        ast.Se,
        ast.SeSenao,
        ast.Enquanto,
    ]


def test_aninhamento_profundo():
    arvore = arvore_de(programa("((((1 2 +) 3 *) 4 -) 5 |)"))
    assert isinstance(arvore.instrucoes[0], ast.OperacaoBinaria)


@pytest.mark.parametrize(
    "fonte",
    [
        "(START)\n(+ 3 2)\n(END)",          # operador antes (não é RPN)
        "(10 3 +)\n(END)",                   # falta (START)
        "(START)\n(10 3 +)",                 # falta (END)
        "(START)\n(3 2 + 5)\n(END)",         # operandos a mais
        "(START)\n(3 2 IFELSE)\n(END)",      # IFELSE com aridade errada
        "(START)\n((1 2 +)\n(END)",          # parêntese não fechado
        "(START)\n(1 RES MEM)\n(END)",       # forma inválida após RES
        "(START)\n(X 3 +)\n(END)",           # identificador nu como valor
    ],
)
def test_erros_sintaticos(fonte):
    with pytest.raises(ErroSintatico):
        arvore_de(fonte)


def test_conteudo_apos_end_e_erro():
    with pytest.raises(ErroSintatico):
        arvore_de("(START)\n(10 3 +)\n(END)\n(1 2 +)")
