"""Erros e diagnósticos do compilador.

Distinguimos dois mecanismos, deliberadamente:

* **Erros léxicos e sintáticos** são *exceções* (:class:`ErroLexico`,
  :class:`ErroSintatico`). Eles interrompem o processamento do arquivo,
  pois sem tokens válidos ou sem uma árvore não há o que analisar adiante.
* **Erros semânticos** são *dados* (:class:`Diagnostico`), acumulados em
  uma lista. A análise semântica não aborta no primeiro problema: ela
  reporta o máximo possível em uma única execução (recuperação de erros).
"""

from __future__ import annotations

from dataclasses import dataclass


class ErroCompilacao(Exception):
    """Base para erros que interrompem uma etapa do compilador."""

    fase = "compilação"

    def __init__(self, mensagem: str, linha: int = 0, coluna: int = 0) -> None:
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        super().__init__(str(self))

    def __str__(self) -> str:
        local = ""
        if self.linha and self.coluna:
            local = f" (linha {self.linha}, coluna {self.coluna})"
        elif self.linha:
            local = f" (linha {self.linha})"
        return f"[{self.fase}]{local} {self.mensagem}"


class ErroLexico(ErroCompilacao):
    fase = "léxico"


class ErroSintatico(ErroCompilacao):
    fase = "sintático"


@dataclass
class Diagnostico:
    """Um erro semântico coletado (não interrompe a análise).

    ``categoria`` agrupa o tipo de problema (``"declaracao"``, ``"tipo"``,
    ``"controle"`` ...) para facilitar a leitura do relatório.
    """

    mensagem: str
    linha: int = 0
    categoria: str = "semântico"

    def __str__(self) -> str:
        local = f" (linha {self.linha})" if self.linha else ""
        return f"[semântico:{self.categoria}]{local} {self.mensagem}"
