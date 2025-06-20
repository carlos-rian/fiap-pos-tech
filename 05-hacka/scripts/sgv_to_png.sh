#!/bin/bash
# filepath: c:\Users\CarlosRianQuartile\Documents\repo\my-repos\fiap-pos-tech\05-hacka\convert_svg_to_png.sh

# Function to check if required tools are available
check_dependencies() {
    if command -v inkscape >/dev/null 2>&1; then
        echo "Using Inkscape for conversion"
        CONVERTER="inkscape"
    elif command -v convert >/dev/null 2>&1; then
        echo "Using ImageMagick for conversion"
        CONVERTER="imagemagick"
    else
        echo "Error: Neither Inkscape nor ImageMagick found."
        echo "Please install one of them:"
        echo "  - Inkscape: https://inkscape.org/release/"
        echo "  - ImageMagick: https://imagemagick.org/script/download.php"
        exit 1
    fi
}

# Function to convert SVG to PNG
convert_svg_to_png() {
    local svg_file="$1"
    local output_dir="$2"
    local width="$3"
    local height="$4"
    
    # Get filename without extension
    local basename=$(basename "$svg_file" .svg)
    local relative_dir=$(dirname "${svg_file#$output_dir/}")
    
    # Create output directory structure
    local target_dir="$output_dir"
    if [[ "$relative_dir" != "." ]]; then
        target_dir="$output_dir/$relative_dir"
        mkdir -p "$target_dir"
    fi
    
    local png_file="$target_dir/${basename}.png"
    
    echo "Converting: $svg_file -> $png_file"
    
    if [[ "$CONVERTER" == "inkscape" ]]; then
        if [[ -n "$width" && -n "$height" ]]; then
            # Use high DPI for better quality when resizing
            inkscape --export-type=png --export-dpi=300 --export-width="$width" --export-height="$height" --export-filename="$png_file" "$svg_file"
        else
            # Use high DPI for original size conversion
            inkscape --export-type=png --export-dpi=300 --export-filename="$png_file" "$svg_file"
        fi
    else
        if [[ -n "$width" && -n "$height" ]]; then
            # Use high density and quality settings for ImageMagick
            convert -background transparent -density 300 "$svg_file" -quality 200 -resize "${width}x${height}" "$png_file"
        else
            # Use high density for original size
            convert -background transparent -density 300 "$svg_file" -quality 200 "$png_file"
        fi
    fi
    
    if [[ $? -eq 0 ]]; then
        echo "Success: Created $png_file"
    else
        echo "Error: Failed to convert $svg_file"
    fi
}

# Function to process all SVG files
process_svg_files() {
    local search_directory="$1"
    local output_directory="$2"
    local width="$3"
    local height="$4"
    
    echo "Searching for SVG files in: $search_directory"
    echo "Output directory: $output_directory"
    
    local count=0
    
    # Find all .svg files recursively
    find "$search_directory" -type f -name "*.svg" | while read -r svg_file; do
        convert_svg_to_png "$svg_file" "$output_directory" "$width" "$height"
        ((count++))
    done
    
    echo "Conversion completed!"
}

# Main script
echo "SVG to PNG Converter"
echo "This script converts all SVG files to PNG format recursively."
echo

# Check dependencies
check_dependencies

# Get arguments
search_directory="${1:-.}"
output_directory="${2:-./png_output}"
width="$3"
height="$4"

# Validate input directory
if [[ ! -d "$search_directory" ]]; then
    echo "Error: Directory '$search_directory' does not exist."
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$output_directory"

echo "Input directory: $search_directory"
echo "Output directory: $output_directory"

if [[ -n "$width" && -n "$height" ]]; then
    echo "Output size: ${width}x${height}"
else
    echo "Output size: Original size"
fi

echo

# Show usage if needed
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [input_directory] [output_directory] [width] [height]"
    echo ""
    echo "Parameters:"
    echo "  input_directory   - Directory to search for SVG files (default: current directory)"
    echo "  output_directory  - Directory to save PNG files (default: ./png_output)"
    echo "  width            - Output width in pixels (optional)"
    echo "  height           - Output height in pixels (optional)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Convert all SVGs in current directory"
    echo "  $0 ./images                  # Convert SVGs from ./images directory"
    echo "  $0 ./images ./output         # Convert to specific output directory"
    echo "  $0 ./images ./output 256 256 # Convert with specific dimensions"
    exit 0
fi

# Confirm before proceeding
read -p "Do you want to proceed? (y/N): " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
    process_svg_files "$search_directory" "$output_directory" "$width" "$height"
else
    echo "Operation cancelled."
fi