import os # Importa o módulo 'os' para interagir com o sistema operacional, como verificar se um arquivo existe.
import copy # Importa o módulo 'copy' para criar cópias de objetos, especialmente útil para listas de dicionários.
import sys # Importa o módulo 'sys' para acessar parâmetros passados pela linha de comando (como o nome do arquivo de entrada).

# Tipos de instrução por opcode
opcode_types = { # Dicionário que mapeia os 7 bits menos significativos (opcode) de uma instrução RISC-V para seu tipo (R, I, S, B, U, J).
    '0110011': 'R',  # tipo R (ex: add, sub) - Instruções aritméticas/lógicas com três registradores.
    '0010011': 'I',  # tipo I (ex: addi, ori) - Instruções com um imediato e dois registradores (um fonte, um destino).
    '0000011': 'I',  # tipo I (ex: lw) - Instruções de load, que também usam o formato I.
    '1100111': 'I',  # tipo I (ex: jalr) - Instrução de jump and link register, formato I.
    '0100011': 'S',  # tipo S (ex: sw) - Instruções de store, com dois registradores fonte e um imediato para deslocamento.
    '1100011': 'B',  # tipo B (ex: beq, bne) - Instruções de branch condicional, com dois registradores fonte e um imediato para deslocamento.
    '0110111': 'U',  # tipo U (ex: lui) - Instruções com um imediato longo e um registrador destino.
    '0010111': 'U',  # tipo U (ex: auipc) - Add Upper Immediate to PC, formato U.
    '1101111': 'J',  # tipo J (ex: jal) - Instrução de jump and link, com um imediato longo e um registrador destino.
    '1110011': 'I',  # tipo I (ecall) - Instrução de system call, usa o formato I mas aqui é tratada de forma genérica.
}

NOP_HEX = "00000013"  # Define a representação hexadecimal da instrução NOP (No Operation) em RISC-V, que é 'ADDI x0, x0, 0'.

def hex_to_bin(hex_str): # Define uma função para converter uma string hexadecimal em uma string binária de 32 bits.
    return bin(int(hex_str, 16))[2:].zfill(32) # Converte a string hexadecimal para inteiro (base 16), depois para binário (prefixo '0b' removido com [2:]), e preenche com zeros à esquerda até ter 32 bits.

def bin_to_hex(bin_str): # Define uma função para converter uma string binária em uma string hexadecimal de 8 caracteres.
    return hex(int(bin_str, 2))[2:].upper().zfill(8) # Converte a string binária para inteiro (base 2), depois para hexadecimal (prefixo '0x' removido com [2:]), converte para maiúsculas e preenche com zeros à esquerda até ter 8 caracteres.

def get_instruction_type(binary_instr): # Define uma função para obter o tipo da instrução (R, I, S, etc.) a partir de sua representação binária.
    return opcode_types.get(binary_instr[-7:], 'Desconhecido') # Retorna o tipo da instrução buscando os 7 últimos bits (opcode) no dicionário 'opcode_types'. Se não encontrado, retorna 'Desconhecido'.

def is_load_instruction(hex_instr): # Define uma função para verificar se uma instrução hexadecimal é do tipo LOAD.
    """Verifica se é instrução LOAD baseada no opcode"""
    bin_instr = hex_to_bin(hex_instr) # Converte a instrução hexadecimal para binário.
    opcode = bin_instr[-7:] # Extrai os 7 bits do opcode.
    return opcode == '0000011' # Retorna True se o opcode corresponde ao de uma instrução LOAD ('lw'), False caso contrário.

def is_store_instruction(hex_instr): # Define uma função para verificar se uma instrução hexadecimal é do tipo STORE.
    """Verifica se é instrução STORE baseada no opcode"""
    bin_instr = hex_to_bin(hex_instr) # Converte a instrução hexadecimal para binário.
    opcode = bin_instr[-7:] # Extrai os 7 bits do opcode.
    return opcode == '0100011' # Retorna True se o opcode corresponde ao de uma instrução STORE ('sw'), False caso contrário.

def is_branch_instruction(hex_instr): # Define uma função para verificar se uma instrução hexadecimal é de desvio (branch ou jump).
    """Verifica se é instrução de branch/jump"""
    bin_instr = hex_to_bin(hex_instr) # Converte a instrução hexadecimal para binário.
    opcode = bin_instr[-7:] # Extrai os 7 bits do opcode.
    return opcode in ['1100011', '1101111', '1100111']  # Retorna True se o opcode é de B (branch), J (jump) ou JALR (jump and link register), False caso contrário.

