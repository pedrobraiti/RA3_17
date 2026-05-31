# Gramática LL(1) — Produções, FIRST, FOLLOW e Tabela

## 1. Produções

| # | Não-terminal | Produção |
|--:|---|---|
| 0 | programa | ( START ) corpo |
| 1 | corpo | ( corpo_resto |
| 2 | corpo_resto | END ) |
| 3 | corpo_resto | expr ) corpo |
| 4 | expr | operando apos1 |
| 5 | apos1 | ε |
| 6 | apos1 | NOT |
| 7 | apos1 | operando apos2 |
| 8 | apos2 | ε |
| 9 | apos2 | binop |
| 10 | apos2 | kw2 |
| 11 | apos2 | operando IFELSE |
| 12 | operando | INTEIRO |
| 13 | operando | REAL |
| 14 | operando | TRUE |
| 15 | operando | FALSE |
| 16 | operando | IDENT |
| 17 | operando | RES |
| 18 | operando | ( expr ) |
| 19 | binop | + |
| 20 | binop | - |
| 21 | binop | * |
| 22 | binop | | |
| 23 | binop | / |
| 24 | binop | % |
| 25 | binop | ^ |
| 26 | binop | > |
| 27 | binop | < |
| 28 | binop | == |
| 29 | binop | != |
| 30 | binop | >= |
| 31 | binop | <= |
| 32 | binop | AND |
| 33 | binop | OR |
| 34 | kw2 | IF |
| 35 | kw2 | WHILE |

## 2. Conjuntos FIRST

