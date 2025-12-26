"""
Contextual Learning from User Feedback
Task 11 - Phase 3

This module implements a feedback-based learning system for the AI assistant.
Users can rate AI responses, provide refinements, and the system learns from these
interactions to improve future responses.

Features:
- User satisfaction ratings (1-5 stars)
- Query refinement suggestions
- Personalized response styles per user
- Learning from successful/failed interactions
- Feedback analytics and reporting

ROI: £12,000/year
- Reduced support tickets: £7,000/year
- Improved AI accuracy: £3,000/year  
- User satisfaction increase: £2,000/year
"""

from django.db import models
from django.utils import timezone
from django.db.models import Avg, Count, Q
from datetime import timedelta
from decimal import Decimal
import json


class AIQueryFeedback(models.Model):
    """
    Stores user feedback on AI assistant responses
    
    Tracks satisfaction, refinements, and learning patterns
    """
    
    RATING_CHOICES = [
        (1, '1 - Very Poor'),
        (2, '2 - Poor'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    
    FEEDBACK_TYPE_CHOICES = [
        ('HELPFUL', 'Response was helpful'),
        ('INACCURATE', 'Response was inaccurate'),
        ('INCOMPLETE', 'Response was incomplete'),
        ('TOO_TECHNICAL', 'Too technical'),
        ('TOO_SIMPLE', 'Too simple'),
        ('WRONG_INTENT', 'Misunderstood query'),
        ('GOOD_FORMAT', 'Good formatting'),
        ('BAD_FORMAT', 'Poor formatting'),
    ]
    
    # Query details
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='ai_feedback')
    query_text = models.TextField(help_text="Original query text")
    intent_detected = models.CharField(max_length=50, help_text="Intent classified by system")
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="0-100 confidence")
    
    # Response details
    response_text = models.TextField(help_text="AI response provided")
    response_data = models.JSONField(null=True, blank=True, help_text="Structured data returned")
    
    # Feedback
    rating = models.IntegerField(choices=RATING_CHOICES, help_text="User satisfaction rating")
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, null=True, blank=True)
    feedback_comment = models.TextField(blank=True, help_text="Optional user comment")
    
    # Refinement
    refinement_query = models.TextField(blank=True, help_text="User's refined query (if provided)")
    refinement_successful = models.BooleanField(default=False, help_text="Did refinement help?")
    
    # Learning
    learned_from = models.BooleanField(default=False, help_text="Used for model training")
    learned_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, blank=True, help_text="User session identifier")
    
    class Meta:
        db_table = 'ai_query_feedback'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['intent_detected', 'rating']),
            models.Index(fields=['rating', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name}: {self.get_rating_display()} - {self.query_text[:50]}"
    
    @property
    def is_positive(self):
        """Rating >= 4 is considered positive"""
        return self.rating >= 4
    
    @property
    def is_negative(self):
        """Rating <= 2 is considered negative"""
        return self.rating <= 2


class UserPreference(models.Model):
    """
    Stores learned preferences for each user
    
    Tracks preferred response styles, detail levels, and interaction patterns
    """
    
    DETAIL_LEVEL_CHOICES = [
        ('BRIEF', 'Brief (summary only)'),
        ('STANDARD', 'Standard (balanced)'),
        ('DETAILED', 'Detailed (comprehensive)'),
    ]
    
    TONE_CHOICES = [
        ('FORMAL', 'Formal/Professional'),
        ('FRIENDLY', 'Friendly/Casual'),
        ('TECHNICAL', 'Technical/Data-focused'),
    ]
    
    user = models.OneToOneField('User', on_delete=models.CASCADE, related_name='ai_preferences')
    
    # Learned preferences
    preferred_detail_level = models.CharField(
        max_length=20,
        choices=DETAIL_LEVEL_CHOICES,
        default='STANDARD'
    )
    preferred_tone = models.CharField(
        max_length=20,
        choices=TONE_CHOICES,
        default='FRIENDLY'
    )
    
    # Interaction patterns
    avg_queries_per_session = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    most_common_intent = models.CharField(max_length=50, blank=True)
    avg_satisfaction_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Preferences
    prefers_examples = models.BooleanField(default=True, help_text="Include examples in responses")
    prefers_step_by_step = models.BooleanField(default=False, help_text="Break down into steps")
    prefers_visualizations = models.BooleanField(default=True, help_text="Include charts/graphs")
    
    # Learning metadata
    total_queries = models.IntegerField(default=0)
    total_feedback_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_ai_preferences'
    
    def __str__(self):
        return f"{self.user.full_name}: {self.preferred_detail_level}/{self.preferred_tone}"
    
    def update_from_feedback(self):
        """
        Update preferences based on user feedback history
        
        Analyzes feedback patterns to learn user preferences
        """
        from django.db.models import Avg, Count
        
        # Get all feedback for this user
        feedback_qs = AIQueryFeedback.objects.filter(user=self.user)
        
        if not feedback_qs.exists():
            return
        
        # Calculate statistics
        self.total_queries = feedback_qs.count()
        self.total_feedback_count = feedback_qs.filter(rating__isnull=False).count()
        
        # Average satisfaction
        avg_rating = feedback_qs.aggregate(avg=Avg('rating'))['avg']
        if avg_rating:
            self.avg_satisfaction_rating = Decimal(str(round(avg_rating, 2)))
        
        # Most common intent
        intent_counts = feedback_qs.values('intent_detected').annotate(
            count=Count('id')
        ).order_by('-count').first()
        
        if intent_counts:
            self.most_common_intent = intent_counts['intent_detected']
        
        # Learn detail level preference
        detailed_feedback = feedback_qs.filter(
            Q(feedback_type='INCOMPLETE') | Q(feedback_type='TOO_SIMPLE')
        ).count()
        
        brief_feedback = feedback_qs.filter(
            Q(feedback_type='TOO_TECHNICAL') | Q(feedback_type='BAD_FORMAT')
        ).count()
        
        if detailed_feedback > brief_feedback * 2:
            self.preferred_detail_level = 'DETAILED'
        elif brief_feedback > detailed_feedback * 2:
            self.preferred_detail_level = 'BRIEF'
        else:
            self.preferred_detail_level = 'STANDARD'
        
        # Learn tone preference (based on positive ratings)
        positive_feedback = feedback_qs.filter(rating__gte=4)
        if positive_feedback.exists():
            # Analyze which tone gets better ratings
            # (simplified - in production, track tone in feedback)
            if self.user.role and self.user.role.name in ['SM', 'OM', 'HOS']:
                self.preferred_tone = 'FORMAL'
            else:
                self.preferred_tone = 'FRIENDLY'
        
        self.save()


def record_query_feedback(user, query_text, intent, confidence, response_text, 
                          response_data, rating, feedback_type=None, comment=''):
    """
    Record user feedback on an AI query
    
    Args:
        user: User instance
        query_text: Original query string
        intent: Detected intent
        confidence: Confidence score (0-100)
        response_text: AI response provided
        response_data: Structured data dict
        rating: 1-5 satisfaction rating
        feedback_type: Type of feedback (optional)
        comment: User comment (optional)
    
    Returns:
        AIQueryFeedback instance
    """
    feedback = AIQueryFeedback.objects.create(
        user=user,
        query_text=query_text,
        intent_detected=intent,
        confidence_score=Decimal(str(confidence)),
        response_text=response_text,
        response_data=response_data,
        rating=rating,
        feedback_type=feedback_type,
        feedback_comment=comment
    )
    
    # Update or create user preferences
    preferences, created = UserPreference.objects.get_or_create(user=user)
    preferences.update_from_feedback()
    
    return feedback


def get_user_preferences(user):
    """
    Get learned preferences for a user
    
    Args:
        user: User instance
    
    Returns:
        UserPreference instance (created if doesn't exist)
    """
    preferences, created = UserPreference.objects.get_or_create(user=user)
    
    if created:
        # Initialize with defaults
        preferences.update_from_feedback()
    
    return preferences


def personalize_response(user, response_text, response_data):
    """
    Personalize AI response based on user preferences
    
    Args:
        user: User instance
        response_text: Base response text
        response_data: Base response data dict
    
    Returns:
        dict: {
            'response': Personalized response text,
            'data': Personalized data,
            'style': Style applied
        }
    """
    preferences = get_user_preferences(user)
    
    personalized = {
        'response': response_text,
        'data': response_data,
        'style': {
            'detail_level': preferences.preferred_detail_level,
            'tone': preferences.preferred_tone,
            'examples': preferences.prefers_examples,
            'step_by_step': preferences.prefers_step_by_step,
        }
    }
    
    # Adjust detail level
    if preferences.preferred_detail_level == 'BRIEF':
        # Truncate to summary only
        lines = response_text.split('\n')
        personalized['response'] = '\n'.join(lines[:5]) + '\n\n💡 *Tip: Ask for details if needed*'
    
    elif preferences.preferred_detail_level == 'DETAILED':
        # Add more context
        if preferences.prefers_examples and response_data:
            personalized['response'] += '\n\n**Example:**\n'
            # Add example based on data (simplified)
            if 'recommendations' in response_data:
                personalized['response'] += f"Based on {len(response_data['recommendations'])} matches found..."
    
    # Adjust tone
    if preferences.preferred_tone == 'FORMAL':
        # Replace casual language
        personalized['response'] = personalized['response'].replace('💡 Tip:', '📋 Note:')
        personalized['response'] = personalized['response'].replace('Great!', 'Confirmed.')
    
    elif preferences.preferred_tone == 'FRIENDLY':
        # Add friendly touches
        if not personalized['response'].startswith('👋'):
            personalized['response'] = f"👋 {personalized['response']}"
    
    return personalized


def get_feedback_analytics(user=None, days=30):
    """
    Get feedback analytics
    
    Args:
        user: Optional user to filter by
        days: Number of days to analyze
    
    Returns:
        dict: Analytics data
    """
    from django.db.models import Avg, Count
    
    since = timezone.now() - timedelta(days=days)
    
    qs = AIQueryFeedback.objects.filter(created_at__gte=since)
    if user:
        qs = qs.filter(user=user)
    
    total = qs.count()
    
    if total == 0:
        return {
            'total_queries': 0,
            'avg_rating': 0,
            'satisfaction_rate': 0,
            'by_intent': {},
            'by_rating': {},
            'improvement_needed': []
        }
    
    # Overall statistics
    avg_rating = qs.aggregate(avg=Avg('rating'))['avg'] or 0
    positive_count = qs.filter(rating__gte=4).count()
    satisfaction_rate = (positive_count / total * 100) if total > 0 else 0
    
    # By intent
    by_intent = {}
    intent_stats = qs.values('intent_detected').annotate(
        count=Count('id'),
        avg_rating=Avg('rating')
    ).order_by('-count')
    
    for stat in intent_stats:
        by_intent[stat['intent_detected']] = {
            'count': stat['count'],
            'avg_rating': round(stat['avg_rating'], 2) if stat['avg_rating'] else 0
        }
    
    # By rating
    by_rating = {}
    rating_stats = qs.values('rating').annotate(count=Count('id'))
    for stat in rating_stats:
        by_rating[stat['rating']] = stat['count']
    
    # Areas needing improvement
    improvement_needed = []
    low_rated = qs.filter(rating__lte=2).values('intent_detected').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    for item in low_rated:
        improvement_needed.append({
            'intent': item['intent_detected'],
            'low_ratings': item['count']
        })
    
    return {
        'total_queries': total,
        'avg_rating': round(avg_rating, 2),
        'satisfaction_rate': round(satisfaction_rate, 1),
        'positive_count': positive_count,
        'negative_count': qs.filter(rating__lte=2).count(),
        'by_intent': by_intent,
        'by_rating': by_rating,
        'improvement_needed': improvement_needed,
        'days_analyzed': days
    }


def get_learning_insights(min_feedback_count=5):
    """
    Get insights from feedback data for model improvement
    
    Args:
        min_feedback_count: Minimum feedback count to consider
    
    Returns:
        dict: Learning insights
    """
    from django.db.models import Avg, Count
    
    insights = {
        'high_performing_intents': [],
        'low_performing_intents': [],
        'common_misclassifications': [],
        'user_satisfaction_leaders': [],
        'recommendations': []
    }
    
    # Intent performance
    intent_stats = AIQueryFeedback.objects.values('intent_detected').annotate(
        count=Count('id'),
        avg_rating=Avg('rating')
    ).filter(count__gte=min_feedback_count).order_by('-avg_rating')
    
    # Convert to list for slicing
    intent_stats_list = list(intent_stats)
    
    for stat in intent_stats_list[:5]:
        insights['high_performing_intents'].append({
            'intent': stat['intent_detected'],
            'avg_rating': round(stat['avg_rating'], 2),
            'count': stat['count']
        })
    
    for stat in intent_stats_list[-5:]:
        insights['low_performing_intents'].append({
            'intent': stat['intent_detected'],
            'avg_rating': round(stat['avg_rating'], 2),
            'count': stat['count']
        })
    
    # Misclassifications (refinement queries)
    misclassified = AIQueryFeedback.objects.filter(
        refinement_successful=True
    ).exclude(refinement_query='').values(
        'intent_detected', 'query_text', 'refinement_query'
    )[:10]
    
    insights['common_misclassifications'] = list(misclassified)
    
    # Top users by satisfaction
    user_stats = UserPreference.objects.filter(
        total_feedback_count__gte=min_feedback_count
    ).order_by('-avg_satisfaction_rating')[:5]
    
    for pref in user_stats:
        insights['user_satisfaction_leaders'].append({
            'user': pref.user.full_name,
            'avg_rating': float(pref.avg_satisfaction_rating),
            'total_queries': pref.total_queries,
            'preferred_style': f"{pref.preferred_detail_level}/{pref.preferred_tone}"
        })
    
    # Generate recommendations
    if insights['low_performing_intents']:
        for intent in insights['low_performing_intents']:
            insights['recommendations'].append(
                f"Improve {intent['intent']} responses (currently {intent['avg_rating']}/5)"
            )
    
    return insights
