#!/bin/bash

# Script universal para otimizar imagens PNG usando ImageMagick
# Funciona no macOS e Ubuntu
# Instalação:
# macOS: brew install imagemagick
# Ubuntu: sudo apt-get install imagemagick

# Configurações padrão
PASTA_ORIGEM=${1:-"./images"}
PASTA_DESTINO=${2:-"./optimized"}
QUALIDADE=${3:-"medium"}
TAMANHO=${4:-""}
THREADS=${5:-$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "6")}

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para mostrar uso
show_usage() {
    echo "Uso: $0 [pasta_origem] [pasta_destino] [qualidade] [tamanho] [threads]"
    echo ""
    echo "Parâmetros:"
    echo "  pasta_origem   - Pasta com imagens PNG (padrão: ./images)"
    echo "  pasta_destino  - Pasta de saída (padrão: ./optimized)"
    echo "  qualidade      - high, medium, low (padrão: medium)"
    echo "  tamanho        - Redimensionar ex: 224x224 (opcional)"
    echo "  threads        - Número de threads paralelas (padrão: CPU cores)"
    echo ""
    echo "Exemplos:"
    echo "  $0 dataset/ output/ medium 224x224 8"
    echo "  $0 images/ compressed/ low \"\" 4"
    echo "  $0 /path/to/images /path/to/output high"
}

# Verificar se ImageMagick está instalado
check_imagemagick() {
    if ! command -v convert &> /dev/null && ! command -v magick &> /dev/null; then
        echo -e "${RED}❌ ImageMagick não encontrado!${NC}"
        echo ""
        echo "Instalação:"
        echo "  macOS:   brew install imagemagick"
        echo "  Ubuntu:  sudo apt-get install imagemagick"
        echo "  Arch:    sudo pacman -S imagemagick"
        exit 1
    fi
    
    # Usar 'magick' se disponível, senão 'convert'
    if command -v magick &> /dev/null; then
        MAGICK_CMD="magick"
        echo -e "${GREEN}✅ ImageMagick detectado: $(magick -version | head -1)${NC}"
    else
        MAGICK_CMD="convert"
        echo -e "${GREEN}✅ ImageMagick detectado: $(convert -version | head -1)${NC}"
    fi
    
    # Verificar se GNU parallel está disponível
    if command -v parallel &> /dev/null; then
        PARALLEL_AVAILABLE=true
        echo -e "${GREEN}✅ GNU parallel detectado - processamento paralelo habilitado${NC}"
        
        # Testar se parallel funciona
        if echo "test" | parallel -j1 echo 2>/dev/null; then
            echo -e "${GREEN}✅ GNU parallel testado e funcionando${NC}"
        else
            echo -e "${YELLOW}⚠️  GNU parallel encontrado mas não funciona corretamente${NC}"
            PARALLEL_AVAILABLE=false
        fi
    else
        PARALLEL_AVAILABLE=false
        echo -e "${YELLOW}⚠️  GNU parallel não encontrado - usando método nativo${NC}"
        echo -e "${BLUE}💡 Para acelerar: brew install parallel (macOS) ou sudo apt-get install parallel (Ubuntu)${NC}"
    fi
}

# Configurar parâmetros de qualidade
setup_quality_params() {
    case $QUALIDADE in
        "high")
            COMPRESS_LEVEL=1
            COLORS=256
            STRIP_META=false
            echo -e "${BLUE}🎯 Modo: Alta qualidade${NC}"
            ;;
        "medium")
            COMPRESS_LEVEL=5
            COLORS=128
            STRIP_META=true
            echo -e "${YELLOW}🎯 Modo: Média qualidade${NC}"
            ;;
        "low")
            COMPRESS_LEVEL=9
            COLORS=64
            STRIP_META=true
            echo -e "${RED}🎯 Modo: Baixa qualidade (máxima compressão)${NC}"
            ;;
        *)
            echo -e "${RED}❌ Qualidade inválida: $QUALIDADE${NC}"
            echo "Use: high, medium, ou low"
            exit 1
            ;;
    esac
}

