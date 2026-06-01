"""Testes ponta a ponta pela CLI (AnalisadorSemantico.main)."""

from __future__ import annotations

import importlib

import pytest

from tests.apoio import RAIZ

cli = importlib.import_module("AnalisadorSemantico")


def roda(nome: str, tmp_path) -> int:
    arquivo = str(RAIZ / nome)
    saida = str(tmp_path / "saida")
    return cli.main([arquivo, "--saida", saida])


@pytest.mark.parametrize("nome", ["teste1.txt", "teste2.txt", "teste3.txt"])
def test_arquivos_validos_geram_assembly(nome, tmp_path):
    assert roda(nome, tmp_path) == 0
    asm = (tmp_path / "saida" / "ultima_execucao.s").read_text(encoding="utf-8")
    assert asm.startswith(".global _start")
    assert ".syntax" not in asm  # diretiva rejeitada pelo montador do Cpulator
    assert "_start:" in asm
    assert ".data" in asm
    assert "__exibir_hex" in asm
    erros = (tmp_path / "saida" / "erros_semanticos.md").read_text(encoding="utf-8")
    assert "Nenhum erro" in erros


def test_erro_lexico_codigo_1(tmp_path):
    assert roda("teste_erro_lexico.txt", tmp_path) == 1
    assert not (tmp_path / "saida" / "ultima_execucao.s").exists()


def test_erro_sintatico_codigo_1(tmp_path):
    assert roda("teste_erro_sintatico.txt", tmp_path) == 1
    assert not (tmp_path / "saida" / "ultima_execucao.s").exists()


def test_erro_semantico_codigo_2_sem_assembly(tmp_path):
    assert roda("teste_erro_semantico.txt", tmp_path) == 2
    assert not (tmp_path / "saida" / "ultima_execucao.s").exists()
    relatorio = (tmp_path / "saida" / "erros_semanticos.md").read_text(encoding="utf-8")
    assert "Total" in relatorio


def test_erro_semantico_remove_assembly_antigo(tmp_path):
    # gera um .s válido e depois roda um arquivo com erro semântico:
    # o .s antigo deve ser apagado.
    saida = tmp_path / "saida"
    cli.main([str(RAIZ / "teste1.txt"), "--saida", str(saida)])
    assert (saida / "ultima_execucao.s").exists()
    cli.main([str(RAIZ / "teste_erro_semantico.txt"), "--saida", str(saida)])
    assert not (saida / "ultima_execucao.s").exists()


def test_assembly_tem_rotulos_de_controle(tmp_path):
    roda("teste1.txt", tmp_path)
    asm = (tmp_path / "saida" / "ultima_execucao.s").read_text(encoding="utf-8")
    # rótulos vindos da árvore atribuída devem aparecer no Assembly
    assert "L_while_ini_" in asm
    assert "L_ifelse_fim_" in asm
