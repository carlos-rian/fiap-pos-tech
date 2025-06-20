#!/bin/bash

# Function to check and install Inkscape on Ubuntu
check_and_install_inkscape() {
    if command -v inkscape >/dev/null 2>&1; then
        echo "Inkscape found!"
        return 0
    else
        echo "Inkscape not found. Installing..."
        echo "To install Inkscape on Ubuntu, run:"
        echo "  sudo apt update"
        echo "  sudo apt install inkscape"
        echo ""
        read -p "Do you want to install Inkscape now? (y/N): " install_confirm
        if [[ $install_confirm =~ ^[Yy]$ ]]; then
            sudo apt update && sudo apt install -y inkscape
            if [[ $? -eq 0 ]]; then
                echo "Inkscape installed successfully!"
                return 0
            else
                echo "Failed to install Inkscape"
                return 1
            fi
        else
            echo "Please install Inkscape manually and run this script again."
            return 1
        fi
    fi
}

# Function to convert SVG to high-quality PNG for PyTorch training
convert_svg_for_pytorch() {
    local svg_file="$1"
    local output_dir="$2"
    local size="$3"
    
    local basename=$(basename "$svg_file" .svg)
    local png_file="$output_dir/${basename}.png"
    
    echo "Converting for PyTorch: $svg_file -> $png_file"
    
    inkscape --export-type=png \
             --export-dpi=300 \
             --export-width="$size" \
             --export-height="$size" \
             --export-background-opacity=0 \
             --export-filename="$png_file" \
             "$svg_file"
}

# Main conversion for ML training
echo "SVG to PyTorch Data Converter"
echo "Converts SVG files to high-quality square PNGs suitable for ML training"
echo ""

# Check/install Inkscape
if ! check_and_install_inkscape; then
    exit 1
fi

search_directory="${1:-.}"
output_directory="${2:-./pytorch_data}"
image_size="${3:-512}"  # Default 512x512 for high quality

mkdir -p "$output_directory"

echo "Converting SVGs to ${image_size}x${image_size} PNGs for PyTorch..."

find "$search_directory" -type f -name "*.svg" | while read -r svg_file; do
    convert_svg_for_pytorch "$svg_file" "$output_directory" "$image_size"
done

echo "Conversion completed! Files ready for PyTorch training."
echo "Total files processed: $(find "$search_directory" -type f -name "*.svg" | wc -l)"
        output_subdir="$output_directory/$relative_path"
        mkdir -p "$output_subdir"
        convert_svg_for_pytorch "$svg_file" "$output_subdir" "$image_size"
    else
        convert_svg_for_pytorch "$svg_file" "$output_directory" "$image_size"
    fi
done

echo "Conversion completed! Files ready for PyTorch training."
echo "Total files processed: $(find "$search_directory" -type f -name "*.svg" | wc -l)"
