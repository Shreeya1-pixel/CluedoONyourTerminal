"""
Game Engine module for the murder mystery game.
Coordinates all modules and manages the game state.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from models import (
    Case, Person, Location, Weapon, Event, Fact, Murder, Clue, Claim, 
    PersonId, LocationId, WeaponId, EventId, Difficulty, TruthStatus, GameState
)
from case_generator import CaseGenerator
from knowledge_base import KnowledgeBase
from lie_model import LieModel
from nlp_pipeline import NLPPipeline
from response_planner import ResponsePlanner
import logging

logger = logging.getLogger(__name__)


class GameEngine:
    """
    Main game engine that coordinates all modules and manages game state.
    Implements the core game loop and logic.
    """
    
    def __init__(self):
        self.case_generator = CaseGenerator()
        self.current_case: Optional[Case] = None
        self.knowledge_base: Optional[KnowledgeBase] = None
        self.lie_model: Optional[LieModel] = None
        self.nlp_pipeline: Optional[NLPipeline] = None
        self.response_planner: Optional[ResponsePlanner] = None
        self.game_state: Optional[GameState] = None
        
        # Game configuration
        self.max_interrogations = 50
        self.contradiction_threshold = 2  # Number of contradictions before flagging
        
    def start_new_game(self, seed: int, difficulty: Difficulty, n_suspects: int = 6) -> Dict[str, Any]:
        """
        Start a new murder mystery game.
        
        Args:
            seed: Random seed for case generation
            difficulty: Game difficulty level
            n_suspects: Number of suspects
            
        Returns:
            Game initialization data
        """
        # Generate case
        self.current_case = self.case_generator.generate_case(seed, difficulty, n_suspects)
        
        # Validate case
        is_valid, issues = self.case_generator.validate_case(self.current_case)
        if not is_valid:
            raise ValueError(f"Generated case is invalid: {issues}")
        
        # Initialize modules
        self.knowledge_base = KnowledgeBase(self.current_case)
        self.lie_model = LieModel(self.current_case, self.knowledge_base)
        self.nlp_pipeline = NLPPipeline(self.current_case)
        self.response_planner = ResponsePlanner(
            self.current_case, 
            self.knowledge_base, 
            self.lie_model, 
            self.nlp_pipeline
        )
        
        # Initialize game state
        self.game_state = GameState(
            case=self.current_case,
            suspicion_scores={suspect: 0.5 for suspect in self.current_case.suspects}
        )
        
        # Get initial information
        initial_info = self._get_initial_information()
        
        return {
            "case_id": self.current_case.id,
            "victim": self._get_person_info(self.current_case.victim),
            "suspects": [self._get_person_info(suspect) for suspect in self.current_case.suspects],
            "locations": [self._get_location_info(location) for location in self.current_case.locations],
            "weapons": [self._get_weapon_info(weapon) for weapon in self.current_case.weapons],
            "initial_clues": initial_info["clues"],
            "suggested_questions": self.nlp_pipeline.suggest_questions()
        }
    
    def interrogate_suspect(self, suspect_id: PersonId, question: str) -> Dict[str, Any]:
        """
        Interrogate a suspect with a question.
        
        Args:
            suspect_id: ID of the suspect to interrogate
            question: Player's question
            
        Returns:
            Response and game state update
        """
        if not self.game_state:
            raise ValueError("No active game")
        
        if suspect_id not in self.current_case.suspects:
            raise ValueError(f"Invalid suspect ID: {suspect_id}")
        
        # Update current suspect
        self.game_state.current_suspect = suspect_id
        
        # Process the question and generate response
        response_text, claim, processing_info = self.response_planner.process_player_input(
            question, suspect_id, self._get_game_state_dict()
        )
        
        # Add claim to case if valid
        if claim:
            self.current_case.claims[claim.id] = claim
            
            # Update suspicion scores
            self._update_suspicion_scores(claim)
            
            # Check for contradictions
            contradictions = self._check_contradictions(claim)
            
            # Add to interrogation history
            dialogue_turn = {
                "speaker": "player",
                "addressee": suspect_id,
                "time": datetime.now(),
                "intent": processing_info["intent"],
                "entities": processing_info["entities"],
                "utterance": question,
                "truth_status": TruthStatus.TRUE,
                "claim_id": None
            }
            self.game_state.interrogation_history.append(dialogue_turn)
            
            # Add suspect response to history
            suspect_turn = {
                "speaker": suspect_id,
                "addressee": "player",
                "time": datetime.now(),
                "intent": processing_info["intent"],
                "entities": processing_info["entities"],
                "utterance": response_text,
                "truth_status": claim.truth_status,
                "claim_id": claim.id
            }
            self.game_state.interrogation_history.append(suspect_turn)
        
        # Get insights about the response
        insights = self.response_planner.get_response_insights(claim) if claim else {}
        
        return {
            "response": response_text,
            "suspect": self._get_person_info(suspect_id),
            "insights": insights,
            "contradictions": contradictions,
            "suspicion_scores": self.game_state.suspicion_scores,
            "suggested_questions": self.nlp_pipeline.suggest_questions(suspect_id)
        }
    
    def make_accusation(self, accused_suspect: PersonId, weapon: WeaponId, location: LocationId) -> Dict[str, Any]:
        """
        Make an accusation to solve the case.
        
        Args:
            accused_suspect: ID of the accused suspect
            weapon: ID of the weapon used
            location: ID of the location where murder occurred
            
        Returns:
            Accusation result and game completion data
        """
        if not self.game_state:
            raise ValueError("No active game")
        
        # Check if accusation is correct
        is_correct = (
            accused_suspect == self.current_case.murder.murderer and
            weapon == self.current_case.murder.weapon and
            location == self.current_case.murder.location
        )
        
        # Calculate score
        score = self._calculate_score()
        
        # Mark game as completed
        self.game_state.game_completed = True
        self.game_state.accusation = {
            "accused_suspect": accused_suspect,
            "weapon": weapon,
            "location": location,
            "is_correct": is_correct,
            "score": score,
            "correct_answer": {
                "murderer": self.current_case.murder.murderer,
                "weapon": self.current_case.murder.weapon,
                "location": self.current_case.murder.location,
                "motive": self.current_case.murder.motive
            }
        }
        
        return {
            "is_correct": is_correct,
            "score": score,
            "correct_answer": self.game_state.accusation["correct_answer"],
            "explanation": self._generate_explanation(),
            "game_stats": self._get_game_stats()
        }
    
    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state information."""
        if not self.game_state:
            return {"error": "No active game"}
        
        return {
            "case_id": self.current_case.id,
            "current_suspect": self.game_state.current_suspect,
            "suspicion_scores": self.game_state.suspicion_scores,
            "discovered_clues": list(self.game_state.discovered_clues),
            "interrogation_count": len(self.game_state.interrogation_history) // 2,  # Each interrogation has 2 turns
            "game_completed": self.game_state.game_completed,
            "available_suspects": [self._get_person_info(s) for s in self.current_case.suspects],
            "available_locations": [self._get_location_info(l) for l in self.current_case.locations],
            "available_weapons": [self._get_weapon_info(w) for w in self.current_case.weapons]
        }
    
    def get_timeline(self) -> List[Dict[str, Any]]:
        """Get the case timeline."""
        if not self.current_case:
            return []
        
        timeline = []
        for event in self.current_case.timeline:
            timeline.append({
                "id": event.id,
                "time": event.time.isoformat(),
                "actor": self._get_person_info(event.actor),
                "action": event.action,
                "location": self._get_location_info(event.location),
                "objects": [self._get_weapon_info(obj) for obj in event.objects if obj.startswith("weapon_")],
                "description": event.description,
                "is_crime": event.is_crime
            })
        
        return timeline
    
    def get_claims_analysis(self) -> Dict[str, Any]:
        """Get analysis of all claims made during interrogation."""
        if not self.current_case:
            return {}
        
        analysis = {
            "total_claims": len(self.current_case.claims),
            "claims_by_suspect": {},
            "truth_status_distribution": {},
            "contradictions": [],
            "corroborations": []
        }
        
        # Analyze claims by suspect
        for suspect_id in self.current_case.suspects:
            suspect_claims = [c for c in self.current_case.claims.values() if c.speaker == suspect_id]
            analysis["claims_by_suspect"][suspect_id] = {
                "count": len(suspect_claims),
                "truthful": len([c for c in suspect_claims if c.truth_status == TruthStatus.TRUE]),
                "lies": len([c for c in suspect_claims if c.truth_status == TruthStatus.LIE]),
                "evasions": len([c for c in suspect_claims if c.truth_status == TruthStatus.EVASION]),
                "omissions": len([c for c in suspect_claims if c.truth_status == TruthStatus.OMISSION])
            }
        
        # Analyze truth status distribution
        for claim in self.current_case.claims.values():
            status = claim.truth_status.value
            analysis["truth_status_distribution"][status] = analysis["truth_status_distribution"].get(status, 0) + 1
        
        # Find contradictions and corroborations
        for claim in self.current_case.claims.values():
            if claim.contradictions:
                analysis["contradictions"].append({
                    "claim_id": claim.id,
                    "speaker": claim.speaker,
                    "contradictions": claim.contradictions
                })
            
            if claim.corroborations:
                analysis["corroborations"].append({
                    "claim_id": claim.id,
                    "speaker": claim.speaker,
                    "corroborations": claim.corroborations
                })
        
        return analysis
    
    def _get_initial_information(self) -> Dict[str, Any]:
        """Get initial information revealed to the player."""
        # Reveal some basic clues
        revealed_clues = []
        for i, clue in enumerate(self.current_case.clues[:3]):  # Reveal first 3 clues
            clue.discovered = True
            self.game_state.discovered_clues.add(clue.id)
            revealed_clues.append({
                "id": clue.id,
                "type": clue.clue_type.value,
                "description": clue.description,
                "origin": clue.origin,
                "reliability": clue.reliability_prior
            })
        
        return {
            "clues": revealed_clues,
            "victim_info": self._get_person_info(self.current_case.victim),
            "crime_scene": self._get_location_info(self.current_case.murder.location)
        }
    
    def _get_person_info(self, person_id: PersonId) -> Dict[str, Any]:
        """Get person information for display."""
        # This would normally look up from a person database
        # For now, return basic info
        return {
            "id": person_id,
            "name": f"Person {person_id}",
            "is_victim": person_id == self.current_case.victim,
            "suspicion_score": self.game_state.suspicion_scores.get(person_id, 0.5) if self.game_state else 0.5
        }
    
    def _get_location_info(self, location_id: LocationId) -> Dict[str, Any]:
        """Get location information for display."""
        return {
            "id": location_id,
            "name": f"Location {location_id}",
            "is_crime_scene": location_id == self.current_case.murder.location
        }
    
    def _get_weapon_info(self, weapon_id: WeaponId) -> Dict[str, Any]:
        """Get weapon information for display."""
        return {
            "id": weapon_id,
            "name": f"Weapon {weapon_id}",
            "is_murder_weapon": weapon_id == self.current_case.murder.weapon
        }
    
    def _get_game_state_dict(self) -> Dict[str, Any]:
        """Get game state as dictionary for modules."""
        if not self.game_state:
            return {}
        
        return {
            "current_suspect": self.game_state.current_suspect,
            "suspicion_scores": self.game_state.suspicion_scores,
            "discovered_clues": list(self.game_state.discovered_clues),
            "interrogation_count": len(self.game_state.interrogation_history) // 2,
            "game_completed": self.game_state.game_completed
        }
    
    def _update_suspicion_scores(self, claim: Claim):
        """Update suspicion scores based on a claim."""
        if not claim:
            return
        
        # Adjust suspicion based on truth status and contradictions
        base_adjustment = 0.1
        
        if claim.truth_status == TruthStatus.LIE:
            # Increase suspicion for lies
            self.game_state.suspicion_scores[claim.speaker] += base_adjustment * 2
        elif claim.truth_status == TruthStatus.TRUE:
            # Slightly decrease suspicion for truth
            self.game_state.suspicion_scores[claim.speaker] -= base_adjustment * 0.5
        
        # Additional adjustment for contradictions
        if claim.contradictions:
            self.game_state.suspicion_scores[claim.speaker] += base_adjustment * len(claim.contradictions)
        
        # Clamp scores to [0, 1]
        self.game_state.suspicion_scores[claim.speaker] = max(0.0, min(1.0, self.game_state.suspicion_scores[claim.speaker]))
    
    def _check_contradictions(self, claim: Claim) -> List[Dict[str, Any]]:
        """Check for contradictions with the new claim."""
        if not claim:
            return []
        
        contradictions = []
        for contradiction_id in claim.contradictions:
            contradicting_claim = self.current_case.claims.get(contradiction_id)
            if contradicting_claim:
                contradictions.append({
                    "claim_id": claim.id,
                    "contradicting_claim_id": contradiction_id,
                    "speaker": claim.speaker,
                    "contradicting_speaker": contradicting_claim.speaker,
                    "description": f"{claim.speaker} contradicts {contradicting_claim.speaker}"
                })
        
        return contradictions
    
    def _calculate_score(self) -> float:
        """Calculate final game score."""
        if not self.game_state:
            return 0.0
        
        base_score = 100.0
        
        # Deduct points for incorrect accusations
        if not self.game_state.accusation["is_correct"]:
            base_score -= 50.0
        
        # Bonus for efficient solving (fewer interrogations)
        interrogation_count = len(self.game_state.interrogation_history) // 2
        if interrogation_count < 10:
            base_score += 20.0
        elif interrogation_count < 20:
            base_score += 10.0
        
        # Bonus for discovering contradictions
        total_contradictions = sum(len(claim.contradictions) for claim in self.current_case.claims.values())
        base_score += total_contradictions * 5.0
        
        return max(0.0, base_score)
    
    def _generate_explanation(self) -> str:
        """Generate explanation of the solution."""
        if not self.game_state or not self.game_state.accusation:
            return "No accusation made."
        
        accusation = self.game_state.accusation
        correct = accusation["correct_answer"]
        
        if accusation["is_correct"]:
            return f"Correct! {correct['murderer']} committed the murder using the {correct['weapon']} in the {correct['location']}. Motive: {correct['motive']}."
        else:
            return f"Incorrect. The murderer was {correct['murderer']} using the {correct['weapon']} in the {correct['location']}. Motive: {correct['motive']}."
    
    def _get_game_stats(self) -> Dict[str, Any]:
        """Get comprehensive game statistics."""
        if not self.game_state:
            return {}
        
        return {
            "total_interrogations": len(self.game_state.interrogation_history) // 2,
            "total_claims": len(self.current_case.claims),
            "discovered_clues": len(self.game_state.discovered_clues),
            "suspicion_scores": self.game_state.suspicion_scores,
            "truth_status_distribution": self._get_truth_status_distribution(),
            "contradictions_found": sum(len(claim.contradictions) for claim in self.current_case.claims.values()),
            "corroborations_found": sum(len(claim.corroborations) for claim in self.current_case.claims.values())
        }
    
    def _get_truth_status_distribution(self) -> Dict[str, int]:
        """Get distribution of truth statuses across all claims."""
        distribution = {}
        for claim in self.current_case.claims.values():
            status = claim.truth_status.value
            distribution[status] = distribution.get(status, 0) + 1
        return distribution
