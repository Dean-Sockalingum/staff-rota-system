"""
PDSA Success Predictor
Machine learning model to predict project success probability
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Dict, List, Optional
from pathlib import Path


class PDSASuccessPredictor:
    """
    Predict likelihood of PDSA project success using Random Forest classifier.
    Trains on historical project data and provides probability + feature importance.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the success predictor.
        
        Args:
            model_path: Path to saved model file (if exists)
        """
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'smartness_score',
            'team_size',
            'improvement_magnitude',
            'category_encoded',
            'priority_encoded',
            'has_clear_hypothesis',
            'baseline_data_quality'
        ]
        self.model_path = model_path or self._get_default_model_path()
        self._load_or_initialize_model()
    
    def _get_default_model_path(self) -> str:
        """Get default path for model storage"""
        base_path = Path(__file__).parent.parent / 'ml_models'
        base_path.mkdir(exist_ok=True)
        return str(base_path / 'success_predictor.joblib')
    
    def _load_or_initialize_model(self):
        """Load existing model or initialize new one"""
        if os.path.exists(self.model_path):
            try:
                saved_data = joblib.load(self.model_path)
                self.model = saved_data['model']
                self.scaler = saved_data['scaler']
                print(f"Loaded trained model from {self.model_path}")
            except Exception as e:
                print(f"Error loading model: {e}. Initializing new model.")
                self._initialize_new_model()
        else:
            self._initialize_new_model()
    
    def _initialize_new_model(self):
        """Initialize a new Random Forest model"""
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
        print("Initialized new Random Forest model")
    
    def train_model(self, min_projects: int = 10) -> Dict[str, any]:
        """
        Train the model on historical PDSA projects.
        
        Args:
            min_projects: Minimum number of completed projects needed for training
            
        Returns:
            Training results with accuracy, feature importance, etc.
        """
        # Import here to avoid circular imports
        from quality_audits.models import PDSAProject
        
        # Get completed projects with outcomes
        projects = PDSAProject.objects.filter(
            status__in=['completed', 'closed']
        ).exclude(
            baseline_value__isnull=True
        ).exclude(
            target_value__isnull=True
        )
        
        if projects.count() < min_projects:
            return {
                'success': False,
                'message': f'Need at least {min_projects} completed projects for training. '
                          f'Currently have {projects.count()}.',
                'trained': False
            }
        
        # Extract features and labels
        X = []
        y = []
        
        for project in projects:
            features = self._extract_features(project)
            label = self._determine_success(project)
            X.append(features)
            y.append(label)
        
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        
        # Calculate feature importance
        importance = dict(zip(self.feature_names, self.model.feature_importances_))
        importance_sorted = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        
        # Save model
        self._save_model()
        
        # Calculate accuracy (on training data - in production use cross-validation)
        accuracy = self.model.score(X_scaled, y)
        
        return {
            'success': True,
            'trained': True,
            'n_projects': len(X),
            'accuracy': round(accuracy, 3),
            'feature_importance': [
                {'feature': name, 'importance': round(imp, 3)}
                for name, imp in importance_sorted
            ],
            'model_path': self.model_path
        }
    
    def predict_success(
        self,
        project_data: Dict[str, any],
        explain: bool = True
    ) -> Dict[str, any]:
        """
        Predict success probability for a PDSA project.
        
        Args:
            project_data: Dictionary with project features
            explain: Whether to include feature contributions
            
        Returns:
            Dictionary with:
                - success_probability: 0-1 probability
                - predicted_outcome: 'success' or 'needs_attention'
                - confidence: Model confidence
                - key_factors: Top factors affecting prediction
                - recommendations: Actionable suggestions
        """
        if self.model is None:
            return {
                'success_probability': 0.5,
                'predicted_outcome': 'unknown',
                'message': 'Model not trained yet'
            }
        
        # Extract features from project data
        features = self._extract_features_from_dict(project_data)
        features_array = np.array([features])
        
        # Scale features
        features_scaled = self.scaler.transform(features_array)
        
        # Predict probability
        probabilities = self.model.predict_proba(features_scaled)[0]
        success_prob = probabilities[1] if len(probabilities) > 1 else probabilities[0]
        
        # Determine outcome
        predicted_outcome = 'success' if success_prob >= 0.6 else 'needs_attention'
        
        # Calculate confidence
        confidence = max(probabilities)
        
        result = {
            'success_probability': round(float(success_prob), 3),
            'predicted_outcome': predicted_outcome,
            'confidence': round(float(confidence), 3)
        }
        
        if explain:
            # Get feature importance for this prediction
            feature_importance = self.model.feature_importances_
            feature_values = dict(zip(self.feature_names, features))
            
            # Sort features by importance
            importance_ranking = sorted(
                zip(self.feature_names, feature_importance, features),
                key=lambda x: x[1],
                reverse=True
            )
            
            result['key_factors'] = [
                {
                    'factor': self._humanize_feature_name(name),
                    'importance': round(imp, 3),
                    'value': val
                }
                for name, imp, val in importance_ranking[:5]
            ]
            
            # Generate recommendations
            result['recommendations'] = self._generate_recommendations(
                feature_values,
                success_prob
            )
        
        return result
    
    def _extract_features(self, project) -> List[float]:
        """Extract features from a PDSAProject instance"""
        from quality_audits.models import PDSATeamMember
        
        # SMART-ness score (0-100)
        smartness = project.ai_success_score or 50
        
        # Team size
        team_size = PDSATeamMember.objects.filter(project=project).count()
        
        # Improvement magnitude (percentage change from baseline to target)
        if project.baseline_value and project.target_value and project.baseline_value != 0:
            improvement_mag = abs((project.target_value - project.baseline_value) / 
                                 project.baseline_value * 100)
        else:
            improvement_mag = 20  # Default moderate improvement
        
        # Category encoding (simple numeric mapping)
        category_map = {
            'medication': 1, 'falls': 2, 'infection_control': 3,
            'nutrition': 4, 'staffing': 5, 'clinical_care': 6,
            'dignity_respect': 7, 'activities': 8, 'documentation': 9,
            'other': 10
        }
        category_encoded = category_map.get(project.category, 10)
        
        # Priority encoding
        priority_map = {'low': 1, 'medium': 2, 'high': 3, 'urgent': 4}
        priority_encoded = priority_map.get(project.priority, 2)
        
        # Has clear hypothesis (from description length as proxy)
        has_hypothesis = 1 if len(project.problem_description or '') > 50 else 0
        
        # Baseline data quality (has baseline value)
        baseline_quality = 1 if project.baseline_value is not None else 0
        
        return [
            smartness,
            team_size,
            improvement_mag,
            category_encoded,
            priority_encoded,
            has_hypothesis,
            baseline_quality
        ]
    
    def _extract_features_from_dict(self, data: Dict) -> List[float]:
        """Extract features from dictionary (for predictions on new projects)"""
        smartness = data.get('smartness_score', 50)
        team_size = data.get('team_size', 3)
        
        baseline = data.get('baseline_value', 10)
        target = data.get('target_value', 15)
        improvement_mag = abs((target - baseline) / baseline * 100) if baseline != 0 else 20
        
        category_map = {
            'medication': 1, 'falls': 2, 'infection_control': 3,
            'nutrition': 4, 'staffing': 5, 'clinical_care': 6,
            'dignity_respect': 7, 'activities': 8, 'documentation': 9,
            'other': 10
        }
        category_encoded = category_map.get(data.get('category'), 10)
        
        priority_map = {'low': 1, 'medium': 2, 'high': 3, 'urgent': 4}
        priority_encoded = priority_map.get(data.get('priority', 'medium'), 2)
        
        has_hypothesis = 1 if data.get('has_hypothesis', False) else 0
        baseline_quality = 1 if baseline is not None else 0
        
        return [
            smartness,
            team_size,
            improvement_mag,
            category_encoded,
            priority_encoded,
            has_hypothesis,
            baseline_quality
        ]
    
    def _determine_success(self, project) -> int:
        """
        Determine if a completed project was successful.
        1 = success, 0 = not successful
        """
        # Project is successful if:
        # 1. Status is completed (not abandoned)
        # 2. Has at least one cycle with 'continue' decision
        # 3. Moved towards target (if applicable)
        
        if project.status == 'abandoned':
            return 0
        
        # Check if any cycles succeeded
        from quality_audits.models import PDSACycle
        successful_cycles = PDSACycle.objects.filter(
            project=project,
            act_decision='continue'
        ).exists()
        
        if successful_cycles:
            return 1
        
        # If no explicit success, check if moved towards target
        if project.baseline_value and project.target_value:
            # Get latest data point
            from quality_audits.models import PDSADataPoint
            latest_data = PDSADataPoint.objects.filter(
                cycle__project=project
            ).order_by('-date').first()
            
            if latest_data:
                # Check if moving in right direction
                if project.target_value > project.baseline_value:
                    # Want increase
                    return 1 if latest_data.value > project.baseline_value else 0
                else:
                    # Want decrease
                    return 1 if latest_data.value < project.baseline_value else 0
        
        # Default: assume partial success if completed
        return 1 if project.status == 'completed' else 0
    
    def _humanize_feature_name(self, feature: str) -> str:
        """Convert feature name to human-readable form"""
        mapping = {
            'smartness_score': 'SMART Aim Quality',
            'team_size': 'Team Size',
            'improvement_magnitude': 'Improvement Target Ambition',
            'category_encoded': 'Project Category',
            'priority_encoded': 'Priority Level',
            'has_clear_hypothesis': 'Clear Change Hypothesis',
            'baseline_data_quality': 'Baseline Data Available'
        }
        return mapping.get(feature, feature.replace('_', ' ').title())
    
    def _generate_recommendations(
        self,
        features: Dict[str, float],
        success_prob: float
    ) -> List[str]:
        """Generate recommendations to improve success probability"""
        recommendations = []
        
        if success_prob < 0.6:
            recommendations.append(
                "⚠️ Project has lower predicted success - consider strengthening key factors"
            )
        
        if features.get('smartness_score', 50) < 70:
            recommendations.append(
                "Improve SMART aim clarity - ensure all SMART criteria are met"
            )
        
        if features.get('team_size', 3) < 2:
            recommendations.append(
                "Consider expanding team - collaborative projects tend to succeed more"
            )
        
        if features.get('improvement_magnitude', 20) > 40:
            recommendations.append(
                "Target improvement is ambitious - consider smaller incremental goals"
            )
        
        if features.get('has_clear_hypothesis') == 0:
            recommendations.append(
                "Develop a clear change hypothesis before starting"
            )
        
        if features.get('baseline_data_quality') == 0:
            recommendations.append(
                "Collect baseline data before implementing changes"
            )
        
        if success_prob >= 0.8:
            recommendations.append(
                "✅ Strong success indicators - proceed with confidence and monitor progress"
            )
        
        return recommendations
    
    def _save_model(self):
        """Save trained model and scaler to disk"""
        try:
            joblib.dump({
                'model': self.model,
                'scaler': self.scaler
            }, self.model_path)
            print(f"Model saved to {self.model_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
