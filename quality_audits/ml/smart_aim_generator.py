"""
SMART Aim Generator
Uses local LLM to generate well-formed SMART aims for PDSA projects
"""

import re
from typing import Dict, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


class SMARTAimGenerator:
    """
    Generate SMART (Specific, Measurable, Achievable, Relevant, Time-bound) aims
    for PDSA improvement projects using local LLM.
    """
    
    def __init__(self, model_name: str = "gpt2"):
        """
        Initialize the SMART aim generator.
        
        Args:
            model_name: HuggingFace model to use (gpt2, gpt2-medium, or gpt2-large)
                       Using GPT-2 as fallback for quick local generation
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._initialized = False
    
    def _lazy_load(self):
        """Lazy load the model to avoid startup delays"""
        if not self._initialized:
            print(f"Loading {self.model_name} model...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self._initialized = True
            print("Model loaded successfully")
    
    def generate_smart_aim(
        self,
        problem_description: str,
        baseline_value: Optional[float] = None,
        baseline_unit: str = "",
        target_value: Optional[float] = None,
        target_unit: str = "",
        target_population: str = "",
        timeframe_weeks: int = 12
    ) -> Dict[str, any]:
        """
        Generate a SMART aim statement based on problem description and parameters.
        
        Args:
            problem_description: Description of the quality issue
            baseline_value: Current measurement value
            baseline_unit: Unit of measurement
            target_value: Desired target value
            target_unit: Unit for target
            target_population: Who is affected
            timeframe_weeks: Timeline in weeks
            
        Returns:
            Dictionary with:
                - aim_statement: Generated SMART aim
                - smartness_score: Score 0-100
                - specific: Whether aim is specific (bool)
                - measurable: Whether aim is measurable (bool)
                - achievable: Whether aim is achievable (bool)
                - relevant: Whether aim is relevant (bool)
                - time_bound: Whether aim is time-bound (bool)
                - suggestions: List of improvement suggestions
        """
        self._lazy_load()
        
        # Build structured prompt
        prompt = self._build_prompt(
            problem_description,
            baseline_value,
            baseline_unit,
            target_value,
            target_unit,
            target_population,
            timeframe_weeks
        )
        
        # Generate aim using LLM
        generated_aim = self._generate_text(prompt)
        
        # Score the SMART-ness
        score_result = self._calculate_smartness_score(
            generated_aim,
            baseline_value,
            target_value,
            timeframe_weeks
        )
        
        return {
            'aim_statement': generated_aim,
            **score_result
        }
    
    def _build_prompt(
        self,
        problem: str,
        baseline: Optional[float],
        baseline_unit: str,
        target: Optional[float],
        target_unit: str,
        population: str,
        weeks: int
    ) -> str:
        """Build a structured prompt for aim generation"""
        
        # Calculate percentage improvement if we have values
        improvement = ""
        if baseline and target:
            pct = abs((target - baseline) / baseline * 100)
            direction = "increase" if target > baseline else "reduce"
            improvement = f"{direction} by {pct:.1f}%"
        
        prompt = f"""Generate a SMART aim statement for a quality improvement project:

Problem: {problem}
Current baseline: {baseline} {baseline_unit if baseline else 'Not specified'}
Target: {target} {target_unit if target else 'Not specified'}
Population: {population or 'All relevant staff/patients'}
Timeframe: {weeks} weeks

A SMART aim must be:
- Specific: Clear and unambiguous
- Measurable: Include numeric targets
- Achievable: Realistic given resources
- Relevant: Addresses the problem
- Time-bound: Has a clear deadline

SMART Aim Statement:"""
        
        return prompt
    
    def _generate_text(self, prompt: str, max_length: int = 150) -> str:
        """Generate text using the LLM"""
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        
        # Generate with controlled parameters
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the aim (after the prompt)
        aim = generated[len(self.tokenizer.decode(inputs[0], skip_special_tokens=True)):]
        
        # Clean up the aim
        aim = aim.strip()
        if '\n' in aim:
            aim = aim.split('\n')[0]  # Take first line
        
        return aim
    
    def _calculate_smartness_score(
        self,
        aim: str,
        baseline: Optional[float],
        target: Optional[float],
        weeks: int
    ) -> Dict[str, any]:
        """
        Calculate how SMART the aim is.
        
        Returns:
            Dictionary with SMART criteria scores and suggestions
        """
        suggestions = []
        
        # Specific: Contains clear action verbs and details
        specific_keywords = ['improve', 'reduce', 'increase', 'achieve', 'implement', 'establish']
        is_specific = any(keyword in aim.lower() for keyword in specific_keywords)
        if not is_specific:
            suggestions.append("Add a specific action verb (improve, reduce, increase, etc.)")
        
        # Measurable: Contains numbers or quantifiable metrics
        has_numbers = bool(re.search(r'\d+', aim))
        is_measurable = has_numbers or (baseline is not None and target is not None)
        if not is_measurable:
            suggestions.append("Include measurable numeric targets")
        
        # Achievable: Check if improvement is reasonable (< 50% change typically)
        is_achievable = True
        if baseline and target:
            change_pct = abs((target - baseline) / baseline * 100)
            if change_pct > 50:
                is_achievable = False
                suggestions.append(f"Target represents {change_pct:.1f}% change - ensure this is achievable")
        
        # Relevant: Contains care/quality related terms
        relevant_keywords = ['care', 'quality', 'safety', 'patient', 'resident', 'staff', 'service']
        is_relevant = any(keyword in aim.lower() for keyword in relevant_keywords)
        if not is_relevant:
            suggestions.append("Clarify relevance to care quality or patient outcomes")
        
        # Time-bound: Contains timeframe
        time_keywords = ['week', 'month', 'by', 'within', str(weeks)]
        is_time_bound = any(keyword in aim.lower() for keyword in time_keywords)
        if not is_time_bound:
            suggestions.append(f"Add timeframe (e.g., 'within {weeks} weeks')")
        
        # Calculate overall score
        score_components = [is_specific, is_measurable, is_achievable, is_relevant, is_time_bound]
        smartness_score = (sum(score_components) / len(score_components)) * 100
        
        return {
            'smartness_score': round(smartness_score, 1),
            'specific': is_specific,
            'measurable': is_measurable,
            'achievable': is_achievable,
            'relevant': is_relevant,
            'time_bound': is_time_bound,
            'suggestions': suggestions
        }
    
    def improve_aim(self, aim: str, score_result: Dict) -> str:
        """
        Take an existing aim and improve it based on SMART criteria gaps.
        
        Args:
            aim: Current aim statement
            score_result: Result from _calculate_smartness_score
            
        Returns:
            Improved aim statement
        """
        if score_result['smartness_score'] >= 80:
            return aim  # Already good enough
        
        # Build improvement prompt
        missing_criteria = []
        if not score_result['specific']:
            missing_criteria.append("more specific action")
        if not score_result['measurable']:
            missing_criteria.append("measurable targets")
        if not score_result['time_bound']:
            missing_criteria.append("timeframe")
        
        prompt = f"""Improve this aim to be more SMART by adding {', '.join(missing_criteria)}:

Current aim: {aim}

Improved SMART aim:"""
        
        improved = self._generate_text(prompt, max_length=120)
        return improved.strip()
