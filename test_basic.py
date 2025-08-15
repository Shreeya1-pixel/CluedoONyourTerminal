#!/usr/bin/env python3
"""
Basic tests for the AI-driven murder mystery game.
"""

import sys
import traceback
from models import Difficulty
from game_engine import GameEngine
from case_generator import CaseGenerator
from knowledge_base import KnowledgeBase
from lie_model import LieModel
from nlp_pipeline import NLPPipeline

def test_case_generation():
    """Test case generation functionality."""
    print("Testing case generation...")
    
    try:
        generator = CaseGenerator()
        case = generator.generate_case(seed=42, difficulty=Difficulty.MEDIUM, n_suspects=6)
        
        # Validate case
        is_valid, issues = generator.validate_case(case)
        if not is_valid:
            print(f"❌ Case validation failed: {issues}")
            return False
        
        print(f"✅ Case generated successfully:")
        print(f"   - Case ID: {case.id}")
        print(f"   - Suspects: {len(case.suspects)}")
        print(f"   - Locations: {len(case.locations)}")
        print(f"   - Weapons: {len(case.weapons)}")
        print(f"   - Timeline events: {len(case.timeline)}")
        print(f"   - Clues: {len(case.clues)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Case generation failed: {e}")
        traceback.print_exc()
        return False

def test_knowledge_base():
    """Test knowledge base functionality."""
    print("\nTesting knowledge base...")
    
    try:
        # Generate a case first
        generator = CaseGenerator()
        case = generator.generate_case(seed=42, difficulty=Difficulty.EASY, n_suspects=4)
        
        # Create knowledge base
        kb = KnowledgeBase(case)
        
        print(f"✅ Knowledge base created successfully:")
        print(f"   - Facts: {len(kb.facts)}")
        print(f"   - Events: {len(kb.events)}")
        
        # Test a simple query
        if case.suspects:
            suspect_id = case.suspects[0]
            fact = kb.query(suspect_id, "where_were_you", {"time": case.murder.time})
            if fact:
                print(f"   - Sample query result: {fact.subject} was at {fact.object}")
        
        return True
        
    except Exception as e:
        print(f"❌ Knowledge base test failed: {e}")
        traceback.print_exc()
        return False

def test_nlp_pipeline():
    """Test NLP pipeline functionality."""
    print("\nTesting NLP pipeline...")
    
    try:
        # Generate a case first
        generator = CaseGenerator()
        case = generator.generate_case(seed=42, difficulty=Difficulty.EASY, n_suspects=4)
        
        # Create NLP pipeline
        nlp = NLPPipeline(case)
        
        # Test intent classification
        test_questions = [
            "Where were you at 9 PM?",
            "What were you doing?",
            "Who saw you?",
            "What weapon did you use?",
            "Can you prove your alibi?"
        ]
        
        print("✅ NLP pipeline created successfully:")
        for question in test_questions:
            result = nlp.process_input(question)
            print(f"   - '{question}' -> {result['intent']} (confidence: {result['confidence']:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ NLP pipeline test failed: {e}")
        traceback.print_exc()
        return False

def test_lie_model():
    """Test lie model functionality."""
    print("\nTesting lie model...")
    
    try:
        # Generate a case first
        generator = CaseGenerator()
        case = generator.generate_case(seed=42, difficulty=Difficulty.EASY, n_suspects=4)
        
        # Create knowledge base and lie model
        kb = KnowledgeBase(case)
        lie_model = LieModel(case, kb)
        
        # Test lie decision
        if case.suspects:
            suspect_id = case.suspects[0]
            context = {
                "speaker": suspect_id,
                "question_type": "where_were_you",
                "params": {"time": case.murder.time}
            }
            
            decision = lie_model.decide(context)
            print(f"✅ Lie model created successfully:")
            print(f"   - Decision: {decision['mode']}")
            print(f"   - Score: {decision['score']:.2f}")
            print(f"   - Probabilities: {decision['probabilities']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lie model test failed: {e}")
        traceback.print_exc()
        return False

def test_game_engine():
    """Test game engine functionality."""
    print("\nTesting game engine...")
    
    try:
        game_engine = GameEngine()
        
        # Start a new game
        game_data = game_engine.start_new_game(
            seed=42,
            difficulty=Difficulty.EASY,
            n_suspects=4
        )
        
        print(f"✅ Game engine created successfully:")
        print(f"   - Case ID: {game_data['case_id']}")
        print(f"   - Victim: {game_data['victim']['name']}")
        print(f"   - Suspects: {len(game_data['suspects'])}")
        print(f"   - Locations: {len(game_data['locations'])}")
        print(f"   - Weapons: {len(game_data['weapons'])}")
        
        # Test interrogation
        if game_data['suspects']:
            suspect_id = game_data['suspects'][0]['id']
            question = "Where were you at 9 PM?"
            
            result = game_engine.interrogate_suspect(suspect_id, question)
            print(f"   - Interrogation test: '{question}' -> '{result['response']}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Game engine test failed: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all basic tests."""
    print("🧪 Running basic tests for AI Murder Mystery Game")
    print("=" * 50)
    
    tests = [
        test_case_generation,
        test_knowledge_base,
        test_nlp_pipeline,
        test_lie_model,
        test_game_engine
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
