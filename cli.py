#!/usr/bin/env python3
"""
Simple CLI for the AI-driven murder mystery game.
"""

import sys
from models import Difficulty
from game_engine import GameEngine

def main():
    """Main CLI function."""
    print("🔍 AI-Driven Murder Mystery Game")
    print("=" * 40)
    
    game_engine = GameEngine()
    
    # Start a new game
    print("\nStarting new game...")
    try:
        game_data = game_engine.start_new_game(
            seed=42,
            difficulty=Difficulty.MEDIUM,
            n_suspects=6
        )
        
        print(f"Game started! Case ID: {game_data['case_id']}")
        print(f"Victim: {game_data['victim']['name']}")
        print(f"Suspects: {len(game_data['suspects'])}")
        
        # Demo interrogation
        print("\n--- Demo Interrogation ---")
        suspect_id = game_data['suspects'][0]['id']
        question = "Where were you at 9 PM?"
        
        print(f"Question: {question}")
        result = game_engine.interrogate_suspect(suspect_id, question)
        print(f"Response: {result['response']}")
        print(f"Insights: {result['insights']}")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
