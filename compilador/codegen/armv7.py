"""Geração de Assembly ARMv7 a partir da Árvore Sintática Atribuída.

Ambiente-alvo: **Cpulator ARMv7 DEC1-SOC (v16.1)** (Cortex-A9 + VFPv3).

Estratégia (a mesma validada nas fases anteriores deste projeto):

* **Todo valor trafega como ``double`` IEEE-754 de 64 bits** no registrador
  ``d0``. ``bool`` é representado por ``0.0`` (falso) e ``1.0`` (verdadeiro).
* Como o ARMv7 não tem ``PUSH``/``POP`` para registradores VFP, usamos o par
  ``r4:r5`` como intermediário (``VMOV`` + ``PUSH``/``POP``) — uma pilha de
  ``double`` em memória avalia as expressões aninhadas.
* Operações sem instrução nativa (divisão inteira ``/``, resto ``%``,
  potência ``^``, divisão de 32 bits, exibição nos displays HEX) são
  sub-rotinas em Assembly puro.
* Os **rótulos de salto** das estruturas de controle vêm da árvore atribuída
  (``no.meta['rotulos']``), garantindo que o Assembly seja coerente com a
  árvore — nenhuma decisão estrutural é reinventada aqui.

A geração percorre a árvore recursivamente; cada nó deixa seu resultado no
topo da pilha. Após cada instrução de topo, o resultado é guardado em
``resultado_<i>`` (suporte a ``(N RES)``) e exibido nos displays HEX.
"""

from __future__ import annotations

from compilador.dominio import ast_nodes as ast

_RELACIONAIS_PARA_DESVIO = {
    ">": "BGT",
    "<": "BLT",
    ">=": "BGE",
    "<=": "BLE",
    "==": "BEQ",
    "!=": "BNE",
}


