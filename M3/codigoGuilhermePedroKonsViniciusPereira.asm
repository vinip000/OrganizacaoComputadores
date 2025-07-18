.data
	matriz: .word 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99
	matriz2: .word 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99
	matrizR: .word 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
	solicita: .asciz "Informe a ordem da matriz (Min: 1 e Max: 10): "	
	invalido: .asciz "Valor invalido!"	
	matrizresultado: .asciz "Matriz resultado: "	
	leitura: .asciz "Voce deseja ler a matriz em linha-coluna (0) ou coluna-linha(1)? "
	linha: .asciz "\n"
	tab: .asciz "\t"
	
.text
jal zero, main

	# Abaixo estao definidas as funcoes, todas as elas possuem duas versoes, uma pra caso o usuario decida usar coluna-linha e outra para linha-coluna

	imprime_matriz_coluna:
	add t6, zero, a0 #passa a ordem da matriz para t6

	#Imprime string
	addi a7, zero, 4
	la a0, matrizresultado
	ecall
	
	#pula linha	
	addi a7, zero, 4
	la a0, linha
	ecall
	
	for_i:
		beq t1, t6, fim_i #se t1 for igual a t6, chama fim_i
		add t0, zero, zero #j=0
		for_j:
			beq t0, t6, fim_j
			#calculo da posicao da matriz
			mul t2, t0, t6 #t2 = linha*ordem 
			slli t2, t2, 2 # 4*t2
			slli t3, t1, 2 # 4*j
			add t4, t2, t3  
			add t5, t4, a1 #m[t2][t3]
			lw a0, 0(t5)   #a0 = m[t2][t3]
			
			add t5, t4, a2 #m[t2][t3]
			lw a4, 0(t5)   #a4 = m2[t2][t3]
			
			add a4, a4, a0 #realiza a soma
			
			add t5, t4, a3 #mR[t2][t3]
			sw a4, 0(t5) #salva na matriz resultado
			lw a0, 0(t5) #carrega em a0 para ser impresso
			#imprime
			addi a7, zero, 1
			ecall
			#imprime tabulacao
			addi a7, zero, 4
			la a0, tab
			ecall
		
			addi t0, t0, 1 #j++
			jal zero, for_j #chama for_j
		fim_j:
		#imprime pula linha
		addi a7, zero, 4
		la a0, linha
		ecall
		
		addi t1, t1, 1 #i++
		jal zero, for_i #chama for_i
	fim_i:
	jalr zero, ra, 0 #retorno
	
imprime_matriz_linha:
	
	add t6, zero, a0 #salva a ordem em t6

	#Imprime string
	addi a7, zero, 4
	la a0, matrizresultado
	ecall
	
	#pula linha	
	addi a7, zero, 4
	la a0, linha
	ecall
	
	for_ii:
		beq t0, t6, fim_ii #se t0 for igual a t6, chama fim_ii
		add t1, zero, zero #j=0
		for_jj:
			beq t1, t6, fim_jj #se t1 for igual a t6, chama fim_jj
			#calculo da posicao da matriz
			mul t2, t0, t6 #t2 = linha*ordem 
			slli t2, t2, 2 # 4*t2
			slli t3, t1, 2 # 4*j
			add t4, t2, t3  
			add t5, t4, a1 #m[t2][t3]
			lw a0, 0(t5)   #a0 = m[t2][t3]
			
			add t5, t4, a2 #m[t2][t3]
			lw a4, 0(t5)   #a4 = m2[t2][t3]
			
			add a4, a4, a0 #realiza a soma
			
			add t5, t4, a3 #mR[t2][t3]
			sw a4, 0(t5) #salva na matriz resultado
			lw a0, 0(t5) #carrega em a0 para ser impresso
			#imprime
			addi a7, zero, 1
			ecall
			#imprime tabulacao
			addi a7, zero, 4
			la a0, tab
			ecall
		
			addi t1, t1, 1 #j++
			jal zero, for_jj
		fim_jj:
		#imprime pula linha
		addi a7, zero, 4
		la a0, linha
		ecall
		
		addi t0, t0, 1 #i++
		jal zero, for_ii
	fim_ii:
	jalr zero, ra, 0 #retorno

solicitar_linha:
	#pula linha	
	addi a7, zero, 4
	la a0, linha
	ecall

	#Imprime string
	addi a7, zero, 4
	la a0, solicita
	ecall
	
	#Le inteiro
	addi a7, zero, 5
	ecall
	
	li t1, 1 #t1 = 1
	blt a0, t1, pula_linha #se a0 (input) for menor que t1(1) chama pula_linha
	li t1, 11 #t1 = 11
	bge a0, t1, pula_linha #se a0 (input) for maior ou igual que t1(11) chama pula_linha
	
	add t1, zero, zero #t1 = 0
	
	#a0, contem a ordem da matriz
	la a1, matriz #carrega a matriz
	la a2, matriz2 #carrega a matriz2
	la a3, matrizR #carrega a matrizR
	jal ra, imprime_matriz_linha #chama a funcao
	
	#Finaliza programa
	addi a7, zero, 10
	ecall
	
solicitar_coluna:

	#mesma coisa da funcao anterior

	#pula linha	
	addi a7, zero, 4
	la a0, linha
	ecall

	#Imprime string
	addi a7, zero, 4
	la a0, solicita
	ecall
	
	#Le inteiro
	addi a7, zero, 5
	ecall
	
	li t1, 1
	blt a0, t1, pula_coluna
	li t1, 11
	bge a0, t1, pula_coluna
	
	add t1, zero, zero
	
	#a0, contem a ordem da matriz
	la a1, matriz
	la a2, matriz2
	la a3, matrizR
	jal ra, imprime_matriz_coluna
	
	#Finaliza programa
	addi a7, zero, 10
	ecall
	
pula_linha:			 #avisa da entrada invalida e solicita novamente
	
	#pula linha	
	addi a7, zero, 4
	la a0, linha
	ecall

	#Imprime string
	addi a7, zero, 4
	la a0, invalido
	ecall
	
	jal ra, solicitar_linha
	
pula_coluna:			 #avisa da entrada invalida e solicita novamente
	
	#pula linha	
	addi a7, zero, 4
	la a0, linha
	ecall

	#Imprime string
	addi a7, zero, 4
	la a0, invalido
	ecall
	
	jal ra, solicitar_coluna

main:

definir_leitura:		 #define a ordem de leitura da matriz
	
	#pula linha	
	addi a7, zero, 4
	la a0, linha
	ecall

	#Imprime string
	addi a7, zero, 4
	la a0, leitura
	ecall
	
	#Le inteiro
	addi a7, zero, 5
	ecall
	
	li t1, 0 #t1 = 0
	beq a0, t1, solicitar_linha #se a0 (input) for igual a t1(0) chama solicitar_linha
	li t1, 1 #t1 = 1
	beq a0, t1, solicitar_coluna #se a0 (input) for igual a t1(1) chama solicitar_coluna
	
	#se nao for nem 0 nem 1, avisa da entrada invalida e chama novamente
	
	#pula linha	
	addi a7, zero, 4
	la a0, linha
	ecall

	#Imprime string
	addi a7, zero, 4
	la a0, invalido
	ecall
	
	jal ra, definir_leitura #chama a funcao novamente
	
	add t1, zero, zero #t1 = 0
