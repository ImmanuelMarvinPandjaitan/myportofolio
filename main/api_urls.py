from django.urls import path

from main import api_views

app_name = "api"

urlpatterns = [
    # Education (Tutorial 07)
    path("education/", api_views.education_list, name="education-list"),
    path("education/<uuid:education_id>/", api_views.education_detail, name="education-detail"),
    path("education/<uuid:education_id>/star/", api_views.education_star, name="education-star"),
    # Experience (Tugas 6)
    path("experience/", api_views.experience_list, name="experience-list"),
    path("experience/<uuid:experience_id>/", api_views.experience_detail, name="experience-detail"),
    path("experience/<uuid:experience_id>/star/", api_views.experience_star, name="experience-star"),
]

from django.urls import path  # noqa: E402
from rest_framework.authtoken import views as authtoken_views  # noqa: E402
from main import api_views as _api_views  # noqa: E402

# Tutorial 10: endpoint autentikasi token
urlpatterns += [
    path("auth/token/", authtoken_views.obtain_auth_token, name="api_token_auth"),
    path("auth/logout/", _api_views.api_logout, name="api_logout"),
]
