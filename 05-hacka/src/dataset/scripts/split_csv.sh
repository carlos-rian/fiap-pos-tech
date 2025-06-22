#!/bin/bash

# Script para dividir arquivo CSV em lotes de 200 linhas
# Uso: ./split_csv.sh arquivo.csv

# Função para exibir ajuda
show_help() {
    echo "Uso: $0 <arquivo.csv> [tamanho_lote]"
    echo ""
    echo "Parâmetros:"
    echo "  arquivo.csv    - Arquivo CSV de entrada"
    echo "  tamanho_lote   - Número de linhas por lote (padrão: 200)"
    echo ""
    echo "Exemplo:"
    echo "  $0 mapping.csv"
    echo "  $0 mapping.csv 150"
}

# Verificar se foi fornecido pelo menos um parâmetro
if [ $# -lt 1 ]; then
    echo "Erro: Arquivo CSV não especificado"
    show_help
    exit 1
fi

# Definir variáveis
INPUT_FILE="$1"
BATCH_SIZE="${2:-200}"  # Padrão 200 se não especificado

# Verificar se o arquivo existe
if [ ! -f "$INPUT_FILE" ]; then
    echo "Erro: Arquivo '$INPUT_FILE' não encontrado"
    exit 1
fi

# Verificar se o arquivo é um CSV (extensão)
if [[ ! "$INPUT_FILE" =~ \.csv$ ]]; then
    echo "Aviso: O arquivo não possui extensão .csv"
fi

# Obter o nome base do arquivo (sem extensão)
BASE_NAME=$(basename "$INPUT_FILE" .csv)
DIR_NAME=$(dirname "$INPUT_FILE")

# Criar diretório de saída se não existir
OUTPUT_DIR="${DIR_NAME}/batches_${BASE_NAME}"
mkdir -p "$OUTPUT_DIR"

echo "Iniciando divisão do arquivo: $INPUT_FILE"
echo "Tamanho do lote: $BATCH_SIZE linhas"
echo "Diretório de saída: $OUTPUT_DIR"

# Contar total de linhas
TOTAL_LINES=$(wc -l < "$INPUT_FILE")
echo "Total de linhas no arquivo: $TOTAL_LINES"

# Extrair cabeçalho (primeira linha)
HEADER=$(head -n 1 "$INPUT_FILE")

# Calcular número de lotes necessários
TOTAL_BATCHES=$(( (TOTAL_LINES - 1 + BATCH_SIZE - 1) / BATCH_SIZE ))
echo "Número de lotes a serem criados: $TOTAL_BATCHES"

# Dividir o arquivo em lotes
BATCH_NUM=1
LINE_START=2  # Começar da linha 2 (pular cabeçalho)

while [ $LINE_START -le $TOTAL_LINES ]; do
    # Calcular linha final do lote atual
    LINE_END=$((LINE_START + BATCH_SIZE - 1))
    
    # Ajustar se exceder o total de linhas
    if [ $LINE_END -gt $TOTAL_LINES ]; then
        LINE_END=$TOTAL_LINES
    fi
    
    # Nome do arquivo de saída (com zero padding)
    OUTPUT_FILE="${OUTPUT_DIR}/${BASE_NAME}_lote_$(printf "%03d" $BATCH_NUM).csv"
    
    # Criar arquivo de lote com cabeçalho
    echo "$HEADER" > "$OUTPUT_FILE"
    
    # Adicionar linhas do lote
    sed -n "${LINE_START},${LINE_END}p" "$INPUT_FILE" >> "$OUTPUT_FILE"
    
    # Contar linhas no lote atual (sem o cabeçalho)
    BATCH_LINES=$((LINE_END - LINE_START + 1))
    
    echo "Lote $BATCH_NUM criado: $OUTPUT_FILE ($BATCH_LINES linhas de dados)"
    
    # Próximo lote
    LINE_START=$((LINE_END + 1))
    BATCH_NUM=$((BATCH_NUM + 1))
done

echo ""
echo "Divisão concluída!"
echo "Arquivos criados em: $OUTPUT_DIR"
echo "Total de lotes: $((BATCH_NUM - 1))"

# Listar arquivos criados
echo ""
echo "Arquivos gerados:"
ls -la "$OUTPUT_DIR"/*.csv | awk '{print $9, "(" $5, "bytes)"}'