def decode_registers(bin_instr): # Define uma função para decodificar os registradores (rs1, rs2, rd) de uma instrução binária.
    opcode = bin_instr[-7:] # Extrai os 7 bits do opcode.
    instr_type = get_instruction_type(bin_instr) # Obtém o tipo da instrução (R, I, S, etc.).
    rs1 = rs2 = rd = None # Inicializa os registradores como None.

    if instr_type == 'R': # Se a instrução é do tipo R:
        rd = int(bin_instr[20:25], 2) # O registrador destino (rd) está nos bits 20 a 24 (índices 20 a 25-1).
        rs1 = int(bin_instr[12:17], 2) # O primeiro registrador fonte (rs1) está nos bits 12 a 16.
        rs2 = int(bin_instr[7:12], 2) # O segundo registrador fonte (rs2) está nos bits 7 a 11.
    elif instr_type == 'I': # Se a instrução é do tipo I:
        rd = int(bin_instr[20:25], 2) # O registrador destino (rd) está nos bits 20 a 24.
        rs1 = int(bin_instr[12:17], 2) # O primeiro registrador fonte (rs1) está nos bits 12 a 16.
        # rs2 não é usado diretamente como um campo de 5 bits neste formato para todas as instruções I, mas o campo imediato ocupa essa posição.
    elif instr_type == 'S': # Se a instrução é do tipo S:
        rs1 = int(bin_instr[12:17], 2) # O primeiro registrador fonte (rs1 - base address) está nos bits 12 a 16.
        rs2 = int(bin_instr[7:12], 2) # O segundo registrador fonte (rs2 - data to store) está nos bits 7 a 11.
        # rd não é usado.
    elif instr_type == 'B': # Se a instrução é do tipo B:
        rs1 = int(bin_instr[12:17], 2) # O primeiro registrador fonte (rs1) está nos bits 12 a 16.
        rs2 = int(bin_instr[7:12], 2) # O segundo registrador fonte (rs2) está nos bits 7 a 11.
        # rd não é usado.
    elif instr_type == 'U' or instr_type == 'J': # Se a instrução é do tipo U ou J:
        rd = int(bin_instr[20:25], 2) # O registrador destino (rd) está nos bits 20 a 24.
        # rs1 e rs2 não são usados.
    
    return instr_type, rs1, rs2, rd # Retorna o tipo da instrução e os valores inteiros dos registradores decodificados.

def read_instructions(file_path): # Define uma função para ler instruções de um arquivo.
    instructions = [] # Inicializa uma lista vazia para armazenar as instruções processadas.
    with open(file_path, 'r') as f: # Abre o arquivo especificado em modo de leitura ('r').
        for line in f: # Itera sobre cada linha do arquivo.
            hex_instr = line.strip().upper() # Remove espaços em branco no início/fim da linha e converte para maiúsculas.
            if not hex_instr: # Se a linha estiver vazia após o strip, pula para a próxima.
                continue
            bin_instr = hex_to_bin(hex_instr) # Converte a instrução hexadecimal para binário.
            instr_type, rs1, rs2, rd = decode_registers(bin_instr) # Decodifica os registradores da instrução binária.
            instructions.append({ # Adiciona um dicionário à lista 'instructions' contendo informações da instrução.
                'hex': hex_instr, # A instrução original em hexadecimal.
                'bin': bin_instr, # A instrução em binário.
                'type': instr_type, # O tipo da instrução (R, I, S, etc.).
                'rs1': rs1, # O registrador fonte rs1 (ou None).
                'rs2': rs2, # O registrador fonte rs2 (ou None).
                'rd': rd, # O registrador destino rd (ou None).
                'is_load': is_load_instruction(hex_instr), # Booleano: True se for uma instrução de LOAD.
                'is_store': is_store_instruction(hex_instr), # Booleano: True se for uma instrução de STORE.
                'is_branch': is_branch_instruction(hex_instr) # Booleano: True se for uma instrução de branch/jump.
            })
    return instructions # Retorna a lista de dicionários de instruções.

def detect_data_conflicts(instructions, forwarding=False): # Define uma função para detectar conflitos de dados (RAW hazards).
    """Detecta conflitos de dados (RAW hazards)"""
    conflicts = [] # Inicializa uma lista vazia para armazenar os conflitos detectados.
    
    for i in range(len(instructions)): # Itera sobre cada instrução (instrução atual).
        current = instructions[i] # Pega a instrução atual.
        
        # Verifica conflitos com instruções anteriores (até 3 instruções antes, pois um pipeline de 5 estágios pode ter dependências nessa janela).
        for j in range(max(0, i-3), i): # Itera sobre as instruções anteriores à atual ('prev'). O 'max(0, i-3)' evita índices negativos.
            prev = instructions[j] # Pega uma instrução anterior.
            distance = i - j # Calcula a distância entre a instrução atual e a anterior.
            
            # Só considera conflito se a instrução anterior escreve em um registrador válido (rd não é None e rd não é x0, o registrador zero).
            if prev['rd'] is not None and prev['rd'] != 0:
                # Verifica se a instrução atual lê (usa rs1 ou rs2) o registrador que a instrução anterior escreve (prev['rd']).
                read_conflict = False
                if current['rs1'] == prev['rd'] or \
                   (current['rs2'] is not None and current['rs2'] == prev['rd']): # Garante que current['rs2'] não seja None antes de comparar.
                    read_conflict = True
                
                if read_conflict: # Se há uma potencial dependência RAW.
                    conflict_exists = False # Flag para indicar se o conflito realmente causa uma bolha/NOP.
                    if not forwarding: # Se o forwarding NÃO está habilitado:
                        # Sem forwarding: conflito se a distância entre a escrita e a leitura for menor ou igual a 2 ciclos (resultando em bolhas).
                        # (Escrita no estágio WB, Leitura no estágio ID. WB de I_prev ocorre no ciclo k+4, ID de I_curr no ciclo k+2. Se I_curr é I_j e I_prev é I_i, j=i+1 -> conflito de 2 bolhas, j=i+2 -> conflito de 1 bolha)
                        if distance <= 2:
                            conflict_exists = True
                    else: # Se o forwarding ESTÁ habilitado:
                        # Com forwarding: conflito ocorre apenas para load-use hazard, onde a instrução anterior é um LOAD e a distância é 1.
                        # (LOAD no estágio MEM, a instrução seguinte no estágio EX. O dado do LOAD só está disponível após MEM).
                        if distance == 1 and prev['is_load']:
                            conflict_exists = True
                    
                    if conflict_exists: # Se o conflito requer uma bolha.
                        conflicts.append({ # Adiciona informações sobre o conflito à lista.
                            'position': i, # Posição (índice) da instrução atual que sofre o conflito.
                            'source': j, # Posição (índice) da instrução anterior que causa o conflito.
                            'register': prev['rd'], # Registrador envolvido no conflito.
                            'distance': distance, # Distância entre as instruções.
                            'is_load_use': prev['is_load'] and distance == 1 # True se for um conflito load-use.
                        })
    
    return conflicts # Retorna a lista de conflitos de dados detectados.

