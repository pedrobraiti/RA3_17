.syntax unified
.cpu cortex-a9
.fpu vfpv3
.global _start

.text
_start:
    @ ---- instrução 1 (linha 8) ----
    LDR r0, =const_0
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_1
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VADD.F64 d0, d0, d1
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_0
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 2 (linha 9) ----
    LDR r0, =const_0
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_1
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VSUB.F64 d0, d0, d1
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_1
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 3 (linha 10) ----
    LDR r0, =const_2
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_3
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VMUL.F64 d0, d0, d1
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_2
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 4 (linha 11) ----
    LDR r0, =const_0
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_2
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    BL __op_idiv
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_3
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 5 (linha 12) ----
    LDR r0, =const_0
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_2
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    BL __op_mod
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_4
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 6 (linha 13) ----
    LDR r0, =const_4
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_5
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    BL __op_pow
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_5
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 7 (linha 16) ----
    LDR r0, =const_6
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_5
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VDIV.F64 d0, d0, d1
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_6
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 8 (linha 17) ----
    LDR r0, =const_7
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_8
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VADD.F64 d0, d0, d1
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_9
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_7
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VMUL.F64 d0, d0, d1
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VDIV.F64 d0, d0, d1
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_7
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 9 (linha 20) ----
    LDR r0, =const_10
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =mem_PECAS
    VSTR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_8
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 10 (linha 21) ----
    LDR r0, =mem_PECAS
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_1
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VMUL.F64 d0, d0, d1
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_9
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 11 (linha 22) ----
    LDR r0, =resultado_8
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_10
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 12 (linha 25) ----
    LDR r0, =mem_PECAS
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_11
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BGE L_cmp_v_1
    LDR r0, =const_zero
    VLDR.F64 d0, [r0]
    B L_cmp_f_2
L_cmp_v_1:
    LDR r0, =const_one
    VLDR.F64 d0, [r0]
L_cmp_f_2:
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_11
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 13 (linha 26) ----
    LDR r0, =mem_PECAS
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_zero
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BGT L_cmp_v_3
    LDR r0, =const_zero
    VLDR.F64 d0, [r0]
    B L_cmp_f_4
L_cmp_v_3:
    LDR r0, =const_one
    VLDR.F64 d0, [r0]
L_cmp_f_4:
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =mem_PECAS
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_12
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BLE L_cmp_v_5
    LDR r0, =const_zero
    VLDR.F64 d0, [r0]
    B L_cmp_f_6
L_cmp_v_5:
    LDR r0, =const_one
    VLDR.F64 d0, [r0]
L_cmp_f_6:
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VMUL.F64 d0, d0, d1
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_12
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 14 (linha 27) ----
    LDR r0, =const_zero
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_one
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VADD.F64 d0, d0, d1
    LDR r0, =const_zero
    VLDR.F64 d1, [r0]
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BNE L_bool_v_7
    LDR r0, =const_zero
    VLDR.F64 d0, [r0]
    B L_bool_f_8
L_bool_v_7:
    LDR r0, =const_one
    VLDR.F64 d0, [r0]
L_bool_f_8:
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =const_one
    VLDR.F64 d1, [r0]
    VSUB.F64 d0, d1, d0
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_13
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 15 (linha 28) ----
    LDR r0, =mem_PECAS
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_12
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BGT L_cmp_v_9
    LDR r0, =const_zero
    VLDR.F64 d0, [r0]
    B L_cmp_f_10
L_cmp_v_9:
    LDR r0, =const_one
    VLDR.F64 d0, [r0]
L_cmp_f_10:
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =mem_ALERTA
    VSTR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_14
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 16 (linha 31) ----
L_while_ini_1:
    LDR r0, =mem_PECAS
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_13
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BLT L_cmp_v_11
    LDR r0, =const_zero
    VLDR.F64 d0, [r0]
    B L_cmp_f_12
L_cmp_v_11:
    LDR r0, =const_one
    VLDR.F64 d0, [r0]
L_cmp_f_12:
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =const_zero
    VLDR.F64 d1, [r0]
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BEQ L_while_fim_1
    LDR r0, =mem_PECAS
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_14
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VADD.F64 d0, d0, d1
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =mem_PECAS
    VSTR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    B L_while_ini_1
L_while_fim_1:
    LDR r0, =const_zero
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_15
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 17 (linha 32) ----
    LDR r0, =mem_PECAS
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    LDR r0, =const_15
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d1, r4, r5
    POP {r4, r5}
    VMOV d0, r4, r5
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BEQ L_cmp_v_13
    LDR r0, =const_zero
    VLDR.F64 d0, [r0]
    B L_cmp_f_14
L_cmp_v_13:
    LDR r0, =const_one
    VLDR.F64 d0, [r0]
L_cmp_f_14:
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =const_zero
    VLDR.F64 d1, [r0]
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BEQ L_if_fim_2
    LDR r0, =const_16
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =mem_FALTA
    VSTR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
L_if_fim_2:
    LDR r0, =const_zero
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_16
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex
    @ ---- instrução 18 (linha 33) ----
    LDR r0, =mem_ALERTA
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =const_zero
    VLDR.F64 d1, [r0]
    VCMP.F64 d0, d1
    VMRS APSR_nzcv, FPSCR
    BEQ L_else_3
    LDR r0, =const_one
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =mem_STATUS
    VSTR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    B L_ifelse_fim_3
L_else_3:
    LDR r0, =const_zero
    VLDR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =mem_STATUS
    VSTR.F64 d0, [r0]
    VMOV r4, r5, d0
    PUSH {r4, r5}
L_ifelse_fim_3:
    POP {r4, r5}
    VMOV d0, r4, r5
    LDR r0, =resultado_17
    VSTR.F64 d0, [r0]
    VCVT.S32.F64 s0, d0
    VMOV r0, s0
    BL __exibir_hex

fim_programa:
    B fim_programa

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

.data
.align 3
const_zero: .double 0.0
const_one:  .double 1.0
const_0: .double 48.0
const_1: .double 6.0
const_2: .double 7.0
const_3: .double 9.0
const_4: .double 3.0
const_5: .double 4.0
const_6: .double 18.0
const_7: .double 2.0
const_8: .double 3.5
const_9: .double 1.5
const_10: .double 40.0
const_11: .double 30.0
const_12: .double 100.0
const_13: .double 80.0
const_14: .double 5.0
const_15: .double 50.0
const_16: .double 999.0
mem_ALERTA: .double 0.0
mem_FALTA: .double 0.0
mem_PECAS: .double 0.0
mem_STATUS: .double 0.0
resultado_0: .double 0.0
resultado_1: .double 0.0
resultado_2: .double 0.0
resultado_3: .double 0.0
resultado_4: .double 0.0
resultado_5: .double 0.0
resultado_6: .double 0.0
resultado_7: .double 0.0
resultado_8: .double 0.0
resultado_9: .double 0.0
resultado_10: .double 0.0
resultado_11: .double 0.0
resultado_12: .double 0.0
resultado_13: .double 0.0
resultado_14: .double 0.0
resultado_15: .double 0.0
resultado_16: .double 0.0
resultado_17: .double 0.0

@ tabela de 7 segmentos (dígitos 0-9) para os displays HEX
__hex_tabela:
    .byte 0x3F  @ 0
    .byte 0x06  @ 1
    .byte 0x5B  @ 2
    .byte 0x4F  @ 3
    .byte 0x66  @ 4
    .byte 0x6D  @ 5
    .byte 0x7D  @ 6
    .byte 0x07  @ 7
    .byte 0x7F  @ 8
    .byte 0x6F  @ 9
