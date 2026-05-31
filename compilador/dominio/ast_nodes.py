"""Nós da Árvore Sintática Abstrata (AST) e da Árvore Atribuída.

A AST é construída pelo parser (etapa sintática). As etapas semânticas
**anotam** cada nó com:

* ``tipo``  — o tipo inferido (preenchido por ``verificarTipos``);
* ``meta``  — metadados para a geração de código (preenchidos por
  ``gerarArvoreAtribuida``): registrador-alvo, rótulos de salto, etc.

Usamos ``dataclasses`` (um nó = uma classe) em vez de dicionários genéricos:
isso dá nomes de campo verificáveis, habilita o *visitor* por despacho de
classe e mantém o código de cada etapa legível. A serialização para JSON /
Markdown é responsabilidade de :mod:`compilador.relatorios`, não dos nós.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class No:
    """Base de todo nó da árvore.

    ``linha`` localiza o nó no arquivo-fonte (para mensagens de erro).
    ``tipo`` e ``meta`` começam vazios e são preenchidos pelas etapas
    semânticas — manter os campos no nó evita estruturas paralelas.
    """

    linha: int = 0
    tipo: str | None = field(default=None)
    meta: dict = field(default_factory=dict)

    def rotulo(self) -> str:
        """Rótulo curto do nó para impressão da árvore (sobrescrito)."""
        return type(self).__name__

    def filhos(self) -> list["No"]:
        """Subnós, na ordem de avaliação (sobrescrito por nós compostos)."""
        return []


# --------------------------------------------------------------------------
# Raiz
# --------------------------------------------------------------------------


@dataclass
class Programa(No):
    instrucoes: list[No] = field(default_factory=list)

    def rotulo(self) -> str:
        return "programa"

    def filhos(self) -> list[No]:
        return list(self.instrucoes)


# --------------------------------------------------------------------------
# Literais
# --------------------------------------------------------------------------


@dataclass
class LiteralInteiro(No):
    valor: int = 0

    def rotulo(self) -> str:
        return f"int({self.valor})"


@dataclass
class LiteralReal(No):
    valor: float = 0.0

    def rotulo(self) -> str:
        return f"real({self.valor})"


@dataclass
class LiteralBool(No):
    valor: bool = False

    def rotulo(self) -> str:
        return f"bool({'TRUE' if self.valor else 'FALSE'})"


# --------------------------------------------------------------------------
# Memória e histórico
# --------------------------------------------------------------------------


@dataclass
class LeituraMemoria(No):
    """``(MEM)`` — lê o valor armazenado em ``MEM``."""

    nome: str = ""

    def rotulo(self) -> str:
        return f"ler({self.nome})"


@dataclass
class EscritaMemoria(No):
    """``(V MEM)`` — armazena o valor da expressão ``V`` em ``MEM``."""

    nome: str = ""
    valor: No | None = None

    def rotulo(self) -> str:
        return f"escrever({self.nome})"

    def filhos(self) -> list[No]:
        return [self.valor] if self.valor is not None else []


@dataclass
class ResultadoAnterior(No):
    """``(N RES)`` — resultado da expressão ``N`` linhas atrás."""

    n: int = 0

    def rotulo(self) -> str:
        return f"res({self.n})"


# --------------------------------------------------------------------------
# Operações
# --------------------------------------------------------------------------


@dataclass
class OperacaoBinaria(No):
    """``(a b op)`` — aritmética, relacional ou lógica binária (AND/OR)."""

    operador: str = ""
    esquerda: No | None = None
    direita: No | None = None

    def rotulo(self) -> str:
        return f"op({self.operador})"

    def filhos(self) -> list[No]:
        return [n for n in (self.esquerda, self.direita) if n is not None]


@dataclass
class OperacaoUnaria(No):
    """``(a NOT)`` — negação lógica."""

    operador: str = "NOT"
    operando: No | None = None

    def rotulo(self) -> str:
        return f"unario({self.operador})"

    def filhos(self) -> list[No]:
        return [self.operando] if self.operando is not None else []


# --------------------------------------------------------------------------
# Estruturas de controle
# --------------------------------------------------------------------------


@dataclass
class Se(No):
    """``(cond bloco IF)``."""

    condicao: No | None = None
    entao: No | None = None

    def rotulo(self) -> str:
        return "se"

    def filhos(self) -> list[No]:
        return [n for n in (self.condicao, self.entao) if n is not None]


@dataclass
class SeSenao(No):
    """``(cond entao senao IFELSE)``."""

    condicao: No | None = None
    entao: No | None = None
    senao: No | None = None

    def rotulo(self) -> str:
        return "se_senao"

    def filhos(self) -> list[No]:
        return [n for n in (self.condicao, self.entao, self.senao) if n is not None]


@dataclass
class Enquanto(No):
    """``(cond corpo WHILE)``."""

    condicao: No | None = None
    corpo: No | None = None

    def rotulo(self) -> str:
        return "enquanto"

    def filhos(self) -> list[No]:
        return [n for n in (self.condicao, self.corpo) if n is not None]


# --------------------------------------------------------------------------
# Visitor por despacho de classe
# --------------------------------------------------------------------------


class Visitante:
    """Visitante genérico: despacha para ``visitar_<NomeDaClasse>``.

    Subclasses implementam apenas os métodos dos nós que lhes interessam;
    o *fallback* :meth:`visitar_generico` cobre o resto. Esse padrão (um
    método por tipo de nó) substitui a varredura por ``dict`` e mantém cada
    etapa semântica desacoplada da estrutura interna dos nós.
    """

    def visitar(self, no: No):
        metodo = getattr(self, f"visitar_{type(no).__name__}", self.visitar_generico)
        return metodo(no)

    def visitar_generico(self, no: No):
        for filho in no.filhos():
            self.visitar(filho)