def detect_control_conflicts(instructions): # Define uma função para detectar conflitos de controle (branch/jump hazards).
    """Detecta conflitos de controle (branch/jump hazards)"""
    conflicts = [] # Inicializa uma lista vazia para armazenar os conflitos de controle.
    
    for i, instr in enumerate(instructions): # Itera sobre cada instrução com seu índice.
        if instr['is_branch']: # Se a instrução é um branch ou jump.
            conflicts.append({ # Adiciona informações sobre o conflito de controle.
                'position': i, # Posição (índice) da instrução de branch/jump.
                'type': instr['type'] # Tipo da instrução de branch/jump.
            })
    
    return conflicts # Retorna a lista de conflitos de controle.

def insert_nops_data(instructions, forwarding=False): # Define uma função para inserir NOPs para resolver conflitos de dados.
    """Insere NOPs para resolver conflitos de dados - CORRIGIDO"""
    result = [] # Inicializa uma lista para o código com NOPs inseridos.
    
    # Este laço itera sobre as instruções originais para construir a lista `result`.
    # A lógica de inserção de NOPs acontece *após* adicionar a instrução `current` e antes de processar a `instructions[i+1]`.
    idx = 0 # Índice para percorrer a lista `instructions`.
    while idx < len(instructions): # Enquanto houver instruções originais para processar.
        current_original_instr = instructions[idx] # Pega a instrução original atual.
        result.append(copy.deepcopy(current_original_instr)) # Adiciona uma cópia da instrução original à lista de resultados.

        # Verifica se a instrução que acabou de ser adicionada (`current_original_instr`) escreve em um registrador
        # e pode causar um conflito com as próximas instruções originais.
        if current_original_instr['rd'] is not None and current_original_instr['rd'] != 0:
            nops_to_insert_after_current = 0 # Quantos NOPs precisam ser inseridos após a `current_original_instr`.

            # Olha para as próximas instruções originais para ver se elas dependem da `current_original_instr`.
            # O loop vai até 2 instruções à frente (para `distance` 1 e 2) se não houver forwarding,
            # ou 1 instrução à frente (para `distance` 1) se houver forwarding e `current_original_instr` for um LOAD.
            lookahead_limit = 1 if (forwarding and current_original_instr['is_load']) else 2
            
            for k in range(1, lookahead_limit + 1): # k representa a distância (1 ou 2).
                if idx + k < len(instructions): # Verifica se a próxima instrução (idx + k) existe.
                    next_potential_dependent_instr = instructions[idx + k] # Pega a próxima instrução original.

                    # Verifica se há dependência RAW (next_potential_dependent_instr lê o que current_original_instr escreveu).
                    if (next_potential_dependent_instr['rs1'] == current_original_instr['rd'] or \
                       (next_potential_dependent_instr['rs2'] is not None and next_potential_dependent_instr['rs2'] == current_original_instr['rd'])):
                        
                        nops_needed_for_this_dependency = 0 # NOPs necessários para esta dependência específica.
                        if not forwarding: # Sem forwarding:
                            # Se a distância é 1, são necessários 2 NOPs. (Ex: add R1,R2,R3; add R4,R1,R5 -> R1 lido 2 ciclos depois)
                            # Se a distância é 2, é necessário 1 NOP.   (Ex: add R1,R2,R3; nop; add R4,R1,R5 -> R1 lido 2 ciclos depois)
                            # A instrução que escreve (current_original_instr) está no ciclo C.
                            # A instrução que lê (next_potential_dependent_instr) está no ciclo C+k.
                            # Sem forwarding, a escrita em WB é no ciclo C+4. A leitura em ID é no ciclo C+k+1.
                            # Para não haver stall, C+k+1 > C+4  => k+1 > 4 => k > 3.
                            # Se k=1, precisa de 2 NOPs. (Original: I1, I2. Com NOPs: I1, NOP, NOP, I2)
                            # Se k=2, precisa de 1 NOP.  (Original: I1, I_other, I2. Com NOPs: I1, I_other, NOP, I2)
                            if k == 1: nops_needed_for_this_dependency = 2
                            elif k == 2: nops_needed_for_this_dependency = 1
                        else: # Com forwarding:
                            # NOPs são necessários apenas para load-use hazard.
                            # Se a instrução que escreve (current_original_instr) é um LOAD e a distância é 1 (k=1).
                            if current_original_instr['is_load'] and k == 1:
                                nops_needed_for_this_dependency = 1 # Precisa de 1 NOP.
                        
                        # Mantém o maior número de NOPs necessários encontrado até agora para a `current_original_instr`.
                        nops_to_insert_after_current = max(nops_to_insert_after_current, nops_needed_for_this_dependency)
            
            # Insere os NOPs calculados após a `current_original_instr` na lista `result`.
            for _ in range(nops_to_insert_after_current):
                result.append({
                    'hex': NOP_HEX, 'type': 'NOP', 'rs1': None, 'rs2': None, 'rd': None,
                    'is_load': False, 'is_store': False, 'is_branch': False
                })
        
        idx += 1 # Move para a próxima instrução original.

    nops_added = len(result) - len(instructions) # Calcula o número total de NOPs adicionados.
    return result, nops_added # Retorna a lista de instruções com NOPs e a contagem de NOPs.