class _Emissor:
    def __init__(self, programa: ast.Programa) -> None:
        self.programa = programa
        self.linhas: list[str] = []
        self.constantes: dict[float, str] = {}
        self._n_const = 0
        self._n_interno = 0
        self.indice_instrucao = 0
        self.memorias = list(programa.meta.get("memorias", []))

    # -- emissão de baixo nível ----------------------------------------

    def _add(self, linha: str = "") -> None:
        self.linhas.append(linha)

    def _empilhar_d0(self) -> None:
        self._add("    VMOV r4, r5, d0")
        self._add("    PUSH {r4, r5}")

    def _desempilhar(self, reg: str) -> None:
        self._add("    POP {r4, r5}")
        self._add(f"    VMOV {reg}, r4, r5")

    def _rotulo_constante(self, valor: float) -> str:
        if valor == 0.0:
            return "const_zero"
        if valor == 1.0:
            return "const_one"
        if valor not in self.constantes:
            self.constantes[valor] = f"const_{self._n_const}"
            self._n_const += 1
        return self.constantes[valor]

    def _carregar_constante(self, valor: float, reg: str = "d0") -> None:
        self._add(f"    LDR r0, ={self._rotulo_constante(valor)}")
        self._add(f"    VLDR.F64 {reg}, [r0]")

    def _rotulo_interno(self, base: str) -> str:
        self._n_interno += 1
        return f"L_{base}_{self._n_interno}"

    # -- despacho por tipo de nó ---------------------------------------

    def emitir(self, no: ast.No) -> None:
        getattr(self, f"_emitir_{type(no).__name__}")(no)

    def _emitir_LiteralInteiro(self, no: ast.LiteralInteiro) -> None:
        self._carregar_constante(float(no.valor))
        self._empilhar_d0()

    def _emitir_LiteralReal(self, no: ast.LiteralReal) -> None:
        self._carregar_constante(float(no.valor))
        self._empilhar_d0()

    def _emitir_LiteralBool(self, no: ast.LiteralBool) -> None:
        self._carregar_constante(1.0 if no.valor else 0.0)
        self._empilhar_d0()

    def _emitir_LeituraMemoria(self, no: ast.LeituraMemoria) -> None:
        self._add(f"    LDR r0, ={no.meta['rotulo_mem']}")
        self._add("    VLDR.F64 d0, [r0]")
        self._empilhar_d0()

    def _emitir_EscritaMemoria(self, no: ast.EscritaMemoria) -> None:
        self.emitir(no.valor)
        self._desempilhar("d0")
        self._add(f"    LDR r0, ={no.meta['rotulo_mem']}")
        self._add("    VSTR.F64 d0, [r0]")
        self._empilhar_d0()  # a escrita também "vale" o valor escrito

    def _emitir_ResultadoAnterior(self, no: ast.ResultadoAnterior) -> None:
        alvo = max(self.indice_instrucao - no.n, 0)
        self._add(f"    LDR r0, =resultado_{alvo}")
        self._add("    VLDR.F64 d0, [r0]")
        self._empilhar_d0()

    def _emitir_OperacaoBinaria(self, no: ast.OperacaoBinaria) -> None:
        self.emitir(no.esquerda)
        self.emitir(no.direita)
        self._desempilhar("d1")
        self._desempilhar("d0")
        op = no.operador
        if op == "+":
            self._add("    VADD.F64 d0, d0, d1")
        elif op == "-":
            self._add("    VSUB.F64 d0, d0, d1")
        elif op == "*":
            self._add("    VMUL.F64 d0, d0, d1")
        elif op == "|":
            self._add("    VDIV.F64 d0, d0, d1")
        elif op == "/":
            self._add("    BL __op_idiv")
        elif op == "%":
            self._add("    BL __op_mod")
        elif op == "^":
            self._add("    BL __op_pow")
        elif op == "AND":
            # bool*bool: 0/1 multiplicados dão exatamente o "e" lógico.
            self._add("    VMUL.F64 d0, d0, d1")
        elif op == "OR":
            self._add("    VADD.F64 d0, d0, d1")
            self._normalizar_bool()
        elif op in _RELACIONAIS_PARA_DESVIO:
            self._emitir_comparacao(op)
        else:  # pragma: no cover - barrado pela análise sintática
            raise ValueError(f"operador não suportado na geração: {op}")
        self._empilhar_d0()

    def _emitir_OperacaoUnaria(self, no: ast.OperacaoUnaria) -> None:
        self.emitir(no.operando)
        self._desempilhar("d0")
        # NOT lógico: 1.0 - x  (x é bool, garantido 0.0/1.0 pela análise de tipos)
        self._carregar_constante(1.0, "d1")
        self._add("    VSUB.F64 d0, d1, d0")
        self._empilhar_d0()

    def _emitir_Se(self, no: ast.Se) -> None:
        fim = no.meta["rotulos"]["fim"]
        self.emitir(no.condicao)
        self._desempilhar("d0")
        self._pular_se_falso(fim)
        self.emitir(no.entao)
        self._desempilhar("d0")  # descarta o valor do bloco
        self._add(f"{fim}:")
        self._carregar_constante(0.0)  # IF não produz valor: empilha neutro
        self._empilhar_d0()

    def _emitir_SeSenao(self, no: ast.SeSenao) -> None:
        senao = no.meta["rotulos"]["senao"]
        fim = no.meta["rotulos"]["fim"]
        self.emitir(no.condicao)
        self._desempilhar("d0")
        self._pular_se_falso(senao)
        self.emitir(no.entao)
        self._add(f"    B {fim}")
        self._add(f"{senao}:")
        self.emitir(no.senao)
        self._add(f"{fim}:")
        # o valor do ramo escolhido já está no topo da pilha

    def _emitir_Enquanto(self, no: ast.Enquanto) -> None:
        inicio = no.meta["rotulos"]["inicio"]
        fim = no.meta["rotulos"]["fim"]
        self._add(f"{inicio}:")
        self.emitir(no.condicao)
        self._desempilhar("d0")
        self._pular_se_falso(fim)
        self.emitir(no.corpo)
        self._desempilhar("d0")  # descarta o valor do corpo
        self._add(f"    B {inicio}")
        self._add(f"{fim}:")
        self._carregar_constante(0.0)  # WHILE não produz valor
        self._empilhar_d0()

    # -- auxiliares de fluxo -------------------------------------------

    def _pular_se_falso(self, rotulo_destino: str) -> None:
        """Assume a condição em ``d0``; desvia para ``rotulo_destino`` se 0.0."""
        self._carregar_constante(0.0, "d1")
        self._add("    VCMP.F64 d0, d1")
        self._add("    VMRS APSR_nzcv, FPSCR")
        self._add(f"    BEQ {rotulo_destino}")

    def _emitir_comparacao(self, op: str) -> None:
        """Compara ``d0`` e ``d1`` e deixa ``1.0``/``0.0`` em ``d0``."""
        verdadeiro = self._rotulo_interno("cmp_v")
        fim = self._rotulo_interno("cmp_f")
        self._add("    VCMP.F64 d0, d1")
        self._add("    VMRS APSR_nzcv, FPSCR")
        self._add(f"    {_RELACIONAIS_PARA_DESVIO[op]} {verdadeiro}")
        self._carregar_constante(0.0)
        self._add(f"    B {fim}")
        self._add(f"{verdadeiro}:")
        self._carregar_constante(1.0)
        self._add(f"{fim}:")

    def _normalizar_bool(self) -> None:
        """Mapeia qualquer ``d0`` != 0 para ``1.0`` (usado após OR)."""
        verdadeiro = self._rotulo_interno("bool_v")
        fim = self._rotulo_interno("bool_f")
        self._carregar_constante(0.0, "d1")
        self._add("    VCMP.F64 d0, d1")
        self._add("    VMRS APSR_nzcv, FPSCR")
        self._add(f"    BNE {verdadeiro}")
        self._carregar_constante(0.0)
        self._add(f"    B {fim}")
        self._add(f"{verdadeiro}:")
        self._carregar_constante(1.0)
        self._add(f"{fim}:")

    # -- montagem do arquivo final -------------------------------------

    def gerar(self) -> str:
        self._cabecalho()
        for indice, instrucao in enumerate(self.programa.instrucoes):
            self.indice_instrucao = indice
            self._add(f"    @ ---- instrução {indice + 1} (linha {instrucao.linha}) ----")
            self.emitir(instrucao)
            self._desempilhar("d0")
            self._add(f"    LDR r0, =resultado_{indice}")
            self._add("    VSTR.F64 d0, [r0]")
            self._add("    VCVT.S32.F64 s0, d0")
            self._add("    VMOV r0, s0")
            self._add("    BL __exibir_hex")
        self._add()
        self._add("fim_programa:")
        self._add("    B fim_programa")
        self._add()
        self._add(_ROTINAS_AUXILIARES.strip("\n"))
        self._secao_dados()
        return "\n".join(self.linhas) + "\n"

    def _cabecalho(self) -> None:
        # O Cpulator já fixa CPU/FPU pela linha de comando do montador
        # (-mcpu=cortex-a9 -mfpu=neon-fp16); as diretivas .syntax/.cpu/.fpu no
        # arquivo são redundantes e o montador do Cpulator rejeita `.syntax`.
        # Mantemos só o mínimo, e as instruções VFP usadas não exigem
        # `.syntax unified` em modo ARM.
        self._add(".global _start")
        self._add()
        self._add(".text")
        self._add("_start:")

    def _secao_dados(self) -> None:
        self._add()
        self._add(".data")
        self._add(".align 3")
        self._add("const_zero: .double 0.0")
        self._add("const_one:  .double 1.0")
        for valor, rotulo in self.constantes.items():
            self._add(f"{rotulo}: .double {valor!r}")
        for mem in self.memorias:
            self._add(f"mem_{mem}: .double 0.0")
        total = len(self.programa.instrucoes)
        for indice in range(max(total, 1)):
            self._add(f"resultado_{indice}: .double 0.0")
        self._add()
        self._add("@ tabela de 7 segmentos (dígitos 0-9) para os displays HEX")
        self._add("__hex_tabela:")
        codigos = ("0x3F", "0x06", "0x5B", "0x4F", "0x66", "0x6D", "0x7D", "0x07", "0x7F", "0x6F")
        for digito, codigo in enumerate(codigos):
            self._add(f"    .byte {codigo}  @ {digito}")


