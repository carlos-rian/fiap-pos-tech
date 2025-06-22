#!/bin/bash

# Script para comparar arquivos entre duas pastas
# Uso: ./compare_folders.sh pasta1 pasta2 [extensao]

# Configurações padrão
PASTA1=${1}
PASTA2=${2}
EXTENSAO=${3:-"*"}

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para mostrar uso
show_usage() {
    echo "Uso: $0 pasta1 pasta2 [extensao]"
    echo ""
    echo "Parâmetros:"
    echo "  pasta1     - Primeira pasta (origem)"
    echo "  pasta2     - Segunda pasta (destino)"
    echo "  extensao   - Filtrar por extensão (opcional, ex: png, jpg, *)"
    echo ""
    echo "Exemplos:"
    echo "  $0 dataset_original/ dataset_optimized/"
    echo "  $0 pasta1/ pasta2/ png"
    echo "  $0 /caminho/origem /caminho/destino jpg"
}

# Verificar parâmetros
if [ -z "$PASTA1" ] || [ -z "$PASTA2" ]; then
    echo -e "${RED}❌ Erro: Especifique as duas pastas${NC}"
    show_usage
    exit 1
fi

# Verificar se pastas existem
if [ ! -d "$PASTA1" ]; then
    echo -e "${RED}❌ Pasta não encontrada: $PASTA1${NC}"
    exit 1
fi

if [ ! -d "$PASTA2" ]; then
    echo -e "${RED}❌ Pasta não encontrada: $PASTA2${NC}"
    exit 1
fi

echo -e "${BLUE}📂 Comparando pastas:${NC}"
echo -e "${CYAN}📁 Pasta 1 (origem): $PASTA1${NC}"
echo -e "${CYAN}📁 Pasta 2 (destino): $PASTA2${NC}"
echo -e "${YELLOW}🔍 Extensão: $EXTENSAO${NC}"
echo ""

# Definir padrão de busca baseado na extensão
if [ "$EXTENSAO" = "*" ]; then
    PATTERN="*"
else
    PATTERN="*.$EXTENSAO"
fi

# Criar arquivos temporários para listas
temp_dir=$(mktemp -d)
lista1="$temp_dir/lista1.txt"
lista2="$temp_dir/lista2.txt"

# Gerar lista de arquivos da pasta1 (apenas nomes, sem caminho)
echo -e "${BLUE}🔍 Coletando arquivos da pasta 1...${NC}"
find "$PASTA1" -type f -name "$PATTERN" -exec basename {} \; | sort > "$lista1"
count1=$(wc -l < "$lista1")

# Gerar lista de arquivos da pasta2 (apenas nomes, sem caminho)
echo -e "${BLUE}🔍 Coletando arquivos da pasta 2...${NC}"
find "$PASTA2" -type f -name "$PATTERN" -exec basename {} \; | sort > "$lista2"
count2=$(wc -l < "$lista2")

echo -e "${GREEN}📊 Total de arquivos:${NC}"
echo -e "   Pasta 1: $count1 arquivos"
echo -e "   Pasta 2: $count2 arquivos"
echo ""

# Encontrar arquivos apenas na pasta1 (faltando na pasta2)
echo -e "${RED}❌ Arquivos que existem na Pasta 1 mas NÃO na Pasta 2:${NC}"
missing_in_pasta2=$(comm -23 "$lista1" "$lista2")
missing_count2=0

if [ ! -z "$missing_in_pasta2" ]; then
    while IFS= read -r arquivo; do
        echo -e "${RED}   ➤ $arquivo${NC}"
        missing_count2=$((missing_count2 + 1))
    done <<< "$missing_in_pasta2"
else
    echo -e "${GREEN}   ✅ Nenhum arquivo faltando${NC}"
fi

echo ""

# Encontrar arquivos apenas na pasta2 (extras na pasta2)
echo -e "${YELLOW}⚠️  Arquivos que existem na Pasta 2 mas NÃO na Pasta 1:${NC}"
extra_in_pasta2=$(comm -13 "$lista1" "$lista2")
extra_count=0

if [ ! -z "$extra_in_pasta2" ]; then
    while IFS= read -r arquivo; do
        echo -e "${YELLOW}   ➤ $arquivo${NC}"
        extra_count=$((extra_count + 1))
    done <<< "$extra_in_pasta2"
else
    echo -e "${GREEN}   ✅ Nenhum arquivo extra${NC}"
fi

echo ""

# Encontrar arquivos comuns
echo -e "${GREEN}✅ Arquivos que existem em AMBAS as pastas:${NC}"
common_files=$(comm -12 "$lista1" "$lista2")
common_count=0

if [ ! -z "$common_files" ]; then
    # Mostrar apenas os primeiros 10 para não poluir o terminal
    echo "$common_files" | head -10 | while IFS= read -r arquivo; do
        echo -e "${GREEN}   ✓ $arquivo${NC}"
        common_count=$((common_count + 1))
    done
    
    total_common=$(echo "$common_files" | wc -l)
    if [ $total_common -gt 10 ]; then
        echo -e "${CYAN}   ... e mais $((total_common - 10)) arquivos${NC}"
    fi
    common_count=$total_common
else
    echo -e "${RED}   ❌ Nenhum arquivo em comum${NC}"
fi

echo ""

# Resumo final
echo -e "${BLUE}📊 RESUMO FINAL:${NC}"
echo -e "${CYAN}═══════════════════════════════════════${NC}"
echo -e "📁 Pasta 1: $count1 arquivos"
echo -e "📁 Pasta 2: $count2 arquivos"
echo -e "${GREEN}✅ Arquivos comuns: $common_count${NC}"
echo -e "${RED}❌ Faltando na Pasta 2: $missing_count2${NC}"
echo -e "${YELLOW}⚠️  Extras na Pasta 2: $extra_count${NC}"

# Calcular porcentagem de completude
if [ $count1 -gt 0 ]; then
    percent=$((common_count * 100 / count1))
    echo -e "${BLUE}📈 Completude: ${percent}%${NC}"
fi

# Salvar relatório detalhado
relatorio="$temp_dir/relatorio_comparacao.txt"
echo "RELATÓRIO DE COMPARAÇÃO DE PASTAS" > "$relatorio"
echo "=================================" >> "$relatorio"
echo "Pasta 1: $PASTA1 ($count1 arquivos)" >> "$relatorio"
echo "Pasta 2: $PASTA2 ($count2 arquivos)" >> "$relatorio"
echo "Extensão: $EXTENSAO" >> "$relatorio"
echo "Data: $(date)" >> "$relatorio"
echo "" >> "$relatorio"

echo "ARQUIVOS FALTANDO NA PASTA 2:" >> "$relatorio"
if [ ! -z "$missing_in_pasta2" ]; then
    echo "$missing_in_pasta2" >> "$relatorio"
else
    echo "Nenhum" >> "$relatorio"
fi

echo "" >> "$relatorio"
echo "ARQUIVOS EXTRAS NA PASTA 2:" >> "$relatorio"
if [ ! -z "$extra_in_pasta2" ]; then
    echo "$extra_in_pasta2" >> "$relatorio"
else
    echo "Nenhum" >> "$relatorio"
fi

# Copiar relatório para local acessível
cp "$relatorio" "./relatorio_comparacao_$(date +%Y%m%d_%H%M%S).txt"
echo ""
echo -e "${GREEN}📄 Relatório detalhado salvo em: relatorio_comparacao_$(date +%Y%m%d_%H%M%S).txt${NC}"

# Limpar arquivos temporários
rm -rf "$temp_dir"

echo -e "${BLUE}🏁 Comparação concluída!${NC}"