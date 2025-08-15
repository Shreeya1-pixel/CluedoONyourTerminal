"""
Knowledge Base module for the murder mystery game.
Manages facts, constraints, and provides query capabilities for the consistency engine.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from models import Fact, FactId, PersonId, LocationId, WeaponId, Event, EventId, Case
import logging

logger = logging.getLogger(__name__)


class ConstraintViolation(Exception):
    """Raised when a constraint is violated."""
    pass


class KnowledgeBase:
    """
    Knowledge base that maintains facts and enforces constraints.
    Implements the truth matrix and consistency checking.
    """
    
    def __init__(self, case: Case):
        self.case = case
        self.facts: Dict[FactId, Fact] = case.truth_matrix.copy()
        self.events: Dict[EventId, Event] = {event.id: event for event in case.timeline}
        
        # Build derived facts from events
        self._build_derived_facts()
        
        # Constraint checking
        self._validate_constraints()
    
    def _build_derived_facts(self):
        """Build facts from events in the timeline."""
        for event in self.case.timeline:
            # Location facts
            location_fact = Fact(
                subject=event.actor,
                predicate="was_at",
                object=event.location,
                time=event.time,
                certainty=1.0
            )
            self.add_fact(location_fact)
            
            # Action facts
            action_fact = Fact(
                subject=event.actor,
                predicate="did",
                object=event.action,
                time=event.time,
                certainty=1.0
            )
            self.add_fact(action_fact)
            
            # Object interaction facts
            for obj in event.objects:
                obj_fact = Fact(
                    subject=event.actor,
                    predicate="interacted_with",
                    object=obj,
                    time=event.time,
                    certainty=1.0
                )
                self.add_fact(obj_fact)
    
    def add_fact(self, fact: Fact) -> FactId:
        """Add a fact to the knowledge base."""
        fact_id = fact.id
        self.facts[fact_id] = fact
        return fact_id
    
    def get_fact(self, fact_id: FactId) -> Optional[Fact]:
        """Get a fact by ID."""
        return self.facts.get(fact_id)
    
    def query(self, person: PersonId, question_type: str, params: Dict[str, Any]) -> Optional[Fact]:
        """
        Query the knowledge base for facts.
        
        Args:
            person: The person asking the question
            question_type: Type of question (e.g., 'where_were_you', 'who_saw_you')
            params: Query parameters (time, location, etc.)
        
        Returns:
            Relevant fact or None if not found
        """
        if question_type == "where_were_you":
            return self._query_location(person, params.get("time"))
        elif question_type == "who_saw_you":
            return self._query_witnesses(person, params.get("time"), params.get("location"))
        elif question_type == "what_did_you_do":
            return self._query_action(person, params.get("time"))
        elif question_type == "what_weapon":
            return self._query_weapon(person, params.get("time"))
        elif question_type == "alibi_check":
            return self._query_alibi(person, params.get("time"), params.get("location"))
        else:
            logger.warning(f"Unknown question type: {question_type}")
            return None
    
    def _query_location(self, person: PersonId, time: Optional[datetime]) -> Optional[Fact]:
        """Query where a person was at a specific time."""
        if time is None:
            return None
        
        # Find the closest time match
        closest_fact = None
        min_time_diff = timedelta(hours=24)
        
        for fact in self.facts.values():
            if (fact.subject == person and 
                fact.predicate == "was_at" and 
                fact.time is not None):
                
                time_diff = abs(fact.time - time)
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_fact = fact
        
        return closest_fact
    
    def _query_witnesses(self, person: PersonId, time: Optional[datetime], location: Optional[LocationId]) -> Optional[Fact]:
        """Query who saw a person at a specific time/location."""
        if time is None or location is None:
            return None
        
        # Find witnesses who were at the same location at the same time
        for fact in self.facts.values():
            if (fact.predicate == "was_at" and 
                fact.object == location and 
                fact.time is not None and
                abs(fact.time - time) < timedelta(minutes=30) and
                fact.subject != person):
                
                return Fact(
                    subject=fact.subject,
                    predicate="saw",
                    object=person,
                    time=time,
                    certainty=0.8  # Witness testimony is not 100% certain
                )
        
        return None
    
    def _query_action(self, person: PersonId, time: Optional[datetime]) -> Optional[Fact]:
        """Query what a person did at a specific time."""
        if time is None:
            return None
        
        # Find the closest action in time
        closest_fact = None
        min_time_diff = timedelta(hours=24)
        
        for fact in self.facts.values():
            if (fact.subject == person and 
                fact.predicate == "did" and 
                fact.time is not None):
                
                time_diff = abs(fact.time - time)
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_fact = fact
        
        return closest_fact
    
    def _query_weapon(self, person: PersonId, time: Optional[datetime]) -> Optional[Fact]:
        """Query what weapon a person had at a specific time."""
        if time is None:
            return None
        
        # Find weapon interactions
        for fact in self.facts.values():
            if (fact.subject == person and 
                fact.predicate == "interacted_with" and 
                fact.time is not None and
                abs(fact.time - time) < timedelta(hours=1)):
                
                # Check if the object is a weapon
                if any(weapon.id == fact.object for weapon in self.case.weapons):
                    return fact
        
        return None
    
    def _query_alibi(self, person: PersonId, time: Optional[datetime], location: Optional[LocationId]) -> Optional[Fact]:
        """Query if a person has an alibi for a specific time/location."""
        if time is None or location is None:
            return None
        
        # Check if person was at a different location
        person_location = self._query_location(person, time)
        if person_location and person_location.object != location:
            return Fact(
                subject=person,
                predicate="has_alibi",
                object=f"was_at_{person_location.object}_not_{location}",
                time=time,
                certainty=1.0
            )
        
        return None
    
    def check_consistency(self, new_fact: Fact) -> Tuple[bool, List[str]]:
        """
        Check if a new fact is consistent with existing facts.
        
        Returns:
            (is_consistent, list_of_violations)
        """
        violations = []
        
        # Check temporal consistency (same person can't be in two places at once)
        if new_fact.predicate == "was_at" and new_fact.time is not None:
            for fact in self.facts.values():
                if (fact.subject == new_fact.subject and 
                    fact.predicate == "was_at" and 
                    fact.time is not None and
                    fact.object != new_fact.object and
                    abs(fact.time - new_fact.time) < timedelta(minutes=30)):
                    
                    violations.append(
                        f"Temporal inconsistency: {new_fact.subject} cannot be at "
                        f"{new_fact.object} and {fact.object} at the same time"
                    )
        
        # Check uniqueness constraints
        if new_fact.predicate == "is_murderer":
            murderer_count = sum(1 for f in self.facts.values() 
                               if f.predicate == "is_murderer" and f.object == "true")
            if murderer_count > 0:
                violations.append("Uniqueness violation: Only one murderer allowed")
        
        # Check causality constraints
        if new_fact.predicate == "used_weapon" and new_fact.time is not None:
            # If someone used a weapon, they must have been at the crime scene
            crime_location = self.case.murder.location
            location_fact = self._query_location(new_fact.subject, new_fact.time)
            if not location_fact or location_fact.object != crime_location:
                violations.append(
                    f"Causality violation: {new_fact.subject} used weapon but "
                    f"was not at crime scene {crime_location}"
                )
        
        return len(violations) == 0, violations
    
    def find_contradictions(self, claim_fact: Fact) -> List[Fact]:
        """Find facts that contradict a given claim."""
        contradictions = []
        
        for fact in self.facts.values():
            if self._facts_contradict(claim_fact, fact):
                contradictions.append(fact)
        
        return contradictions
    
    def _facts_contradict(self, fact1: Fact, fact2: Fact) -> bool:
        """Check if two facts contradict each other."""
        # Same subject, predicate, time but different objects
        if (fact1.subject == fact2.subject and 
            fact1.predicate == fact2.predicate and 
            fact1.time == fact2.time and 
            fact1.object != fact2.object):
            return True
        
        # Temporal impossibility (same person in two places at once)
        if (fact1.subject == fact2.subject and 
            fact1.predicate == "was_at" and 
            fact2.predicate == "was_at" and
            fact1.time is not None and 
            fact2.time is not None and
            fact1.object != fact2.object and
            abs(fact1.time - fact2.time) < timedelta(minutes=30)):
            return True
        
        return False
    
    def _validate_constraints(self):
        """Validate that the initial case setup doesn't violate constraints."""
        violations = []
        
        # Check for temporal conflicts in the timeline
        for i, event1 in enumerate(self.case.timeline):
            for event2 in self.case.timeline[i+1:]:
                if (event1.actor == event2.actor and 
                    event1.location != event2.location and
                    abs(event1.time - event2.time) < timedelta(minutes=30)):
                    violations.append(
                        f"Timeline violation: {event1.actor} cannot be at "
                        f"{event1.location} and {event2.location} simultaneously"
                    )
        
        # Check murder constraints
        murder_event = None
        for event in self.case.timeline:
            if event.is_crime:
                murder_event = event
                break
        
        if murder_event:
            if murder_event.actor != self.case.murder.murderer:
                violations.append("Murder event actor doesn't match murderer")
            if murder_event.location != self.case.murder.location:
                violations.append("Murder event location doesn't match murder location")
            if murder_event.time != self.case.murder.time:
                violations.append("Murder event time doesn't match murder time")
        
        if violations:
            raise ConstraintViolation(f"Case setup violates constraints: {'; '.join(violations)}")
    
    def get_facts_about(self, subject: str, predicate: Optional[str] = None) -> List[Fact]:
        """Get all facts about a subject, optionally filtered by predicate."""
        facts = []
        for fact in self.facts.values():
            if fact.subject == subject:
                if predicate is None or fact.predicate == predicate:
                    facts.append(fact)
        return facts
    
    def get_facts_at_time(self, time: datetime, tolerance: timedelta = timedelta(minutes=30)) -> List[Fact]:
        """Get all facts that occurred at or near a specific time."""
        facts = []
        for fact in self.facts.values():
            if fact.time is not None and abs(fact.time - time) <= tolerance:
                facts.append(fact)
        return facts
