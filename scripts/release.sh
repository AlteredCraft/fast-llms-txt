#!/bin/bash
set -e

# Usage: ./scripts/release.sh 0.2.0

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "Usage: ./scripts/release.sh <version>"
    echo "Example: ./scripts/release.sh 0.2.0"
    exit 1
fi

# Validate version format
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version must be in format X.Y.Z (e.g., 0.2.0)"
    exit 1
fi

echo "Releasing version $VERSION..."

# Update pyproject.toml
sed -i '' "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml

# Update __init__.py
sed -i '' "s/^__version__ = \".*\"/__version__ = \"$VERSION\"/" fast_llms_txt/__init__.py

# Show changes
echo ""
echo "Updated files:"
git diff --stat
echo ""
git diff

# Confirm
read -p "Commit and tag v$VERSION? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add pyproject.toml fast_llms_txt/__init__.py
    git commit -m "Bump version to $VERSION"
    git tag "v$VERSION"

    echo ""
    echo "Created commit and tag v$VERSION"
    echo ""
    read -p "Push to origin? (y/n) " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push && git push --tags
        echo "Pushed! GitHub Actions will publish to PyPI."
    else
        echo "Run 'git push && git push --tags' when ready."
    fi
else
    echo "Aborted. Reverting changes..."
    git checkout pyproject.toml fast_llms_txt/__init__.py
fi
