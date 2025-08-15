"""
Core data models for the AI-driven murder mystery game.
Implements the foundational data structures for cases, persons, events, and truth tracking.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Any, Union
from pydantic import BaseModel, Field, ConfigDict
import uuid


class PersonId(str):
    """Type alias for person identifiers."""
    pass


class LocationId(str):
    """Type alias for location identifiers."""
    pass


class WeaponId(str):
    """Type alias for weapon identifiers."""
    pass


class EventId(str):
    """Type alias for event identifiers."""
    pass


class FactId(str):
    """Type alias for fact identifiers."""
    pass


class ClaimId(str):
    """Type alias for claim identifiers."""
    pass


class Difficulty(Enum):
    """Game difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class RelationshipType(Enum):
    """Types of relationships between persons."""
    FRIEND = "friend"
    RIVAL = "rival"
    LOVER = "lover"
    FAMILY = "family"
    COLLEAGUE = "colleague"
    STRANGER = "stranger"
    DEBTOR = "debtor"
    CREDITOR = "creditor"


class TruthStatus(Enum):
    """Truth status of a claim."""
    TRUE = "true"
    LIE = "lie"
    OMISSION = "omission"
    EVASION = "evasion"


class ClueType(Enum):
    """Types of evidence/clues."""
    PHYSICAL = "physical"
    TESTIMONIAL = "testimonial"
    DIGITAL = "digital"


class Relationship(BaseModel):
    """Relationship between two persons."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    person1: PersonId
    person2: PersonId
    relationship_type: RelationshipType
    strength: float = Field(ge=0.0, le=1.0)  # Relationship strength
    description: str = ""


class Person(BaseModel):
    """A person in the murder mystery (suspect, victim, witness)."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: PersonId
    name: str
    persona: Dict[str, Any] = Field(default_factory=dict)  # Personality traits
    relationships: Dict[PersonId, Relationship] = Field(default_factory=dict)
    knowledge_scope: Set[str] = Field(default_factory=set)  # Events/locations they know about
    lying_bias: float = Field(default=0.3, ge=0.0, le=1.0)  # Base propensity to lie
    reliability: float = Field(default=0.5, ge=0.0, le=1.0)  # Current reliability score
    is_victim: bool = False
    is_murderer: bool = False


class Location(BaseModel):
    """A location in the murder mystery."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: LocationId
    name: str
    description: str
    connected_locations: Set[LocationId] = Field(default_factory=set)


class Weapon(BaseModel):
    """A weapon or item in the murder mystery."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: WeaponId
    name: str
    description: str
    is_murder_weapon: bool = False


class Event(BaseModel):
    """An event in the timeline."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: EventId
    time: datetime
    actor: PersonId
    action: str
    location: LocationId
    objects: List[Union[WeaponId, str]] = Field(default_factory=list)
    description: str = ""
    is_crime: bool = False


class Fact(BaseModel):
    """An atomic proposition in the truth table."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: FactId = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    predicate: str
    object: str
    time: Optional[datetime] = None
    certainty: float = Field(default=1.0, ge=0.0, le=1.0)
    
    def __hash__(self):
        return hash((self.subject, self.predicate, self.object, self.time))
    
    def __eq__(self, other):
        if not isinstance(other, Fact):
            return False
        return (self.subject == other.subject and 
                self.predicate == other.predicate and 
                self.object == other.object and 
                self.time == other.time)


class Claim(BaseModel):
    """A claim made by a speaker during interrogation."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: ClaimId = Field(default_factory=lambda: str(uuid.uuid4()))
    speaker: PersonId
    proposition: Fact
    time_of_claim: datetime
    truth_status: TruthStatus
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    justification: str = ""
    contradictions: List[ClaimId] = Field(default_factory=list)
    corroborations: List[ClaimId] = Field(default_factory=list)


class Clue(BaseModel):
    """A piece of evidence or clue."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    clue_type: ClueType
    origin: str  # Where/how it was found
    reliability_prior: float = Field(default=0.8, ge=0.0, le=1.0)
    supports: List[EventId] = Field(default_factory=list)
    contradicts: List[EventId] = Field(default_factory=list)
    description: str = ""
    discovered: bool = False


class Murder(BaseModel):
    """Details of the murder."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    murderer: PersonId
    time: datetime
    location: LocationId
    weapon: WeaponId
    motive: str
    method: str = ""


class Case(BaseModel):
    """A complete murder mystery case."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seed: int
    difficulty: Difficulty
    victim: PersonId
    suspects: List[PersonId]
    locations: List[LocationId]
    weapons: List[WeaponId]
    timeline: List[Event]
    truth_matrix: Dict[FactId, Fact] = Field(default_factory=dict)
    murder: Murder
    clues: List[Clue] = Field(default_factory=list)
    claims: Dict[ClaimId, Claim] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Full objects for easy access
    persons: List[Person] = Field(default_factory=list)
    location_objects: List[Location] = Field(default_factory=list)
    weapon_objects: List[Weapon] = Field(default_factory=list)


class DialogueTurn(BaseModel):
    """A turn in the dialogue/interrogation."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    speaker: PersonId
    addressee: PersonId
    time: datetime
    intent: str
    entities: Dict[str, Any] = Field(default_factory=dict)
    utterance: str
    truth_status: TruthStatus
    justification: str = ""
    claim_id: Optional[ClaimId] = None


class GameState(BaseModel):
    """Current state of the game."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    case: Case
    current_suspect: Optional[PersonId] = None
    discovered_clues: Set[str] = Field(default_factory=set)
    suspicion_scores: Dict[PersonId, float] = Field(default_factory=dict)
    interrogation_history: List[DialogueTurn] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.now)
    game_completed: bool = False
    accusation: Optional[Dict[str, Any]] = None


class PlannedAnswer:
    """Represents a planned answer before surface realization."""
    
    def __init__(self, fact: Optional[Fact], mode: TruthStatus, confidence: float, context: Dict[str, Any]):
        self.fact = fact
        self.mode = mode
        self.confidence = confidence
        self.context = context
        self.justification = ""
        self.contradictions = []
        self.corroborations = []