| Não-terminal | FIRST |
|---|---|
| programa | { ( } |
| corpo | { ( } |
| corpo_resto | { (, END, FALSE, IDENT, INTEIRO, REAL, RES, TRUE } |
| expr | { (, FALSE, IDENT, INTEIRO, REAL, RES, TRUE } |
| apos1 | { (, FALSE, IDENT, INTEIRO, NOT, REAL, RES, TRUE, ε } |
| apos2 | { !=, %, (, *, +, -, /, <, <=, ==, >, >=, AND, FALSE, IDENT, IF, INTEIRO, OR, REAL, RES, TRUE, WHILE, ^, |, ε } |
| operando | { (, FALSE, IDENT, INTEIRO, REAL, RES, TRUE } |
| binop | { !=, %, *, +, -, /, <, <=, ==, >, >=, AND, OR, ^, | } |
| kw2 | { IF, WHILE } |

## 3. Conjuntos FOLLOW

| Não-terminal | FOLLOW |
|---|---|
| programa | { $ } |
| corpo | { $ } |
| corpo_resto | { $ } |
| expr | { ) } |
| apos1 | { ) } |
| apos2 | { ) } |
| operando | { !=, %, (, ), *, +, -, /, <, <=, ==, >, >=, AND, FALSE, IDENT, IF, IFELSE, INTEIRO, NOT, OR, REAL, RES, TRUE, WHILE, ^, | } |
| binop | { ) } |
| kw2 | { ) } |

## 4. Tabela de Análise LL(1)

A tabela é livre de conflitos — a gramática é LL(1).

| M[não-terminal, terminal] | Produção |
|---|---|
| M[apos1, (] | #7: apos1 → operando apos2 |
| M[apos1, )] | #5: apos1 → ε |
| M[apos1, FALSE] | #7: apos1 → operando apos2 |
| M[apos1, IDENT] | #7: apos1 → operando apos2 |
| M[apos1, INTEIRO] | #7: apos1 → operando apos2 |
| M[apos1, NOT] | #6: apos1 → NOT |
| M[apos1, REAL] | #7: apos1 → operando apos2 |
| M[apos1, RES] | #7: apos1 → operando apos2 |
| M[apos1, TRUE] | #7: apos1 → operando apos2 |
| M[apos2, !=] | #9: apos2 → binop |
| M[apos2, %] | #9: apos2 → binop |
| M[apos2, (] | #11: apos2 → operando IFELSE |
| M[apos2, )] | #8: apos2 → ε |
| M[apos2, *] | #9: apos2 → binop |
| M[apos2, +] | #9: apos2 → binop |
| M[apos2, -] | #9: apos2 → binop |
| M[apos2, /] | #9: apos2 → binop |
| M[apos2, <] | #9: apos2 → binop |
| M[apos2, <=] | #9: apos2 → binop |
| M[apos2, ==] | #9: apos2 → binop |
| M[apos2, >] | #9: apos2 → binop |
| M[apos2, >=] | #9: apos2 → binop |
| M[apos2, AND] | #9: apos2 → binop |
| M[apos2, FALSE] | #11: apos2 → operando IFELSE |
| M[apos2, IDENT] | #11: apos2 → operando IFELSE |
| M[apos2, IF] | #10: apos2 → kw2 |
| M[apos2, INTEIRO] | #11: apos2 → operando IFELSE |
| M[apos2, OR] | #9: apos2 → binop |
| M[apos2, REAL] | #11: apos2 → operando IFELSE |
| M[apos2, RES] | #11: apos2 → operando IFELSE |
| M[apos2, TRUE] | #11: apos2 → operando IFELSE |
| M[apos2, WHILE] | #10: apos2 → kw2 |
| M[apos2, ^] | #9: apos2 → binop |
| M[apos2, |] | #9: apos2 → binop |
| M[binop, !=] | #29: binop → != |
| M[binop, %] | #24: binop → % |
| M[binop, *] | #21: binop → * |
| M[binop, +] | #19: binop → + |
| M[binop, -] | #20: binop → - |
| M[binop, /] | #23: binop → / |
| M[binop, <] | #27: binop → < |
| M[binop, <=] | #31: binop → <= |
| M[binop, ==] | #28: binop → == |
| M[binop, >] | #26: binop → > |
| M[binop, >=] | #30: binop → >= |
| M[binop, AND] | #32: binop → AND |
| M[binop, OR] | #33: binop → OR |
| M[binop, ^] | #25: binop → ^ |
| M[binop, |] | #22: binop → | |
| M[corpo, (] | #1: corpo → ( corpo_resto |
| M[corpo_resto, (] | #3: corpo_resto → expr ) corpo |
| M[corpo_resto, END] | #2: corpo_resto → END ) |
| M[corpo_resto, FALSE] | #3: corpo_resto → expr ) corpo |
| M[corpo_resto, IDENT] | #3: corpo_resto → expr ) corpo |
| M[corpo_resto, INTEIRO] | #3: corpo_resto → expr ) corpo |
| M[corpo_resto, REAL] | #3: corpo_resto → expr ) corpo |
| M[corpo_resto, RES] | #3: corpo_resto → expr ) corpo |
| M[corpo_resto, TRUE] | #3: corpo_resto → expr ) corpo |
| M[expr, (] | #4: expr → operando apos1 |
| M[expr, FALSE] | #4: expr → operando apos1 |
| M[expr, IDENT] | #4: expr → operando apos1 |
| M[expr, INTEIRO] | #4: expr → operando apos1 |
| M[expr, REAL] | #4: expr → operando apos1 |
| M[expr, RES] | #4: expr → operando apos1 |
| M[expr, TRUE] | #4: expr → operando apos1 |
| M[kw2, IF] | #34: kw2 → IF |
| M[kw2, WHILE] | #35: kw2 → WHILE |
| M[operando, (] | #18: operando → ( expr ) |
| M[operando, FALSE] | #15: operando → FALSE |
| M[operando, IDENT] | #16: operando → IDENT |
| M[operando, INTEIRO] | #12: operando → INTEIRO |
| M[operando, REAL] | #13: operando → REAL |
| M[operando, RES] | #17: operando → RES |
| M[operando, TRUE] | #14: operando → TRUE |
| M[programa, (] | #0: programa → ( START ) corpo |
