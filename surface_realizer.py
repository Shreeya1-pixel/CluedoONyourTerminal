"""
Surface Realizer module for the murder mystery game.
Converts planned answers into natural language responses using templates and contextual information.
"""

import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from models import PersonId, Fact, TruthStatus, Case, PlannedAnswer
import logging

logger = logging.getLogger(__name__)


class SurfaceRealizer:
    """
    Converts planned answers into natural language responses.
    Uses templates and contextual information to generate varied, natural-sounding responses.
    """
    
    def __init__(self):
        # Response templates organized by intent and truth status
        self.templates = {
            "where_were_you": {
                TruthStatus.TRUE: [
                    "I was at {location}.",
                    "I was in the {location} at that time.",
                    "I remember being in the {location}.",
                    "I was definitely at {location}.",
                    "I can confirm I was in the {location}."
                ],
                TruthStatus.LIE: [
                    "I was at {location}.",
                    "I was in the {location} at that time.",
                    "I remember being in the {location}.",
                    "I was definitely at {location}.",
                    "I can confirm I was in the {location}."
                ],
                TruthStatus.EVASION: [
                    "I don't really remember where I was exactly.",
                    "It's hard to say for certain where I was.",
                    "I might have been in several places.",
                    "I'm not entirely sure about my location.",
                    "That's a bit unclear to me right now."
                ],
                TruthStatus.OMISSION: [
                    "I was around.",
                    "I was in the house somewhere.",
                    "I don't want to get into specifics.",
                    "I was here and there.",
                    "I'd rather not say exactly where."
                ]
            },
            "what_did_you_do": {
                TruthStatus.TRUE: [
                    "I was {action}.",
                    "I was busy {action}.",
                    "I remember {action} at that time.",
                    "I was definitely {action}.",
                    "I can confirm I was {action}."
                ],
                TruthStatus.LIE: [
                    "I was {action}.",
                    "I was busy {action}.",
                    "I remember {action} at that time.",
                    "I was definitely {action}.",
                    "I can confirm I was {action}."
                ],
                TruthStatus.EVASION: [
                    "I was just doing regular things.",
                    "Nothing out of the ordinary.",
                    "I was keeping myself busy.",
                    "I don't really remember what I was doing.",
                    "Just normal activities, I suppose."
                ],
                TruthStatus.OMISSION: [
                    "I was occupied.",
                    "I had things to do.",
                    "I was busy with various tasks.",
                    "I was doing some work.",
                    "I was handling some matters."
                ]
            },
            "who_saw_you": {
                TruthStatus.TRUE: [
                    "I think {witness} saw me.",
                    "I believe {witness} was there.",
                    "I remember seeing {witness}.",
                    "I'm pretty sure {witness} saw me.",
                    "I think {witness} can confirm I was there."
                ],
                TruthStatus.LIE: [
                    "I think {witness} saw me.",
                    "I believe {witness} was there.",
                    "I remember seeing {witness}.",
                    "I'm pretty sure {witness} saw me.",
                    "I think {witness} can confirm I was there."
                ],
                TruthStatus.EVASION: [
                    "I'm not sure who might have seen me.",
                    "I don't really remember who was around.",
                    "It's hard to say who noticed me.",
                    "I wasn't really paying attention to who was watching.",
                    "I don't know if anyone saw me."
                ],
                TruthStatus.OMISSION: [
                    "I was alone most of the time.",
                    "I don't think anyone was paying attention to me.",
                    "I was keeping to myself.",
                    "I wasn't really socializing.",
                    "I was focused on my own activities."
                ]
            },
            "what_weapon": {
                TruthStatus.TRUE: [
                    "I had access to the {weapon}.",
                    "I was using the {weapon} earlier.",
                    "I remember handling the {weapon}.",
                    "I had the {weapon} with me.",
                    "I was working with the {weapon}."
                ],
                TruthStatus.LIE: [
                    "I had access to the {weapon}.",
                    "I was using the {weapon} earlier.",
                    "I remember handling the {weapon}.",
                    "I had the {weapon} with me.",
                    "I was working with the {weapon}."
                ],
                TruthStatus.EVASION: [
                    "I don't really remember what I had access to.",
                    "I'm not sure about weapons or tools.",
                    "I don't want to discuss what I might have used.",
                    "I'm not comfortable talking about that.",
                    "I'd rather not get into details about tools or weapons."
                ],
                TruthStatus.OMISSION: [
                    "I had some things with me.",
                    "I was carrying various items.",
                    "I had tools for my work.",
                    "I had some equipment.",
                    "I was prepared with necessary items."
                ]
            },
            "alibi_check": {
                TruthStatus.TRUE: [
                    "I can prove I was at {location}.",
                    "I have witnesses who saw me at {location}.",
                    "I was definitely at {location}, I can prove it.",
                    "I have evidence I was at {location}.",
                    "I can confirm my alibi with witnesses."
                ],
                TruthStatus.LIE: [
                    "I can prove I was at {location}.",
                    "I have witnesses who saw me at {location}.",
                    "I was definitely at {location}, I can prove it.",
                    "I have evidence I was at {location}.",
                    "I can confirm my alibi with witnesses."
                ],
                TruthStatus.EVASION: [
                    "I'm not sure how to prove where I was.",
                    "I don't really have a solid alibi.",
                    "It's hard to prove where I was exactly.",
                    "I don't have witnesses for my whereabouts.",
                    "I'm not sure I can prove my alibi."
                ],
                TruthStatus.OMISSION: [
                    "I was around, but I don't have proof.",
                    "I was in the area, but no one saw me.",
                    "I was here and there, but I can't prove it.",
                    "I was busy, but I don't have witnesses.",
                    "I was occupied, but I can't verify my location."
                ]
            },
            "small_talk": {
                TruthStatus.TRUE: [
                    "Hello there.",
                    "Hi, how are you?",
                    "Good to see you.",
                    "Hello, what can I help you with?",
                    "Hi, is there something you need?"
                ],
                TruthStatus.LIE: [
                    "Hello there.",
                    "Hi, how are you?",
                    "Good to see you.",
                    "Hello, what can I help you with?",
                    "Hi, is there something you need?"
                ],
                TruthStatus.EVASION: [
                    "Hello.",
                    "Hi.",
                    "Yes?",
                    "What is it?",
                    "Can I help you?"
                ],
                TruthStatus.OMISSION: [
                    "Hello.",
                    "Hi.",
                    "Yes?",
                    "What is it?",
                    "Can I help you?"
                ]
            }
        }
        
        # Emotional modifiers based on truth status
        self.emotional_modifiers = {
            TruthStatus.TRUE: [
                "confidently", "clearly", "definitely", "certainly", "surely"
            ],
            TruthStatus.LIE: [
                "hesitantly", "uncertainly", "vaguely", "nervously", "carefully"
            ],
            TruthStatus.EVASION: [
                "evasively", "uncomfortably", "nervously", "hesitantly", "carefully"
            ],
            TruthStatus.OMISSION: [
                "briefly", "shortly", "minimally", "carefully", "guardedly"
            ]
        }
    
    def realize(self, planned_answer: PlannedAnswer, speaker_id: PersonId) -> str:
        """
        Convert a planned answer into natural language.
        
        Args:
            planned_answer: The planned answer to realize
            speaker_id: ID of the speaking suspect
            
        Returns:
            Natural language response
        """
        if not planned_answer.fact:
            return self._generate_no_information_response(planned_answer.mode)
        
        # Determine the intent from the fact
        intent = self._determine_intent(planned_answer.fact)
        
        # Get appropriate templates
        templates = self.templates.get(intent, {}).get(planned_answer.mode, ["I don't know."])
        
        # Select a random template
        template = random.choice(templates)
        
        # Fill in the template
        response = self._fill_template(template, planned_answer.fact, speaker_id)
        
        # Add emotional modifier if appropriate
        if planned_answer.mode in self.emotional_modifiers:
            modifier = random.choice(self.emotional_modifiers[planned_answer.mode])
            response = f"{response} ({modifier})"
        
        return response
    
    def _determine_intent(self, fact: Fact) -> str:
        """Determine the intent from a fact."""
        if fact.predicate == "was_at":
            return "where_were_you"
        elif fact.predicate == "did":
            return "what_did_you_do"
        elif fact.predicate == "saw":
            return "who_saw_you"
        elif fact.predicate == "interacted_with":
            return "what_weapon"
        elif fact.predicate == "has_alibi":
            return "alibi_check"
        elif fact.predicate in ["evades", "omits"]:
            return "evasion"
        else:
            return "unknown"
    
    def _fill_template(self, template: str, fact: Fact, speaker_id: PersonId) -> str:
        """Fill in a template with fact information."""
        # Replace location placeholders
        if "{location}" in template:
            template = template.replace("{location}", fact.object)
        
        # Replace action placeholders
        if "{action}" in template:
            template = template.replace("{action}", fact.object)
        
        # Replace weapon placeholders
        if "{weapon}" in template:
            template = template.replace("{weapon}", fact.object)
        
        # Replace witness placeholders
        if "{witness}" in template:
            template = template.replace("{witness}", fact.subject)
        
        return template
    
    def _generate_no_information_response(self, mode: TruthStatus) -> str:
        """Generate a response when no information is available."""
        no_info_responses = {
            TruthStatus.TRUE: [
                "I don't remember.",
                "I'm not sure.",
                "I can't recall.",
                "I don't have that information.",
                "I'm not certain about that."
            ],
            TruthStatus.LIE: [
                "I don't remember.",
                "I'm not sure.",
                "I can't recall.",
                "I don't have that information.",
                "I'm not certain about that."
            ],
            TruthStatus.EVASION: [
                "I'd rather not discuss that.",
                "I don't want to get into that.",
                "That's not something I want to talk about.",
                "I'm not comfortable discussing that.",
                "I'd prefer not to answer that."
            ],
            TruthStatus.OMISSION: [
                "I don't have much to say about that.",
                "I'm not sure what to tell you.",
                "I don't have details about that.",
                "I can't provide information about that.",
                "I don't know what to say about that."
            ]
        }
        
        responses = no_info_responses.get(mode, ["I don't know."])
        return random.choice(responses)
    
    def generate_evasion_response(self, context: Dict[str, Any]) -> str:
        """Generate an evasion response when the suspect wants to avoid answering."""
        evasion_templates = [
            "I don't think that's relevant.",
            "Why do you need to know that?",
            "I'm not sure why you're asking.",
            "That's not important right now.",
            "I'd rather focus on other matters.",
            "I don't see how that helps.",
            "Can we talk about something else?",
            "I'm not comfortable with that question.",
            "I think you're asking the wrong questions.",
            "Let's discuss something more relevant."
        ]
        
        return random.choice(evasion_templates)
    
    def generate_omission_response(self, context: Dict[str, Any]) -> str:
        """Generate an omission response when the suspect wants to withhold information."""
        omission_templates = [
            "I don't have much to say about that.",
            "I'm not sure what to tell you.",
            "I don't have details about that.",
            "I can't provide information about that.",
            "I don't know what to say about that.",
            "That's not something I can discuss.",
            "I don't have the information you're looking for.",
            "I'm not the right person to ask about that.",
            "I don't have access to that information.",
            "I can't help you with that."
        ]
        
        return random.choice(omission_templates)
    
    def generate_accusation_response(self, accused_person: PersonId, confidence: float) -> str:
        """Generate a response when the player accuses someone."""
        if confidence > 0.8:
            templates = [
                "I think {person} is definitely guilty.",
                "I'm certain {person} did it.",
                "I have no doubt that {person} is the murderer.",
                "It has to be {person}.",
                "I'm convinced {person} is responsible."
            ]
        elif confidence > 0.5:
            templates = [
                "I suspect {person} might be involved.",
                "I think {person} could be guilty.",
                "I have my suspicions about {person}.",
                "I'm not sure, but {person} seems suspicious.",
                "I think {person} might be the one."
            ]
        else:
            templates = [
                "I'm not sure about {person}.",
                "I don't have enough evidence against {person}.",
                "I can't say for certain about {person}.",
                "I'm not convinced about {person}.",
                "I don't think {person} is necessarily guilty."
            ]
        
        template = random.choice(templates)
        return template.format(person=accused_person)
    
    def generate_insight_response(self, insight: Dict[str, Any]) -> str:
        """Generate a response that provides insight to the player."""
        if insight.get("contradictions", 0) > 0:
            return f"⚠️ This contradicts {insight['contradictions']} previous statements."
        elif insight.get("corroborations", 0) > 0:
            return f"✅ This corroborates {insight['corroborations']} previous statements."
        elif insight.get("reliability", 0) < 0.3:
            return "🤔 This person seems unreliable."
        elif insight.get("reliability", 0) > 0.8:
            return "👍 This person seems trustworthy."
        else:
            return "📝 New information recorded."
