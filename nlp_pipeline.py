"""
NLP Pipeline module for the murder mystery game.
Handles intent classification, entity extraction, and natural language processing.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from models import PersonId, LocationId, WeaponId, Case
import logging

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classifies user intents from natural language input."""
    
    def __init__(self):
        # Define intent patterns
        self.intent_patterns = {
            "where_were_you": [
                r"where (were|was) (you|he|she|they)",
                r"where did (you|he|she|they) go",
                r"what (were|was) (you|he|she|they) doing",
                r"(you|he|she|they) (were|was) where",
                r"location of (you|he|she|they)",
                r"position of (you|he|she|they)"
            ],
            "who_saw_you": [
                r"who saw (you|him|her|them)",
                r"who (was|were) with (you|him|her|them)",
                r"anyone see (you|him|her|them)",
                r"witness.*(you|him|her|them)",
                r"someone.*(you|him|her|them)"
            ],
            "what_did_you_do": [
                r"what (did|were|was) (you|he|she|they) do",
                r"what (were|was) (you|he|she|they) doing",
                r"(you|he|she|they) (did|were|was) what",
                r"activities.*(you|he|she|they)",
                r"actions.*(you|he|he|they)"
            ],
            "what_weapon": [
                r"what weapon",
                r"what (did|were|was) (you|he|she|they) use",
                r"weapon.*(you|he|she|they)",
                r"knife|gun|rope|poison|dagger",
                r"murder weapon",
                r"what (did|were|was) (you|he|she|they) hold"
            ],
            "alibi_check": [
                r"alibi",
                r"prove.*(you|he|she|they)",
                r"evidence.*(you|he|she|they)",
                r"can (you|he|she|they) prove",
                r"verify.*(you|he|she|they)"
            ],
            "accuse": [
                r"accuse",
                r"(you|he|she|they) (did|committed|killed)",
                r"murderer.*(you|he|she|they)",
                r"killer.*(you|he|she|they)",
                r"guilty.*(you|he|she|they)"
            ],
            "small_talk": [
                r"hello|hi|hey",
                r"how are (you|things)",
                r"weather",
                r"nice.*meet",
                r"thank you|thanks"
            ],
            "change_suspect": [
                r"talk to|speak to|question",
                r"switch to|change to",
                r"next suspect",
                r"different person"
            ]
        }
    
    def classify(self, text: str) -> Tuple[str, float]:
        """
        Classify the intent of a text input.
        
        Args:
            text: Input text to classify
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        text_lower = text.lower().strip()
        
        best_intent = "unknown"
        best_confidence = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # Calculate confidence based on pattern match quality
                    confidence = self._calculate_confidence(text_lower, pattern)
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent
        
        return best_intent, best_confidence
    
    def _calculate_confidence(self, text: str, pattern: str) -> float:
        """Calculate confidence score for a pattern match."""
        # Simple confidence calculation based on pattern complexity
        # More specific patterns get higher confidence
        pattern_words = len(pattern.split())
        text_words = len(text.split())
        
        # Base confidence from pattern match
        base_confidence = 0.7
        
        # Boost for longer, more specific patterns
        if pattern_words > 3:
            base_confidence += 0.2
        
        # Boost for exact word matches
        pattern_words_set = set(re.findall(r'\b\w+\b', pattern))
        text_words_set = set(re.findall(r'\b\w+\b', text))
        word_overlap = len(pattern_words_set.intersection(text_words_set))
        overlap_boost = min(word_overlap * 0.1, 0.3)
        
        return min(base_confidence + overlap_boost, 1.0)


class EntityExtractor:
    """Extracts entities from natural language input."""
    
    def __init__(self, case: Case):
        self.case = case
        
        # Build entity mappings
        self.person_names = {person.name.lower(): person.id for person in case.persons}
        self.location_names = {loc.name.lower(): loc.id for loc in case.location_objects}
        self.weapon_names = {weapon.name.lower(): weapon.id for weapon in case.weapon_objects}
        
        # Time patterns
        self.time_patterns = [
            (r"(\d{1,2}):(\d{2})\s*(am|pm)", self._parse_12_hour_time),
            (r"(\d{1,2}):(\d{2})", self._parse_24_hour_time),
            (r"(\d{1,2})\s*(am|pm)", self._parse_hour_only),
            (r"(morning|afternoon|evening|night)", self._parse_time_period),
            (r"(today|yesterday|tonight)", self._parse_relative_time)
        ]
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text input.
        
        Args:
            text: Input text to extract entities from
            
        Returns:
            Dictionary of extracted entities
        """
        text_lower = text.lower()
        entities = {
            "persons": [],
            "locations": [],
            "weapons": [],
            "time": None,
            "raw_text": text
        }
        
        # Extract person names
        for name, person_id in self.person_names.items():
            if name in text_lower:
                entities["persons"].append({
                    "name": name,
                    "id": person_id,
                    "span": self._find_span(text_lower, name)
                })
        
        # Extract location names
        for name, location_id in self.location_names.items():
            if name in text_lower:
                entities["locations"].append({
                    "name": name,
                    "id": location_id,
                    "span": self._find_span(text_lower, name)
                })
        
        # Extract weapon names
        for name, weapon_id in self.weapon_names.items():
            if name in text_lower:
                entities["weapons"].append({
                    "name": name,
                    "id": weapon_id,
                    "span": self._find_span(text_lower, name)
                })
        
        # Extract time
        entities["time"] = self._extract_time(text_lower)
        
        return entities
    
    def _find_span(self, text: str, entity: str) -> Tuple[int, int]:
        """Find the span (start, end) of an entity in text."""
        start = text.find(entity)
        if start != -1:
            return (start, start + len(entity))
        return (-1, -1)
    
    def _extract_time(self, text: str) -> Optional[datetime]:
        """Extract time information from text."""
        for pattern, parser in self.time_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return parser(match)
                except (ValueError, TypeError):
                    continue
        return None
    
    def _parse_12_hour_time(self, match) -> datetime:
        """Parse 12-hour time format (e.g., '3:30 pm')."""
        hour = int(match.group(1))
        minute = int(match.group(2))
        period = match.group(3).lower()
        
        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        
        # Use a reference date (today)
        today = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        return today
    
    def _parse_24_hour_time(self, match) -> datetime:
        """Parse 24-hour time format (e.g., '15:30')."""
        hour = int(match.group(1))
        minute = int(match.group(2))
        
        today = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        return today
    
    def _parse_hour_only(self, match) -> datetime:
        """Parse hour-only format (e.g., '3 pm')."""
        hour = int(match.group(1))
        period = match.group(2).lower()
        
        if period == "pm" and hour != 12:
            hour += 12
        elif period == "am" and hour == 12:
            hour = 0
        
        today = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
        return today
    
    def _parse_time_period(self, match) -> datetime:
        """Parse time period (e.g., 'morning', 'evening')."""
        period = match.group(1).lower()
        
        # Map periods to approximate times
        period_times = {
            "morning": 9,    # 9 AM
            "afternoon": 14, # 2 PM
            "evening": 19,   # 7 PM
            "night": 22      # 10 PM
        }
        
        hour = period_times.get(period, 12)
        today = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
        return today
    
    def _parse_relative_time(self, match) -> datetime:
        """Parse relative time (e.g., 'today', 'yesterday')."""
        relative = match.group(1).lower()
        now = datetime.now()
        
        if relative == "today":
            return now.replace(hour=12, minute=0, second=0, microsecond=0)
        elif relative == "yesterday":
            yesterday = now - timedelta(days=1)
            return yesterday.replace(hour=12, minute=0, second=0, microsecond=0)
        elif relative == "tonight":
            return now.replace(hour=20, minute=0, second=0, microsecond=0)
        
        return now


