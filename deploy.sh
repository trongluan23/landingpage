#!/bin/bash
# Quick deployment script for Render.com

echo "🚀 PageForge Deployment Script"
echo "================================"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git..."
    git init
    git branch -M main
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env and add your OPENAI_API_KEY"
    echo ""
fi

# Git add and commit
echo "📝 Committing changes..."
git add .
git commit -m "Deploy: $(date +'%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"

# Check if remote exists
if ! git remote | grep -q origin; then
    echo ""
    echo "🔗 Git remote not configured"
    echo "Please run:"
    echo "  git remote add origin https://github.com/yourusername/pageforge.git"
    echo "  git push -u origin main"
    echo ""
    echo "Then deploy on Render.com:"
    echo "  1. Go to https://dashboard.render.com"
    echo "  2. New + → Web Service"
    echo "  3. Connect your GitHub repo"
    echo "  4. Render will auto-detect configuration"
    echo ""
else
    echo "⬆️  Pushing to GitHub..."
    git push origin main
    echo ""
    echo "✅ Code pushed to GitHub!"
    echo "🎯 Render.com will auto-deploy if configured"
fi

echo ""
echo "📚 For detailed deployment instructions, see:"
echo "   DEPLOYMENT.md"
