from django.urls import path

from .views import StaffProfileDetailView, StaffProfileListView

app_name = "staff_records"

urlpatterns = [
    path("", StaffProfileListView.as_view(), name="profile_list"),
    path("<str:sap>/", StaffProfileDetailView.as_view(), name="profile_detail"),
]
