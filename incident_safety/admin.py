from django.contrib import admin
from .models import (
    RootCauseAnalysis,
    CorrectivePreventiveAction,
    DutyOfCandourRecord,
    IncidentTrendAnalysis
)

# Simple admin registrations - will enhance with custom admin classes after testing
admin.site.register(RootCauseAnalysis)
admin.site.register(CorrectivePreventiveAction)
admin.site.register(DutyOfCandourRecord)
admin.site.register(IncidentTrendAnalysis)
