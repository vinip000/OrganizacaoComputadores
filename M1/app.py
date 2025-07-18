# Mapeamento dos opcodes para tipos de instrução
opcode_types = {
    '0110011': 'R',  # tipo R (ex: add, sub, sll, etc)
    '0010011': 'I',  # tipo I (ex: addi, ori, xori, etc)
    '0000011': 'I',  # tipo I (ex: lw)
    '1100111': 'I',  # tipo I (ex: jalr)
    '0100011': 'S',  # tipo S (ex: sw)
    '1100011': 'B',  # tipo B (ex: beq, bne)
    '0110111': 'U',  # tipo U (ex: lui)
    '0010111': 'U',  # tipo U (ex: auipc)
    '1101111': 'J',  # tipo J (ex: jal)
    '1110011': 'I',  #Tipo I ecall
}

# Função que converte uma instrução hexadecimal para binário com 32 bits
def hex_to_bin(hex_str):
    return bin(int(hex_str, 16))[2:].zfill(32)  # Converte para inteiro, depois para binário, remove o '0b' e completa com zeros à esquerda

# Função que extrai o opcode (7 bits finais) e retorna o tipo da instrução
def get_instruction_type(binary_instr):
    opcode = binary_instr[-7:]  # Pega os últimos 7 bits da instrução binária (bits de 0 a 6 no padrão RISC-V)
    return opcode_types.get(opcode, 'Desconhecido')  # Procura na tabela, se não encontrar retorna "Desconhecido"

# Função que processa o arquivo com instruções em hexadecimal
def process_instructions(file_path):
    with open(file_path, 'r') as f:  # Abre o arquivo para leitura
        lines = f.readlines()  # Lê todas as linhas do arquivo (uma por instrução)

    instructions = []  # Lista para armazenar as instruções e seus tipos
    type_count = {'R': 0, 'I': 0, 'S': 0, 'B': 0, 'U': 0, 'J': 0, 'Desconhecido': 0}  # Contador de cada tipo de instrução

    for line in lines:  # Percorre cada linha do arquivo
        hex_instr = line.strip()  # Remove espaços em branco e quebras de linha
        if not hex_instr:
            continue  # Se a linha estiver vazia, pula para a próxima
        bin_instr = hex_to_bin(hex_instr)  # Converte a instrução de hex para binário
        instr_type = get_instruction_type(bin_instr)  # Identifica o tipo da instrução com base no opcode
        type_count[instr_type] += 1  # Atualiza o contador do tipo identificado
        instructions.append((hex_instr, instr_type))  # Adiciona a instrução e seu tipo à lista

    return instructions, type_count  # Retorna a lista de instruções e o dicionário com as contagens

# Função principal que executa o programa
def main():
    file_path = "teste3.hex"  # Caminho para o arquivo de entrada (.hex) com as instruções
    instructions, type_count = process_instructions(file_path)  # Processa o arquivo e recebe os dados

    print("\nInstruções classificadas:")  # Título da listagem
    for hex_instr, instr_type in instructions:  # Mostra cada instrução e seu tipo
        print(f"{hex_instr} => Tipo {instr_type}")

    print("\nContagem por tipo:")  # Título da contagem
    for t, count in type_count.items():  # Mostra quantas instruções tem de cada tipo
        print(f"{t}: {count}")

# Ponto de entrada do programa (executa a função main se o script for executado diretamente)
if __name__ == "__main__":
    main()