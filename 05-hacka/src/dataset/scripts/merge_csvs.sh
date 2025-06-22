#!/bin/bash

# Script para combinar múltiplos arquivos CSV em um único arquivo
# Uso: ./merge_csvs.sh [pasta_origem] [arquivo_destino]

# Definir valores padrão
PASTA_ORIGEM=${1:-"./csvs"}
ARQUIVO_DESTINO=${2:-"merged_data.csv"}

# Verificar se a pasta existe
if [ ! -d "$PASTA_ORIGEM" ]; then
    echo "Erro: A pasta '$PASTA_ORIGEM' não existe."
    echo "Uso: $0 [pasta_origem] [arquivo_destino]"
    exit 1
fi

# Verificar se existem arquivos CSV na pasta
if ! ls "$PASTA_ORIGEM"/*.csv 1> /dev/null 2>&1; then
    echo "Erro: Nenhum arquivo CSV encontrado na pasta '$PASTA_ORIGEM'."
    exit 1
fi

# Remover arquivo de destino se já existir
if [ -f "$ARQUIVO_DESTINO" ]; then
    rm "$ARQUIVO_DESTINO"
    echo "Arquivo existente '$ARQUIVO_DESTINO' removido."
fi

echo "Combinando arquivos CSV da pasta '$PASTA_ORIGEM'..."

# Contador para controlar o cabeçalho
primeiro_arquivo=true

# Iterar sobre todos os arquivos CSV na pasta
for arquivo_csv in "$PASTA_ORIGEM"/*.csv; do
    if [ -f "$arquivo_csv" ]; then
        echo "Processando: $(basename "$arquivo_csv")"
        
        if [ "$primeiro_arquivo" = true ]; then
            # Para o primeiro arquivo, incluir o cabeçalho
            cat "$arquivo_csv" >> "$ARQUIVO_DESTINO"
            primeiro_arquivo=false
        else
            # Para os demais arquivos, pular a primeira linha (cabeçalho)
            tail -n +2 "$arquivo_csv" >> "$ARQUIVO_DESTINO"
        fi
    fi
done

# Contar linhas do arquivo final
total_linhas=$(wc -l < "$ARQUIVO_DESTINO")
total_arquivos=$(ls "$PASTA_ORIGEM"/*.csv | wc -l)

echo ""
echo "✅ Combinação concluída!"
echo "📁 Arquivos processados: $total_arquivos"
echo "📄 Arquivo de saída: $ARQUIVO_DESTINO"
echo "📊 Total de linhas: $total_linhas"
echo ""
echo "Para usar o script:"
echo "  ./merge_csvs.sh                    # Usa pasta './csvs' e arquivo 'merged_data.csv'"
echo "  ./merge_csvs.sh /caminho/pasta     # Especifica pasta origem"
echo "  ./merge_csvs.sh pasta arquivo.csv  # Especifica pasta e arquivo de saída"