 .data
a: .word 36    #Numeros de exemplo para 'a' e para 'b'       
b: .word 18    #Numeros de exemplo para 'a' e para 'b'      

    .text
    .globl main

main:
    
    la t0, a   # Carrega 'a' em t0        
    lw t1, 0(t0) # Carrega 'a' em t1         
    la t2, b  # Carrega 'b' em t2           
    lw t3, 0(t2)# Carrega 'b' em t3          

    jal ra, mdc_recursivo #Chama função MDC

    addi a7, zero, 10 #Encerra programa 
    ecall

mdc_recursivo:
   
    addi sp, sp, -12 #Espaço na pilha para os valores       
    sw ra, 8(sp) #Salva ra na pilha
    sw t1, 4(sp)  # Salva t1 na pilha           
    sw t3, 0(sp)  # Salva t3 na pilha           

    add a0, t1, zero        
    add a1, t3, zero        

    beq a0, a1, fim #Condição de parada

    bgt a0, a1, maior_a   #Se 'a' for maior que 'b' chama a função maior-a      
    sub t3, t3, a0   #Caso contrario           
    jal ra, mdc_recursivo  #Chamada recursiva (b)     
    j pilha             

maior_a:
    sub t1, t1, a1              
    jal ra, mdc_recursivo  #Chamada recursiva (a)     

pilha:  # Restaurar os valores de ra, t1, e t3 da pilha
    
    lw ra, 8(sp)            
    lw t1, 4(sp)           
    lw t3, 0(sp)           
    addi sp, sp, 12        
    jr ra                 

fim:
    j pilha
