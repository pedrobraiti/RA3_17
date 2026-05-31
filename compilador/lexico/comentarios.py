"""Remoção de comentários ``*{ ... }*`` antes da tokenização.

Os comentários da linguagem (Fase 3):

* abrem com ``*{`` e fecham com ``}*``;
* podem ocupar uma linha inteira, o fim de uma linha de código ou aparecer
  entre dois tokens de uma mesma expressão;
* podem **atravessar várias linhas**;
* **não** são aninhados — o primeiro ``}*`` encerra o comentário.

A remoção substitui cada caractere comentado por um espaço, preservando o
comprimento das linhas. Assim, a linha e a coluna de cada token *real*
permanecem corretas para as mensagens de erro das etapas seguintes.

Conforme o enunciado, o analisador léxico trata os comentários como tokens
de tipo "comentário" e os **descarta** antes de gerar o vetor de tokens —
aqui devolvemos tanto o texto limpo quanto a lista de comentários removidos
(útil para depuração e testes).
"""

from __future__ import annotations

from dataclasses import dataclass

from compilador.dominio.erros import ErroLexico

_ABRE = "*{"
_FECHA = "}*"


@dataclass(frozen=True)
class Comentario:
    """Um comentário removido, com a posição de abertura."""

    texto: str
    linha: int
    coluna: int


def remover_comentarios(fonte: str) -> tuple[str, list[Comentario]]:
    """Devolve ``(texto_sem_comentarios, comentarios)``.

    Levanta :class:`ErroLexico` se um comentário não for fechado até o fim
    do arquivo.
    """
    linhas = fonte.split("\n")
    limpas: list[str] = []
    comentarios: list[Comentario] = []

    dentro = False
    abertura_linha = 0
    abertura_coluna = 0
    acumulado: list[str] = []

    for numero_linha, linha in enumerate(linhas, start=1):
        saida: list[str] = []
        coluna = 0
        total = len(linha)

        while coluna < total:
            par = linha[coluna : coluna + 2]

            if not dentro:
                if par == _ABRE:
                    dentro = True
                    abertura_linha = numero_linha
                    abertura_coluna = coluna + 1
                    acumulado = [_ABRE]
                    saida.append("  ")
                    coluna += 2
                    continue
                saida.append(linha[coluna])
                coluna += 1
            else:
                if par == _FECHA:
                    acumulado.append(_FECHA)
                    comentarios.append(
                        Comentario(
                            texto="".join(acumulado),
                            linha=abertura_linha,
                            coluna=abertura_coluna,
                        )
                    )
                    dentro = False
                    saida.append("  ")
                    coluna += 2
                    continue
                acumulado.append(linha[coluna])
                saida.append(" ")
                coluna += 1

        if dentro:
            acumulado.append("\n")
        limpas.append("".join(saida))

    if dentro:
        raise ErroLexico(
            "comentário não fechado (faltou '}*' antes do fim do arquivo)",
            linha=abertura_linha,
            coluna=abertura_coluna,
        )

    return "\n".join(limpas), comentarios