def has_dependency(instr1, instr2): # Define uma função para verificar se existe dependência (RAW, WAR, WAW) entre duas instruções.
    """Verifica se existe dependência entre duas instruções"""
    # RAW (Read After Write): instr2 lê um registrador que instr1 escreve.
    if instr1['rd'] is not None and instr1['rd'] != 0: # Se instr1 escreve em um registrador válido.
        if (instr2['rs1'] is not None and instr2['rs1'] == instr1['rd']) or \
           (instr2['rs2'] is not None and instr2['rs2'] == instr1['rd']): # E instr2 lê esse registrador.
            return True # Há uma dependência RAW.
    
    # WAR (Write After Read): instr2 escreve em um registrador que instr1 lê.
    if instr2['rd'] is not None and instr2['rd'] != 0: # Se instr2 escreve em um registrador válido.
        if (instr1['rs1'] is not None and instr1['rs1'] == instr2['rd']) or \
           (instr1['rs2'] is not None and instr1['rs2'] == instr2['rd']): # E instr1 lê esse registrador.
            return True # Há uma dependência WAR.
    
    # WAW (Write After Write): instr2 escreve no mesmo registrador que instr1 escreve.
    if (instr1['rd'] is not None and instr2['rd'] is not None and 
        instr1['rd'] != 0 and instr2['rd'] != 0 and instr1['rd'] == instr2['rd']): # Se ambas escrevem no mesmo registrador válido.
        return True # Há uma dependência WAW.
    
    return False # Nenhuma dependência detectada.

def can_reorder_safely(instructions, pos1, pos2): # Define uma função para verificar se duas instruções (em pos1 e pos2) podem ser reordenadas com segurança.
    """Verifica se duas instruções podem ser reordenadas com segurança"""
    # Assume-se que queremos mover a instrução em pos2 para a posição de pos1, e a de pos1 para pos1+1.
    # Esta função na verdade verifica se instr[pos2] pode ser movida para *antes* de instr[pos1].
    # A lógica em `reorder_to_avoid_nops` tenta mover `candidate` (instr[j]) para *imediatamente após* `current` (instr[i]).
    # O que se quer verificar é se podemos trocar `instructions[pos1]` com `instructions[pos2]`.
    # Ou seja, `instr1` (em `pos1`) e `instr2` (em `pos2`). Original: ..., instr1, ..., instr2, ...  -> Trocado: ..., instr2, ..., instr1, ...

    if pos1 >= pos2 or pos1 < 0 or pos2 >= len(instructions): # Verifica se as posições são válidas e distintas.
        return False
    
    instr1 = instructions[pos1] # Instrução originalmente na primeira posição.
    instr2 = instructions[pos2] # Instrução originalmente na segunda posição.
    
    # Não pode reordenar instruções de controle, pois isso alteraria o fluxo do programa.
    if instr1['is_branch'] or instr2['is_branch']:
        return False
    
    # Não pode reordenar loads/stores em relação a outras loads/stores ou entre si de forma simplista devido a possíveis dependências de memória (aliasing).
    # Para uma reordenação segura, precisaríamos de análise de dependência de memória, o que é complexo.
    # Esta simplificação evita reordenar qualquer load/store.
    if instr1['is_load'] or instr1['is_store'] or instr2['is_load'] or instr2['is_store']:
        return False
    
    # Verifica se a troca (instr2 antes de instr1) introduz novas dependências ou viola existentes.
    # Se instr2 é movida para antes de instr1:
    #   - instr2 não pode depender de instr1 (RAW se instr1 escreve o que instr2 lê).
    #   - instr1 não pode depender de instr2 de forma que a ordem importe (WAR/WAW).
    if has_dependency(instr1, instr2): # Se já existe uma dependência entre instr1 e instr2 na ordem original.
        return False # Trocá-las provavelmente violaria essa dependência.

    # Verifica dependências com instruções intermediárias.
    # Se instr2 é movida para a posição de instr1, e instr1 e as intermediárias são deslocadas.
    # Ex: A, B, C, D. Mover D para a posição de B: A, D, B, C.
    # Aqui, a intenção parece ser trocar `instr1` (em `pos1`) com `instr2` (em `pos2`).
    # `instr1` é `instructions[pos1]`, `instr2` é `instructions[pos2]`.
    # Ordem original: ... I_before_pos1, instr1, I_inter_1, ..., I_inter_k, instr2, I_after_pos2 ...
    # Ordem nova:     ... I_before_pos1, instr2, I_inter_1, ..., I_inter_k, instr1, I_after_pos2 ...
    # Precisamos checar se `instr2` depende de alguma `I_inter_j` ou se alguma `I_inter_j` depende de `instr2` de forma que a nova ordem seja inválida.
    # E similarmente para `instr1` com as `I_inter_j` na nova ordem.

    # A condição na `reorder_to_avoid_nops` é: `temp_list = reordered[:i] + [candidate] + [current] + reordered[i+1:j] + reordered[j+1:]`
    # Onde `current` é `instructions[i]` e `candidate` é `instructions[j]`.
    # Ou seja, `current` é `instr1` e `candidate` é `instr2`.
    # A `candidate` (instr2) é movida para *imediatamente após* `current` (instr1), mas a função aqui é usada para verificar se `instr1` e `instr2` podem ser trocadas.
    # Esta função `can_reorder_safely` parece estar verificando se `instr1` (em `pos1`) pode ser trocada com `instr2` (em `pos2`).
    # Se `instr1` e `instr2` são trocadas:
    #   `instr1` não pode ter dependência WAR ou WAW com `instr2` (porque `instr2` viria antes).
    #   `instr2` não pode ter dependência RAW com `instr1` (porque `instr2` viria antes).
    #   Para cada instrução `intermediate` entre `pos1` e `pos2`:
    #     - `instr1` (que vai para `pos2`) não pode depender de `intermediate` de forma que a nova ordem seja ruim.
    #     - `intermediate` não pode depender de `instr1` de forma que a nova ordem seja ruim.
    #     - `instr2` (que vai para `pos1`) não pode depender de `intermediate` de forma que a nova ordem seja ruim.
    #     - `intermediate` não pode depender de `instr2` de forma que a nova ordem seja ruim.

    # A verificação de dependência direta `has_dependency(instr1, instr2)` já cobre alguns casos.
    # A lógica aqui parece simplificada: se há *qualquer* dependência entre `instr1` ou `instr2` e *qualquer* instrução intermediária, não reordena.
    for k in range(pos1 + 1, pos2): # Itera sobre as instruções entre pos1 e pos2.
        intermediate = instructions[k] # Pega uma instrução intermediária.
        # Se instr1 (originalmente em pos1) tem dependência com intermediate, ou
        # se intermediate tem dependência com instr2 (originalmente em pos2), ou
        # se instr2 tem dependência com intermediate.
        # Esta lógica é um pouco confusa em relação à transformação exata que está sendo permitida.
        # Se a intenção é trocar `instr1` e `instr2`, então:
        # - `instr2` vs `intermediate`: `has_dependency(instr2, intermediate)` (instr2 virá antes de intermediate)
        # - `intermediate` vs `instr1`: `has_dependency(intermediate, instr1)` (intermediate virá antes de instr1)
        if (has_dependency(instr1, intermediate) or # Se instr1 (em pos1) depende ou é dependida por uma intermediária.
            has_dependency(intermediate, instr2) or # Se uma intermediária depende ou é dependida por instr2 (em pos2).
            has_dependency(instr2, intermediate)): # Adicionando a verificação simétrica para instr2 e intermediate.
            # A ideia é que nem `instr1` nem `instr2` podem ter suas dependências com as instruções intermediárias alteradas de forma a quebrar o programa.
            # Se `instr1` vai para depois de `intermediate`, e `intermediate` lia algo que `instr1` escrevia, isso pode ser um problema.
            # Se `instr2` vai para antes de `intermediate`, e `instr2` escreve algo que `intermediate` lia, isso pode ser um problema.
            return False # Não pode reordenar se houver dependência com intermediárias.
    
    return True # Se passou por todas as verificações, pode reordenar.

