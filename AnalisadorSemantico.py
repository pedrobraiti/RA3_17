#!/usr/bin/env python3
# Integrantes do grupo (ordem alfabética):
# Pedro Alessandrini Braiti - pedrobraiti
# Thiago Aguiar - Imthiagoaguiar
#
# Nome do grupo no Canvas: RA3_17
# Instituição: Pontifícia Universidade Católica do Paraná
# Disciplina: Linguagens Formais e Compiladores
# Professor: Frank Coelho de Alcantara
"""Analisador Semântico (Fase 3) — linha de comando.

Uso:
    python AnalisadorSemantico.py teste1.txt [--saida DIRETORIO]

Executa, em ordem, as três análises sobre o arquivo-fonte e gera os
artefatos no diretório de saída (padrão: ``saida/``):

    1. léxica + sintática  (prepararEntradaSemantica)
    2. tabela de símbolos  (construirTabelaSimbolos)
    3. verificação de tipos (verificarTipos)
    4. árvore atribuída    (gerarArvoreAtribuida)
    5. Assembly ARMv7      (gerarAssembly) — só se não houver erros

Códigos de saída: 0 = sem erros; 1 = erro léxico/sintático; 2 = erro
semântico. O Assembly **nunca** é gerado quando há erros — e um ``.s``
antigo é removido para não enganar a avaliação.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from compilador import relatorios
from compilador.codegen.armv7 import gerarAssembly
from compilador.pipeline import prepararEntradaSemantica
from compilador.semantico.arvore_atribuida import gerarArvoreAtribuida
from compilador.semantico.tabela_simbolos import construirTabelaSimbolos
from compilador.semantico.verificacao_tipos import verificarTipos


def _configurar_console() -> None:
    # Garante UTF-8 no terminal Windows para as mensagens acentuadas.
    for fluxo in (sys.stdout, sys.stderr):
        reconfigurar = getattr(fluxo, "reconfigure", None)
        if reconfigurar:
            try:
                reconfigurar(encoding="utf-8")
            except (ValueError, OSError):
                pass


def _secao(titulo: str) -> None:
    print()
    print("=" * 64)
    print(titulo)
    print("=" * 64)


def _escrever(caminho: Path, conteudo: str) -> Path:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


def _remover_assembly_antigo(saida: Path) -> None:
    antigo = saida / "ultima_execucao.s"
    if antigo.exists():
        antigo.unlink()


def main(argv: list[str] | None = None) -> int:
    _configurar_console()
    parser = argparse.ArgumentParser(
        description="Analisador Semântico (Fase 3) — linguagem RPN tipada → ARMv7",
    )
    parser.add_argument("arquivo", help="arquivo-fonte .txt com o programa")
    parser.add_argument(
        "--saida", default="saida", help="diretório dos artefatos (padrão: saida/)"
    )
    args = parser.parse_args(argv)

    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)
    _escrever(saida / "ARQUIVO_USADO.txt", args.arquivo + "\n")

    print(f"Arquivo analisado : {args.arquivo}")

    # ---------------------------------------------------------------
    # 1) Léxico + Sintático
    # ---------------------------------------------------------------
    entrada = prepararEntradaSemantica(args.arquivo)

    if entrada.tokens:
        _escrever(
            saida / "tokens_ultima_execucao.txt",
            relatorios.tokens_para_texto(entrada.tokens),
        )
    if entrada.gramatica is not None:
        _escrever(
            saida / "gramatica_ll1.md",
            relatorios.gramatica_para_markdown(entrada.gramatica),
        )

    _secao("Análise Léxica")
    print(f"Tokens reconhecidos  : {sum(1 for t in entrada.tokens if t.categoria != 'FIM')}")
    print(f"Comentários removidos: {len(entrada.comentarios)}")

    _secao("Análise Sintática")
    if entrada.erros_lexsint:
        for mensagem in entrada.erros_lexsint:
            print(f"  {mensagem}")
        _escrever(
            saida / "erros_lexico_sintatico.md",
            relatorios.erros_para_markdown(
                entrada.erros_lexsint, titulo="Relatório de Erros Léxicos / Sintáticos"
            ),
        )
        _remover_assembly_antigo(saida)
        print()
        print(f"Relatório de erros : {saida / 'erros_lexico_sintatico.md'}")
        print("Assembly NÃO gerado (há erros léxicos/sintáticos).")
        return 1

    print("Árvore sintática construída com sucesso.")
    arvore = entrada.arvore

    # ---------------------------------------------------------------
    # 2) Tabela de símbolos  +  3) Verificação de tipos
    # ---------------------------------------------------------------
    tabela, erros_tabela = construirTabelaSimbolos(arvore)
    arvore, erros_tipos = verificarTipos(arvore, tabela)
    erros_semanticos = list(erros_tabela) + list(erros_tipos)

    caminho_tabela = _escrever(
        saida / "tabela_simbolos.md", relatorios.tabela_para_markdown(tabela)
    )
    _escrever(
        saida / "erros_semanticos.md",
        relatorios.erros_para_markdown(erros_semanticos),
    )

    # ---------------------------------------------------------------
    # 4) Árvore atribuída (gerada sempre, para servir de artefato)
    # ---------------------------------------------------------------
    gerarArvoreAtribuida(arvore, tabela)
    caminho_arvore_md = _escrever(
        saida / "arvore_atribuida.md",
        relatorios.arvore_para_markdown(arvore, "Árvore Sintática Atribuída"),
    )
    _escrever(saida / "arvore_atribuida.json", relatorios.arvore_para_json(arvore))

    _secao("Análise Semântica")
    print(f"Variáveis declaradas : {len(tabela)}")
    print(f"Erros semânticos     : {len(erros_semanticos)}")
    for erro in erros_semanticos:
        print(f"  {erro}")

    if erros_semanticos:
        _remover_assembly_antigo(saida)
        print()
        print(f"Tabela de símbolos : {caminho_tabela}")
        print(f"Árvore atribuída   : {caminho_arvore_md}")
        print(f"Relatório de erros : {saida / 'erros_semanticos.md'}")
        print("Assembly NÃO gerado (há erros semânticos).")
        return 2

    # ---------------------------------------------------------------
    # 5) Geração de Assembly (programa semanticamente válido)
    # ---------------------------------------------------------------
    assembly = gerarAssembly(arvore)
    caminho_asm = _escrever(saida / "ultima_execucao.s", assembly)

    _secao("Resumo")
    print("Análise concluída sem erros. Artefatos gerados:")
    print(f"  Tokens           : {saida / 'tokens_ultima_execucao.txt'}")
    print(f"  Gramática LL(1)  : {saida / 'gramatica_ll1.md'}")
    print(f"  Tabela símbolos  : {caminho_tabela}")
    print(f"  Erros semânticos : {saida / 'erros_semanticos.md'}")
    print(f"  Árvore atribuída : {caminho_arvore_md}")
    print(f"  Árvore (JSON)    : {saida / 'arvore_atribuida.json'}")
    print(f"  Assembly ARMv7   : {caminho_asm}")
    print()
    print("Árvore sintática atribuída (resumo):")
    print(relatorios.arvore_para_texto(arvore))
    return 0


if __name__ == "__main__":
    sys.exit(main())
