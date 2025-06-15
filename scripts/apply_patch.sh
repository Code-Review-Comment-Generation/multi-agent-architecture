#!/bin/bash

# Apply the patch file to the cloned repository to create a version reflecting the PR changes

# Exit on error
set -e

# Function to display usage
usage() {
    echo "Usage: $0 -r REPO_NAME -p PR_NUMBER"
    echo "Example: $0 -r taurus -p 1896"
    exit 1
}

# Parse command line arguments
while getopts "p:r:" opt; do
    case $opt in
        p) PR="$OPTARG" ;;
        r) REPO_NAME="$OPTARG" ;;
        *) usage ;;
    esac
done

# Check if required arguments are provided
if [ -z "$PR" ] || [ -z "$REPO_NAME" ]; then
    usage
fi

# Check if the repository directory exists
if [ ! -d "$REPO_NAME" ]; then
    echo "Error: Repository directory '$REPO_NAME' not found."
    echo "Please run repo_clone.sh first to clone the repository."
    exit 1
fi
echo $PWD
# Check if the patch file exists
PATCH_FILE="pr-$PR.patch"
if [ ! -f "$PATCH_FILE" ]; then
    echo "Error: Patch file '$PATCH_FILE' not found."
    echo "Please run repo_clone.sh first to generate the patch file."
    exit 1
fi

# Create a new directory for the patched version
PATCHED_REPO="${REPO_NAME}_patched"
echo "Creating patched version in $PATCHED_REPO..."

# Copy the original repository to the new directory
cp -r "$REPO_NAME" "$PATCHED_REPO"

# Go to the patched repository directory
cd "$PATCHED_REPO"

# Apply the patch
git apply --check "../$PATCH_FILE" || {
    echo "Warning: Patch may not apply cleanly. Attempting to apply anyway..."
}

# Apply the patch
git apply "../$PATCH_FILE" || {
    echo "Error: Failed to apply the patch."
    cd ..
    rm -rf "$PATCHED_REPO"
    exit 1
}

echo "Patch successfully applied to $PATCHED_REPO"
echo "The patched repository is available in the $PATCHED_REPO directory"