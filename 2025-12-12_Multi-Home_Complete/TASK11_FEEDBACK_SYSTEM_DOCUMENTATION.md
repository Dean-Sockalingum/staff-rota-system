# Task 11: AI Assistant Feedback & Learning System - Documentation

## Overview

The AI Assistant Feedback & Learning System enables continuous improvement by learning from user interactions. The system collects feedback on AI responses, learns user preferences, and personalizes future responses.

**ROI Target:** £12,000/year through improved response quality and user satisfaction  
**Target Metric:** 80% user satisfaction rate

---

## 1. User Guide: Submitting Feedback

### How to Provide Feedback

After every AI assistant response, you'll see a feedback widget with a star rating system:

1. **Rate the Response (1-5 stars)**
   - ⭐ = Very unhelpful
   - ⭐⭐ = Somewhat unhelpful
   - ⭐⭐⭐ = Neutral
   - ⭐⭐⭐⭐ = Helpful
   - ⭐⭐⭐⭐⭐ = Very helpful

2. **Select Feedback Type** (optional but helpful)
   - ✅ **Helpful** - The response was exactly what you needed
   - ❌ **Inaccurate** - The information provided was incorrect
   - 📋 **Incomplete** - The response was missing important details
   - 🎓 **Too Technical** - The response used too much jargon
   - 📖 **Too Simple** - The response didn't provide enough depth
   - 🎯 **Wrong Intent** - The AI misunderstood what you were asking

3. **Add Comments** (optional)
   - Provide additional context about what worked or didn't work
   - Suggest improvements for future responses

4. **Submit**
   - Click "Submit Feedback"
   - You'll see a confirmation message
   - The widget will be disabled to prevent duplicate submissions

### What Happens to Your Feedback?

Your feedback helps the system learn your preferences:

- **Detail Level**: If you mark responses as "Too Technical", future responses will be briefer and use simpler language
- **Tone**: The system learns whether you prefer formal or friendly communication
- **Content Type**: The system tracks which types of queries you find most helpful
- **Response Quality**: Low-rated responses trigger improvements in that category

### Privacy

- Feedback is associated with your user account
- Only aggregated analytics are shown to senior staff
- Individual feedback comments are only visible to administrators
- Your feedback helps improve the system for everyone

---

## 2. Admin Guide: Viewing Analytics

### Accessing Feedback Analytics

**Option 1: Django Admin Interface**
1. Navigate to `/admin/scheduling/aiqueryfeedback/`
2. View all feedback submissions with filters
3. Filter by rating, feedback type, user, or date range

**Option 2: API Endpoints**
1. **Analytics API**: `GET /api/ai-assistant/analytics/`
2. **Insights API**: `GET /api/ai-assistant/insights/`

### Understanding Analytics

#### Overall Metrics

```json
{
  "total_queries": 245,
  "average_rating": 4.3,
  "satisfaction_rate": 82.4,
  "period": "last_30_days"
}
```

- **Total Queries**: Number of queries with feedback
- **Average Rating**: Mean star rating (1-5 scale)
- **Satisfaction Rate**: Percentage of 4+ star ratings
- **Period**: Time range for the data

#### Intent-Based Analytics

```json
{
  "by_intent": {
    "STAFF_AVAILABILITY": {
      "count": 45,
      "avg_rating": 4.7,
      "satisfaction_rate": 91.1
    },
    "LEAVE_BALANCE": {
      "count": 38,
      "avg_rating": 3.2,
      "satisfaction_rate": 47.4
    }
  }
}
```

This shows which types of queries are performing well and which need improvement.

#### Low-Performing Queries

```json
{
  "improvement_needed": [
    {
      "intent": "LEAVE_BALANCE",
      "avg_rating": 3.2,
      "count": 38
    }
  ]
}
```

Queries with average ratings below 3.5 are flagged for improvement.

### Custom Date Ranges

Add query parameters to the analytics API:

```
GET /api/ai-assistant/analytics/?start_date=2025-01-01&end_date=2025-01-31
```

### Insights API (Senior Staff Only)

The Insights API provides actionable recommendations:

```json
{
  "high_performing": [
    {
      "intent": "STAFF_AVAILABILITY",
      "avg_rating": 4.7,
      "count": 45
    }
  ],
  "low_performing": [
    {
      "intent": "LEAVE_BALANCE",
      "avg_rating": 3.2,
      "count": 38
    }
  ],
  "recommendations": [
    "Improve LEAVE_BALANCE responses (currently 3.2/5)",
    "Expand COMPLIANCE_CHECK responses (currently 3.4/5)"
  ]
}
```