def gerarAssembly(arvore_atribuida: ast.Programa) -> str:
    """Gera o texto do Assembly ARMv7 a partir da árvore atribuída.

    Deve ser chamada **apenas** para programas sem erros léxicos, sintáticos
    ou semânticos — a coordenação dessa garantia é do orquestrador (CLI).
    """
    if not isinstance(arvore_atribuida, ast.Programa):
        raise ValueError("a raiz da árvore deve ser um nó 'Programa'")
    return _Emissor(arvore_atribuida).gerar()


# As sub-rotinas de inteiro/potência/divisão/exibição são Assembly puro e
# independem da árvore — ficam aqui como um bloco de texto único.
_ROTINAS_AUXILIARES = r"""
@ ===================== sub-rotinas auxiliares =====================

@ divisão inteira: converte d0,d1 (double) -> int, divide, devolve em d0.
__op_idiv:
    PUSH {lr}
    VCVT.S32.F64 s0, d0
    VCVT.S32.F64 s2, d1
    VMOV r0, s0
    VMOV r1, s2
    BL __sdiv32
    VMOV s0, r0
    VCVT.F64.S32 d0, s0
    POP {lr}
    BX lr

@ resto da divisão inteira: r = a - (a/b)*b
__op_mod:
    PUSH {r4, lr}
    VCVT.S32.F64 s0, d0
    VCVT.S32.F64 s2, d1
    VMOV r2, s0
    VMOV r3, s2
    MOV r0, r2
    MOV r1, r3
    BL __sdiv32
    MUL r4, r0, r3
    SUB r2, r2, r4
    VMOV s0, r2
    VCVT.F64.S32 d0, s0
    POP {r4, lr}
    BX lr

@ potência com expoente inteiro (multiplicações sucessivas). base=d0, exp=d1
__op_pow:
    PUSH {lr}
    VCVT.S32.F64 s2, d1
    VMOV r3, s2
    CMP r3, #0
    BLE __pow_base_um
    VMOV.F64 d2, d0
    SUB r3, r3, #1
__pow_loop:
    CMP r3, #0
    BEQ __pow_fim
    VMUL.F64 d2, d2, d0
    SUB r3, r3, #1
    B __pow_loop
__pow_fim:
    VMOV.F64 d0, d2
    POP {lr}
    BX lr
__pow_base_um:
    LDR r0, =const_one
    VLDR.F64 d0, [r0]
    POP {lr}
    BX lr

@ divisão de 32 bits com sinal por subtrações (Cortex-A9 não tem SDIV)
__sdiv32:
    PUSH {r2, r3, r4, lr}
    CMP r1, #0
    BEQ __sdiv32_zero
    MOV r2, #0
    CMP r0, #0
    RSBMI r0, r0, #0
    EORMI r2, r2, #1
    CMP r1, #0
    RSBMI r1, r1, #0
    EORMI r2, r2, #1
    MOV r3, #0
__sdiv32_loop:
    CMP r0, r1
    BLT __sdiv32_fim
    SUB r0, r0, r1
    ADD r3, r3, #1
    B __sdiv32_loop
__sdiv32_fim:
    CMP r2, #0
    RSBNE r3, r3, #0
    MOV r0, r3
    POP {r2, r3, r4, lr}
    BX lr
__sdiv32_zero:
    MOV r0, #0
    POP {r2, r3, r4, lr}
    BX lr

@ exibe o inteiro em r0 nos displays HEX (0xFF200020) do DE1-SoC
__exibir_hex:
    PUSH {r1, r2, r3, r4, r5, r6, lr}
    LDR r1, =__hex_tabela
    LDR r6, =0xFF200020
    MOV r5, #0
    CMP r0, #0
    RSBMI r0, r0, #0
    MOVMI r5, #1
    MOV r4, #0
    MOV r2, #10
    BL __udiv10
    LDRB r3, [r1, r3]
    ORR r4, r4, r3
    MOV r2, #10
    BL __udiv10
    LDRB r3, [r1, r3]
    ORR r4, r4, r3, LSL #8
    MOV r2, #10
    BL __udiv10
    LDRB r3, [r1, r3]
    ORR r4, r4, r3, LSL #16
    CMP r5, #1
    MOVEQ r3, #0x40
    BEQ __exibir_hex_sinal
    MOV r2, #10
    BL __udiv10
    LDRB r3, [r1, r3]
    ORR r4, r4, r3, LSL #24
    B __exibir_hex_store
__exibir_hex_sinal:
    ORR r4, r4, r3, LSL #24
__exibir_hex_store:
    STR r4, [r6]
    POP {r1, r2, r3, r4, r5, r6, lr}
    BX lr

@ divisão por 10 sem sinal: quociente em r0, resto em r3
__udiv10:
    MOV r3, #0
__udiv10_loop:
    CMP r0, r2
    BLT __udiv10_fim
    SUB r0, r0, r2
    ADD r3, r3, #1
    B __udiv10_loop
__udiv10_fim:
    MOV r12, r0
    MOV r0, r3
    MOV r3, r12
    BX lr
"""