def reorder_to_avoid_nops(instructions, forwarding=False): # Define uma função para reordenar instruções para minimizar NOPs devido a conflitos de dados.
    """Reordena instruções para minimizar NOPs - CORRIGIDO"""
    # Primeiro, calcula NOPs sem reordenação para ter uma linha de base.
    _, original_nops = insert_nops_data(instructions, forwarding) # O '_' ignora o primeiro valor retornado (lista de instruções com NOPs).
    
    reordered = copy.deepcopy(instructions) # Cria uma cópia profunda da lista de instruções para manipular.
    improvements_made = True # Flag para controlar o loop de otimização.
    
    # Aplica várias passadas de otimização enquanto melhorias puderem ser feitas.
    while improvements_made:
        improvements_made = False # Reseta a flag no início de cada passada.
        
        # Itera sobre as instruções na lista (potencialmente já reordenada).
        # O `i` é o índice da instrução que pode estar causando um futuro stall (produtora).
        for i in range(len(reordered)): 
            current_producer = reordered[i] # A instrução atual que pode ser uma produtora de dados.
            
            # Se esta instrução (`current_producer`) escreve em um registrador (é uma produtora potencial de conflito RAW).
            if current_producer['rd'] is not None and current_producer['rd'] != 0:
                # Tenta encontrar uma instrução independente (`candidate_consumer_or_independent`) nas próximas posições (janela de até 3 instruções)
                # que poderia ser adiantada para preencher um slot de NOP que seria causado pela `current_producer`.
                # A ideia é: se `current_producer` é seguida por `instr_A` que depende dela, causando NOPs,
                # talvez possamos encontrar `instr_B` (que não depende de `current_producer`) mais à frente
                # e movê-la para entre `current_producer` e `instr_A`.
                # Original: P, A (causa NOPs), B -> Com reordenação: P, B, A (idealmente B não depende de P, e A não depende de B).
                
                # O loop `j` procura por uma instrução `candidate_to_move_up` que pode ser movida para logo após `current_producer`.
                # Este `j` é o índice da instrução que será considerada para ser movida para a posição `i+1`.
                for j in range(i + 1, min(i + 4, len(reordered))): # Janela de busca.
                    candidate_to_move_up = reordered[j] # A instrução que estamos considerando mover.
                    
                    # Verifica se `candidate_to_move_up` (de `reordered[j]`) pode ser movida para a posição `i+1`,
                    # ou seja, entre `reordered[i]` (current_producer) e `reordered[i+1]` (se existir).
                    # A função `can_reorder_safely` precisa ser interpretada corretamente aqui.
                    # `can_reorder_safely(lista, pos_A, pos_B)` verifica se `lista[pos_A]` e `lista[pos_B]` podem ser trocadas.
                    # Aqui, a intenção é mover `candidate_to_move_up` (de `j`) para `i+1`.
                    # Isso significa que `current_producer` (em `i`) permanece, `candidate_to_move_up` (de `j`) vai para `i+1`,
                    # e as instruções entre `i+1` e `j-1` são deslocadas para `i+2` até `j`.
                    
                    # Vamos simplificar a condição de reordenação:
                    #   1. `candidate_to_move_up` não pode depender de `current_producer`.
                    #   2. Nenhuma instrução entre `current_producer` e `candidate_to_move_up` pode depender de `candidate_to_move_up`.
                    #   3. `candidate_to_move_up` não pode ser branch, load ou store (para simplificar).
                    
                    can_move_candidate = True
                    if candidate_to_move_up['is_branch'] or candidate_to_move_up['is_load'] or candidate_to_move_up['is_store']:
                        can_move_candidate = False
                    if has_dependency(current_producer, candidate_to_move_up): # Se a candidata depende da produtora, não pode mover para logo depois sem NOPs (a menos que a produtora seja LW e haja forwarding).
                        can_move_candidate = False # Essa condição é forte, queremos mover algo *independente* da produtora.
                    
                    if can_move_candidate:
                        for k_inter in range(i + 1, j): # Verifica dependências com as instruções que seriam "puladas".
                            intermediate_instr = reordered[k_inter]
                            # Se a candidata escreve algo que a intermediária lê (RAW), ou lê algo que a intermediária escreve (WAR),
                            # ou escreve no mesmo lugar (WAW).
                            if has_dependency(candidate_to_move_up, intermediate_instr) or has_dependency(intermediate_instr, candidate_to_move_up):
                                can_move_candidate = False
                                break
                    
                    if can_move_candidate:
                        # Simula a movimentação: `candidate_to_move_up` (de `j`) é inserida em `i+1`.
                        temp_list = list(reordered) # Cria uma cópia para simulação.
                        moved_instr = temp_list.pop(j) # Remove a candidata da sua posição original.
                        temp_list.insert(i + 1, moved_instr) # Insere a candidata após `current_producer`.
                        
                        _, temp_nops = insert_nops_data(temp_list, forwarding) # Calcula NOPs com a lista temporária reordenada.
                        _, current_nops = insert_nops_data(reordered, forwarding) # Calcula NOPs com a lista atual (antes da tentativa de reordenação).
                        
                        if temp_nops < current_nops: # Se a reordenação reduziu o número de NOPs.
                            reordered = temp_list # Aplica a mudança à lista principal.
                            improvements_made = True # Indica que uma melhoria foi feita nesta passada.
                            break # Sai do loop interno `j` e tenta reavaliar desde o início da lista `reordered` (devido ao `while improvements_made`).
            
            if improvements_made: # Se uma melhoria foi feita no loop interno `j`.
                break # Sai do loop externo `i` para reiniciar o processo `while` e reavaliar toda a lista.
    
    # Após o loop de reordenação, insere os NOPs finais na lista otimizada.
    final_result, final_nops = insert_nops_data(reordered, forwarding)
    nops_saved = max(0, original_nops - final_nops) # Calcula quantos NOPs foram economizados.
    
    return final_result, nops_saved # Retorna a lista final de instruções (com NOPs) e o número de NOPs economizados.