**Use insights to:**
- Identify which query types need attention
- Prioritize improvements based on usage + low ratings
- Track improvement over time

---

## 3. API Documentation

### Submit Feedback

**Endpoint:** `POST /api/ai-assistant/feedback/`

**Authentication:** Required (logged-in users)

**Request Body:**
```json
{
  "query_text": "Who can work tomorrow?",
  "intent_detected": "STAFF_AVAILABILITY",
  "confidence_score": 95,
  "response_text": "3 staff members can work tomorrow: Alice, Bob, Carol",
  "response_data": {"count": 3, "staff": ["Alice", "Bob", "Carol"]},
  "rating": 5,
  "feedback_type": "HELPFUL",
  "feedback_comment": "Exactly what I needed!"
}
```

**Required Fields:**
- `query_text` (string): The original question asked
- `response_text` (string): The AI's response
- `rating` (integer 1-5): Star rating

**Optional Fields:**
- `intent_detected` (string): The detected query intent
- `confidence_score` (integer 0-100): AI confidence level
- `response_data` (object): Structured response data
- `feedback_type` (string): One of HELPFUL, INACCURATE, INCOMPLETE, TOO_TECHNICAL, TOO_SIMPLE, WRONG_INTENT
- `feedback_comment` (string): Additional comments

**Response:**
```json
{
  "status": "success",
  "feedback_id": 123,
  "preferences_updated": true
}
```

**Status Codes:**
- `201 Created`: Feedback successfully recorded
- `400 Bad Request`: Missing required fields or invalid rating
- `401 Unauthorized`: User not logged in

### Get Analytics

**Endpoint:** `GET /api/ai-assistant/analytics/`

**Authentication:** Required

**Query Parameters:**
- `start_date` (optional): Filter from this date (YYYY-MM-DD)
- `end_date` (optional): Filter to this date (YYYY-MM-DD)
- `period` (optional): Predefined period (last_7_days, last_30_days, last_90_days)

**Response:**
```json
{
  "total_queries": 245,
  "average_rating": 4.3,
  "satisfaction_rate": 82.4,
  "by_intent": {
    "STAFF_AVAILABILITY": {
      "count": 45,
      "avg_rating": 4.7,
      "satisfaction_rate": 91.1
    }
  },
  "improvement_needed": [
    {
      "intent": "LEAVE_BALANCE",
      "avg_rating": 3.2,
      "count": 38
    }
  ],
  "period": "last_30_days"
}
```

### Get Insights

**Endpoint:** `GET /api/ai-assistant/insights/`

**Authentication:** Required (Senior Staff or Admin only)

**Response:**
```json
{
  "high_performing": [...],
  "low_performing": [...],
  "recommendations": [
    "Improve LEAVE_BALANCE responses (currently 3.2/5)"
  ]
}
```

**Status Codes:**
- `200 OK`: Insights generated successfully
- `401 Unauthorized`: User not logged in
- `403 Forbidden`: User is not Senior Staff or Admin

---

## 4. Technical Implementation

### Database Models

#### AIQueryFeedback
Stores individual feedback submissions.

**Fields:**
- `user` (ForeignKey): User who submitted feedback
- `query_text` (TextField): Original query
- `intent_detected` (CharField): Detected intent
- `confidence_score` (IntegerField): AI confidence (0-100)
- `response_text` (TextField): AI's response
- `response_data` (JSONField): Structured response data
- `rating` (IntegerField): Star rating (1-5)
- `feedback_type` (CharField): Type of feedback
- `feedback_comment` (TextField): Optional comment
- `created_at` (DateTimeField): Submission timestamp

**Properties:**
- `is_positive`: True if rating >= 4
- `is_negative`: True if rating <= 2

#### UserPreference
Stores learned preferences for each user.

**Fields:**
- `user` (OneToOneField): Associated user
- `preferred_detail_level` (CharField): BRIEF, BALANCED, or DETAILED
- `preferred_tone` (CharField): FORMAL, BALANCED, or FRIENDLY
- `avg_satisfaction_rating` (FloatField): Average rating
- `total_queries` (IntegerField): Total feedback count
- `last_updated` (DateTimeField): Last preference update

