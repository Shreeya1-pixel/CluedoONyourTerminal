#!/bin/bash

# CluedoONyourTerminal Git Setup Script
# This script helps you set up the GitHub repository

echo "CluedoONyourTerminal - Git Setup"
echo "================================="
echo ""

# Check if we're in the right directory
if [ ! -f "play_game.py" ]; then
    echo "Error: Please run this script from the CluedoONyourTerminal directory"
    exit 1
fi

echo "Current directory: $(pwd)"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
fi

# Check if we have commits
if ! git rev-parse HEAD >/dev/null 2>&1; then
    echo "Making initial commit..."
    git add .
    git commit -m "Initial commit: CluedoONyourTerminal - AI-powered murder mystery game"
fi

echo ""
echo "Git repository is ready!"
echo ""
echo "Next steps:"
echo "1. Go to https://github.com/new"
echo "2. Create a new repository named 'CluedoONyourTerminal'"
echo "3. Make it public"
echo "4. Don't initialize with README (we already have one)"
echo "5. Copy the repository URL"
echo ""
echo "Then run these commands:"
echo "git remote add origin https://github.com/Shreeya1-pixel/CluedoONyourTerminal.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "Or if you prefer SSH:"
echo "git remote add origin git@github.com:Shreeya1-pixel/CluedoONyourTerminal.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""

# Check if remote is already set
if git remote get-url origin >/dev/null 2>&1; then
    echo "Remote origin is already set to: $(git remote get-url origin)"
    echo ""
    echo "To push to GitHub, run:"
    echo "git branch -M main"
    echo "git push -u origin main"
fi
