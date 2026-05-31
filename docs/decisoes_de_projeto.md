# Decisões de Projeto

Registro curto das escolhas de design da Fase 3 e do **porquê** de cada uma —
útil para a manutenção e para a defesa do trabalho.

## 1. `bool` como tipo de primeira classe (com literais e operadores)

O enunciado pede os tipos `int`, `real` e **`bool`**, além de testes com
**literais lógicos** e **operações lógicas**. Por isso a linguagem ganhou:

* **literais** `TRUE` e `FALSE`;
* **operadores lógicos** `AND`, `OR` (binários) e `NOT` (unário).

Sem eles, `bool` seria um tipo "sem saída" (só nasceria de relacionais e só
seria consumido como condição), o que deixaria as "regras de combinação entre
tipos" incompletas. Com `AND`/`OR`/`NOT`, `bool` participa de expressões como
qualquer outro tipo.

## 2. Tipagem forte, estática e **sem promoção implícita**

`(1 2.5 +)` é erro, não `3.5`. Motivos:

1. coerência com a exigência de tipos estáticos e fortes;
2. o gerador de Assembly usa instruções/rotinas diferentes para inteiro e
   real — manter os tipos disjuntos torna a geração direta e previsível.

Para evitar a armadilha de "uma etapa promove e a outra proíbe", **um único
módulo** (`compilador/dominio/tipos.py`) decide o tipo de toda operação, e
tanto a tabela de símbolos quanto a verificação de tipos o consultam.

## 3. Estruturas de controle pós-fixadas

`(cond bloco IF)`, `(cond então senão IFELSE)`, `(cond corpo WHILE)`. Manter a
palavra-chave **no fim** preserva o estilo RPN e mantém a gramática **LL(1)**:
o parser lê os operandos e, com 1 token de *lookahead*, decide se está diante
de um operador, de um controle de 2 itens, de um `IFELSE` (3 itens) ou de uma
negação.

## 4. Parser preditivo recursivo (uma função por não-terminal)

Em vez de uma tabela + pilha explícita, o parser é um descendente recursivo
preditivo — equivalente em poder (LL(1)), porém mais legível e com mensagens
de erro mais diretas. A tabela LL(1) ainda é construída (e validada quanto a
conflitos) em `gramatica.py`, servindo de artefato e de prova de que a
gramática é LL(1).

## 5. AST com `dataclasses` + *visitor*

Cada nó é uma `dataclass` (campos nomeados e verificáveis), e as etapas
semânticas usam um *visitor* por despacho de classe. Isso mantém cada etapa
desacoplada da estrutura interna dos nós e evita a varredura genérica por
dicionários.

## 6. Geração de código: tudo em `double` na VFP

Todo valor (inclusive `bool`, como `0.0`/`1.0`) trafega como `double`
IEEE-754 de 64 bits em `d0`, com uma pilha de `double` em memória para as
subexpressões. Operações sem instrução nativa (`/`, `%`, `^`, divisão de 32
bits, exibição nos HEX) são sub-rotinas em Assembly puro. Os **rótulos de
salto** das estruturas de controle vêm da árvore atribuída, garantindo que o
Assembly seja coerente com a árvore.

## 7. Contrato de erros e geração

* Erros léxicos/sintáticos **abortam** (sem tokens/árvore não há o que
  analisar).
* Erros semânticos **não abortam**: são acumulados para um relatório único.
* O Assembly é gerado **apenas** para programas sem nenhum erro; um `.s`
  antigo é removido quando há erro, para não enganar a avaliação.