### Learning Functions

#### record_query_feedback()
Records feedback and updates preferences automatically.

```python
feedback = record_query_feedback(
    user=request.user,
    query_text="Who can work tomorrow?",
    intent="STAFF_AVAILABILITY",
    confidence=95,
    response_text="3 staff available",
    response_data={'count': 3},
    rating=5,
    feedback_type="HELPFUL"
)
```

#### get_user_preferences()
Retrieves preferences, creating defaults if needed.

```python
prefs = get_user_preferences(user)
# Returns UserPreference instance
```

#### personalize_ai_response()
Applies personalization based on learned preferences.

```python
personalized = personalize_ai_response(
    response_text="Here are the results...",
    user_preferences=prefs
)
# Returns modified response and metadata
```

#### get_ai_analytics()
Calculates aggregated analytics.

```python
analytics = get_ai_analytics(
    user=request.user,
    start_date=date(2025, 1, 1),
    end_date=date(2025, 1, 31)
)
```

#### generate_improvement_insights()
Generates actionable recommendations.

```python
insights = generate_improvement_insights()
# Returns high/low performers and recommendations
```

### Personalization Logic

**Detail Level:**
- **BRIEF**: Responses truncated to 5 lines + "For more details, ask follow-up"
- **BALANCED**: No modification (default)
- **DETAILED**: No truncation, full details provided

**Tone:**
- **FORMAL**: Casual language → formal ("Great!" → "Confirmed.", remove emojis except 📋)
- **BALANCED**: No modification (default)
- **FRIENDLY**: Adds greeting emoji if not present (💡, 👋, 🎯)

**Learning Triggers:**
- **5+ TOO_TECHNICAL feedbacks** → Switch to BRIEF
- **5+ TOO_SIMPLE feedbacks** → Switch to DETAILED
- **5+ feedbacks with formal language preference** → Switch to FORMAL
- **5+ feedbacks with friendly preference** → Switch to FRIENDLY

### Frontend Integration

The feedback widget is implemented in `/scheduling/templates/scheduling/feedback_widget.html` and included in the AI assistant page.

**Key Functions:**
- `createFeedbackWidget()`: Builds the DOM element
- `submitFeedback()`: Sends data to API
- `storeQueryData()`: Stores query context

**Workflow:**
1. User asks a question
2. AI responds with text and metadata (intent, confidence, data)
3. `addMessage()` creates response message
4. Widget is attached to AI message
5. User rates and submits feedback
6. Feedback sent to `/api/ai-assistant/feedback/`
7. Preferences updated automatically
8. Future responses personalized

---

## 5. Testing

### Running Tests

```bash
python manage.py test scheduling.tests_task11_feedback
```

### Test Coverage

**8 Test Classes:**
1. **FeedbackRecordingTests**: Feedback creation and classification
2. **PreferenceLearningTests**: Preference learning algorithms
3. **PersonalizationTests**: Response personalization logic
4. **AnalyticsTests**: Analytics calculations
5. **InsightsTests**: Insights generation
6. **APIEndpointTests**: API functionality and validation
7. **IntegrationTests**: End-to-end workflows

**28 Test Methods** covering:
- Positive/negative feedback detection
- Preference auto-creation
- Detail level learning (BRIEF/DETAILED)
- Tone adaptation (FORMAL/FRIENDLY)
- Average satisfaction calculation
- Most common intent tracking
- Brief personalization (truncation)
- Formal tone replacement
- Friendly tone emoji addition
- Total query counts
- Average rating calculation
- Satisfaction rate percentage
- Intent grouping
- Low performer identification
- Date filtering
- High/low performer detection
- Recommendation generation
- API validation (400, 403 status codes)
- Authentication checks
- Permission checks (Senior Staff only)
- Full feedback workflows

---

## 6. Performance Optimization

### Caching Strategy

**Preference Caching:**
```python
from django.core.cache import cache

def get_cached_preferences(user):
    cache_key = f'user_prefs_{user.id}'
    prefs = cache.get(cache_key)
    if not prefs:
        prefs = get_user_preferences(user)
        cache.set(cache_key, prefs, 300)  # 5 minutes
    return prefs
```

**Analytics Caching:**
```python
def get_cached_analytics(period='last_30_days'):
    cache_key = f'analytics_{period}'
    analytics = cache.get(cache_key)
    if not analytics:
        analytics = get_ai_analytics(period=period)
        cache.set(cache_key, analytics, 600)  # 10 minutes
    return analytics
```

