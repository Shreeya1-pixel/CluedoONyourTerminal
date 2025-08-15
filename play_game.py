#!/usr/bin/env python3
"""
Interactive Murder Mystery Game
Play the AI-driven murder mystery game with full interrogation capabilities!
"""

import sys
import random
from datetime import datetime
from typing import Optional
from game_engine import GameEngine
from models import Difficulty

class InteractiveGame:
    def __init__(self):
        self.game_engine = GameEngine()
        self.current_suspect: Optional[str] = None
        self.game_data = None
        
    def start_game(self):
        """Start a new game and show the setup"""
        print("🎭 CluedoONyourTerminal")
        print("=" * 50)
        print()
        print("🌙 A DARK NIGHT AT BLACKWOOD MANOR")
        print("🎭 The Ultimate Terminal Murder Mystery")
        print("=" * 50)
        print()
        print("The year is 1923. You are Detective Inspector James Blackwood, called to")
        print("investigate a murder at the grand Blackwood Manor estate. The victim was")
        print("found in the library, and six suspects are being held for questioning.")
        print()
        print("Each suspect has their own personality, motives, and secrets. Some will")
        print("tell the truth, others will lie, and some will try to evade your questions.")
        print("It's up to you to piece together the evidence and identify the killer.")
        print()
        print("🎯 YOUR MISSION:")
        print("• Interrogate each suspect carefully")
        print("• Look for contradictions in their stories")
        print("• Pay attention to their reliability scores")
        print("• Gather enough evidence to make an accusation")
        print()
        print("⚡ GAME FEATURES:")
        print("• AI-powered suspects with realistic personalities")
        print("• Dynamic responses that change based on your questions")
        print("• Probabilistic deception system (suspects may lie or evade)")
        print("• Consistency tracking to catch contradictions")
        print("• Multiple difficulty levels and unique cases")
        print()
        print("Let the investigation begin...")
        print()
        print("=" * 50)
        print()
        
        # Start new game
        self.game_data = self.game_engine.start_new_game(
            seed=random.randint(1, 1000),
            difficulty=Difficulty.MEDIUM,
            n_suspects=6
        )
        
        print(f"📋 CASE SUMMARY")
        print(f"Case ID: {self.game_data['case_id']}")
        print(f"Victim: {self.game_data['victim']['name']}")
        print(f"Time of Discovery: {datetime.now().strftime('%B %d, 1923 at %I:%M %p')}")
        print(f"Location: Blackwood Manor Library")
        print(f"Status: Active Investigation")
        print()
        
        print("👥 SUSPECTS IN CUSTODY:")
        print("The following individuals are being held for questioning:")
        for i, suspect in enumerate(self.game_data['suspects'], 1):
            suspicion_level = "Low" if suspect['suspicion_score'] < 0.4 else "Medium" if suspect['suspicion_score'] < 0.7 else "High"
            print(f"{i}. {suspect['name']} - Suspicion Level: {suspicion_level}")
        print()
        
        print("📍 CRIME SCENE LOCATIONS:")
        print("The following areas of Blackwood Manor are relevant to the investigation:")
        for i, location in enumerate(self.game_data['locations'], 1):
            crime_scene = " ⚠️ CRIME SCENE" if location['is_crime_scene'] else ""
            print(f"{i}. {location['name']}{crime_scene}")
        print()
        
        print("🔪 POTENTIAL WEAPONS:")
        print("The following items were found at the scene or in the manor:")
        for i, weapon in enumerate(self.game_data['weapons'], 1):
            murder_weapon = " ⚠️ MURDER WEAPON" if weapon['is_murder_weapon'] else ""
            print(f"{i}. {weapon['name']}{murder_weapon}")
        print()
        
    def show_help(self):
        """Show available commands"""
        print("\n📖 INVESTIGATION COMMANDS:")
        print("interrogate <suspect_number> - Begin questioning a suspect")
        print("ask <question> - Ask the current suspect a question")
        print("switch <suspect_number> - Move to a different suspect")
        print("timeline - Review the case timeline and events")
        print("analysis - Analyze all statements for contradictions")
        print("accuse <suspect_number> - Make your final accusation")
        print("help - Show this help menu")
        print("quit - End the investigation")
        print()
        print("💡 INVESTIGATION TIPS:")
        print("• Start with basic questions: 'Where were you at 9 PM?'")
        print("• Ask about relationships: 'Did you know the victim?'")
        print("• Check alibis: 'Can anyone confirm your whereabouts?'")
        print("• Look for contradictions between suspects")
        print("• Pay attention to nervous behavior and evasive answers")
        print("• Use 'timeline' to understand the sequence of events")
        print("• Use 'analysis' to see who might be lying")
        print()
        
    def interrogate_suspect(self, suspect_num: int):
        """Start interrogating a specific suspect"""
        try:
            suspect_idx = int(suspect_num) - 1
            if 0 <= suspect_idx < len(self.game_data['suspects']):
                self.current_suspect = self.game_data['suspects'][suspect_idx]['id']
                suspect_name = self.game_data['suspects'][suspect_idx]['name']
                print(f"\n🔍 Now interrogating: {suspect_name}")
                print("Ask questions using 'ask <your question>'")
                print("Example: ask Where were you at 9 PM?")
                print()
            else:
                print("❌ Invalid suspect number!")
        except ValueError:
            print("❌ Please enter a valid number!")
            
    def ask_question(self, question: str):
        """Ask the current suspect a question"""
        if not self.current_suspect:
            print("❌ No suspect selected! Use 'interrogate <number>' first.")
            return
            
        print(f"\n❓ Question: {question}")
        result = self.game_engine.interrogate_suspect(self.current_suspect, question)
        
        print(f"💬 Response: {result['response']}")
        print(f"📊 Insights:")
        print(f"   Reliability: {result['insights']['reliability']:.2f}")
        print(f"   Truth Status: {result['insights']['truth_status']}")
        print(f"   Contradictions: {result['insights']['contradictions']}")
        print(f"   Corroborations: {result['insights']['corroborations']}")
        if result['insights']['justification']:
            print(f"   Justification: {result['insights']['justification']}")
        print()
        
    def show_timeline(self):
        """Show the case timeline"""
        timeline = self.game_engine.get_timeline()
        print("\n⏰ CASE TIMELINE:")
        for event in timeline:
            print(f"   {event['time']}: {event['description']}")
        print()
        
    def show_analysis(self):
        """Show claims analysis"""
        analysis = self.game_engine.get_claims_analysis()
        print("\n📈 CLAIMS ANALYSIS:")
        print(f"Total Claims: {analysis['total_claims']}")
        print(f"Contradictions: {analysis['contradictions']}")
        print(f"Corroborations: {analysis['corroborations']}")
        print(f"Unverified: {analysis['unverified']}")
        print()
        
    def make_accusation(self, suspect_num: int):
        """Make an accusation"""
        try:
            suspect_idx = int(suspect_num) - 1
            if 0 <= suspect_idx < len(self.game_data['suspects']):
                suspect_id = self.game_data['suspects'][suspect_idx]['id']
                suspect_name = self.game_data['suspects'][suspect_idx]['name']
                
                print(f"\n🎯 Making accusation against: {suspect_name}")
                result = self.game_engine.make_accusation(suspect_id)
                
                if result['correct']:
                    print("🎉 CONGRATULATIONS! You solved the case!")
                    print(f"The murderer was indeed {suspect_name}!")
                else:
                    print("❌ WRONG ACCUSATION!")
                    print(f"{suspect_name} was innocent.")
                    print(f"The real murderer was: {result['correct_suspect']}")
                    
                print(f"Final Score: {result['score']}")
                print()
            else:
                print("❌ Invalid suspect number!")
        except ValueError:
            print("❌ Please enter a valid number!")
            
    def run(self):
        """Main game loop"""
        self.start_game()
        self.show_help()
        
        while True:
            try:
                command = input("🕵️‍♂️ Detective > ").strip().lower()
                
                if command == "quit" or command == "exit":
                    print("👋 Thanks for playing!")
                    break
                elif command == "help":
                    self.show_help()
                elif command.startswith("interrogate "):
                    parts = command.split(" ", 1)
                    if len(parts) > 1:
                        self.interrogate_suspect(parts[1])
                    else:
                        print("❌ Usage: interrogate <suspect_number>")
                elif command.startswith("ask "):
                    parts = command.split(" ", 1)
                    if len(parts) > 1:
                        self.ask_question(parts[1])
                    else:
                        print("❌ Usage: ask <your question>")
                elif command.startswith("switch "):
                    parts = command.split(" ", 1)
                    if len(parts) > 1:
                        self.interrogate_suspect(parts[1])
                    else:
                        print("❌ Usage: switch <suspect_number>")
                elif command == "timeline":
                    self.show_timeline()
                elif command == "analysis":
                    self.show_analysis()
                elif command.startswith("accuse "):
                    parts = command.split(" ", 1)
                    if len(parts) > 1:
                        self.make_accusation(parts[1])
                    else:
                        print("❌ Usage: accuse <suspect_number>")
                elif command == "":
                    continue
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Thanks for playing!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    game = InteractiveGame()
    game.run()

if __name__ == "__main__":
    main()
