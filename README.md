# RA3_17 — Analisador Semântico de uma Linguagem RPN Tipada (Fase 3)

Compilador de uma linguagem de programação em **notação polonesa reversa
(RPN)** que, na sua terceira fase, ganha **análise semântica**: tabela de
símbolos, **tipos estáticos e fortes** (`int`, `real`, `bool`), árvore
sintática **atribuída** e **geração de Assembly ARMv7** para o simulador
**Cpulator DEC1-SOC (v16.1)**.

| | |
|---|---|
| **Instituição** | Pontifícia Universidade Católica do Paraná (PUCPR) |
| **Disciplina** | Linguagens Formais e Compiladores |
| **Professor** | Frank Coelho de Alcantara |
| **Ano** | 2026 |
| **Grupo (Canvas)** | RA3_17 |
| **Fase** | 3 — Analisador Semântico |
| **Linguagem de implementação** | Python (≥ 3.10), sem dependências de execução |

### Integrantes (ordem alfabética)

| Nome | Usuário no GitHub |
|---|---|
| Pedro Alessandrini Braiti | [pedrobraiti](https://github.com/pedrobraiti) |
| Thiago Aguiar | [Imthiagoaguiar](https://github.com/Imthiagoaguiar) |

---

## Sumário

1. [O que o programa faz](#1-o-que-o-programa-faz)
2. [Como executar, testar e depurar](#2-como-executar-testar-e-depurar)
3. [A linguagem](#3-a-linguagem)
4. [Tipos suportados](#4-tipos-suportados)
5. [Definição e uso de variáveis](#5-definição-e-uso-de-variáveis)
6. [Exemplos válidos e inválidos](#6-exemplos-válidos-e-inválidos)
7. [Arquitetura e organização](#7-arquitetura-e-organização)
8. [Artefatos de saída](#8-artefatos-de-saída)
9. [Tratamento de erros](#9-tratamento-de-erros)
10. [Documentação complementar](#10-documentação-complementar)
11. [Distribuição do trabalho](#11-distribuição-do-trabalho)

---

## 1. O que o programa faz

A partir de um arquivo-fonte, o programa executa **três análises encadeadas**
e, ao final, **gera código**:

```
arquivo.txt
   → remoção de comentários *{ ... }*        (léxico, Fase 3)
   → AFD (tokenização, sem regex)            (léxico, Fase 1)
   → parser LL(1) preditivo → AST            (sintático, Fase 2)
   → tabela de símbolos                      (semântico, Fase 3)
   → verificação de tipos → AST tipada       (semântico, Fase 3)
   → árvore atribuída (tipos + metadados)    (semântico, Fase 3)
   → Assembly ARMv7 (Cpulator DEC1-SOC)      (geração de código)
```

A geração de Assembly **só acontece se o programa não tiver nenhum erro**
léxico, sintático ou semântico. Havendo erro, o `.s` de uma execução anterior
é **apagado** para não induzir a avaliação a executar código obsoleto.

Códigos de saída do processo: **0** sem erros · **1** erro léxico/sintático ·
**2** erro semântico.

## 2. Como executar, testar e depurar

> Pré-requisito: **Python 3.10+**. Nenhuma dependência externa para executar.

### Executar

```bash
python AnalisadorSemantico.py teste1.txt
```

Os artefatos vão para `saida/` (ou para o diretório indicado em `--saida`):

```bash
python AnalisadorSemantico.py teste2.txt --saida saida_t2
```

A execução imprime, no mínimo: arquivo analisado, resultado da análise léxica,
da sintática, da semântica, a lista de erros (se houver) e os caminhos dos
artefatos gerados.

### Testar

```bash
python -m venv .venv
# Windows:  .venv\Scripts\Activate.ps1     (se necessário: Set-ExecutionPolicy -Scope Process Bypass)
# Linux/Mac: source .venv/bin/activate
pip install pytest
python -m pytest
```

A suíte cobre o léxico (comentários, números, operadores, erros), o parser
(formas válidas, aninhamento, erros), a semântica (tipos, tabela de símbolos,
comandos especiais, controle) e o fluxo ponta a ponta pela CLI.

### Depurar

Como o programa é Python puro, a depuração se dá inspecionando os artefatos
intermediários:

| Sintoma | Onde olhar |
|---|---|
| `[léxico] linha L, coluna C: ...` | caractere/número inválido ou comentário aberto; abra o `.txt` na linha indicada |
| `[sintático] linha L, coluna C: ...` | estrutura RPN violada; a mensagem diz o que era esperado |
| `[semântico:...] (linha L) ...` | tipos/declarações; veja `saida/erros_semanticos.md` |
| dúvida sobre tokens | `saida/tokens_ultima_execucao.txt` |
| dúvida sobre tipos/árvore | `saida/arvore_atribuida.md` / `.json` |
| Assembly não roda no Cpulator | `saida/ultima_execucao.s`; rode passo a passo e observe `d0`, `SP` e os displays HEX |

## 3. A linguagem

Toda instrução é escrita em **RPN entre parênteses**. Um programa **começa**
com `(START)` e termina com `(END)`, uma instrução por linha.

| Categoria | Sintaxe | Exemplo |
|---|---|---|
| Aritmética | `(a b op)`, `op ∈ + - * \| / % ^` | `(10 3 +)` |
| Divisão real / inteira | `\|` real · `/` inteira · `%` resto | `(7.5 2.5 \|)` · `(10 3 /)` |
| Relacional | `(a b op)`, `op ∈ > < == != >= <=` | `((CONT) 0 >)` |
| Lógica | `(a b AND)` · `(a b OR)` · `(a NOT)` | `(TRUE FALSE OR)` |
| Escrita de memória | `(v MEM)` | `(5 CONT)` |
| Leitura de memória | `(MEM)` | `(CONT)` |
| Histórico | `(N RES)` | `(2 RES)` |
| Decisão | `(cond bloco IF)` · `(cond então senão IFELSE)` | `((X) (1 Y) IF)` |
| Repetição | `(cond corpo WHILE)` | `(((C) 0 >) (((C) 1 -) C) WHILE)` |
| Comentário | `*{ ... }*` (multilinha, em qualquer posição) | `(10 3 +) *{ soma }*` |

As expressões podem ser **aninhadas sem limite**:
`((A B +) (C D *) |)` divide a soma de `A` e `B` pelo produto de `C` e `D`.

> **Por que palavras-chave no fim?** A forma pós-fixada (`cond bloco IF`)
> preserva o estilo RPN e mantém a gramática **LL(1)**: o parser lê os
> operandos antes de saber, com 1 token, qual estrutura está montando.

## 4. Tipos suportados

| Tipo | Como surge |
|---|---|
| `int` | literais sem ponto (`42`), `/` `%`, e operações entre inteiros |
| `real` | literais com ponto (`3.14`), `\|`, e operações entre reais |
| `bool` | literais `TRUE`/`FALSE`, relacionais e lógicos (`AND`/`OR`/`NOT`) |

Os tipos são **estáticos e fortes** e **não há promoção implícita**:
`(1 2.5 +)` é **erro** — não soma `1.0 + 2.5`. As regras formais (em cálculo
de sequentes) estão em [`regras_semanticas.md`](regras_semanticas.md).

## 5. Definição e uso de variáveis

* **Definição:** `(v MEM)` fixa o tipo de `MEM` com o tipo de `v` na primeira
  vez. `MEM` é um identificador em **letras maiúsculas** (`CONT`, `SALDO`).
* **Leitura:** `(MEM)` só vale **depois** da definição. Usar antes → erro.
  Identificador "nu" (sem parênteses) só é válido como **destino de escrita**;
  para usar o valor de uma variável, escreva `(MEM)`.
* **Redefinição:** `(v2 MEM)` é permitida apenas se `tipo(v2)` for igual ao
  tipo fixado; caso contrário → erro.
* **Escopo:** um arquivo = um escopo global único.

## 6. Exemplos válidos e inválidos

### Válido

```text
(START)
(5 CONT)                                  *{ CONT : int }*
((CONT) 0 >)                              *{ bool }*
(((CONT) 0 >) (((CONT) 1 -) CONT) WHILE)  *{ laco }*
(((CONT) 0 ==) (1 FLAG) (0 FLAG) IFELSE)  *{ decisao }*
(TRUE FALSE OR)                           *{ logica }*
(END)
```

### Inválido (erros semânticos)

```text
((NAODECL) 1 +)        *{ uso antes da definição }*
(10 X) (2.5 X)         *{ redefinição int → real }*
(1 2.5 +)              *{ sem promoção implícita }*
(10 3 |)               *{ '|' exige reais }*
((1 2 +) (3 4 +) IF)   *{ condição do IF não é bool }*
(TRUE 1 AND)           *{ AND exige dois bool }*
```

Os arquivos [`teste1.txt`](teste1.txt), [`teste2.txt`](teste2.txt) e
[`teste3.txt`](teste3.txt) são programas **válidos e completos**;
[`teste_erro_lexico.txt`](teste_erro_lexico.txt),
[`teste_erro_sintatico.txt`](teste_erro_sintatico.txt) e
[`teste_erro_semantico.txt`](teste_erro_semantico.txt) exercitam o tratamento
de erros.

## 7. Arquitetura e organização

O código é organizado **por etapa de compilação** (e não por tipo técnico de
arquivo), tornando cada fronteira explícita:

```
RA3_17/
├── AnalisadorSemantico.py        ponto de entrada (CLI)
├── compilador/
│   ├── dominio/                  tokens, tipos, nós da árvore (dataclasses + visitor)
│   ├── lexico/                   remoção de comentários + AFD
│   ├── sintatico/                gramática LL(1) + parser preditivo
│   ├── semantico/                tabela de símbolos, tipos, árvore atribuída
│   ├── codegen/                  gerador de Assembly ARMv7
│   ├── pipeline.py               prepararEntradaSemantica
│   └── relatorios.py             serialização dos artefatos
├── tests/                        suíte pytest (léxico, sintático, semântico, e2e)
├── teste*.txt                    arquivos de teste
├── gramatica_ebnf.md             gramática EBNF + ações semânticas
├── regras_semanticas.md          sistema de tipos (cálculo de sequentes)
└── saida/                        artefatos da última execução
```

As funções exigidas pelo enunciado têm exatamente os nomes pedidos:
`prepararEntradaSemantica`, `construirTabelaSimbolos`, `verificarTipos`,
`gerarArvoreAtribuida` e `gerarAssembly`.

## 8. Artefatos de saída

Gerados em `saida/` a cada execução:

| Arquivo | Conteúdo |
|---|---|
| `ARQUIVO_USADO.txt` | nome do `.txt` da última execução |
| `tokens_ultima_execucao.txt` | tokens reconhecidos pelo AFD |
| `gramatica_ll1.md` | produções, FIRST, FOLLOW e tabela LL(1) |
| `tabela_simbolos.md` | tabela de símbolos final |
| `erros_semanticos.md` | relatório de erros semânticos (vazio = "nenhum erro") |
| `arvore_atribuida.md` / `.json` | árvore atribuída (tipos + metadados) |
| `ultima_execucao.s` | Assembly ARMv7 — **só** quando não há erros |

Em caso de erro léxico/sintático, é gerado `erros_lexico_sintatico.md`.

### Rodar o Assembly no Cpulator

1. Abra <https://cpulator.01xz.net/?sys=arm-de1soc>.
2. Cole o conteúdo de `saida/ultima_execucao.s` no editor.
3. **Assemble** e **execute** (Continue).
4. O resultado de cada instrução é exibido nos displays **HEX3–HEX0**.

## 9. Tratamento de erros

| Etapa | Mecanismo | Forma da mensagem |
|---|---|---|
| Léxico | exceção (aborta) | `[léxico] (linha L, coluna C) ...` |
| Sintático | exceção (aborta) | `[sintático] (linha L, coluna C) ...` |
| Semântico | acumula numa lista (não aborta) | `[semântico:categoria] (linha L) ...` |

A análise semântica **não para no primeiro erro**: lista todos numa única
execução. O Assembly nunca é gerado quando há qualquer erro.

## 10. Documentação complementar

* [`gramatica_ebnf.md`](gramatica_ebnf.md) — gramática EBNF e ações
  semânticas (atributos e atualização da tabela de símbolos).
* [`regras_semanticas.md`](regras_semanticas.md) — sistema de tipos em cálculo de
  sequentes.
* [`saida/gramatica_ll1.md`](saida/gramatica_ll1.md) — FIRST, FOLLOW e tabela
  LL(1) da última execução.
* [`docs/decisoes_de_projeto.md`](docs/decisoes_de_projeto.md) — decisões de
  projeto e o porquê de cada uma.

## 11. Distribuição do trabalho

O grupo seguiu o modelo do enunciado: **um único administrador** do
repositório (Pedro) com acesso de escrita; o outro integrante (Thiago)
contribui por **fork + pull request**, e o administrador integra. As
contribuições ficam rastreáveis pelos commits e pull requests.

| Integrante | Responsabilidades principais |
|---|---|
| **Pedro Alessandrini Braiti** (pedrobraiti) | domínio (tokens/tipos/AST), análise sintática (gramática LL(1) + parser), verificação de tipos, gerador de Assembly ARMv7, CLI e integração |
| **Thiago Aguiar** (Imthiagoaguiar) | análise léxica (AFD + comentários), tabela de símbolos, árvore atribuída, arquivos de teste e suíte de testes, documentação |

> O histórico de commits e pull requests no repositório registra, de forma
> rastreável, a contribuição de cada integrante.
