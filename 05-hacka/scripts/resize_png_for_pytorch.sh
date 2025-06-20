#!/bin/bash

# Function to check dependencies
check_dependencies() {
    if command -v convert >/dev/null 2>&1; then
        echo "ImageMagick found!"
        return 0
    else
        echo "Error: ImageMagick not found."
        echo "To install on Ubuntu:"
        echo "  sudo apt update"
        echo "  sudo apt install imagemagick"
        exit 1
    fi
}

# Function to resize PNG for PyTorch with quality preservation
resize_png_for_pytorch() {
    local png_file="$1"
    local output_dir="$2"
    local target_size="$3"
    local quality_mode="$4"
    
    local basename=$(basename "$png_file" .png)
    local output_file="$output_dir/${basename}.png"
    
    echo "Resizing: $png_file -> $output_file"
    
    if [[ "$quality_mode" == "upscale" ]]; then
        # Best for upscaling small PNGs - use Mitchell filter for better results
        convert "$png_file" \
                -filter Mitchell \
                -resize "${target_size}x${target_size}!" \
                -unsharp 0x0.75+0.75+0.008 \
                -quality 100 \
                "$output_file"
    elif [[ "$quality_mode" == "crop" ]]; then
        # Center crop to exact square
        convert "$png_file" \
                -filter Lanczos \
                -resize "${target_size}x${target_size}^" \
                -gravity center \
                -crop "${target_size}x${target_size}+0+0" \
                -quality 100 \
                "$output_file"
    elif [[ "$quality_mode" == "high" ]]; then
        # Maintain aspect ratio with transparent padding
        convert "$png_file" \
                -filter Lanczos \
                -resize "${target_size}x${target_size}>" \
                -background transparent \
                -gravity center \
                -extent "${target_size}x${target_size}" \
                -quality 100 \
                "$output_file"
    else
        # Force resize (may distort aspect ratio)
        convert "$png_file" \
                -filter Lanczos \
                -resize "${target_size}x${target_size}!" \
                -quality 100 \
                "$output_file"
    fi
    
    if [[ $? -eq 0 ]]; then
        echo "Success: Created $output_file"
    else
        echo "Error: Failed to resize $png_file"
    fi
}

# Function to process all PNG files
process_png_files() {
    local search_directory="$1"
    local output_directory="$2"
    local target_size="$3"
    local quality_mode="$4"
    
    echo "Processing PNG files from: $search_directory"
    echo "Output directory: $output_directory"
    echo "Target size: ${target_size}x${target_size}"
    echo "Quality mode: $quality_mode"
    echo
    
    local count=0
    
    find "$search_directory" -type f -name "*.png" | while read -r png_file; do
        resize_png_for_pytorch "$png_file" "$output_directory" "$target_size" "$quality_mode"
        ((count++))
    done
    
    echo "Processing completed!"
    echo "Total files processed: $(find "$search_directory" -type f -name "*.png" | wc -l)"
}

# Main script
echo "PNG Resizer for PyTorch Training"
echo "Resizes PNG files to optimal dimensions for ML training while preserving quality."
echo

# Check dependencies
check_dependencies

# Get arguments
search_directory="${1:-.}"
output_directory="${2:-./pytorch_resized}"
target_size="${3:-224}"
quality_mode="${4:-upscale}"

# Validate arguments
if [[ ! -d "$search_directory" ]]; then
    echo "Error: Directory '$search_directory' does not exist."
    exit 1
fi

# Create output directory
mkdir -p "$output_directory"

# Show usage if needed
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [input_directory] [output_directory] [size] [mode]"
    echo ""
    echo "Parameters:"
    echo "  input_directory   - Directory with PNG files (default: current directory)"
    echo "  output_directory  - Output directory (default: ./pytorch_resized)"
    echo "  size             - Target size in pixels (default: 224)"
    echo "  mode             - Quality mode: 'upscale', 'high', 'crop', or 'force' (default: upscale)"
    echo ""
    echo "Common PyTorch sizes:"
    echo "  224 - Standard for most CNN models (ResNet, VGG, etc.)"
    echo "  256 - Good balance of quality and performance"
    echo "  512 - High resolution for detailed models"
    echo ""
    echo "Quality modes:"
    echo "  upscale  - Best for enlarging small PNGs (recommended)"
    echo "  high     - Preserve aspect ratio with padding"
    echo "  crop     - Center crop to exact square"
    echo "  force    - Force resize (may distort)"
    echo ""
    echo "Examples:"
    echo "  $0                              # Resize to 224x224 with upscale quality"
    echo "  $0 ./images ./output 256        # Resize to 256x256 with upscale"
    echo "  $0 ./images ./output 512 crop   # Resize to 512x512 with center crop"
    exit 0
fi

echo "Input directory: $search_directory"
echo "Output directory: $output_directory"
echo "Target size: ${target_size}x${target_size}"
echo "Quality mode: $quality_mode"
echo

# Confirm before proceeding
read -p "Do you want to proceed? (y/N): " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
    process_png_files "$search_directory" "$output_directory" "$target_size" "$quality_mode"
else
    echo "Operation cancelled."
fi
    echo "Error: Directory '$search_directory' does not exist."
    exit 1
fi

# Create output directory
mkdir -p "$output_directory"

# Show usage if needed
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [input_directory] [output_directory] [size] [mode]"
    echo ""
    echo "Parameters:"
    echo "  input_directory   - Directory with PNG files (default: current directory)"
    echo "  output_directory  - Output directory (default: ./pytorch_resized)"
    echo "  size             - Target size in pixels (default: 224)"
    echo "  mode             - Quality mode: 'high', 'crop', or 'standard' (default: high)"
    echo ""
    echo "Common PyTorch sizes:"
    echo "  224 - Standard for most CNN models (ResNet, VGG, etc.)"
    echo "  256 - Good balance of quality and performance"
    echo "  512 - High resolution for detailed models"
    echo ""
    echo "Quality modes:"
    echo "  high     - Preserve aspect ratio with padding (recommended)"
    echo "  crop     - Center crop to exact square"
    echo "  standard - Simple resize"
    echo ""
    echo "Examples:"
    echo "  $0                              # Resize to 224x224 with high quality"
    echo "  $0 ./images ./output 256        # Resize to 256x256"
    echo "  $0 ./images ./output 512 crop   # Resize to 512x512 with center crop"
    exit 0
fi

echo "Input directory: $search_directory"
echo "Output directory: $output_directory"
echo "Target size: ${target_size}x${target_size}"
echo "Quality mode: $quality_mode"
echo

# Confirm before proceeding
read -p "Do you want to proceed? (y/N): " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
    process_png_files "$search_directory" "$output_directory" "$target_size" "$quality_mode"
else
    echo "Operation cancelled."
fi
