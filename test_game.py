#!/usr/bin/env python3
"""
Quick test script for CluedoONyourTerminal
Tests all major components to ensure they're working properly.
"""

import sys
import traceback

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing imports...")
    try:
        from models import Case, Person, Difficulty
        from case_generator import CaseGenerator
        from knowledge_base import KnowledgeBase
        from lie_model import LieModel
        from nlp_pipeline import NLPPipeline
        from response_planner import ResponsePlanner
        from surface_realizer import SurfaceRealizer
        from game_engine import GameEngine
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_case_generation():
    """Test case generation."""
    print("\n🎭 Testing case generation...")
    try:
        from case_generator import CaseGenerator
        from models import Difficulty
        
        cg = CaseGenerator()
        case = cg.generate_case(123, Difficulty.MEDIUM, 6)
        
        print(f"✅ Case generated successfully")
        print(f"   - Suspects: {len(case.suspects)}")
        print(f"   - Locations: {len(case.locations)}")
        print(f"   - Weapons: {len(case.weapons)}")
        print(f"   - Timeline events: {len(case.timeline)}")
        return True
    except Exception as e:
        print(f"❌ Case generation failed: {e}")
        traceback.print_exc()
        return False

def test_game_engine():
    """Test game engine initialization."""
    print("\n🎮 Testing game engine...")
    try:
        from game_engine import GameEngine
        from models import Difficulty
        
        ge = GameEngine()
        game_data = ge.start_new_game(456, Difficulty.MEDIUM, 6)
        
        print(f"✅ Game engine started successfully")
        print(f"   - Case ID: {game_data['case_id']}")
        print(f"   - Suspects: {len(game_data['suspects'])}")
        print(f"   - Locations: {len(game_data['locations'])}")
        print(f"   - Weapons: {len(game_data['weapons'])}")
        return True
    except Exception as e:
        print(f"❌ Game engine failed: {e}")
        traceback.print_exc()
        return False

def test_interrogation():
    """Test a complete interrogation."""
    print("\n🕵️‍♂️ Testing interrogation...")
    try:
        from game_engine import GameEngine
        from models import Difficulty
        
        ge = GameEngine()
        game_data = ge.start_new_game(789, Difficulty.MEDIUM, 6)
        
        # Get first suspect
        suspect_id = game_data['suspects'][0]['id']
        
        # Test interrogation
        result = ge.interrogate_suspect(suspect_id, "Where were you at 9 PM?")
        
        print(f"✅ Interrogation successful")
        print(f"   - Response: {result['response'][:50]}...")
        print(f"   - Truth Status: {result['insights']['truth_status']}")
        print(f"   - Reliability: {result['insights']['reliability']:.2f}")
        return True
    except Exception as e:
        print(f"❌ Interrogation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🎭 CluedoONyourTerminal - System Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_case_generation,
        test_game_engine,
        test_interrogation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CluedoONyourTerminal is ready to play!")
        print("\n🚀 To start playing, run:")
        print("   python play_game.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
