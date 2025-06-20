#!/bin/bash
# filepath: c:\Users\CarlosRianQuartile\Documents\repo\my-repos\fiap-pos-tech\05-hacka\rename_png_files.sh

# Function to process and rename files
rename_png_files() {
    local search_directory="${1:-.}"
    
    echo "Searching for PNG files in: $search_directory"
    
    # Find all .png files recursively
    find "$search_directory" -type f -name "*.png" | while read -r filepath; do
        # Get directory and filename
        directory=$(dirname "$filepath")
        filename=$(basename "$filepath")
        
        # Remove extension to work with base name
        basename_no_ext="${filename%.*}"
        extension="${filename##*.}"
        
        # Check if filename starts with any of the prefixes and remove them
        new_basename="$basename_no_ext"
        
        if [[ "$basename_no_ext" =~ ^Arch_.* ]]; then
            new_basename="${basename_no_ext#Arch_}"
        elif [[ "$basename_no_ext" =~ ^Res_.* ]]; then
            new_basename="${basename_no_ext#Res_}"
        elif [[ "$basename_no_ext" =~ ^Amazon.* ]]; then
            new_basename="${basename_no_ext#Amazon}"
        fi
        
        # Convert to lowercase
        new_basename=$(echo "$new_basename" | tr '[:upper:]' '[:lower:]')
        new_filename="${new_basename}.${extension,,}"
        
        # Only rename if the name actually changed
        if [[ "$filename" != "$new_filename" ]]; then
            new_filepath="$directory/$new_filename"
            
            echo "Renaming: $filename -> $new_filename"
            
            # Check if target file already exists
            if [[ -e "$new_filepath" ]]; then
                echo "Warning: Target file already exists: $new_filepath"
                echo "Skipping: $filepath"
            else
                mv "$filepath" "$new_filepath"
                echo "Success: Renamed to $new_filepath"
            fi
        else
            echo "No change needed: $filename"
        fi
    done
}

# Main script
echo "PNG File Renamer"
echo "This script will rename PNG files by removing 'Arch_', 'Res_', or 'Amazon' prefixes"
echo "and converting filenames to lowercase."
echo

# Get target directory from argument or use current directory
target_directory="${1:-.}"

if [[ ! -d "$target_directory" ]]; then
    echo "Error: Directory '$target_directory' does not exist."
    exit 1
fi

echo "Target directory: $target_directory"
echo

# Confirm before proceeding
read -p "Do you want to proceed? (y/N): " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
    rename_png_files "$target_directory"
    echo
    echo "Operation completed!"
else
    echo "Operation cancelled."
fi