def handle_branch_conflicts_nop(instructions): # Define uma função para tratar conflitos de controle inserindo um NOP após cada instrução de branch/jump.
    """Adiciona NOPs após instruções de controle"""
    result = [] # Inicializa uma lista para o resultado.
    nops_added = 0 # Contador de NOPs adicionados.
    
    for instr in instructions: # Itera sobre cada instrução original.
        result.append(copy.deepcopy(instr)) # Adiciona a instrução atual ao resultado.
        
        if instr['is_branch']: # Se a instrução é um branch/jump.
            result.append({ # Adiciona um NOP após ela.
                'hex': NOP_HEX, 'type': 'NOP', 'rs1': None, 'rs2': None, 'rd': None,
                'is_load': False, 'is_store': False, 'is_branch': False
            })
            nops_added += 1 # Incrementa o contador de NOPs.
    
    return result, nops_added # Retorna a lista com NOPs de branch e a contagem de NOPs adicionados.

def handle_delayed_branch(instructions): # Define uma função para implementar a técnica de delayed branch.
    """Implementa delayed branch - CORRIGIDO"""
    # A ideia é preencher o "delay slot" (a instrução imediatamente após um branch) com uma instrução útil.
    result = [] # Lista para as instruções processadas com delayed branch.
    nops_added_for_delay_slots = 0 # NOPs adicionados se não foi possível preencher o slot.
    # `useful_moved` não é usado no retorno, mas poderia contar quantas vezes o slot foi preenchido utilmente.
    
    i = 0 # Índice para percorrer a lista de instruções original.
    while i < len(instructions): # Itera sobre as instruções.
        current_instr = instructions[i] # Pega a instrução atual.
        
        if current_instr['is_branch']: # Se a instrução atual é um branch.
            # Adiciona a instrução de branch primeiro.
            result.append(copy.deepcopy(current_instr))
            
            # Tenta encontrar uma instrução ANTERIOR para mover para o delay slot (após o branch).
            # Esta é uma estratégia "branch-likely" ou "move from before".
            slot_filled_with_useful_instruction = False
            
            # Procura nas instruções já adicionadas a `result` (ou seja, antes do branch).
            # `len(result) - 1` é o branch. `len(result) - 2` é a instrução antes do branch.
            # Tenta mover uma instrução de até 3 posições antes do branch (índices `idx_candidate_to_move`).
            for lookback_idx in range(1, min(4, len(result))): # Olha 1, 2 ou 3 instruções para trás.
                idx_candidate_to_move = len(result) - 1 - lookback_idx # Índice da candidata em `result`.
                if idx_candidate_to_move < 0: break # Não há mais instruções para trás.

                candidate_instr = result[idx_candidate_to_move] # Pega a instrução candidata.
                
                can_move_to_slot = True
                # 1. A candidata não pode ser ela mesma um branch, load ou store (simplificação).
                if candidate_instr['is_branch'] or candidate_instr['is_load'] or candidate_instr['is_store'] or candidate_instr['type'] == 'NOP':
                    can_move_to_slot = False
                
                # 2. A candidata não pode modificar os registradores lidos pela instrução de branch.
                if can_move_to_slot and candidate_instr['rd'] is not None and candidate_instr['rd'] != 0:
                    if (current_instr['rs1'] is not None and current_instr['rs1'] == candidate_instr['rd']) or \
                       (current_instr['rs2'] is not None and current_instr['rs2'] == candidate_instr['rd']):
                        can_move_to_slot = False
                
                # 3. A candidata não pode depender de instruções entre ela e o branch (que permaneceriam antes do branch).
                # (Se a candidata lia algo que uma instrução intermediária escrevia, mover a candidata para depois do branch quebraria isso).
                if can_move_to_slot:
                    for k_inter in range(idx_candidate_to_move + 1, len(result) - 1): # Instruções entre a candidata e o branch.
                        intermediate_instr_before_branch = result[k_inter]
                        if has_dependency(intermediate_instr_before_branch, candidate_instr): # Se a candidata (que será movida) depende da intermediária.
                            can_move_to_slot = False
                            break
                
                if can_move_to_slot:
                    moved_instr = result.pop(idx_candidate_to_move) # Remove a candidata de sua posição original.
                    result.append(moved_instr) # Adiciona a candidata no delay slot (após o branch).
                    slot_filled_with_useful_instruction = True
                    break # Slot preenchido, sai do loop de busca.
            
            if not slot_filled_with_useful_instruction:
                # Se não encontrou instrução útil para mover, insere um NOP no delay slot.
                result.append({
                    'hex': NOP_HEX, 'type': 'NOP', 'rs1': None, 'rs2': None, 'rd': None,
                    'is_load': False, 'is_store': False, 'is_branch': False
                })
                nops_added_for_delay_slots += 1
            
            i += 1 # Avança o índice da instrução original (branch já processado).
        else:
            # Se não for um branch, apenas adiciona a instrução ao resultado.
            result.append(copy.deepcopy(current_instr))
            i += 1 # Avança o índice.
            
    return result, nops_added_for_delay_slots # Retorna a lista com delayed branches e NOPs adicionados.

