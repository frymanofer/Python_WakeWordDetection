#!/bin/bash

# Define the pattern of files to delete
PATTERN="com.davoice.keyworddetection"

echo "Searching for example folders..."

# Find all example* directories
EXAMPLE_DIRS=$(find . -maxdepth 1 -type d -name "example*")

if [ -z "$EXAMPLE_DIRS" ]; then
    echo "No example directories found."
    exit 1
fi

for DIR in $EXAMPLE_DIRS; do
    TARGET_DIR="$DIR/ios/"
    
    if [ -d "$TARGET_DIR" ]; then
        echo "Processing $TARGET_DIR ..."

        # Remove files from Git index but keep them locally
        git rm -r --cached "$TARGET_DIR"*"$PATTERN"* 2>/dev/null

        # Remove them from disk
        rm -rf "$TARGET_DIR"*"$PATTERN"*

        # Add to .gitignore inside each example folder
        GITIGNORE="$DIR/.gitignore"
        echo -e "\n# Ignore app-generated data files\nios/*${PATTERN}*" >> "$GITIGNORE"

        echo "Cleaned $TARGET_DIR and updated .gitignore."
    else
        echo "Skipping $DIR (No iOS directory found)."
    fi
done

# Commit the cleanup
git add .
git commit -m "Removed generated build files and updated .gitignore for all example folders"
git push origin main  # Change 'main' to your branch if needed

echo "Done! The files are removed and ignored in all example folders."
