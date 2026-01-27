from django.contrib import admin
from .models import (
    RootCauseAnalysis,
    SafetyActionPlan,
    DutyOfCandourRecord,
    IncidentTrendAnalysis
)

# Simple admin registrations - enhancements will come after models are verified
admin.site.register(RootCauseAnalysis)
admin.site.register(SafetyActionPlan)
admin.site.register(DutyOfCandourRecord)
admin.site.register(IncidentTrendAnalysis)
