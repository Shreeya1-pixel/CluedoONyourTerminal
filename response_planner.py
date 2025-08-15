"""
Response Planner module for the murder mystery game.
Coordinates between knowledge base, lie model, and NLP pipeline to generate coherent responses.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from models import (
    PersonId, Fact, TruthStatus, Claim, ClaimId, DialogueTurn, 
    Case, PlannedAnswer
)
from knowledge_base import KnowledgeBase
from lie_model import LieModel
from nlp_pipeline import NLPPipeline
from surface_realizer import SurfaceRealizer
import logging

logger = logging.getLogger(__name__)





class ResponsePlanner:
    """
    Plans responses by coordinating between knowledge base, lie model, and NLP pipeline.
    Implements the core response generation logic.
    """
    
    def __init__(self, case: Case, knowledge_base: KnowledgeBase, lie_model: LieModel, nlp_pipeline: NLPPipeline):
        self.case = case
        self.kb = knowledge_base
        self.lie_model = lie_model
        self.nlp_pipeline = nlp_pipeline
        self.surface_realizer = SurfaceRealizer()
    
    def plan_response(self, speaker_id: PersonId, intent: str, params: Dict[str, Any], game_state: Dict[str, Any]) -> PlannedAnswer:
        """
        Plan a response for a suspect based on the intent and parameters.
        
        Args:
            speaker_id: ID of the suspect responding
            intent: Classified intent of the question
            params: Query parameters
            game_state: Current game state
            
        Returns:
            Planned answer with fact, mode, and context
        """
        # Get the truth from knowledge base
        truth_fact = self.kb.query(speaker_id, intent, params)
        
        # Build context for lie model
        context = {
            "speaker": speaker_id,
            "question_type": intent,
            "params": params,
            "truth_fact": truth_fact,
            "game_state": game_state
        }
        
        # Decide whether to lie, tell truth, or evade
        decision = self.lie_model.decide(context)
        mode = decision["mode"]
        
        # Plan the response based on the decision
        if mode == TruthStatus.TRUE:
            planned = self._plan_truthful_response(truth_fact, context)
        elif mode == TruthStatus.LIE:
            planned = self._plan_lie_response(truth_fact, context)
        elif mode == TruthStatus.EVASION:
            planned = self._plan_evasion_response(context)
        else:
            planned = self._plan_omission_response(context)
        
        # Add context information
        planned.context = context
        planned.confidence = decision["score"]
        
        return planned
    
    def _plan_truthful_response(self, truth_fact: Optional[Fact], context: Dict[str, Any]) -> PlannedAnswer:
        """Plan a truthful response."""
        if truth_fact is None:
            # No information available
            return PlannedAnswer(
                fact=None,
                mode=TruthStatus.TRUE,
                confidence=1.0,
                context=context
            )
        
        # Check for contradictions with existing claims
        contradictions = self.kb.find_contradictions(truth_fact)
        
        return PlannedAnswer(
            fact=truth_fact,
            mode=TruthStatus.TRUE,
            confidence=truth_fact.certainty,
            context=context
        )
    
    def _plan_lie_response(self, truth_fact: Optional[Fact], context: Dict[str, Any]) -> PlannedAnswer:
        """Plan a lie response."""
        # Sample an alternative fact
        alternative_fact = self.lie_model.sample_alternative(context, truth_fact)
        
        if alternative_fact is None:
            # Fall back to evasion if no plausible alternative
            return self._plan_evasion_response(context)
        
        # Check if the alternative is consistent
        is_consistent, violations = self.kb.check_consistency(alternative_fact)
        
        if not is_consistent:
            # Try to find a different alternative
            for _ in range(3):  # Try up to 3 times
                alternative_fact = self.lie_model.sample_alternative(context, truth_fact)
                if alternative_fact:
                    is_consistent, violations = self.kb.check_consistency(alternative_fact)
                    if is_consistent:
                        break
            
            if not is_consistent:
                # Fall back to evasion
                return self._plan_evasion_response(context)
        
        return PlannedAnswer(
            fact=alternative_fact,
            mode=TruthStatus.LIE,
            confidence=alternative_fact.certainty,
            context=context
        )
    
    def _plan_evasion_response(self, context: Dict[str, Any]) -> PlannedAnswer:
        """Plan an evasion response."""
        # Create a generic evasion fact
        evasion_fact = Fact(
            subject=context["speaker"],
            predicate="evades",
            object="question",
            time=datetime.now(),
            certainty=0.8
        )
        
        return PlannedAnswer(
            fact=evasion_fact,
            mode=TruthStatus.EVASION,
            confidence=0.8,
            context=context
        )
    
    def _plan_omission_response(self, context: Dict[str, Any]) -> PlannedAnswer:
        """Plan an omission response."""
        # Create a generic omission fact
        omission_fact = Fact(
            subject=context["speaker"],
            predicate="omits",
            object="information",
            time=datetime.now(),
            certainty=0.7
        )
        
        return PlannedAnswer(
            fact=omission_fact,
            mode=TruthStatus.OMISSION,
            confidence=0.7,
            context=context
        )
    
    def generate_response(self, planned_answer: PlannedAnswer, speaker_id: PersonId) -> Tuple[str, Claim]:
        """
        Generate the final response text and create a claim record.
        
        Args:
            planned_answer: The planned answer
            speaker_id: ID of the responding suspect
            
        Returns:
            Tuple of (response_text, claim_record)
        """
        # Generate the response text
        response_text = self.surface_realizer.realize(planned_answer, speaker_id)
        
        # Create a claim record
        claim = self._create_claim(planned_answer, speaker_id)
        
        return response_text, claim
    
    def _create_claim(self, planned_answer: PlannedAnswer, speaker_id: PersonId) -> Claim:
        """Create a claim record for the response."""
        # Find contradictions and corroborations
        contradictions = []
        corroborations = []
        
        if planned_answer.fact:
            # Check against existing claims
            for existing_claim in self.case.claims.values():
                if existing_claim.speaker != speaker_id:  # Don't compare with self
                    if self._claims_contradict(planned_answer.fact, existing_claim.proposition):
                        contradictions.append(existing_claim.id)
                    elif self._claims_corroborate(planned_answer.fact, existing_claim.proposition):
                        corroborations.append(existing_claim.id)
        
        # Create justification
        justification = self._create_justification(planned_answer, contradictions, corroborations)
        
        claim = Claim(
            speaker=speaker_id,
            proposition=planned_answer.fact or Fact(
                subject=speaker_id,
                predicate="responded",
                object="to_question",
                time=datetime.now(),
                certainty=planned_answer.confidence
            ),
            time_of_claim=datetime.now(),
            truth_status=planned_answer.mode,
            confidence=planned_answer.confidence,
            justification=justification,
            contradictions=contradictions,
            corroborations=corroborations
        )
        
        return claim
    
    def _claims_contradict(self, fact1: Fact, fact2: Fact) -> bool:
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
    
    def _claims_corroborate(self, fact1: Fact, fact2: Fact) -> bool:
        """Check if two facts corroborate each other."""
        # Same fact
        if (fact1.subject == fact2.subject and 
            fact1.predicate == fact2.predicate and 
            fact1.object == fact2.object and 
            fact1.time == fact2.time):
            return True
        
        # Witness corroboration
        if (fact1.predicate == "saw" and 
            fact2.predicate == "was_at" and
            fact1.object == fact2.subject and
            fact1.time == fact2.time):
            return True
        
        return False
    
    def _create_justification(self, planned_answer: PlannedAnswer, contradictions: List[ClaimId], corroborations: List[ClaimId]) -> str:
        """Create a justification for the claim."""
        justification_parts = []
        
        if planned_answer.mode == TruthStatus.TRUE:
            justification_parts.append("Truthful response based on knowledge")
        elif planned_answer.mode == TruthStatus.LIE:
            justification_parts.append("Deceptive response to avoid incrimination")
        elif planned_answer.mode == TruthStatus.EVASION:
            justification_parts.append("Evaded the question")
        elif planned_answer.mode == TruthStatus.OMISSION:
            justification_parts.append("Omitted relevant information")
        
        if contradictions:
            justification_parts.append(f"Contradicts {len(contradictions)} previous claims")
        
        if corroborations:
            justification_parts.append(f"Corroborated by {len(corroborations)} previous claims")
        
        return "; ".join(justification_parts)
    
    def process_player_input(self, text: str, current_suspect: PersonId, game_state: Dict[str, Any]) -> Tuple[str, Claim, Dict[str, Any]]:
        """
        Process player input and generate a suspect response.
        
        Args:
            text: Player's input text
            current_suspect: Currently interrogated suspect
            game_state: Current game state
            
        Returns:
            Tuple of (response_text, claim_record, processing_info)
        """
        # Process the input
        processing_result = self.nlp_pipeline.process_input(text, current_suspect)
        
        # Validate input
        is_valid, error_msg = self.nlp_pipeline.validate_input(text)
        if not is_valid:
            return error_msg, None, processing_result
        
        # Plan the response
        planned_answer = self.plan_response(
            current_suspect,
            processing_result["intent"],
            processing_result["params"],
            game_state
        )
        
        # Generate the response
        response_text, claim = self.generate_response(planned_answer, current_suspect)
        
        return response_text, claim, processing_result
    
    def get_response_insights(self, claim: Claim) -> Dict[str, Any]:
        """
        Get insights about a response for the player.
        
        Args:
            claim: The claim to analyze
            
        Returns:
            Dictionary with insights about the response
        """
        insights = {
            "reliability": claim.confidence,
            "truth_status": claim.truth_status.value,
            "contradictions": len(claim.contradictions),
            "corroborations": len(claim.corroborations),
            "justification": claim.justification
        }
        
        # Add specific insights based on contradictions
        if claim.contradictions:
            insights["contradiction_details"] = [
                {
                    "claim_id": claim_id,
                    "speaker": self.case.claims[claim_id].speaker,
                    "proposition": self.case.claims[claim_id].proposition.object
                }
                for claim_id in claim.contradictions
            ]
        
        return insights