### Async Processing

For high-traffic scenarios, process feedback asynchronously:

```python
from celery import shared_task

@shared_task
def process_feedback_async(feedback_id):
    feedback = AIQueryFeedback.objects.get(id=feedback_id)
    # Update preferences based on feedback
    update_user_preferences(feedback.user, feedback)
```

### Database Indexes

Already optimized with indexes on:
- `user` + `created_at` (for user-specific queries)
- `intent_detected` + `rating` (for analytics)
- `created_at` (for date filtering)

### Query Optimization

Use `select_related()` to reduce database queries:

```python
feedbacks = AIQueryFeedback.objects.select_related('user').filter(...)
```

---

## 7. Monitoring & Maintenance

### Key Metrics to Monitor

1. **Satisfaction Rate**: Should be ≥80%
   - If below 75%, review low-performing intents
   
2. **Feedback Volume**: Aim for >50% of queries
   - Low volume may indicate UI/UX issues
   
3. **Response Time**: API should respond <200ms
   - Monitor `/api/ai-assistant/feedback/` endpoint
   
4. **Preference Convergence**: Users should stabilize preferences within 10-15 queries
   - Frequent changes may indicate learning issues

### Database Maintenance

**Archive Old Feedback** (quarterly):
```python
from datetime import timedelta
from django.utils import timezone

cutoff_date = timezone.now() - timedelta(days=180)
old_feedback = AIQueryFeedback.objects.filter(created_at__lt=cutoff_date)
# Archive to separate table or export to CSV
old_feedback.delete()
```

**Reset Preferences** (if user requests):
```python
prefs = UserPreference.objects.get(user=user)
prefs.preferred_detail_level = 'BALANCED'
prefs.preferred_tone = 'BALANCED'
prefs.avg_satisfaction_rating = 0.0
prefs.total_queries = 0
prefs.save()
```

### Troubleshooting

**Issue: Widget not appearing**
- Check that `{% include 'scheduling/feedback_widget.html' %}` is present
- Verify `createFeedbackWidget()` function exists
- Check browser console for JavaScript errors

**Issue: Feedback not saving**
- Verify CSRF token is present
- Check API endpoint is accessible
- Review server logs for errors

**Issue: Preferences not updating**
- Verify `record_query_feedback()` is called
- Check that preference thresholds are met (5+ feedbacks)
- Review `UserPreference` table in admin

**Issue: Personalization not working**
- Check that `personalize_ai_response()` is called
- Verify preferences are loaded correctly
- Test with known preference settings

---

## 8. Future Enhancements

### Phase 1 Improvements
- **Multi-language support**: Detect user language preference
- **A/B testing**: Test different response styles
- **Sentiment analysis**: Analyze feedback comments with NLP

### Phase 2 Features
- **Team analytics**: Compare satisfaction across teams/homes
- **Trend analysis**: Track satisfaction trends over time
- **Automated reports**: Weekly summary emails to managers

### Phase 3 Integration
- **Proactive suggestions**: AI learns which queries are common
- **Response templates**: Build library of high-performing responses
- **Voice feedback**: Allow audio feedback collection

---

## Support

**Technical Issues:**
- Check Django logs: `/var/log/staff_rota/django.log`
- Review test suite: `python manage.py test scheduling.tests_task11_feedback`
- Contact system administrator

**Feature Requests:**
- Submit via admin interface or email
- Include use case and expected benefit
- Prioritized based on ROI potential

**Documentation Updates:**
- Submit pull request with changes
- Tag with `documentation` label
- Include screenshots for UI changes

---

## Appendix: Feedback Type Definitions

| Type | Emoji | Meaning | Action |
|------|-------|---------|--------|
| HELPFUL | ✅ | Response was exactly what was needed | Reinforce current approach |
| INACCURATE | ❌ | Information was incorrect | Review data sources |
| INCOMPLETE | 📋 | Missing important details | Add more context |
| TOO_TECHNICAL | 🎓 | Too much jargon | Simplify language |
| TOO_SIMPLE | 📖 | Not enough depth | Add more details |
| WRONG_INTENT | 🎯 | Misunderstood the question | Improve intent detection |

---

**Last Updated:** December 2025  
**Version:** 1.0  
**Maintained By:** Staff Rota Development Team