class NLPPipeline:
    """Main NLP pipeline that combines intent classification and entity extraction."""
    
    def __init__(self, case: Case):
        self.case = case
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor(case)
    
    def process_input(self, text: str, current_suspect: Optional[PersonId] = None) -> Dict[str, Any]:
        """
        Process natural language input to extract intent and entities.
        
        Args:
            text: Input text from user
            current_suspect: Currently interrogated suspect (if any)
            
        Returns:
            Dictionary with intent, entities, and processed information
        """
        # Classify intent
        intent, confidence = self.intent_classifier.classify(text)
        
        # Extract entities
        entities = self.entity_extractor.extract_entities(text)
        
        # Build query parameters
        params = self._build_query_params(intent, entities, current_suspect)
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "params": params,
            "raw_text": text
        }
    
    def _build_query_params(self, intent: str, entities: Dict[str, Any], current_suspect: PersonId) -> Dict[str, Any]:
        """Build query parameters based on intent and entities."""
        params = {}
        
        # Add time if extracted
        if entities["time"]:
            params["time"] = entities["time"]
        
        # Add location if extracted
        if entities["locations"]:
            params["location"] = entities["locations"][0]["id"]
        
        # Add weapon if extracted
        if entities["weapons"]:
            params["weapon"] = entities["weapons"][0]["id"]
        
        # Add person if extracted (for accusations or specific questions)
        if entities["persons"]:
            params["target_person"] = entities["persons"][0]["id"]
        
        # Add current suspect for context
        if current_suspect:
            params["current_suspect"] = current_suspect
        
        return params
    
    def validate_input(self, text: str) -> Tuple[bool, str]:
        """
        Validate if input is appropriate for the game.
        
        Args:
            text: Input text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Please provide some input."
        
        if len(text) > 500:
            return False, "Input too long. Please keep it under 500 characters."
        
        # Check for inappropriate content (basic check)
        inappropriate_words = ["kill", "murder", "death", "blood", "gun", "knife"]
        text_lower = text.lower()
        for word in inappropriate_words:
            if word in text_lower:
                return False, f"Please avoid using the word '{word}' in your questions."
        
        return True, ""
    
    def suggest_questions(self, current_suspect: Optional[PersonId] = None) -> List[str]:
        """
        Suggest questions the player can ask.
        
        Args:
            current_suspect: Currently interrogated suspect
            
        Returns:
            List of suggested questions
        """
        suggestions = [
            "Where were you at 9 PM?",
            "What were you doing this evening?",
            "Did anyone see you?",
            "What weapons do you have access to?",
            "Can you prove your alibi?",
            "What's your relationship to the victim?"
        ]
        
        if current_suspect:
            # Add suspect-specific suggestions
            suspect_name = next((p.name for p in self.case.persons if p.id == current_suspect), "the suspect")
            suggestions.extend([
                f"What do you know about {suspect_name}?",
                f"Where was {suspect_name} during the murder?",
                f"Did you see {suspect_name} with any weapons?"
            ])
        
        return suggestions
