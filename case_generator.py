"""
Case Generator module for the murder mystery game.
Builds coherent murder mystery cases with suspects, locations, weapons, timeline, and truth matrix.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple
from models import (
    Case, Person, Location, Weapon, Event, Fact, Murder, Clue, 
    PersonId, LocationId, WeaponId, EventId, FactId, Difficulty, RelationshipType
)
import logging

logger = logging.getLogger(__name__)


class CaseGenerator:
    """
    Generates coherent murder mystery cases with proper constraints and relationships.
    Implements procedural case generation with difficulty scaling.
    """
    
    def __init__(self):
        # Predefined entities for case generation
        self.person_templates = [
            {"name": "Colonel Mustard", "persona": {"profession": "military", "personality": "authoritative"}},
            {"name": "Professor Plum", "persona": {"profession": "academic", "personality": "intellectual"}},
            {"name": "Miss Scarlet", "persona": {"profession": "socialite", "personality": "charming"}},
            {"name": "Mrs. White", "persona": {"profession": "housekeeper", "personality": "efficient"}},
            {"name": "Mr. Green", "persona": {"profession": "businessman", "personality": "ambitious"}},
            {"name": "Dr. Orchid", "persona": {"profession": "scientist", "personality": "analytical"}},
            {"name": "Reverend Green", "persona": {"profession": "clergy", "personality": "moral"}},
            {"name": "Mrs. Peacock", "persona": {"profession": "politician", "personality": "diplomatic"}}
        ]
        
        self.location_templates = [
            {"name": "Study", "description": "A cozy room with bookshelves and a fireplace"},
            {"name": "Library", "description": "Quiet room filled with books and reading chairs"},
            {"name": "Conservatory", "description": "Glass-enclosed room with plants and comfortable seating"},
            {"name": "Kitchen", "description": "Well-equipped kitchen with modern appliances"},
            {"name": "Dining Room", "description": "Elegant room with a large table and fine china"},
            {"name": "Ballroom", "description": "Large open space with polished floors"},
            {"name": "Lounge", "description": "Comfortable sitting room with sofas and coffee tables"},
            {"name": "Hall", "description": "Grand entrance hall with marble floors"},
            {"name": "Billiard Room", "description": "Game room with pool table and bar"},
            {"name": "Garden", "description": "Beautiful outdoor garden with paths and benches"}
        ]
        
        self.weapon_templates = [
            {"name": "Candlestick", "description": "Heavy brass candlestick", "is_murder_weapon": False},
            {"name": "Dagger", "description": "Sharp ceremonial dagger", "is_murder_weapon": False},
            {"name": "Lead Pipe", "description": "Heavy metal pipe", "is_murder_weapon": False},
            {"name": "Revolver", "description": "Antique revolver", "is_murder_weapon": False},
            {"name": "Rope", "description": "Strong rope", "is_murder_weapon": False},
            {"name": "Wrench", "description": "Heavy wrench", "is_murder_weapon": False},
            {"name": "Poison", "description": "Deadly poison", "is_murder_weapon": False},
            {"name": "Axe", "description": "Sharp axe", "is_murder_weapon": False}
        ]
        
        self.motive_templates = [
            "Financial gain",
            "Revenge",
            "Jealousy",
            "Fear of exposure",
            "Power struggle",
            "Love triangle",
            "Inheritance",
            "Blackmail",
            "Professional rivalry",
            "Family feud"
        ]
    
    def generate_case(self, seed: int, difficulty: Difficulty, n_suspects: int = 6) -> Case:
        """
        Generate a complete murder mystery case.
        
        Args:
            seed: Random seed for reproducible generation
            difficulty: Game difficulty level
            n_suspects: Number of suspects to include
            
        Returns:
            Complete case with all entities and relationships
        """
        random.seed(seed)
        
        # Select entities
        persons = self._select_persons(n_suspects)
        locations = self._select_locations(6)  # Always 6 locations
        weapons = self._select_weapons(6)  # Always 6 weapons
        
        # Build relationships
        self._build_relationships(persons)
        
        # Select murderer and victim
        victim = random.choice(persons)
        murderer = random.choice([p for p in persons if p.id != victim.id])
        
        # Generate timeline
        timeline = self._generate_timeline(persons, locations, weapons, victim, murderer, difficulty)
        
        # Generate murder details
        murder = self._generate_murder(murderer, victim, timeline, weapons)
        
        # Generate clues
        clues = self._generate_clues(timeline, murder, difficulty)
        
        # Build truth matrix
        truth_matrix = self._build_truth_matrix(timeline, persons, locations, weapons)
        
        # Create case
        case = Case(
            seed=seed,
            difficulty=difficulty,
            victim=victim.id,
            suspects=[p.id for p in persons if p.id != victim.id],
            locations=[loc.id for loc in locations],
            weapons=[weapon.id for weapon in weapons],
            timeline=timeline,
            truth_matrix=truth_matrix,
            murder=murder,
            clues=clues,
            persons=persons,
            location_objects=locations,
            weapon_objects=weapons
        )
        
        # Validate case
        is_valid, issues = self.validate_case(case)
        if not is_valid:
            print(f"Generated case has issues: {issues[:2]}...")
            # Try to generate a simpler case
            return self._generate_simple_case(seed, difficulty, n_suspects)
        
        return case
    
    def _select_persons(self, n_suspects: int) -> List[Person]:
        """Select persons for the case."""
        selected_templates = random.sample(self.person_templates, n_suspects + 1)  # +1 for victim
        
        persons = []
        for i, template in enumerate(selected_templates):
            person = Person(
                id=PersonId(f"person_{i}"),
                name=template["name"],
                persona=template["persona"],
                lying_bias=random.uniform(0.2, 0.8),
                reliability=random.uniform(0.3, 0.9)
            )
            persons.append(person)
        
        return persons
    
    def _select_locations(self, n_locations: int) -> List[Location]:
        """Select locations for the case."""
        selected_templates = random.sample(self.location_templates, n_locations)
        
        locations = []
        for i, template in enumerate(selected_templates):
            location = Location(
                id=LocationId(f"location_{i}"),
                name=template["name"],
                description=template["description"]
            )
            locations.append(location)
        
        # Add connections between locations
        for location in locations:
            connected = random.sample([loc.id for loc in locations if loc.id != location.id], 
                                    random.randint(2, 4))
            location.connected_locations = set(connected)
        
        return locations
    
    def _select_weapons(self, n_weapons: int) -> List[Weapon]:
        """Select weapons for the case."""
        selected_templates = random.sample(self.weapon_templates, n_weapons)
        
        weapons = []
        for i, template in enumerate(selected_templates):
            weapon = Weapon(
                id=WeaponId(f"weapon_{i}"),
                name=template["name"],
                description=template["description"],
                is_murder_weapon=template["is_murder_weapon"]
            )
            weapons.append(weapon)
        
        return weapons
    
    def _build_relationships(self, persons: List[Person]):
        """Build relationships between persons."""
        for i, person1 in enumerate(persons):
            for j, person2 in enumerate(persons[i+1:], i+1):
                if random.random() < 0.7:  # 70% chance of having a relationship
                    relationship_type = random.choice(list(RelationshipType))
                    strength = random.uniform(0.1, 1.0)
                    
                    relationship = {
                        "person1": person1.id,
                        "person2": person2.id,
                        "relationship_type": relationship_type,
                        "strength": strength,
                        "description": f"{relationship_type.value} relationship"
                    }
                    
                    person1.relationships[person2.id] = relationship
                    person2.relationships[person1.id] = relationship
    
    def _generate_timeline(self, persons: List[Person], locations: List[Location], 
                          weapons: List[Weapon], victim: Person, murderer: Person, 
                          difficulty: Difficulty) -> List[Event]:
        """Generate a coherent timeline of events."""
        timeline = []
        base_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)  # 6 PM
        
        # Pre-murder events (2-4 hours before)
        pre_murder_hours = {"easy": 2, "medium": 3, "hard": 4}[difficulty.value]
        
        for hour in range(pre_murder_hours):
            time = base_time + timedelta(hours=hour)
            
            # Generate 2-4 events per hour
            n_events = random.randint(2, 4)
            for _ in range(n_events):
                event = self._generate_random_event(persons, locations, weapons, time, victim, murderer)
                if event:
                    timeline.append(event)
        
        # Murder event
        murder_time = base_time + timedelta(hours=pre_murder_hours)
        murder_location = random.choice(locations)
        murder_weapon = random.choice(weapons)
        
        murder_event = Event(
            id=EventId("event_murder"),
            time=murder_time,
            actor=murderer.id,
            action="committed murder",
            location=murder_location.id,
            objects=[murder_weapon.id],
            description=f"{murderer.name} murdered {victim.name} in the {murder_location.name}",
            is_crime=True
        )
        timeline.append(murder_event)
        
        # Post-murder events (1-2 hours after)
        post_murder_hours = {"easy": 1, "medium": 1, "hard": 2}[difficulty.value]
        
        for hour in range(post_murder_hours):
            time = murder_time + timedelta(hours=hour + 1)
            
            # Generate 1-3 events per hour
            n_events = random.randint(1, 3)
            for _ in range(n_events):
                event = self._generate_random_event(persons, locations, weapons, time, victim, murderer)
                if event:
                    timeline.append(event)
        
        # Sort timeline by time
        timeline.sort(key=lambda e: e.time)
        
        return timeline
    
    def _generate_random_event(self, persons: List[Person], locations: List[Location], 
                              weapons: List[Weapon], time: datetime, victim: Person, 
                              murderer: Person) -> Optional[Event]:
        """Generate a random event for the timeline."""
        actor = random.choice(persons)
        location = random.choice(locations)
        
        # Don't have victim in events after murder time
        if actor.id == victim.id and time > datetime.now():
            return None
        
        # Event types
        event_types = [
            ("was reading", []),
            ("was cooking", []),
            ("was cleaning", []),
            ("was sleeping", []),
            ("was working", []),
            ("was exercising", []),
            ("was gardening", []),
            ("was shopping", []),
            ("was visiting", []),
            ("was using", random.choice(weapons).id),
            ("was carrying", random.choice(weapons).id)
        ]
        
        action, obj = random.choice(event_types)
        objects = [obj] if obj else []
        
        event = Event(
            id=EventId(f"event_{len(persons)}_{time.hour}_{time.minute}"),
            time=time,
            actor=actor.id,
            action=action,
            location=location.id,
            objects=objects,
            description=f"{actor.name} was {action} in the {location.name}"
        )
        
        return event
    
    def _generate_murder(self, murderer: Person, victim: Person, timeline: List[Event], 
                        weapons: List[Weapon]) -> Murder:
        """Generate murder details."""
        # Find murder event
        murder_event = next(event for event in timeline if event.is_crime)
        
        # Select murder weapon
        murder_weapon = random.choice(weapons)
        murder_weapon.is_murder_weapon = True
        
        # Select motive
        motive = random.choice(self.motive_templates)
        
        return Murder(
            murderer=murderer.id,
            time=murder_event.time,
            location=murder_event.location,
            weapon=murder_weapon.id,
            motive=motive,
            method="murder"
        )
    
    def _generate_clues(self, timeline: List[Event], murder: Murder, difficulty: Difficulty) -> List[Clue]:
        """Generate clues based on the timeline and murder."""
        clues = []
        
        # Physical clues
        n_physical_clues = {"easy": 3, "medium": 4, "hard": 5}[difficulty.value]
        for i in range(n_physical_clues):
            clue = Clue(
                clue_type="physical",
                origin=f"Found at crime scene",
                reliability_prior=random.uniform(0.7, 0.95),
                description=f"Physical evidence #{i+1}",
                discovered=False
            )
            clues.append(clue)
        
        # Testimonial clues
        n_testimonial_clues = {"easy": 2, "medium": 3, "hard": 4}[difficulty.value]
        for i in range(n_testimonial_clues):
            clue = Clue(
                clue_type="testimonial",
                origin="Witness testimony",
                reliability_prior=random.uniform(0.5, 0.8),
                description=f"Witness statement #{i+1}",
                discovered=False
            )
            clues.append(clue)
        
        # Digital clues
        n_digital_clues = {"easy": 1, "medium": 2, "hard": 3}[difficulty.value]
        for i in range(n_digital_clues):
            clue = Clue(
                clue_type="digital",
                origin="Digital records",
                reliability_prior=random.uniform(0.8, 0.95),
                description=f"Digital evidence #{i+1}",
                discovered=False
            )
            clues.append(clue)
        
        return clues
    
    def _build_truth_matrix(self, timeline: List[Event], persons: List[Person], 
                           locations: List[Location], weapons: List[Weapon]) -> Dict[str, Fact]:
        """Build the truth matrix from the timeline."""
        truth_matrix = {}
        
        for event in timeline:
            # Location facts
            location_fact = Fact(
                subject=event.actor,
                predicate="was_at",
                object=event.location,
                time=event.time,
                certainty=1.0
            )
            truth_matrix[FactId(location_fact.id)] = location_fact
            
            # Action facts
            action_fact = Fact(
                subject=event.actor,
                predicate="did",
                object=event.action,
                time=event.time,
                certainty=1.0
            )
            truth_matrix[FactId(action_fact.id)] = action_fact
            
            # Object interaction facts
            for obj in event.objects:
                obj_fact = Fact(
                    subject=event.actor,
                    predicate="interacted_with",
                    object=obj,
                    time=event.time,
                    certainty=1.0
                )
                truth_matrix[FactId(obj_fact.id)] = obj_fact
        
        return truth_matrix
    
    def validate_case(self, case: Case) -> Tuple[bool, List[str]]:
        """
        Validate that a generated case is coherent and solvable.
        
        Args:
            case: The case to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check that there's exactly one murderer
        if case.murder.murderer not in case.suspects:
            issues.append("Murderer is not in suspects list")
        
        # Check that victim is not in suspects
        if case.victim in case.suspects:
            issues.append("Victim is in suspects list")
        
        # Check timeline consistency
        for i, event1 in enumerate(case.timeline):
            for event2 in case.timeline[i+1:]:
                if (event1.actor == event2.actor and 
                    event1.location != event2.location and
                    abs(event1.time - event2.time) < timedelta(minutes=30)):
                    issues.append(f"Temporal conflict: {event1.actor} cannot be in two places at once")
        
        # Check that murder event exists
        murder_events = [e for e in case.timeline if e.is_crime]
        if len(murder_events) != 1:
            issues.append("Must have exactly one murder event")
        
        # Check that there are enough clues
        if len(case.clues) < 3:
            issues.append("Not enough clues for a solvable case")
        
        return len(issues) == 0, issues
    
    def _generate_simple_case(self, seed: int, difficulty: Difficulty, n_suspects: int) -> Case:
        """Generate a simple, guaranteed valid case."""
        random.seed(seed + 999)  # Different seed for simple case
        
        # Select entities
        persons = self._select_persons(n_suspects)
        locations = self._select_locations(6)
        weapons = self._select_weapons(6)
        
        # Build relationships
        self._build_relationships(persons)
        
        # Select victim and murderer
        victim = random.choice(persons)
        murderer = random.choice([p for p in persons if p.id != victim.id])
        
        # Set flags
        victim.is_victim = True
        murderer.is_murderer = True
        
        # Generate simple timeline with no conflicts
        timeline = []
        base_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        
        # Pre-murder events (spread out)
        for i, person in enumerate(persons):
            if person.id != victim.id:
                time = base_time + timedelta(hours=i, minutes=random.randint(0, 30))
                location = random.choice(locations)
                event = Event(
                    id=EventId(f"event_pre_{i}"),
                    time=time,
                    actor=person.id,
                    action="was present",
                    location=location.id,
                    objects=[],
                    description=f"{person.name} was in the {location.name}"
                )
                timeline.append(event)
        
        # Murder event
        murder_time = base_time + timedelta(hours=len(persons))
        murder_location = random.choice(locations)
        murder_weapon = random.choice(weapons)
        
        murder_event = Event(
            id=EventId("event_murder"),
            time=murder_time,
            actor=murderer.id,
            action="committed murder",
            location=murder_location.id,
            objects=[murder_weapon.id],
            description=f"{murderer.name} murdered {victim.name} in the {murder_location.name}",
            is_crime=True
        )
        timeline.append(murder_event)
        
        # Generate murder details
        murder = Murder(
            victim=victim.id,
            murderer=murderer.id,
            location=murder_location.id,
            weapon=murder_weapon.id,
            time=murder_time,
            motive=random.choice(self.motive_templates)
        )
        
        # Generate simple clues
        clues = []
        for i in range(3):
            clue = Clue(
                clue_type="physical",
                origin="Crime scene",
                reliability_prior=random.uniform(0.7, 0.9),
                description=f"Physical evidence #{i+1}",
                discovered=False
            )
            clues.append(clue)
        
        # Build truth matrix
        truth_matrix = self._build_truth_matrix(timeline, persons, locations, weapons)
        
        # Create case
        case = Case(
            seed=seed,
            difficulty=difficulty,
            victim=victim.id,
            suspects=[p.id for p in persons if p.id != victim.id],
            locations=[loc.id for loc in locations],
            weapons=[weapon.id for weapon in weapons],
            timeline=timeline,
            truth_matrix=truth_matrix,
            murder=murder,
            clues=clues,
            persons=persons,
            location_objects=locations,
            weapon_objects=weapons
        )
        
        return case
