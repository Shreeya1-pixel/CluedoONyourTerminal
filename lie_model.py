"""
Lie Model module for the murder mystery game.
Implements probabilistic deception with features like threat level, relationship bias, and alternative fact sampling.
"""

import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from models import (
    Person, PersonId, Fact, LocationId, WeaponId, TruthStatus, 
    Case, RelationshipType
)
from knowledge_base import KnowledgeBase
from sklearn.linear_model import LogisticRegression
import logging

logger = logging.getLogger(__name__)


class LieModel:
    """
    Probabilistic model for determining when and how suspects lie.
    Implements the lie decision classifier and alternative fact sampler.
    """
    
    def __init__(self, case: Case, knowledge_base: KnowledgeBase):
        self.case = case
        self.kb = knowledge_base
        self.persons = {person.id: person for person in case.persons}
        
        # Initialize the lie classifier (logistic regression)
        self.classifier = LogisticRegression(random_state=42)
        self._train_classifier()
    
    def _train_classifier(self):
        """Train the lie classifier with synthetic data based on case characteristics."""
        # Generate synthetic training data based on case features
        X = []
        y = []
        
        for person_id in self.case.suspects:
            person = self.persons[person_id]
            
            # Generate features for different scenarios
            for _ in range(100):  # 100 training examples per person
                features = self._extract_features(person_id, "where_were_you", {
                    "time": self.case.murder.time + timedelta(hours=random.randint(-2, 2))
                })
                X.append(features)
                
                # Label based on person's lying bias and threat level
                threat_level = self._calculate_threat_level(person_id, "where_were_you", features)
                lie_prob = person.lying_bias * threat_level
                y.append(1 if random.random() < lie_prob else 0)
        
        # Train the classifier
        if X and y:
            self.classifier.fit(X, y)
    
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decide whether to tell the truth, lie, or evade.
        
        Args:
            context: Context including speaker, question_type, params, etc.
        
        Returns:
            Dictionary with 'mode' (truth/lie/evasion) and 'score'
        """
        speaker_id = context["speaker"]
        question_type = context["question_type"]
        params = context.get("params", {})
        
        # Extract features
        features = self._extract_features(speaker_id, question_type, params)
        
        # Get base probabilities from classifier
        if hasattr(self.classifier, 'predict_proba'):
            probs = self.classifier.predict_proba([features])[0]
            lie_prob = probs[1] if len(probs) > 1 else 0.5
        else:
            lie_prob = 0.5
        
        # Adjust based on person-specific factors
        person = self.persons[speaker_id]
        threat_level = self._calculate_threat_level(speaker_id, question_type, params)
        
        # Final probabilities
        truth_prob = (1 - person.lying_bias) * (1 - threat_level) * (1 - lie_prob)
        lie_prob = person.lying_bias * threat_level * lie_prob
        evasion_prob = 1 - truth_prob - lie_prob
        
        # Normalize
        total = truth_prob + lie_prob + evasion_prob
        if total > 0:
            truth_prob /= total
            lie_prob /= total
            evasion_prob /= total
        
        # Make decision
        rand = random.random()
        if rand < truth_prob:
            mode = TruthStatus.TRUE
            score = truth_prob
        elif rand < truth_prob + lie_prob:
            mode = TruthStatus.LIE
            score = lie_prob
        else:
            mode = TruthStatus.EVASION
            score = evasion_prob
        
        return {
            "mode": mode,
            "score": score,
            "probabilities": {
                "truth": truth_prob,
                "lie": lie_prob,
                "evasion": evasion_prob
            }
        }
    
    def sample_alternative(self, context: Dict[str, Any], truth_fact: Optional[Fact]) -> Optional[Fact]:
        """
        Sample an alternative fact for a lie that is plausible and consistent.
        
        Args:
            context: Context including speaker, question_type, params
            truth_fact: The true fact being lied about
        
        Returns:
            Alternative fact or None if no plausible alternative
        """
        speaker_id = context["speaker"]
        question_type = context["question_type"]
        params = context.get("params", {})
        
        if question_type == "where_were_you":
            return self._sample_alternative_location(speaker_id, params.get("time"), truth_fact)
        elif question_type == "what_did_you_do":
            return self._sample_alternative_action(speaker_id, params.get("time"), truth_fact)
        elif question_type == "what_weapon":
            return self._sample_alternative_weapon(speaker_id, params.get("time"), truth_fact)
        else:
            return None
    
    def _sample_alternative_location(self, speaker_id: PersonId, time: Optional[datetime], truth_fact: Optional[Fact]) -> Optional[Fact]:
        """Sample an alternative location for a lie."""
        if time is None:
            return None
        
        # Get all available locations
        available_locations = [loc.id for loc in self.case.location_objects]
        
        # Remove the true location if known
        if truth_fact and truth_fact.predicate == "was_at":
            available_locations = [loc for loc in available_locations if loc != truth_fact.object]
        
        # Score locations by plausibility
        location_scores = []
        for location_id in available_locations:
            score = self._score_location_plausibility(speaker_id, location_id, time)
            location_scores.append((location_id, score))
        
        # Sort by score and sample from top candidates
        location_scores.sort(key=lambda x: x[1], reverse=True)
        top_candidates = location_scores[:3]  # Top 3 candidates
        
        if not top_candidates:
            return None
        
        # Sample with softmax
        scores = [score for _, score in top_candidates]
        probs = self._softmax(scores, temperature=0.5)
        
        chosen_idx = np.random.choice(len(top_candidates), p=probs)
        chosen_location = top_candidates[chosen_idx][0]
        
        return Fact(
            subject=speaker_id,
            predicate="was_at",
            object=chosen_location,
            time=time,
            certainty=0.7  # Lies have lower certainty
        )
    
    def _sample_alternative_action(self, speaker_id: PersonId, time: Optional[datetime], truth_fact: Optional[Fact]) -> Optional[Fact]:
        """Sample an alternative action for a lie."""
        if time is None:
            return None
        
        # Common innocent actions
        innocent_actions = [
            "reading", "cooking", "cleaning", "sleeping", "watching_tv",
            "working", "exercising", "gardening", "shopping", "visiting_friend"
        ]
        
        # Remove the true action if known
        if truth_fact and truth_fact.predicate == "did":
            innocent_actions = [action for action in innocent_actions if action != truth_fact.object]
        
        # Score actions by plausibility
        action_scores = []
        for action in innocent_actions:
            score = self._score_action_plausibility(speaker_id, action, time)
            action_scores.append((action, score))
        
        # Sample from top candidates
        action_scores.sort(key=lambda x: x[1], reverse=True)
        top_candidates = action_scores[:3]
        
        if not top_candidates:
            return None
        
        scores = [score for _, score in top_candidates]
        probs = self._softmax(scores, temperature=0.5)
        
        chosen_idx = np.random.choice(len(top_candidates), p=probs)
        chosen_action = top_candidates[chosen_idx][0]
        
        return Fact(
            subject=speaker_id,
            predicate="did",
            object=chosen_action,
            time=time,
            certainty=0.7
        )
    
    def _sample_alternative_weapon(self, speaker_id: PersonId, time: Optional[datetime], truth_fact: Optional[Fact]) -> Optional[Fact]:
        """Sample an alternative weapon interaction for a lie."""
        if time is None:
            return None
        
        # Get non-murder weapons
        innocent_weapons = [weapon.id for weapon in self.case.weapon_objects if not weapon.is_murder_weapon]
        
        # Remove the true weapon if known
        if truth_fact and truth_fact.predicate == "interacted_with":
            innocent_weapons = [weapon for weapon in innocent_weapons if weapon != truth_fact.object]
        
        if not innocent_weapons:
            return None
        
        # Choose a random innocent weapon
        chosen_weapon = random.choice(innocent_weapons)
        
        return Fact(
            subject=speaker_id,
            predicate="interacted_with",
            object=chosen_weapon,
            time=time,
            certainty=0.6
        )
    
    def _extract_features(self, speaker_id: PersonId, question_type: str, params: Dict[str, Any]) -> List[float]:
        """Extract features for the lie classifier."""
        person = self.persons[speaker_id]
        
        features = [
            person.lying_bias,  # Base lying propensity
            self._calculate_threat_level(speaker_id, question_type, params),  # Threat level
            self._calculate_relationship_bias(speaker_id),  # Relationship to victim
            self._calculate_pressure_level(speaker_id),  # Recent contradictions
            self._calculate_difficulty_factor(),  # Game difficulty
            self._calculate_time_factor(params.get("time")),  # Time proximity to crime
            self._calculate_location_factor(params.get("location")),  # Location proximity to crime
        ]
        
        return features
    
    def _calculate_threat_level(self, speaker_id: PersonId, question_type: str, params: Dict[str, Any]) -> float:
        """Calculate how threatening a question is to the speaker."""
        threat_score = 0.0
        
        # Time proximity to murder
        if "time" in params and params["time"]:
            time_diff = abs(params["time"] - self.case.murder.time)
            if time_diff < timedelta(hours=1):
                threat_score += 0.8
            elif time_diff < timedelta(hours=2):
                threat_score += 0.5
            elif time_diff < timedelta(hours=3):
                threat_score += 0.2
        
        # Location proximity to crime scene
        if "location" in params and params["location"]:
            if params["location"] == self.case.murder.location:
                threat_score += 0.9
        
        # Question type threat levels
        question_threats = {
            "where_were_you": 0.7,
            "who_saw_you": 0.6,
            "what_did_you_do": 0.8,
            "what_weapon": 0.9,
            "alibi_check": 0.8,
            "small_talk": 0.1
        }
        
        threat_score += question_threats.get(question_type, 0.5)
        
        # If speaker is the murderer, increase threat
        if speaker_id == self.case.murder.murderer:
            threat_score *= 1.5
        
        return min(threat_score, 1.0)
    
    def _calculate_relationship_bias(self, speaker_id: PersonId) -> float:
        """Calculate relationship bias based on connections to victim."""
        # This would be more sophisticated in a full implementation
        # For now, return a simple bias based on whether they're the murderer
        if speaker_id == self.case.murder.murderer:
            return 0.8
        else:
            return 0.3
    
    def _calculate_pressure_level(self, speaker_id: PersonId) -> float:
        """Calculate pressure level based on recent contradictions."""
        # Count recent contradictions for this speaker
        recent_contradictions = 0
        for claim in self.case.claims.values():
            if (claim.speaker == speaker_id and 
                claim.truth_status == TruthStatus.LIE and
                len(claim.contradictions) > 0):
                recent_contradictions += 1
        
        # Normalize to [0, 1]
        return min(recent_contradictions / 5.0, 1.0)
    
    def _calculate_difficulty_factor(self) -> float:
        """Calculate difficulty factor based on game difficulty."""
        difficulty_factors = {
            "easy": 0.3,
            "medium": 0.6,
            "hard": 0.9
        }
        return difficulty_factors.get(self.case.difficulty.value, 0.5)
    
    def _calculate_time_factor(self, time: Optional[datetime]) -> float:
        """Calculate time factor based on proximity to crime time."""
        if time is None:
            return 0.0
        
        time_diff = abs(time - self.case.murder.time)
        if time_diff < timedelta(minutes=30):
            return 1.0
        elif time_diff < timedelta(hours=1):
            return 0.8
        elif time_diff < timedelta(hours=2):
            return 0.5
        else:
            return 0.2
    
    def _calculate_location_factor(self, location: Optional[LocationId]) -> float:
        """Calculate location factor based on proximity to crime scene."""
        if location is None:
            return 0.0
        
        if location == self.case.murder.location:
            return 1.0
        else:
            return 0.3
    
    def _score_location_plausibility(self, speaker_id: PersonId, location_id: LocationId, time: datetime) -> float:
        """Score how plausible it is for a person to be at a location."""
        score = 0.5  # Base score
        
        # Check if person has been at this location before
        location_facts = self.kb.get_facts_about(speaker_id, "was_at")
        for fact in location_facts:
            if fact.object == location_id:
                score += 0.3
                break
        
        # Check if location is connected to other locations person has been
        person_locations = set(fact.object for fact in location_facts)
        location = next((loc for loc in self.case.location_objects if loc.id == location_id), None)
        if location:
            for connected_loc in location.connected_locations:
                if connected_loc in person_locations:
                    score += 0.2
                    break
        
        # Avoid crime scene unless it's the murderer
        if location_id == self.case.murder.location and speaker_id != self.case.murder.murderer:
            score -= 0.5
        
        return max(0.0, min(1.0, score))
    
    def _score_action_plausibility(self, speaker_id: PersonId, action: str, time: datetime) -> float:
        """Score how plausible an action is for a person."""
        score = 0.5  # Base score
        
        # Check if person has done this action before
        action_facts = self.kb.get_facts_about(speaker_id, "did")
        for fact in action_facts:
            if fact.object == action:
                score += 0.3
                break
        
        # Time-based plausibility
        hour = time.hour
        if action in ["sleeping"] and 6 <= hour <= 22:
            score -= 0.3
        elif action in ["cooking"] and (hour < 6 or hour > 22):
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _softmax(self, scores: List[float], temperature: float = 1.0) -> List[float]:
        """Convert scores to probabilities using softmax."""
        if not scores:
            return []
        
        # Apply temperature
        scaled_scores = [score / temperature for score in scores]
        
        # Compute softmax
        max_score = max(scaled_scores)
        exp_scores = [np.exp(score - max_score) for score in scaled_scores]
        sum_exp = sum(exp_scores)
        
        if sum_exp == 0:
            return [1.0 / len(scores)] * len(scores)
        
        return [exp_score / sum_exp for exp_score in exp_scores]