# Otimizar uma única imagem
optimize_image() {
    local input_file="$1"
    local output_file="$2"
    
    # Construir comando ImageMagick
    local cmd="$MAGICK_CMD \"$input_file\""
    
    # Redimensionar se especificado
    if [ ! -z "$TAMANHO" ]; then
        cmd="$cmd -resize $TAMANHO"
    fi
    
    # Aplicar otimizações baseadas na qualidade
    if [ "$STRIP_META" = true ]; then
        cmd="$cmd -strip"  # Remove metadados
    fi
    
    # Reduzir cores se necessário
    if [ $COLORS -lt 256 ]; then
        cmd="$cmd -colors $COLORS"
    fi
    
    # Configurar compressão PNG
    cmd="$cmd -define png:compression-level=$COMPRESS_LEVEL"
    cmd="$cmd -define png:compression-strategy=2"
    cmd="$cmd -define png:compression-filter=0"
    
    # Otimizações específicas para ML/PyTorch
    cmd="$cmd -colorspace sRGB"  # Garantir espaço de cor consistente
    cmd="$cmd -background white -alpha remove"  # Remover transparência
    
    # Arquivo de saída
    cmd="$cmd \"$output_file\""
    
    # Executar comando
    eval $cmd 2>/dev/null
}

# Contador global de imagens processadas
PROCESSED_COUNT=0
FAILED_COUNT=0

# Função para processar uma imagem (usada no processamento paralelo)
process_single_image() {
    local input_file="$1"
    local pasta_origem="$2"
    local pasta_destino="$3"
    
    # Calcular caminho relativo e arquivo de saída
    local relative_path="${input_file#$pasta_origem/}"
    local output_file="$pasta_destino/$relative_path"
    local output_dir=$(dirname "$output_file")
    
    # Criar diretório de saída se necessário
    mkdir -p "$output_dir"
    
    # Obter tamanho original
    local original_size=$(stat -f%z "$input_file" 2>/dev/null || stat -c%s "$input_file" 2>/dev/null)
    
    # Otimizar imagem
    if optimize_image "$input_file" "$output_file"; then
        local optimized_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
        
        # Calcular redução
        local reduction=$(( (original_size - optimized_size) * 100 / original_size ))
        
        # Copiar arquivo XML correspondente se existir
        local xml_file="${input_file%.*}.xml"
        local output_xml="${output_file%.*}.xml"
        
        if [ -f "$xml_file" ]; then
            cp "$xml_file" "$output_xml"
            echo "✅ $(basename "$input_file"): $(echo "$original_size" | awk '{print int($1/1024)}')KB → $(echo "$optimized_size" | awk '{print int($1/1024)}')KB ($reduction%) + XML"
        else
            echo "✅ $(basename "$input_file"): $(echo "$original_size" | awk '{print int($1/1024)}')KB → $(echo "$optimized_size" | awk '{print int($1/1024)}')KB ($reduction%)"
        fi
        
        # Incrementar contador (thread-safe usando lock de arquivo)
        echo "success" >> "${pasta_destino}/.counter"
    else
        echo "❌ Falha: $(basename "$input_file")"
        echo "failed" >> "${pasta_destino}/.counter"
        # Salvar arquivo que falhou para reprocessamento
        echo "$input_file" >> "${pasta_destino}/failed_files.txt"
    fi
}

