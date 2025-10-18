#!/bin/bash

# --- Configuration ---
NUM_STAGES=10
REPO_NAME=$(basename "$PWD") # Gets the current directory name

echo "🚀 Starting setup for $REPO_NAME with $NUM_STAGES stages..."

# --- Stage Directory Creation Loop ---
echo "--- Creating Stage Directories and READMEs ---"

# Loop from Stage-0 to Stage-10
for i in $(seq 0 $NUM_STAGES); do
    DIR_NAME="Stage-$i"
    FILE_PATH="$DIR_NAME/README.md"

    # 1. Create the directory
    if [ ! -d "$DIR_NAME" ]; then
        mkdir -p "$DIR_NAME"
        echo "   ✅ Created directory: $DIR_NAME"
    fi

    # 2. Create the Stage README.md
    if [ ! -f "$FILE_PATH" ]; then
        cat << EOF > "$FILE_PATH"
# HNG Internship - $DIR_NAME

## 🎯 Project Goal
The objective for this stage is to [**DESCRIBE THE PROJECT GOAL HERE**].

## 💻 Technologies Used
List technologies here (e.g., HTML, CSS, JavaScript, Python, etc.).

## 📝 Implementation Notes
Briefly describe key architectural decisions, challenges, and solutions here.
EOF
        echo "   📄 Created README in $DIR_NAME"
    fi
done

# --- Root README Update (Optional but Recommended) ---
echo "--- Updating Root README.md ---"
# Check if the root README exists, if not, create a basic one
if [ ! -f "README.md" ]; then
    echo "# $REPO_NAME" > README.md
fi

# Append a Table of Contents to the root README
cat << EOF >> README.md

## 🗺️ Internship Stages Overview

| Stage | Focus/Problem | Technologies | Link |
| :---: | :--- | :--- | :--- |
$(for i in $(seq 0 $NUM_STAGES); do echo "| **$i** | Placeholder: Update this description | Placeholder: Update this list | [Stage $i](Stage-$i) |"; done)
EOF

echo "   ✅ Updated root README with stage links."


# --- Git Actions ---
echo "--- Performing Git Actions ---"

# Add all changes (new directories, stage READMEs, and updated root README)
git add .
echo "   ✅ Staged all new files."

# Commit the new structure
git commit -m "STAGE 0: Initializing $NUM_STAGES-stage portfolio structure and README templates."
echo "   ✅ Created initial structure commit."

echo "--- Setup Complete! ---"
echo "You can now push your changes to GitHub with: git push origin main"