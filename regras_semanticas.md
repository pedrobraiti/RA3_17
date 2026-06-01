# Sistema de Tipos — Regras em Cálculo de Sequentes (Fase 3)

Este documento define **formalmente** o sistema de tipos da linguagem. As
regras abaixo correspondem, uma a uma, ao que está implementado em
[`compilador/dominio/tipos.py`](compilador/dominio/tipos.py) e aplicado por
[`compilador/semantico/verificacao_tipos.py`](compilador/semantico/verificacao_tipos.py).

## Tipos e ambiente

```
τ ::= int | real | bool | unit
Γ  : IDENT ⇀ τ          (tabela de símbolos; escopo único global por arquivo)
```

* `unit` é o "tipo sem valor", produzido apenas por um laço `WHILE`.
* `indef` é um tipo **interno** usado na recuperação de erros: ele nunca
  aparece num programa correto — sempre que surge, um erro já foi emitido.
  Por isso ele é omitido das regras abaixo (que descrevem o caso bem-tipado).

Os tipos são **estáticos e fortes**. O tipo de uma variável é fixado na sua
**primeira** definição e não pode mudar.

> **Decisão de projeto — sem promoção implícita.** Não existe conversão
> automática entre `int` e `real`. Toda operação aritmética/relacional exige
> operandos do **mesmo** tipo numérico. Justificativa: (1) coerência com a
> tipagem forte exigida no enunciado; (2) o gerador de Assembly escolhe
> instruções e rotinas distintas para inteiro e real, então manter os tipos
> separados torna a geração de código direta e previsível.

A notação `Γ ⊢ e : τ` lê-se "no ambiente `Γ`, a expressão `e` tem tipo `τ`".

---

## 1. Literais

```
 n é literal sem ponto                 r é literal com ponto
──────────────────────── (T-Int)      ──────────────────────── (T-Real)
      Γ ⊢ n : int                            Γ ⊢ r : real


────────────────── (T-True)            ────────────────── (T-False)
 Γ ⊢ TRUE : bool                        Γ ⊢ FALSE : bool
```

Diferente de fases anteriores, `bool` é um tipo de **primeira classe**: tem
literais próprios (`TRUE`, `FALSE`) e operadores próprios (§5).

---

## 2. Aritmética de mesmo tipo — `+ - * ^`

```
 Γ ⊢ e₁ : τ      Γ ⊢ e₂ : τ      τ ∈ { int, real }
──────────────────────────────────────────────────── (T-Arit)
 Γ ⊢ (e₁ e₂ op) : τ           op ∈ { +, -, *, ^ }
```

Operandos de tipos diferentes (ex.: `(1 2.5 +)`) → **erro** (sem promoção).

---

## 3. Divisão inteira e resto — `/  %`

```
 Γ ⊢ e₁ : int      Γ ⊢ e₂ : int
──────────────────────────────── (T-DivInt)
 Γ ⊢ (e₁ e₂ op) : int      op ∈ { /, % }
```

Operandos `real` em `/` ou `%` → **erro** (use `|` para divisão real).

## 4. Divisão real — `|`

```
 Γ ⊢ e₁ : real      Γ ⊢ e₂ : real
──────────────────────────────────── (T-DivReal)
 Γ ⊢ (e₁ e₂ |) : real
```

Operandos `int` em `|` → **erro**.

---

## 5. Operadores relacionais e lógicos

```
 Γ ⊢ e₁ : τ   Γ ⊢ e₂ : τ   τ ∈ { int, real }
─────────────────────────────────────────────── (T-Rel)
 Γ ⊢ (e₁ e₂ op) : bool   op ∈ { >, <, ==, !=, >=, <= }


 Γ ⊢ e₁ : bool   Γ ⊢ e₂ : bool                  Γ ⊢ e : bool
──────────────────────────────── (T-Log2)      ──────────────── (T-Not)
 Γ ⊢ (e₁ e₂ op) : bool                           Γ ⊢ (e NOT) : bool
            op ∈ { AND, OR }
```

Relacionais comparam dois numéricos **do mesmo tipo** e produzem `bool`. Os
lógicos `AND`/`OR`/`NOT` operam **somente** sobre `bool`.

---

## 6. Memória — definição e leitura

```
 Γ ⊢ v : τ
──────────────────────────── (T-Def)        Γ' = Γ, IDENT : τ
 Γ ⊢ (v IDENT) : τ  ⊣  Γ'


 IDENT : τ ∈ Γ
────────────────── (T-Read)
 Γ ⊢ (IDENT) : τ
```

* **(T-Def)** fixa o tipo de `IDENT` no tipo de `v`. Redefinir `IDENT` com um
  `v` de tipo diferente do já fixado → **erro** (tipagem forte e estática).
* **(T-Read)** exige que `IDENT` já esteja em `Γ`. Ler antes de definir →
  **erro** (uso antes da declaração).

---

## 7. Histórico — `(N RES)`

```
 N ∈ ℕ      1 ≤ N ≤ k       (k = nº de instruções já emitidas)
──────────────────────────────────────────────────────────────── (T-Res)
 Γ ⊢ (N RES) : τ_{ instrução[k − N] }
```

O tipo de `(N RES)` é o tipo da instrução `N` posições atrás. `N` fora da
faixa → **erro**.

---

## 8. Estruturas de controle

```
 Γ ⊢ c : bool   Γ ⊢ b : τ                 Γ ⊢ c : bool   Γ ⊢ t : τ   Γ ⊢ s : τ
──────────────────────────── (T-If)       ──────────────────────────────────── (T-IfElse)
 Γ ⊢ (c b IF) : τ                          Γ ⊢ (c t s IFELSE) : τ


 Γ ⊢ c : bool      Γ ⊢ b : τ
──────────────────────────────── (T-While)
 Γ ⊢ (c b WHILE) : unit
```

* A condição de `IF`, `IFELSE` e `WHILE` **precisa** ser `bool`.
* `IFELSE` exige que os dois ramos tenham o **mesmo** tipo `τ` (sem unificação
  por promoção).
* `WHILE` é avaliado por efeito colateral: seu tipo é `unit`.

---

## 9. Resumo das mensagens de erro

| Regra violada | Mensagem (resumida) |
|---|---|
| T-Read | `uso da variável 'X' antes da definição` |
| T-Def | `redefinição da variável 'X' com tipo incompatível: era 'τ1', recebeu 'τ2'` |
| T-Arit | `operador 'op' exige dois operandos numéricos do mesmo tipo (sem promoção implícita)` |
| T-DivReal | `divisão real '\|' exige dois operandos 'real'` |
| T-DivInt | `operador inteiro 'op' exige dois operandos 'int'` |
| T-Rel | `operador relacional 'op' exige dois operandos numéricos do mesmo tipo` |
| T-Log2 | `operador lógico 'op' exige dois operandos 'bool'` |
| T-Not | `operador lógico 'NOT' exige um operando 'bool'` |
| T-If/While | `a condição do IF/WHILE deve ser do tipo 'bool'` |
| T-IfElse | `os ramos do IFELSE têm tipos divergentes` |
| T-Res | `(N RES) referencia N instruções atrás, mas só há k antes desta` |

A verificação **não aborta** no primeiro erro: ela acumula todos os
diagnósticos numa única passagem (recuperação de erros), produzindo o
relatório [`saida/erros_semanticos.md`](saida/erros_semanticos.md).