# Função principal de otimização
optimize_dataset() {
    echo -e "${BLUE}📁 Processando pasta: $PASTA_ORIGEM${NC}"
    echo -e "${BLUE}📁 Saída: $PASTA_DESTINO${NC}"
    echo -e "${YELLOW}🔧 Threads: $THREADS${NC}"
    
    # Criar pasta de destino
    mkdir -p "$PASTA_DESTINO"
    
    # Encontrar todas as imagens PNG
    local png_files=($(find "$PASTA_ORIGEM" -type f -iname "*.png"))
    
    if [ ${#png_files[@]} -eq 0 ]; then
        echo -e "${RED}❌ Nenhum arquivo PNG encontrado em $PASTA_ORIGEM${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}🖼️  Encontradas ${#png_files[@]} imagens PNG${NC}"
    
    # Limpar arquivos temporários anteriores
    rm -f "${PASTA_DESTINO}/.counter" "${PASTA_DESTINO}/failed_files.txt"
    
    # Exportar funções e variáveis para subprocessos
    export -f optimize_image process_single_image
    export MAGICK_CMD TAMANHO COMPRESS_LEVEL COLORS STRIP_META
    
    echo -e "${BLUE}🔧 Verificando método de paralelização...${NC}"
    echo -e "${BLUE}📊 PARALLEL_AVAILABLE: $PARALLEL_AVAILABLE${NC}"
    
    if [ "$PARALLEL_AVAILABLE" = true ]; then
        echo -e "${GREEN}🚀 Usando GNU parallel com $THREADS threads${NC}"
        echo -e "${BLUE}📡 Iniciando processamento paralelo...${NC}"
        
        # Usar GNU parallel para processamento paralelo
        printf '%s\n' "${png_files[@]}" | \
        parallel -j"$THREADS" --bar --eta process_single_image {} "$PASTA_ORIGEM" "$PASTA_DESTINO"
        
    else
        echo -e "${YELLOW}⚙️  Processamento paralelo nativo com $THREADS threads${NC}"
        
        # Processar imagens em paralelo usando xargs
        printf '%s\n' "${png_files[@]}" | \
        xargs -n 1 -P "$THREADS" -I {} bash -c '
            source_path="$1"
            input_dir="$2" 
            output_dir="$3"
            
            # Recriar função localmente
            optimize_single() {
                local input_file="$1"
                local pasta_origem="$2"
                local pasta_destino="$3"
                
                # Calcular caminho relativo e arquivo de saída
                local relative_path="${input_file#$pasta_origem/}"
                local output_file="$pasta_destino/$relative_path"
                local output_dir=$(dirname "$output_file")
                
                # Criar diretório de saída se necessário
                mkdir -p "$output_dir"
                
                # Obter tamanho original
                local original_size=$(stat -f%z "$input_file" 2>/dev/null || stat -c%s "$input_file" 2>/dev/null)
                
                # Construir comando ImageMagick
                local cmd="'"$MAGICK_CMD"' \"$input_file\""
                
                # Redimensionar se especificado
                if [ ! -z "'"$TAMANHO"'" ]; then
                    cmd="$cmd -resize '"$TAMANHO"'"
                fi
                
                # Aplicar otimizações baseadas na qualidade
                if [ "'"$STRIP_META"'" = true ]; then
                    cmd="$cmd -strip"
                fi
                
                # Reduzir cores se necessário
                if [ '"$COLORS"' -lt 256 ]; then
                    cmd="$cmd -colors '"$COLORS"'"
                fi
                
                # Configurar compressão PNG
                cmd="$cmd -define png:compression-level='"$COMPRESS_LEVEL"'"
                cmd="$cmd -define png:compression-strategy=2"
                cmd="$cmd -define png:compression-filter=0"
                cmd="$cmd -colorspace sRGB"
                cmd="$cmd -background white -alpha remove"
                cmd="$cmd \"$output_file\""
                
                # Executar comando
                if eval $cmd 2>/dev/null; then
                    local optimized_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null)
                    local reduction=$(( (original_size - optimized_size) * 100 / original_size ))
                    
                    # Copiar arquivo XML correspondente se existir
                    local xml_file="${input_file%.*}.xml"
                    local output_xml="${output_file%.*}.xml"
                    
                    if [ -f "$xml_file" ]; then
                        cp "$xml_file" "$output_xml"
                        echo "✅ $(basename "$input_file"): $(echo "$original_size" | awk "{print int(\$1/1024)}")KB → $(echo "$optimized_size" | awk "{print int(\$1/1024)}")KB ($reduction%) + XML"
                    else
                        echo "✅ $(basename "$input_file"): $(echo "$original_size" | awk "{print int(\$1/1024)}")KB → $(echo "$optimized_size" | awk "{print int(\$1/1024)}")KB ($reduction%)"
                    fi
                    
                    echo "success" >> "${pasta_destino}/.counter"
                else
                    echo "❌ Falha: $(basename "$input_file")"
                    echo "failed" >> "${pasta_destino}/.counter"
                    echo "$input_file" >> "${pasta_destino}/failed_files.txt"
                fi
            }
            
            optimize_single "$1" "$2" "$3"
        ' _ {} "$PASTA_ORIGEM" "$PASTA_DESTINO"
        
        echo -e "${GREEN}⏳ Processamento paralelo nativo concluído${NC}"
    fi
    
    # Calcular estatísticas finais
    calculate_final_stats "$PASTA_DESTINO"
}

# Calcular estatísticas finais
calculate_final_stats() {
    local pasta_destino="$1"
    local processed=0
    local failed=0
    
    echo ""
    echo -e "${BLUE}📊 Calculando estatísticas finais...${NC}"
    
    # Contar sucessos e falhas do arquivo .counter
    if [ -f "${pasta_destino}/.counter" ]; then
        processed=$(grep -c "success" "${pasta_destino}/.counter" 2>/dev/null || echo "0")
        failed=$(grep -c "failed" "${pasta_destino}/.counter" 2>/dev/null || echo "0")
        
        # Remover arquivo temporário
        rm -f "${pasta_destino}/.counter"
    fi
    
    # Relatório final
    echo ""
    echo -e "${BLUE}📊 Relatório Final:${NC}"
    echo -e "${GREEN}✅ Processadas: $processed${NC}"
    echo -e "${RED}❌ Falharam: $failed${NC}"
    echo -e "${BLUE}📦 Total de imagens: $((processed + failed))${NC}"
    
    # Mostrar informação sobre arquivos que falharam
    if [ $failed -gt 0 ] && [ -f "${pasta_destino}/failed_files.txt" ]; then
        echo -e "${RED}📄 Arquivos que falharam salvos em: ${pasta_destino}/failed_files.txt${NC}"
        echo -e "${YELLOW}💡 Use este arquivo para reprocessar apenas as imagens que falharam${NC}"
    fi
    
    if [ ! -z "$TAMANHO" ]; then
        echo -e "${YELLOW}📐 Redimensionadas para: $TAMANHO${NC}"
    fi
}

# Função principal
main() {
    echo -e "${BLUE}🚀 Otimizador de PNG Universal (macOS/Ubuntu)${NC}"
    echo ""
    
    # Mostrar ajuda se solicitado
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        show_usage
        exit 0
    fi
    
    # Verificar ImageMagick
    check_imagemagick
    
    # Verificar se pasta origem existe
    if [ ! -d "$PASTA_ORIGEM" ]; then
        echo -e "${RED}❌ Pasta não encontrada: $PASTA_ORIGEM${NC}"
        show_usage
        exit 1
    fi
    
    # Configurar parâmetros
    setup_quality_params
    
    if [ ! -z "$TAMANHO" ]; then
        echo -e "${YELLOW}📐 Redimensionar para: $TAMANHO${NC}"
    fi
    
    echo ""
    
    # Executar otimização
    optimize_dataset
    
    echo ""
    echo -e "${GREEN}🎉 Otimização concluída!${NC}"
    echo -e "${BLUE}💡 Dica: Use as imagens otimizadas no PyTorch com DataLoader para melhor performance${NC}"
}

# Executar script
main "$@"