def write_output(filename, instrs): # Define uma função para escrever a lista de instruções (em formato hexadecimal) em um arquivo.
    with open(filename, 'w') as f: # Abre o arquivo especificado em modo de escrita ('w').
        for instr in instrs: # Itera sobre cada instrução na lista.
            f.write(instr['hex'] + '\n') # Escreve o campo 'hex' da instrução seguido de uma nova linha.

def write_conflicts_report(filename, conflicts, title): # Define uma função para escrever um relatório de conflitos em um arquivo.
    with open(filename, 'w') as f: # Abre o arquivo em modo de escrita.
        f.write(f"=== {title} ===\n\n") # Escreve o título do relatório.
        if not conflicts: # Se a lista de conflitos estiver vazia.
            f.write("Nenhum conflito detectado.\n") # Informa que não há conflitos.
        else: # Se houver conflitos.
            for conflict in conflicts: # Itera sobre cada conflito.
                if 'register' in conflict:  # Se for um conflito de dados (possui a chave 'register').
                    conflict_type_str = "Load-Use" if conflict.get('is_load_use', False) else "RAW" # Determina se é Load-Use ou RAW genérico.
                    f.write(f"Conflito {conflict_type_str} na posição {conflict['position']}: ") # Escreve o tipo e posição do conflito.
                    f.write(f"Registrador x{conflict['register']} ") # Escreve o registrador envolvido.
                    f.write(f"(fonte: pos {conflict['source']}, distância: {conflict['distance']})\n") # Escreve a origem e distância do conflito.
                else:  # Se for um conflito de controle (não possui 'register', mas tem 'type').
                    f.write(f"Conflito de controle na posição {conflict['position']}: ") # Escreve a posição.
                    f.write(f"Instrução tipo {conflict['type']}\n") # Escreve o tipo da instrução de controle.

