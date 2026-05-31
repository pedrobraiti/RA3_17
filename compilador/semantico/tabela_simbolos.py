"""Tabela de símbolos e validação de declarações.

``construirTabelaSimbolos`` percorre a AST e registra cada variável de
memória (``MEM``) com seu tipo inferido, a linha de definição e as linhas
de uso. Durante o percurso valida:

* **uso antes da definição** — ``(MEM)`` antes de qualquer ``(V MEM)``;
* **redefinição incompatível** — ``(V2 MEM)`` com tipo diferente do fixado
  na primeira definição (tipos são fixos, fortes e estáticos);
* **``(N RES)`` fora de faixa** — ``N`` maior que o número de instruções
  anteriores.

A análise não aborta no primeiro problema: acumula uma lista de
:class:`~compilador.dominio.erros.Diagnostico`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from compilador.dominio import ast_nodes as ast
from compilador.dominio.erros import Diagnostico
from compilador.dominio.tipos import INDEF
from compilador.semantico.inferencia import inferir


@dataclass
class Simbolo:
    nome: str
    tipo: str
    linha_definicao: int
    linhas_uso: list[int] = field(default_factory=list)
    escopo: str = "global"


class TabelaSimbolos:
    """Mapa ``nome -> Simbolo`` com escopo único global (um arquivo = um escopo)."""

    def __init__(self) -> None:
        self._simbolos: dict[str, Simbolo] = {}

    def declarar(self, nome: str, tipo: str, linha: int) -> list[Diagnostico]:
        existente = self._simbolos.get(nome)
        if existente is None:
            self._simbolos[nome] = Simbolo(nome=nome, tipo=tipo, linha_definicao=linha)
            return []
        # Promove de indef para um tipo concreto, sem reclamar.
        if existente.tipo == INDEF and tipo != INDEF:
            existente.tipo = tipo
            return []
        if tipo == INDEF or existente.tipo == tipo:
            return []
        return [
            Diagnostico(
                f"redefinição da variável '{nome}' com tipo incompatível: "
                f"era '{existente.tipo}', recebeu '{tipo}'",
                linha,
                categoria="declaracao",
            )
        ]

    def registrar_uso(self, nome: str, linha: int) -> list[Diagnostico]:
        simbolo = self._simbolos.get(nome)
        if simbolo is None:
            return [
                Diagnostico(
                    f"uso da variável '{nome}' antes da definição "
                    f"(faltou um '(valor {nome})' antes)",
                    linha,
                    categoria="declaracao",
                )
            ]
        if linha and linha not in simbolo.linhas_uso:
            simbolo.linhas_uso.append(linha)
        return []

    def tipo_de(self, nome: str) -> str:
        simbolo = self._simbolos.get(nome)
        return simbolo.tipo if simbolo else INDEF

    def obter(self, nome: str) -> Simbolo | None:
        return self._simbolos.get(nome)

    def itens(self) -> list[Simbolo]:
        return [self._simbolos[n] for n in sorted(self._simbolos)]

    def __len__(self) -> int:
        return len(self._simbolos)

    def __contains__(self, nome: str) -> bool:
        return nome in self._simbolos


def construirTabelaSimbolos(arvore: ast.Programa) -> tuple[TabelaSimbolos, list[Diagnostico]]:
    """Constrói a tabela de símbolos e devolve ``(tabela, erros)``."""
    tabela = TabelaSimbolos()
    erros: list[Diagnostico] = []

    if not isinstance(arvore, ast.Programa):
        return tabela, erros

    def visitar(no: ast.No | None, instrucoes_anteriores: int) -> None:
        if no is None:
            return

        if isinstance(no, ast.EscritaMemoria):
            # Desce primeiro no valor: ele pode usar OUTRAS variáveis já
            # definidas, mas não a própria que está sendo definida agora.
            visitar(no.valor, instrucoes_anteriores)
            tipo = inferir(no.valor, tabela)
            erros.extend(tabela.declarar(no.nome, tipo, no.linha))
            return

        if isinstance(no, ast.LeituraMemoria):
            erros.extend(tabela.registrar_uso(no.nome, no.linha))
            return

        if isinstance(no, ast.ResultadoAnterior):
            if no.n > instrucoes_anteriores:
                erros.append(
                    Diagnostico(
                        f"(N RES) referencia {no.n} instrução(ões) atrás, mas só há "
                        f"{instrucoes_anteriores} antes desta",
                        no.linha,
                        categoria="declaracao",
                    )
                )
            return

        for filho in no.filhos():
            visitar(filho, instrucoes_anteriores)

    for indice, instrucao in enumerate(arvore.instrucoes):
        visitar(instrucao, indice)

    return tabela, erros
