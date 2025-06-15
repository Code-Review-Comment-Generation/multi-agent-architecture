#!/bin/bash

# Clone the repository, Go to PR's base commit, and create a patch file with all PR changes

# Exit on error
set -e

# Function to display usage
usage() {
    echo "Usage: $0 -r REPO_URL -p PR_NUMBER"
    echo "Example: $0 -r https://github.com/Blazemeter/taurus.git -p 1896"
    exit 1
}

# Parse command line arguments
while getopts "p:r:" opt; do
    case $opt in
        p) PR="$OPTARG" ;;
        r) REPO_LINK="$OPTARG" ;;
        *) usage ;;
    esac
done

# Check if required arguments are provided
if [ -z "$PR" ] || [ -z "$REPO_LINK" ]; then
    usage
fi

# Extract repo name from URL
REPO_NAME=$(basename "$REPO_LINK" .git)
echo "Processing PR #$PR from $REPO_LINK"

# Create a clean directory for the repo
rm -rf "$REPO_NAME"
git clone "$REPO_LINK"
cd "$REPO_NAME"

# Fetch the PR and origin
git fetch origin "pull/$PR/head:pr-$PR"
git fetch origin

# Get the base branch commit (the commit the PR was branched from)
BASE_COMMIT=$(git merge-base origin/main "pr-$PR")

# Checkout the base commit
git checkout "$BASE_COMMIT"

# Print the base commit hash
echo "Base commit hash (commit the PR was started from):"
git rev-parse HEAD

# Create a patch file with all PR changes
echo "Generating patch file..."
git diff "$BASE_COMMIT" "pr-$PR" > "../pr-$PR.patch"

echo "Patch file has been saved as pr-$PR.patch in the parent directory"

