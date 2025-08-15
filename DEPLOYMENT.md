# CluedoONyourTerminal - Deployment Guide

## Quick Setup Commands

### 1. Test the Game Locally
```bash
# Navigate to project directory
cd /Users/shreeyagupta/game1

# Activate virtual environment
source venv/bin/activate

# Run system test
python test_game.py

# Start the game
python play_game.py
```

### 2. Create GitHub Repository

**Option A: Using GitHub Web Interface**
1. Go to https://github.com/new
2. Repository name: `CluedoONyourTerminal`
3. Make it public
4. Don't initialize with README (we already have one)
5. Click "Create repository"

**Option B: Using GitHub CLI (if installed)**
```bash
gh repo create Shreeya1-pixel/CluedoONyourTerminal --public --description "AI-powered murder mystery game for terminal"
```

### 3. Push to GitHub

**Using HTTPS:**
```bash
git remote add origin https://github.com/Shreeya1-pixel/CluedoONyourTerminal.git
git branch -M main
git push -u origin main
```

**Using SSH (if you have SSH keys set up):**
```bash
git remote add origin git@github.com:Shreeya1-pixel/CluedoONyourTerminal.git
git branch -M main
git push -u origin main
```

### 4. Verify Deployment
```bash
# Check remote is set correctly
git remote -v

# Check status
git status

# View commit history
git log --oneline
```

## Complete Terminal Session

Here's the complete sequence of commands to run:

```bash
# 1. Navigate to project
cd /Users/shreeyagupta/game1

# 2. Activate environment
source venv/bin/activate

# 3. Test the game
python test_game.py

# 4. Run setup script
./setup_git.sh

# 5. Add remote (after creating GitHub repo)
git remote add origin https://github.com/Shreeya1-pixel/CluedoONyourTerminal.git

# 6. Push to GitHub
git branch -M main
git push -u origin main
```

## Game Testing Commands

Once the game is running, test these commands:

```bash
# Start game
python play_game.py

# In-game commands to test:
interrogate 1
ask Where were you at 9 PM?
ask Did you know the victim?
switch 2
ask Where were you at 9 PM?
timeline
analysis
accuse 1
quit
```

## Troubleshooting

### If you get authentication errors:
```bash
# Configure Git with your GitHub credentials
git config --global user.name "Shreeya1-pixel"
git config --global user.email "your-email@example.com"
```

### If you need to force push (be careful):
```bash
git push -u origin main --force
```

### If you need to update the repository:
```bash
git add .
git commit -m "Update: [describe your changes]"
git push origin main
```

## Repository Structure

```
CluedoONyourTerminal/
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── play_game.py          # Main game interface
├── cli.py                # Demo script
├── test_game.py          # System test script
├── setup_git.sh          # Git setup helper
├── models.py             # Data models
├── case_generator.py     # Case generation
├── knowledge_base.py     # Truth store
├── lie_model.py          # AI deception system
├── nlp_pipeline.py       # Natural language processing
├── response_planner.py   # Response coordination
├── surface_realizer.py   # Text generation
├── game_engine.py        # Main game logic
├── .gitignore           # Git ignore rules
├── LICENSE              # MIT license
└── DEPLOYMENT.md        # This file
```

## Success Indicators

After successful deployment, you should see:
- ✅ Repository created on GitHub
- ✅ All files pushed successfully
- ✅ README displays properly on GitHub
- ✅ Game runs locally without errors
- ✅ System tests pass

## Next Steps

1. **Share the repository**: https://github.com/Shreeya1-pixel/CluedoONyourTerminal
2. **Add topics/tags** on GitHub: `terminal-game`, `murder-mystery`, `ai-game`, `python`
3. **Create releases** for stable versions
4. **Add issues** for feature requests and bugs
5. **Set up GitHub Pages** for a project website (optional)

Your CluedoONyourTerminal is now ready for the world! 🎭
