"""
Multi-language Support Service Layer
Task 37: Functions for language management, translation, and localization
"""

from django.utils import translation
from django.utils.translation import gettext as _, gettext_lazy
from django.contrib.auth.models import User
from django.conf import settings
from collections import defaultdict

from .models import UserLanguagePreference, Translation


# ==================== USER LANGUAGE PREFERENCES ====================

def get_user_language(user):
    """
    Get the preferred language for a user
    
    Args:
        user: User object
    
    Returns:
        Language code (e.g., 'en', 'gd', 'pl')
    """
    try:
        preference = UserLanguagePreference.objects.get(user=user)
        return preference.language_code
    except UserLanguagePreference.DoesNotExist:
        return settings.LANGUAGE_CODE


def set_user_language(user, language_code, date_format=None, time_format=None, 
                     use_12_hour=False, timezone='Europe/London'):
    """
    Set or update user language preference
    
    Args:
        user: User object
        language_code: Language code from LANGUAGE_CHOICES
        date_format: Optional custom date format
        time_format: Optional custom time format
        use_12_hour: Use 12-hour clock format
        timezone: Timezone string
    
    Returns:
        UserLanguagePreference object
    """
    preference, created = UserLanguagePreference.objects.get_or_create(user=user)
    
    preference.language_code = language_code
    if date_format:
        preference.date_format = date_format
    if time_format:
        preference.time_format = time_format
    preference.use_12_hour = use_12_hour
    preference.timezone = timezone
    preference.save()
    
    # Activate the language for current session
    translation.activate(language_code)
    
    return preference


def get_user_format_preferences(user):
    """
    Get user's formatting preferences
    
    Returns:
        Dict with date_format, time_format, use_12_hour, timezone, currency_symbol
    """
    try:
        preference = UserLanguagePreference.objects.get(user=user)
        return {
            'language_code': preference.language_code,
            'language_name': preference.get_language_name(),
            'date_format': preference.date_format,
            'time_format': preference.time_format,
            'use_12_hour': preference.use_12_hour,
            'timezone': preference.timezone,
            'currency_symbol': preference.currency_symbol,
        }
    except UserLanguagePreference.DoesNotExist:
        return {
            'language_code': 'en',
            'language_name': 'English',
            'date_format': '%d/%m/%Y',
            'time_format': '%H:%M',
            'use_12_hour': False,
            'timezone': 'Europe/London',
            'currency_symbol': '£',
        }


def get_available_languages():
    """
    Get list of available languages
    
    Returns:
        List of (code, name) tuples
    """
    return UserLanguagePreference.LANGUAGE_CHOICES


def get_language_statistics():
    """
    Get statistics on language usage
    
    Returns:
        Dict with language counts and percentages
    """
    from django.db.models import Count
    
    total_users = User.objects.filter(is_active=True).count()
    
    language_counts = UserLanguagePreference.objects.values('language_code').annotate(
        count=Count('user')
    ).order_by('-count')
    
    # Calculate percentages
    stats = []
    for item in language_counts:
        stats.append({
            'language_code': item['language_code'],
            'language_name': dict(UserLanguagePreference.LANGUAGE_CHOICES).get(item['language_code'], 'Unknown'),
            'count': item['count'],
            'percentage': (item['count'] / total_users * 100) if total_users > 0 else 0
        })
    
    # Add users with no preference (defaults to English)
    users_with_preference = sum(item['count'] for item in language_counts)
    users_no_preference = total_users - users_with_preference
    
    if users_no_preference > 0:
        stats.append({
            'language_code': 'en',
            'language_name': 'English (Default)',
            'count': users_no_preference,
            'percentage': (users_no_preference / total_users * 100) if total_users > 0 else 0
        })
    
    return {
        'total_users': total_users,
        'languages': stats
    }


# ==================== CUSTOM TRANSLATIONS ====================

def get_custom_translation(key, language_code, care_home=None, default=None):
    """
    Get a custom translation for a specific key
    
    Args:
        key: Translation key
        language_code: Language code
        care_home: Optional care home for care home-specific translations
        default: Default text if translation not found
    
    Returns:
        Translated text or default
    """
    try:
        # Try care home-specific translation first
        if care_home:
            translation = Translation.objects.get(
                key=key,
                language_code=language_code,
                care_home=care_home,
                is_approved=True
            )
            return translation.translated_text
        
        # Fall back to global translation
        translation = Translation.objects.get(
            key=key,
            language_code=language_code,
            care_home__isnull=True,
            is_approved=True
        )
        return translation.translated_text
    
    except Translation.DoesNotExist:
        return default or key


def add_custom_translation(key, language_code, translated_text, context='', 
                          care_home=None, created_by=None):
    """
    Add or update a custom translation
    
    Args:
        key: Translation key
        language_code: Language code
        translated_text: Translated text
        context: Optional context
        care_home: Optional care home
        created_by: User who created the translation
    
    Returns:
        Translation object
    """
    translation, created = Translation.objects.update_or_create(
        key=key,
        language_code=language_code,
        care_home=care_home,
        defaults={
            'translated_text': translated_text,
            'context': context,
            'created_by': created_by,
            'is_approved': False  # Requires approval
        }
    )
    
    return translation


def approve_translation(translation_id, approver):
    """
    Approve a custom translation
    
    Args:
        translation_id: Translation ID
        approver: User approving the translation
    
    Returns:
        Translation object
    """
    translation = Translation.objects.get(id=translation_id)
    translation.is_approved = True
    translation.approved_by = approver
    translation.save()
    
    return translation


