"""
Hypothesis Suggester
Uses embeddings and semantic similarity to suggest change ideas from successful past cycles
"""

from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from django.db.models import Q


class HypothesisSuggester:
    """
    Suggest change hypotheses based on similarity to successful past PDSA cycles.
    Uses sentence embeddings for semantic matching.
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize hypothesis suggester.
        
        Args:
            model_name: Sentence transformer model name
                       'all-MiniLM-L6-v2' is lightweight and fast (80MB)
        """
        self.model_name = model_name
        self.model = None
        self._initialized = False
    
    def _lazy_load(self):
        """Lazy load the sentence transformer model"""
        if not self._initialized:
            print(f"Loading sentence transformer model {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            self._initialized = True
            print("Model loaded successfully")
    
    def suggest_hypotheses(
        self,
        problem_description: str,
        category: str = None,
        top_n: int = 5
    ) -> List[Dict[str, any]]:
        """
        Suggest change hypotheses based on similar successful projects.
        
        Args:
            problem_description: Description of current problem
            category: Project category to filter by
            top_n: Number of suggestions to return
            
        Returns:
            List of dictionaries with:
                - hypothesis: Suggested change idea
                - similarity_score: 0-1 similarity score
                - source_project: Title of source project
                - outcome: What happened when tried before
                - success_rate: Historical success metric
        """
        self._lazy_load()
        
        # Import here to avoid circular imports
        from quality_audits.models import PDSACycle, PDSAProject
        
        # Get successful past cycles
        successful_cycles = PDSACycle.objects.filter(
            act_decision='continue'  # Continued means it worked
        ).select_related('project')
        
        if category:
            successful_cycles = successful_cycles.filter(project__category=category)
        
        if not successful_cycles.exists():
            return self._get_default_hypotheses(category)
        
        # Encode the problem description
        problem_embedding = self.model.encode(problem_description)
        
        # Calculate similarities
        suggestions = []
        for cycle in successful_cycles:
            # Create hypothesis text from cycle
            hypothesis_text = f"{cycle.plan_change_description}"
            if cycle.study_results_summary:
                hypothesis_text += f" Result: {cycle.study_results_summary}"
            
            # Encode hypothesis
            hypothesis_embedding = self.model.encode(hypothesis_text)
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(problem_embedding, hypothesis_embedding)
            
            # Build suggestion
            suggestions.append({
                'hypothesis': cycle.plan_change_description,
                'similarity_score': round(float(similarity), 3),
                'source_project': cycle.project.title,
                'outcome': cycle.study_results_summary or "Positive outcome achieved",
                'category': cycle.project.category,
                'success_metric': cycle.study_target_achieved
            })
        
        # Sort by similarity and return top N
        suggestions.sort(key=lambda x: x['similarity_score'], reverse=True)
        return suggestions[:top_n]
    
    def _cosine_similarity(self, vec1, vec2) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)
    
    def _get_default_hypotheses(self, category: str = None) -> List[Dict[str, any]]:
        """
        Return default evidence-based hypotheses when no history available.
        Based on IHI and NHS improvement science.
        """
        defaults = {
            'medication': [
                {
                    'hypothesis': 'Implement double-check system for high-risk medications',
                    'similarity_score': 0.0,
                    'source_project': 'IHI Best Practice',
                    'outcome': 'Reduces medication errors by 50-70%',
                    'category': 'medication'
                },
                {
                    'hypothesis': 'Use color-coded medication administration times',
                    'similarity_score': 0.0,
                    'source_project': 'IHI Best Practice',
                    'outcome': 'Improves timing accuracy and reduces missed doses',
                    'category': 'medication'
                }
            ],
            'falls': [
                {
                    'hypothesis': 'Implement hourly intentional rounding',
                    'similarity_score': 0.0,
                    'source_project': 'Studer Group Evidence',
                    'outcome': 'Reduces falls by 30-50%',
                    'category': 'falls'
                },
                {
                    'hypothesis': 'Use non-slip footwear and bed alarms for high-risk residents',
                    'similarity_score': 0.0,
                    'source_project': 'NHS Scotland Practice',
                    'outcome': 'Significant reduction in falls-related injuries',
                    'category': 'falls'
                }
            ],
            'infection_control': [
                {
                    'hypothesis': 'Implement visual hand hygiene reminders at all entry points',
                    'similarity_score': 0.0,
                    'source_project': 'WHO Guidelines',
                    'outcome': 'Increases hand hygiene compliance by 20-40%',
                    'category': 'infection_control'
                }
            ],
            'nutrition': [
                {
                    'hypothesis': 'Introduce protected mealtimes with no interruptions',
                    'similarity_score': 0.0,
                    'source_project': 'Age UK Research',
                    'outcome': 'Improves food intake and resident satisfaction',
                    'category': 'nutrition'
                }
            ],
            'staffing': [
                {
                    'hypothesis': 'Implement daily safety huddles at shift start',
                    'similarity_score': 0.0,
                    'source_project': 'IHI Framework',
                    'outcome': 'Improves communication and reduces errors',
                    'category': 'staffing'
                }
            ]
        }
        
        # Return category-specific defaults or general ones
        if category and category in defaults:
            return defaults[category]
        
        # Return mix of all categories
        all_defaults = []
        for hypotheses in defaults.values():
            all_defaults.extend(hypotheses[:2])  # 2 from each category
        return all_defaults[:5]
    
    def enrich_hypothesis(self, hypothesis: str) -> Dict[str, any]:
        """
        Enrich a hypothesis with evidence-based implementation guidance.
        
        Args:
            hypothesis: The change idea to enrich
            
        Returns:
            Dictionary with implementation details
        """
        self._lazy_load()
        
        # Use embeddings to find evidence-based resources
        hypothesis_embedding = self.model.encode(hypothesis)
        
        # Placeholder for evidence library (could be built out)
        return {
            'hypothesis': hypothesis,
            'implementation_steps': [
                'Define clear success criteria',
                'Identify team members and roles',
                'Plan small-scale test',
                'Collect baseline data',
                'Implement change'
            ],
            'measurement_suggestions': [
                'Process measure: Compliance with new process',
                'Outcome measure: Change in target metric',
                'Balancing measure: Unintended consequences'
            ],
            'potential_barriers': [
                'Staff resistance to change',
                'Resource constraints',
                'Time limitations'
            ],
            'mitigation_strategies': [
                'Involve staff in planning',
                'Start with willing participants',
                'Provide adequate training and support'
            ]
        }
