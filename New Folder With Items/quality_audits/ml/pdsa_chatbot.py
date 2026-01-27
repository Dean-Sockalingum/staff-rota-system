"""
PDSA AI Chatbot
Conversational AI assistant for PDSA guidance using local LLM
"""

from typing import Dict, List, Optional
from datetime import datetime
import json


class PDSAChatbot:
    """
    AI chatbot for PDSA guidance using local LLM.
    Provides context-aware assistance for each phase of PDSA cycle.
    """
    
    def __init__(self):
        """Initialize the PDSA chatbot"""
        self.conversation_history = []
        self.llm = None
        self._initialized = False
    
    def _lazy_load(self):
        """Lazy load llama.cpp model"""
        if not self._initialized:
            try:
                from llama_cpp import Llama
                
                # In production, download a small model like TinyLlama or Phi-2
                # For now, use GPT-2 via transformers as fallback
                print("Initializing chatbot LLM...")
                
                # Note: In production, load actual llama.cpp model:
                # self.llm = Llama(model_path="models/tinyllama-1.1b.gguf")
                
                # Fallback to transformers for development
                from transformers import AutoTokenizer, AutoModelForCausalLM
                self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
                self.model = AutoModelForCausalLM.from_pretrained("gpt2")
                
                self._initialized = True
                print("Chatbot ready")
            except Exception as e:
                print(f"Error loading chatbot model: {e}")
                self._initialized = False
    
    def ask(
        self,
        question: str,
        project_context: Optional[Dict] = None,
        cycle_context: Optional[Dict] = None,
        phase: str = 'general'
    ) -> Dict[str, any]:
        """
        Ask the chatbot a question with PDSA context.
        
        Args:
            question: User's question
            project_context: Dict with project details (title, aim, category, etc.)
            cycle_context: Dict with current cycle details (phase, change, etc.)
            phase: Current PDSA phase ('plan', 'do', 'study', 'act', or 'general')
            
        Returns:
            Dictionary with:
                - answer: Chatbot's response
                - confidence: Confidence score 0-1
                - sources: Relevant guidance sources
                - follow_up_suggestions: Suggested next questions
        """
        self._lazy_load()
        
        if not self._initialized:
            return self._get_fallback_response(question, phase)
        
        # Build context-aware prompt
        prompt = self._build_contextual_prompt(
            question,
            project_context,
            cycle_context,
            phase
        )
        
        # Generate response
        response = self._generate_response(prompt)
        
        # Extract answer and confidence
        answer = response.get('text', '')
        confidence = response.get('confidence', 0.7)
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'answer': answer,
            'phase': phase,
            'project': project_context.get('title') if project_context else None
        })
        
        # Get follow-up suggestions based on phase
        follow_ups = self._get_follow_up_suggestions(phase, question)
        
        return {
            'answer': answer,
            'confidence': confidence,
            'sources': self._get_relevant_sources(phase),
            'follow_up_suggestions': follow_ups,
            'timestamp': datetime.now().isoformat()
        }
    
    def _build_contextual_prompt(
        self,
        question: str,
        project_ctx: Optional[Dict],
        cycle_ctx: Optional[Dict],
        phase: str
    ) -> str:
        """Build context-aware prompt for LLM"""
        
        # Base system prompt
        system_prompt = """You are a PDSA (Plan-Do-Study-Act) improvement expert assistant for healthcare settings.
Provide concise, actionable guidance based on IHI Model for Improvement and NHS Quality Improvement principles.
"""
        
        # Add phase-specific guidance
        phase_prompts = {
            'plan': """PLAN Phase: Help with setting aims, forming hypotheses, and planning tests of change.
Key questions: What are we trying to accomplish? How will we know a change is an improvement? What changes can we make?""",
            
            'do': """DO Phase: Guide implementation of small-scale tests.
Focus on: Carrying out the test, documenting problems and unexpected observations, beginning data analysis.""",
            
            'study': """STUDY Phase: Help analyze data and compare to predictions.
Focus on: Complete data analysis, compare results to predictions, summarize and reflect on what was learned.""",
            
            'act': """ACT Phase: Guide decisions about next steps.
Focus on: Decide whether to adopt, adapt, or abandon the change. Plan next cycle if continuing."""
        }
        
        context_parts = [system_prompt]
        
        # Add phase context
        if phase in phase_prompts:
            context_parts.append(phase_prompts[phase])
        
        # Add project context
        if project_ctx:
            project_info = f"""
Current Project: {project_ctx.get('title', 'Unnamed')}
Aim: {project_ctx.get('aim', 'Not specified')}
Category: {project_ctx.get('category', 'General')}
"""
            context_parts.append(project_info)
        
        # Add cycle context
        if cycle_ctx:
            cycle_info = f"""
Current Cycle: #{cycle_ctx.get('cycle_number', 1)}
Change Being Tested: {cycle_ctx.get('change_description', 'Not specified')}
"""
            context_parts.append(cycle_info)
        
        # Build final prompt
        full_prompt = "\n\n".join(context_parts)
        full_prompt += f"\n\nUser Question: {question}\n\nAssistant Response:"
        
        return full_prompt
    
    def _generate_response(self, prompt: str) -> Dict[str, any]:
        """Generate response using LLM"""
        try:
            # Use transformers as fallback
            import torch
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=300,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract response (after prompt)
            response_text = generated[len(self.tokenizer.decode(inputs[0], skip_special_tokens=True)):]
            response_text = response_text.strip()
            
            # Clean up response
            if '\n' in response_text:
                # Take first substantial paragraph
                paragraphs = [p.strip() for p in response_text.split('\n') if p.strip()]
                response_text = paragraphs[0] if paragraphs else response_text
            
            return {
                'text': response_text,
                'confidence': 0.75
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                'text': "I apologize, but I'm having trouble generating a response. Please try rephrasing your question.",
                'confidence': 0.0
            }
    
    def _get_fallback_response(self, question: str, phase: str) -> Dict[str, any]:
        """Provide fallback response when LLM not available"""
        
        # Simple keyword-based responses
        question_lower = question.lower()
        
        responses = {
            'smart': "A SMART aim is: Specific (clear who/what), Measurable (numeric target), Achievable (realistic), Relevant (addresses problem), Time-bound (deadline). Example: 'Reduce medication errors by 50% in Ward A within 12 weeks'.",
            
            'hypothesis': "A change hypothesis states what you think will happen. Format: 'We believe that [change] will result in [outcome] for [population].' Be specific about the mechanism.",
            
            'measure': "Use 3 types of measures: Outcome (did it improve?), Process (was change implemented?), Balancing (any negative effects?). Track weekly for sensitive change detection.",
            
            'sample': "Start with small samples - test on 1 patient, 1 day, 1 unit first. Small tests reduce risk and allow quick learning before scaling up.",
            
            'control': "Control charts show variation over time. Points outside limits or patterns indicate special causes requiring investigation. Stable process = common cause variation.",
            
            'ramp': "After successful test, use ramp strategy: Pilot → Implement → Spread → Sustain. Don't skip steps. Monitor for sustainability."
        }
        
        # Check for keyword matches
        for keyword, response in responses.items():
            if keyword in question_lower:
                return {
                    'answer': response,
                    'confidence': 0.8,
                    'sources': self._get_relevant_sources(phase),
                    'follow_up_suggestions': self._get_follow_up_suggestions(phase, question)
                }
        
        # Default response
        return {
            'answer': "I can help with PDSA methodology. Try asking about: SMART aims, change hypotheses, measurement strategies, control charts, or scaling successful changes.",
            'confidence': 0.6,
            'sources': self._get_relevant_sources('general'),
            'follow_up_suggestions': [
                "How do I write a SMART aim?",
                "What makes a good change hypothesis?",
                "How many data points do I need?"
            ]
        }
    
    def _get_relevant_sources(self, phase: str) -> List[Dict[str, str]]:
        """Get relevant guidance sources for current phase"""
        
        base_sources = [
            {
                'title': 'The Improvement Guide (IHI)',
                'url': 'http://www.ihi.org/resources/Pages/HowtoImprove/default.aspx',
                'relevance': 'Core PDSA methodology'
            },
            {
                'title': 'NHS Scotland QI Hub',
                'url': 'https://learn.nes.nhs.scot/qihub',
                'relevance': 'UK healthcare QI resources'
            }
        ]
        
        phase_sources = {
            'plan': [{
                'title': 'Writing SMART Aims',
                'url': 'http://www.ihi.org/resources/Pages/Tools/Quality-Improvement-Essentials-Toolkit.aspx',
                'relevance': 'Aim statement development'
            }],
            'study': [{
                'title': 'Run Charts and Control Charts',
                'url': 'https://www.england.nhs.uk/improvement-hub/wp-content/uploads/sites/44/2017/11/Statistical-Process-Control-Guidance.pdf',
                'relevance': 'Data analysis for QI'
            }],
            'act': [{
                'title': 'Scaling Up Improvement',
                'url': 'http://www.ihi.org/resources/Pages/IHIWhitePapers/ScalingUpImprovementWhitePaper.aspx',
                'relevance': 'Spreading successful changes'
            }]
        }
        
        sources = base_sources.copy()
        if phase in phase_sources:
            sources.extend(phase_sources[phase])
        
        return sources
    
    def _get_follow_up_suggestions(self, phase: str, question: str) -> List[str]:
        """Generate relevant follow-up question suggestions"""
        
        suggestions_by_phase = {
            'plan': [
                "How do I write a good SMART aim?",
                "What's the difference between outcome and process measures?",
                "How large should my initial test be?",
                "What makes a strong change hypothesis?"
            ],
            'do': [
                "How do I document unexpected events during testing?",
                "Should I stop if the test isn't going as planned?",
                "How do I collect data during implementation?"
            ],
            'study': [
                "How many data points do I need for analysis?",
                "What do control limits tell me?",
                "How do I know if the change is working?",
                "When is variation significant?"
            ],
            'act': [
                "Should I continue, modify, or abandon this change?",
                "How do I scale up a successful test?",
                "What's the difference between adopt and adapt?",
                "How do I sustain improvements long-term?"
            ],
            'general': [
                "How do I get started with PDSA?",
                "What are the most common PDSA mistakes?",
                "How long should a PDSA cycle take?",
                "How do I engage staff in improvement work?"
            ]
        }
        
        return suggestions_by_phase.get(phase, suggestions_by_phase['general'])[:3]
    
    def get_conversation_history(self) -> List[Dict]:
        """Return conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def export_conversation(self) -> str:
        """Export conversation history as JSON"""
        return json.dumps(self.conversation_history, indent=2)