def main(): # Define a função principal do programa.
    # Permite especificar arquivo via linha de comando.
    if len(sys.argv) > 1: # Se mais de um argumento foi passado na linha de comando (o primeiro é o nome do script).
        input_file = sys.argv[1] # Usa o segundo argumento como nome do arquivo de entrada.
    else:
        input_file = "teste5.hex" # Nome padrão do arquivo de entrada se nenhum for fornecido.
    
    if not os.path.exists(input_file): # Verifica se o arquivo de entrada existe.
        print(f"Arquivo {input_file} não encontrado!") # Informa se o arquivo não foi encontrado.
        return # Encerra o programa.
    
    original = read_instructions(input_file) # Lê as instruções do arquivo de entrada.
    
    print("=== ANÁLISE DE CONFLITOS NO PIPELINE ===\n") # Imprime um cabeçalho.
    print(f"Arquivo de entrada: {input_file}") # Imprime o nome do arquivo de entrada.
    print(f"Total de instruções: {len(original)}\n") # Imprime o número total de instruções originais.
    
    # Técnica 1: Detectar conflitos de dados sem forwarding.
    data_conflicts_sf = detect_data_conflicts(original, forwarding=False) # Detecta conflitos de dados sem forwarding.
    write_conflicts_report("conflitos_dados_sem_forwarding.txt", # Escreve o relatório.
                           data_conflicts_sf, "CONFLITOS DE DADOS SEM FORWARDING")
    
    # Técnica 2: Detectar conflitos de dados com forwarding.
    data_conflicts_cf = detect_data_conflicts(original, forwarding=True) # Detecta conflitos de dados com forwarding.
    write_conflicts_report("conflitos_dados_com_forwarding.txt", # Escreve o relatório.
                           data_conflicts_cf, "CONFLITOS DE DADOS COM FORWARDING")
    
    # Detectar conflitos de controle.
    control_conflicts = detect_control_conflicts(original) # Detecta conflitos de controle.
    write_conflicts_report("conflitos_controle.txt", # Escreve o relatório.
                           control_conflicts, "CONFLITOS DE CONTROLE")
    
    # Técnica 3: Inserção de NOPs para conflitos de dados, sem forwarding.
    instrs_nop_sf, nops_sf_count = insert_nops_data(copy.deepcopy(original), forwarding=False) # Insere NOPs. (nops_sf_count é o número de NOPs adicionados)
    write_output("saida_nop_sem_forwarding.hex", instrs_nop_sf) # Escreve o resultado em arquivo.
    
    # Técnica 4: Inserção de NOPs para conflitos de dados, com forwarding.
    instrs_nop_cf, nops_cf_count = insert_nops_data(copy.deepcopy(original), forwarding=True) # Insere NOPs. (nops_cf_count é o número de NOPs adicionados)
    write_output("saida_nop_com_forwarding.hex", instrs_nop_cf) # Escreve o resultado.
    
    # Técnica 5: Reordenação de instruções para evitar NOPs, sem forwarding.
    instrs_reord_sf, saved_sf = reorder_to_avoid_nops(copy.deepcopy(original), forwarding=False) # Reordena e insere NOPs.
    write_output("saida_reord_sem_forwarding.hex", instrs_reord_sf) # Escreve o resultado.
    
    # Técnica 6: Reordenação de instruções para evitar NOPs, com forwarding.
    instrs_reord_cf, saved_cf = reorder_to_avoid_nops(copy.deepcopy(original), forwarding=True) # Reordena e insere NOPs.
    write_output("saida_reord_com_forwarding.hex", instrs_reord_cf) # Escreve o resultado.
    
    # Técnica 7: Tratamento de conflito de controle com inserção de NOP.
    instrs_branch_nop, ctrl_nops_count = handle_branch_conflicts_nop(copy.deepcopy(original)) # Insere NOPs após branches. (ctrl_nops_count é o número de NOPs adicionados)
    write_output("saida_branch_nop.hex", instrs_branch_nop) # Escreve o resultado.
    
    # Técnica 8: Tratamento de conflito de controle com Delayed Branch.
    instrs_branch_delay, delay_nops_count = handle_delayed_branch(copy.deepcopy(original)) # Aplica delayed branch. (delay_nops_count é o número de NOPs inseridos nos delay slots não preenchidos)
    write_output("saida_branch_delay.hex", instrs_branch_delay) # Escreve o resultado.
    
    # Técnica 9: Combinação otimizada (Exemplo: Reordenação com forwarding + Delayed Branch).
    # Aplica reordenação com forwarding primeiro.
    combined_reord_cf, _ = reorder_to_avoid_nops(copy.deepcopy(original), forwarding=True) # O '_' ignora os NOPs salvos aqui.
    # Depois trata conflitos de controle na lista já reordenada usando delayed branch.
    combined_final, _ = handle_delayed_branch(combined_reord_cf) # O '_' ignora os NOPs de delay slot.
    write_output("saida_comb_4e6.hex", combined_final) # Escreve o resultado combinado. (O nome do arquivo sugere combinação das técnicas 4 (NOP com forwarding) e 6 (Reordenação com forwarding), mas o código implementa Reordenação com forwarding + Delayed Branch).
    
    # Relatório final impresso no console.
    print("=== RELATÓRIO DE DETECÇÃO ===")
    print(f"Conflitos de dados sem forwarding: {len(data_conflicts_sf)}")
    print(f"Conflitos de dados com forwarding: {len(data_conflicts_cf)}")
    print(f"Conflitos de controle: {len(control_conflicts)}")
    print()
    
    print("=== RELATÓRIO DE SOBRECUSTO (TOTAL DE INSTRUÇÕES APÓS TRATAMENTO) ===")
    original_count = len(original)
    print(f"Instruções originais: {original_count}")
    print(f"Técnica 3 - NOPs (dados) s/ forwarding: {len(instrs_nop_sf)} (+{len(instrs_nop_sf) - original_count} NOPs)")
    print(f"Técnica 4 - NOPs (dados) c/ forwarding: {len(instrs_nop_cf)} (+{len(instrs_nop_cf) - original_count} NOPs)")
    print(f"Técnica 5 - Reord. (dados) s/ forwarding: {len(instrs_reord_sf)} (+{len(instrs_reord_sf) - original_count}, NOPs economizados pela reord.: {saved_sf})")
    print(f"Técnica 6 - Reord. (dados) c/ forwarding: {len(instrs_reord_cf)} (+{len(instrs_reord_cf) - original_count}, NOPs economizados pela reord.: {saved_cf})")
    print(f"Técnica 7 - NOPs (controle): {len(instrs_branch_nop)} (+{len(instrs_branch_nop) - original_count} NOPs)")
    print(f"Técnica 8 - Delayed Branch (controle): {len(instrs_branch_delay)} (+{len(instrs_branch_delay) - original_count} NOPs/slots preenchidos)") # O número de NOPs aqui é `delay_nops_count`.
    print(f"Técnica 9 - Combinação (Reord. c/ Fwd + Delayed Branch): {len(combined_final)} (+{len(combined_final) - original_count})")
    print("================================\n")
    
    print("Arquivos de saída e relatórios gerados com sucesso!")

if __name__ == "__main__": # Bloco padrão em Python: verifica se o script está sendo executado diretamente (não importado como módulo).
    main() # Chama a função principal.