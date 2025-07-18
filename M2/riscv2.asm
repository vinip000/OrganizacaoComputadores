.data
  texto1: .asciz "\nEntre com o n�mero 1: "
  texto2: .asciz "\nEntre com o n�mero 2: "
  texto3: .asciz "\nEntre com o n�mero 3: "
  texto4: .asciz "\nOs valores, em ordem crescente, s�o: "

.text
  # Pedir o n�mero 1
  addi a7, zero, 4
  la a0, texto1
  ecall
  
  # Entrar com o n�mero 1
  addi a7, zero, 5
  ecall
  add t0, zero, a0
  
  # Pedir o n�mero 2
  addi a7, zero, 4
  la a0, texto2
  ecall
  
  # Entrar com o n�mero 2
  addi a7, zero, 5
  ecall
  add t1, zero, a0
  
  # Pedir o n�mero 3
  addi a7, zero, 4
  la a0, texto3
  ecall
  
  # Entrar com o n�mero 3
  addi a7, zero, 5
  ecall
  add t2, zero, a0
  
  blt t1, t0, verificacao1
  
  jal zero, skip
  
  verificacao1:
    add t3, zero, t1
    add t1, zero, t0
    add t0, zero, t3
  
  skip:
    blt t2, t1, verificacao2
    
  verificacao2:
    bge t2, t1, fim
    
    add t3, zero, t1
    add t1, zero, t2
    add t2, zero, t3
    
  blt t1, t0, verificacao1
    
  fim:
    addi a7, zero, 1
    add a0, zero, t0
    ecall
    
    addi a7, zero, 1
    add a0, zero, t1
    ecall
    
    addi a7, zero, 1
    add a0, zero, t2
    ecall