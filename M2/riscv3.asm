.data 
texto: .asciz "Entre com o valor de X: "
texto1: .asciz "Entre com o valor de Y: "
texto2: .asciz "Resultado: "

.text

addi a7, zero, 4
la a0, texto
ecall

addi a7, zero, 5
ecall
add s1, zero, a0

addi a7, zero, 4
la a0, texto1
ecall

addi a7, zero, 5
ecall
add s2,zero, a0

add s0, zero, zero
add t0, zero, s2

add s3, zero, zero

for: 
bge s0, t0, fim

add s3, s3, s1

addi s0, s0, 1
jal zero, for

fim:

addi a7, zero, 4
la a0, texto2
ecall

addi a7, zero, 1
add a0, zero, s3
ecall
