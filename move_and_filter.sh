#!/bin/bash

# Check if exactly two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 source_directory target_directory"
    exit 1
fi

# Assign arguments to variables
source_dir="$2"
target_dir="$1"

# Check if source directory exists
if [ ! -d "$source_dir" ]; then
    echo "Error: Source directory '$source_dir' does not exist"
    exit 1
fi

# Check if target directory exists, create it if it doesn't
if [ ! -d "$target_dir" ]; then
    mkdir -p "$target_dir"
fi



# Print information about the operation
echo "Operation Summary:"
echo "Source Directory: $source_dir"
echo "Target Directory: $target_dir"
echo "Actions to be performed:"
echo "- Remove all subdirectories in '$source_dir'"
echo "- Delete files that are not .mp4, .mkv, or .jpg in '$source_dir'"
echo "- Delete .mp4 files smaller than 100MB in '$source_dir'"
echo "- Move the source directory '$source_dir' to '$target_dir'"
echo

# Prompt user for confirmation
read -p "Do you want to proceed? Enter Y or 1 to confirm, any other character to cancel: " confirmation

# Check user input
if [ "$confirmation" != "Y" ] && [ "$confirmation" != "1" ]; then
    echo "Operation cancelled by user."
    exit 0
fi


# Remove all subdirectories in source directory
find "$source_dir" -type d -mindepth 1 -exec rm -rf {} \;

# Delete files that are not .mp4, .mkv, or .jpg
find "$source_dir" -type f ! -name "*.mp4" ! -name "*.mkv" ! -name "*.jpg" -exec rm -f {} \;

# Delete .mp4 files smaller than 100MB
find "$source_dir" -type f -name "*.mp4" -size -100M -exec rm -f {} \;

# Delete .mkv files smaller than 100MB
find "$source_dir" -type f -name "*.mkv" -size -100M -exec rm -f {} \;

# Move the source directory to the target directory
mv "$source_dir" "$target_dir"/

echo "Directory moved successfully from $source_dir to $target_dir"