def get_pending_translations(care_home=None, language_code=None):
    """
    Get pending translations awaiting approval
    
    Args:
        care_home: Optional care home filter
        language_code: Optional language filter
    
    Returns:
        QuerySet of Translation objects
    """
    translations = Translation.objects.filter(is_approved=False)
    
    if care_home:
        translations = translations.filter(care_home=care_home)
    
    if language_code:
        translations = translations.filter(language_code=language_code)
    
    return translations.select_related('created_by', 'care_home').order_by('-created_at')


def bulk_import_translations(translations_dict, language_code, care_home=None, created_by=None):
    """
    Bulk import translations from a dictionary
    
    Args:
        translations_dict: Dict of {key: translated_text}
        language_code: Language code
        care_home: Optional care home
        created_by: User creating the translations
    
    Returns:
        Number of translations created
    """
    translations_to_create = []
    
    for key, translated_text in translations_dict.items():
        translation = Translation(
            key=key,
            language_code=language_code,
            translated_text=translated_text,
            care_home=care_home,
            created_by=created_by,
            is_approved=False
        )
        translations_to_create.append(translation)
    
    Translation.objects.bulk_create(translations_to_create, ignore_conflicts=True)
    
    return len(translations_to_create)


# ==================== TRANSLATION HELPERS ====================

def translate_shift_type(shift_type, language_code):
    """Helper to translate shift type names"""
    translations = {
        'en': {
            'EARLY': 'Early Shift',
            'LATE': 'Late Shift',
            'NIGHT': 'Night Shift',
            'DAY': 'Day Shift',
            'SLEEP_IN': 'Sleep-in',
        },
        'gd': {
            'EARLY': 'Shift Tràth',
            'LATE': 'Shift Anmoch',
            'NIGHT': 'Shift Oidhche',
            'DAY': 'Shift Latha',
            'SLEEP_IN': 'Cadal A-staigh',
        },
        'pl': {
            'EARLY': 'Wczesna Zmiana',
            'LATE': 'Późna Zmiana',
            'NIGHT': 'Zmiana Nocna',
            'DAY': 'Zmiana Dzienna',
            'SLEEP_IN': 'Dyżur Nocny',
        },
        'ro': {
            'EARLY': 'Tura de dimineață',
            'LATE': 'Tura de seară',
            'NIGHT': 'Tura de noapte',
            'DAY': 'Tura de zi',
            'SLEEP_IN': 'Tura de somn',
        },
    }
    
    return translations.get(language_code, {}).get(shift_type, shift_type)


def translate_leave_type(leave_type, language_code):
    """Helper to translate leave type names"""
    translations = {
        'en': {
            'ANNUAL': 'Annual Leave',
            'SICK': 'Sick Leave',
            'PERSONAL': 'Personal Leave',
            'MATERNITY': 'Maternity Leave',
            'PATERNITY': 'Paternity Leave',
        },
        'gd': {
            'ANNUAL': 'Saor-làithean Bliadhnail',
            'SICK': 'Saor-làithean Tinn',
            'PERSONAL': 'Saor-làithean Pearsanta',
            'MATERNITY': 'Saor-làithean Màthaireil',
            'PATERNITY': 'Saor-làithean Athaireil',
        },
        'pl': {
            'ANNUAL': 'Urlop Roczny',
            'SICK': 'Zwolnienie Lekarskie',
            'PERSONAL': 'Urlop Osobisty',
            'MATERNITY': 'Urlop Macierzyński',
            'PATERNITY': 'Urlop Ojcowski',
        },
        'ro': {
            'ANNUAL': 'Concediu Anual',
            'SICK': 'Concediu Medical',
            'PERSONAL': 'Concediu Personal',
            'MATERNITY': 'Concediu Maternal',
            'PATERNITY': 'Concediu Paternal',
        },
    }
    
    return translations.get(language_code, {}).get(leave_type, leave_type)


def get_localized_weekdays(language_code):
    """Get localized weekday names"""
    weekdays = {
        'en': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        'gd': ['Diluain', 'Dimàirt', 'Diciadain', 'Diardaoin', 'Dihaoine', 'Disathairne', 'Didòmhnaich'],
        'pl': ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela'],
        'ro': ['Luni', 'Marți', 'Miercuri', 'Joi', 'Vineri', 'Sâmbătă', 'Duminică'],
        'cy': ['Dydd Llun', 'Dydd Mawrth', 'Dydd Mercher', 'Dydd Iau', 'Dydd Gwener', 'Dydd Sadwrn', 'Dydd Sul'],
    }
    
    return weekdays.get(language_code, weekdays['en'])


def get_localized_months(language_code):
    """Get localized month names"""
    months = {
        'en': ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December'],
        'gd': ['Am Faoilleach', 'An Gearran', 'Am Màrt', 'An Giblean', 'An Cèitean', 'An t-Ògmhios',
               'An t-Iuchar', 'An Lùnastal', 'An t-Sultain', 'An Dàmhair', 'An t-Samhain', 'An Dùbhlachd'],
        'pl': ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
               'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'],
        'ro': ['Ianuarie', 'Februarie', 'Martie', 'Aprilie', 'Mai', 'Iunie',
               'Iulie', 'August', 'Septembrie', 'Octombrie', 'Noiembrie', 'Decembrie'],
    }
    
    return months.get(language_code, months['en'])
