# Gramática Atribuída (EBNF) — Fase 3

Gramática **LL(1)** da linguagem, anotada com as **ações semânticas** que
constroem a árvore atribuída e atualizam a tabela de símbolos. Convenção do
enunciado: **não-terminais em minúsculas**, **TERMINAIS em maiúsculas** ou
pelo próprio lexema do operador.

> Os conjuntos **FIRST**, **FOLLOW** e a **tabela de análise LL(1)** completos
> são gerados a cada execução em
> [`saida/gramatica_ll1.md`](saida/gramatica_ll1.md) — a própria construção da
> tabela valida que a gramática é livre de conflitos (ver
> [`compilador/sintatico/gramatica.py`](compilador/sintatico/gramatica.py)).

## 1. Terminais

| Terminal | Lexema(s) | Origem |
|---|---|---|
| `INTEIRO` | `0`, `42`, `100` | categoria léxica |
| `REAL` | `3.14`, `0.0` | categoria léxica |
| `IDENT` | `CONT`, `SALDO` (letras maiúsculas) | categoria léxica |
| `TRUE` `FALSE` | literais lógicos | palavra reservada |
| `START` `END` `RES` `IF` `IFELSE` `WHILE` | estrutura/comandos | palavra reservada |
| `AND` `OR` `NOT` | operadores lógicos | palavra reservada |
| `+ - * \| / % ^` | aritméticos (`\|` real, `/` inteira) | lexema |
| `> < == != >= <=` | relacionais | lexema |
| `(` `)` | agrupamento | lexema |

Comentários `*{ ... }*` são removidos pelo léxico
([`compilador/lexico/comentarios.py`](compilador/lexico/comentarios.py)) e
**não** aparecem na gramática.

## 2. Forma EBNF (leitura humana)

```ebnf
programa   = "(" START ")" , corpo ;
corpo      = { "(" expr ")" } , "(" END ")" ;
expr       = operando , [ NOT | ( operando , [ operando , IFELSE | ε_op ] ) ] ;
operando   = INTEIRO | REAL | TRUE | FALSE | IDENT | RES | "(" expr ")" ;
binop      = "+" | "-" | "*" | "|" | "/" | "%" | "^"
           | ">" | "<" | "==" | "!=" | ">=" | "<=" | AND | OR ;
kw2        = IF | WHILE ;
```

`ε_op` indica que, após dois operandos, pode vir um `binop`, um `kw2`
(`IF`/`WHILE`) ou nada (formas `(V MEM)` e `(N RES)`). A forma BNF fatorada
abaixo é a que o parser realmente usa.

## 3. Forma BNF fatorada (base da tabela LL(1))

```
(0)  programa     → ( START ) corpo
(1)  corpo        → ( corpo_resto
(2)  corpo_resto  → END )
(3)  corpo_resto  → expr ) corpo
(4)  expr         → operando apos1
(5)  apos1        → ε
(6)  apos1        → NOT
(7)  apos1        → operando apos2
(8)  apos2        → ε
(9)  apos2        → binop
(10) apos2        → kw2
(11) apos2        → operando IFELSE
(12) operando     → INTEIRO
(13) operando     → REAL
(14) operando     → TRUE
(15) operando     → FALSE
(16) operando     → IDENT
(17) operando     → RES
(18) operando     → ( expr )
(19..33) binop    → + | - | * | | | / | % | ^ | > | < | == | != | >= | <= | AND | OR
(34) kw2          → IF
(35) kw2          → WHILE
```

### Por que é LL(1)

* **`corpo` fatorado à esquerda**: tanto `(END)` quanto `(expr)` começam com
  `(`. A produção (1) consome o `(` antes de decidir, e então um único token
  (`END` vs. início de `operando`) escolhe entre (2) e (3).
* **`apos1`/`apos2` anuláveis só quando necessário**: o `ε` é escolhido apenas
  quando o *lookahead* é `)` (que está em FOLLOW). Em qualquer outro caso a
  produção concreta é determinada por um único token.
* **Palavras-chave pós-fixadas**: `IF`/`WHILE`/`IFELSE`/`NOT` e os operadores
  ficam **no fim**, então o parser lê os operandos primeiro e, com 1 token de
  *lookahead*, distingue operador binário, controle de 2 itens, controle de 3
  itens (`IFELSE`) ou negação. Os FIRST dessas alternativas são disjuntos.

## 4. Ações semânticas (construção da árvore atribuída)

A AST é montada durante a descida recursiva
([`compilador/sintatico/parser.py`](compilador/sintatico/parser.py)); as
etapas semânticas a anotam depois. A tabela abaixo resume, por forma
sintática, o nó gerado e a ação semântica associada.

| Forma reconhecida | Nó da árvore | Ação semântica |
|---|---|---|
| `INTEIRO` / `REAL` | `LiteralInteiro` / `LiteralReal` | `tipo := int / real` (T-Int/T-Real) |
| `TRUE` / `FALSE` | `LiteralBool` | `tipo := bool` (T-True/T-False) |
| `( IDENT )` | `LeituraMemoria` | registra **uso**; `tipo := Γ(IDENT)` (T-Read) |
| `( v IDENT )` | `EscritaMemoria` | `Γ := Γ, IDENT:tipo(v)`; `tipo := tipo(v)` (T-Def) |
| `( N RES )` | `ResultadoAnterior` | valida `1 ≤ N ≤ k`; `tipo := tipo(instr[k−N])` (T-Res) |
| `( e₁ e₂ op )` | `OperacaoBinaria` | `tipo := tipo_de_operacao(op, t₁, t₂)` (T-Arit/Rel/Log/Div) |
| `( e NOT )` | `OperacaoUnaria` | exige `t = bool`; `tipo := bool` (T-Not) |
| `( c b IF )` | `Se` | exige `c : bool`; `tipo := tipo(b)` (T-If) |
| `( c t s IFELSE )` | `SeSenao` | exige `c : bool` e `tipo(t)=tipo(s)` (T-IfElse) |
| `( c b WHILE )` | `Enquanto` | exige `c : bool`; `tipo := unit` (T-While) |

### Atributos anexados a cada nó

A etapa `gerarArvoreAtribuida`
([`compilador/semantico/arvore_atribuida.py`](compilador/semantico/arvore_atribuida.py))
acrescenta, em cada nó, um `meta` com a informação necessária à geração de
código:

| Campo de `meta` | Em quais nós | Conteúdo |
|---|---|---|
| `tipo` | todos | `int` / `real` / `bool` / `unit` (posto por `verificarTipos`) |
| `registrador` | nós de valor | `d0` (todo valor trafega como `double`) |
| `valor_double` | literais | valor já convertido para `double` (`bool` → `0.0`/`1.0`) |
| `rotulo_mem` | leitura/escrita | rótulo da variável na seção `.data` |
| `rotulos` | `Se`, `SeSenao`, `Enquanto` | rótulos de salto únicos usados no Assembly |
| `simbolo` | leitura/escrita | referência ao símbolo na tabela (`nome`, `tipo`) |

Esses rótulos de controle são **os mesmos** consumidos pelo gerador
([`compilador/codegen/armv7.py`](compilador/codegen/armv7.py)), garantindo que
o Assembly seja coerente com a árvore atribuída.
