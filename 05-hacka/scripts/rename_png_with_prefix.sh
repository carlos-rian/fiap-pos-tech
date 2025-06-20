#!/bin/bash

# Function to rename PNG files with prefix
rename_png_with_prefix() {
    local search_directory="$1"
    local prefix="$2"
    local output_directory="$3"
    
    echo "Searching for PNG files in: $search_directory"
    echo "Adding prefix: $prefix"
    if [[ -n "$output_directory" ]]; then
        echo "Output directory: $output_directory"
        mkdir -p "$output_directory"
    else
        echo "Mode: Rename in place"
    fi
    
    local count=0
    
    # Find all .png files recursively
    find "$search_directory" -type f -name "*.png" | while read -r filepath; do
        # Get directory and filename
        directory=$(dirname "$filepath")
        filename=$(basename "$filepath")
        
        # Remove extension to work with base name
        basename_no_ext="${filename%.*}"
        extension="${filename##*.}"
        
        # Convert to lowercase and replace hyphens with underscores
        clean_basename=$(echo "$basename_no_ext" | tr '[:upper:]' '[:lower:]' | tr '-' '_')
        
        # Remove leading hyphens or underscores from the beginning only
        while [[ "$clean_basename" =~ ^[_-] ]]; do
            clean_basename="${clean_basename:1}"
        done
        
        # Only add prefix if it doesn't already start with it
        if [[ "$clean_basename" =~ ^${prefix}.* ]]; then
            new_filename="${clean_basename}.${extension,,}"
            echo "Already has prefix: $filename"
        else
            new_filename="${prefix}${clean_basename}.${extension,,}"
        fi
        
        # Set target path based on output directory
        if [[ -n "$output_directory" ]]; then
            new_filepath="$output_directory/$new_filename"
        else
            new_filepath="$directory/$new_filename"
        fi
        
        # Only process if the name actually changed or copying to output dir
        if [[ "$filename" != "$new_filename" ]] || [[ -n "$output_directory" ]]; then
            if [[ -n "$output_directory" ]]; then
                echo "Copying: $filepath -> $new_filepath"
            else
                echo "Renaming: $filename -> $new_filename"
            fi
            
            # Check if target file already exists
            if [[ -e "$new_filepath" ]]; then
                echo "Warning: Target file already exists: $new_filepath"
                echo "Skipping: $filepath"
            else
                if [[ -n "$output_directory" ]]; then
                    cp "$filepath" "$new_filepath"
                else
                    mv "$filepath" "$new_filepath"
                fi
                echo "Success: $(if [[ -n "$output_directory" ]]; then echo "Copied"; else echo "Renamed"; fi) to $new_filename"
                ((count++))
            fi
        else
            echo "No change needed: $filename"
        fi
    done
    
    echo "Processing completed! Total files processed: $count"
}

# Main script
echo "PNG File Renamer with Prefix"
echo "This script renames PNG files by adding a prefix, converting to lowercase,"
echo "and replacing hyphens with underscores."
echo

# Get arguments
search_directory="${1:-.}"
prefix="${2}"
output_directory="${3}"

# Validate arguments
if [[ -z "$prefix" ]]; then
    echo "Usage: $0 [directory] <prefix> [output_directory]"
    echo ""
    echo "Parameters:"
    echo "  directory        - Directory to search for PNG files (default: current directory)"
    echo "  prefix          - Prefix to add to filenames (required)"
    echo "  output_directory - Copy files to this directory instead of renaming in place (optional)"
    echo ""
    echo "Examples:"
    echo "  $0 . aws_                    # Add 'aws_' prefix, rename in place"
    echo "  $0 ./images icon_            # Add 'icon_' prefix, rename in place"
    echo "  $0 ./images aws_ ./output    # Add 'aws_' prefix, copy to ./output"
    exit 1
fi

if [[ ! -d "$search_directory" ]]; then
    echo "Error: Directory '$search_directory' does not exist."
    exit 1
fi

echo "Target directory: $search_directory"
echo "Prefix to add: $prefix"
if [[ -n "$output_directory" ]]; then
    echo "Output directory: $output_directory"
else
    echo "Mode: Rename files in place"
fi
echo

# Confirm before proceeding
read -p "Do you want to proceed? (y/N): " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
    rename_png_with_prefix "$search_directory" "$prefix" "$output_directory"
else
    echo "Operation cancelled."
fi
