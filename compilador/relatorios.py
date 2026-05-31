"""Serialização dos artefatos do compilador (texto, Markdown e JSON).

Mantemos a serialização concentrada aqui — fora dos nós da árvore e das
etapas de análise — para que cada etapa permaneça focada na sua lógica e os
formatos de saída possam evoluir sem tocá-las.
"""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass

from compilador.dominio import ast_nodes as ast
from compilador.dominio.tokens import Token


# --------------------------------------------------------------------------
# Tokens
# --------------------------------------------------------------------------


def tokens_para_texto(tokens: list[Token]) -> str:
    linhas = ["# Tokens da última execução", "# categoria | lexema | linha | coluna", ""]
    for token in tokens:
        if token.categoria == "FIM":
            continue
        linhas.append(f"{token.categoria}\t{token.lexema}\t{token.linha}\t{token.coluna}")
    return "\n".join(linhas) + "\n"


# --------------------------------------------------------------------------
# Árvore (texto e JSON) — serve para a AST e para a árvore atribuída
# --------------------------------------------------------------------------


def arvore_para_texto(no: ast.No, _nivel: int = 0) -> str:
    recuo = "  " * _nivel
    cabecalho = recuo + no.rotulo()
    extras = []
    if no.tipo:
        extras.append(f"tipo={no.tipo}")
    if no.meta:
        if "rotulos" in no.meta:
            extras.append("rotulos=" + ",".join(no.meta["rotulos"].values()))
        if "rotulo_mem" in no.meta:
            extras.append(no.meta["rotulo_mem"])
    if extras:
        cabecalho += "  [" + " ".join(extras) + "]"
    linhas = [cabecalho]
    for filho in no.filhos():
        linhas.append(arvore_para_texto(filho, _nivel + 1))
    return "\n".join(linhas)


def no_para_dict(no: ast.No) -> dict:
    """Converte um nó (e seus filhos) num dicionário JSON-serializável."""
    dados: dict = {"no": type(no).__name__, "linha": no.linha}
    if no.tipo:
        dados["tipo"] = no.tipo
    for campo in fields(no):
        if campo.name in ("linha", "tipo", "meta"):
            continue
        valor = getattr(no, campo.name)
        dados[campo.name] = _valor_para_json(valor)
    if no.meta:
        dados["meta"] = no.meta
    return dados


def _valor_para_json(valor):
    if isinstance(valor, ast.No):
        return no_para_dict(valor)
    if isinstance(valor, list):
        return [_valor_para_json(item) for item in valor]
    if is_dataclass(valor):
        return {c.name: _valor_para_json(getattr(valor, c.name)) for c in fields(valor)}
    return valor


def arvore_para_json(programa: ast.Programa) -> str:
    return json.dumps(no_para_dict(programa), ensure_ascii=False, indent=2)


def arvore_para_markdown(programa: ast.Programa, titulo: str) -> str:
    linhas = [f"# {titulo}", ""]
    linhas.append("Cada nó traz seu `tipo` inferido e, quando aplicável, os")
    linhas.append("metadados de geração de código (`meta`).")
    linhas.append("")
    linhas.append("```text")
    linhas.append(arvore_para_texto(programa))
    linhas.append("```")
    return "\n".join(linhas) + "\n"


# --------------------------------------------------------------------------
# Tabela de símbolos
# --------------------------------------------------------------------------


def tabela_para_markdown(tabela) -> str:
    linhas = ["# Tabela de Símbolos", ""]
    if len(tabela) == 0:
        linhas.append("_Nenhuma variável de memória declarada._")
        return "\n".join(linhas) + "\n"
    linhas.append("| Nome | Tipo | Escopo | Linha def. | Linhas de uso |")
    linhas.append("|------|------|--------|-----------:|---------------|")
    for simbolo in tabela.itens():
        usos = ", ".join(str(u) for u in simbolo.linhas_uso) or "—"
        linhas.append(
            f"| `{simbolo.nome}` | {simbolo.tipo} | {simbolo.escopo} | "
            f"{simbolo.linha_definicao} | {usos} |"
        )
    return "\n".join(linhas) + "\n"


# --------------------------------------------------------------------------
# Erros semânticos
# --------------------------------------------------------------------------


def erros_para_markdown(erros: list, titulo: str = "Relatório de Erros Semânticos") -> str:
    linhas = [f"# {titulo}", ""]
    if not erros:
        linhas.append("_Nenhum erro encontrado na última execução._")
        return "\n".join(linhas) + "\n"
    linhas.append(f"Total: **{len(erros)}**")
    linhas.append("")
    for i, erro in enumerate(erros, 1):
        linhas.append(f"{i}. {erro}")
    return "\n".join(linhas) + "\n"


# --------------------------------------------------------------------------
# Gramática LL(1): produções, FIRST, FOLLOW e tabela
# --------------------------------------------------------------------------


def gramatica_para_markdown(gramatica: dict) -> str:
    def fmt(conjunto: set[str]) -> str:
        itens = sorted(s if s else "ε" for s in conjunto)
        return "{ " + ", ".join(itens) + " }" if itens else "{ }"

    linhas = ["# Gramática LL(1) — Produções, FIRST, FOLLOW e Tabela", ""]
    linhas.append("## 1. Produções")
    linhas.append("")
    linhas.append("| # | Não-terminal | Produção |")
    linhas.append("|--:|---|---|")
    for i, (lhs, rhs) in enumerate(gramatica["producoes"]):
        corpo = " ".join(rhs) if rhs else "ε"
        linhas.append(f"| {i} | {lhs} | {corpo} |")

    linhas.append("")
    linhas.append("## 2. Conjuntos FIRST")
    linhas.append("")
    linhas.append("| Não-terminal | FIRST |")
    linhas.append("|---|---|")
    for nt in gramatica["nao_terminais"]:
        linhas.append(f"| {nt} | {fmt(gramatica['first'][nt])} |")

    linhas.append("")
    linhas.append("## 3. Conjuntos FOLLOW")
    linhas.append("")
    linhas.append("| Não-terminal | FOLLOW |")
    linhas.append("|---|---|")
    for nt in gramatica["nao_terminais"]:
        linhas.append(f"| {nt} | {fmt(gramatica['follow'][nt])} |")

    linhas.append("")
    linhas.append("## 4. Tabela de Análise LL(1)")
    linhas.append("")
    linhas.append("A tabela é livre de conflitos — a gramática é LL(1).")
    linhas.append("")
    linhas.append("| M[não-terminal, terminal] | Produção |")
    linhas.append("|---|---|")
    for (nt, terminal), indice in sorted(gramatica["tabela"].items()):
        lhs, rhs = gramatica["producoes"][indice]
        corpo = " ".join(rhs) if rhs else "ε"
        linhas.append(f"| M[{nt}, {terminal}] | #{indice}: {lhs} → {corpo} |")
    return "\n".join(linhas) + "\n"
