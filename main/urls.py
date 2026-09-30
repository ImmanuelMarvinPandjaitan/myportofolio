from django.urls import path

from main.views import (
    show_main,
    show_experience,
    get_experience_json,
    show_education,
    create_education,
    create_education_ajax,
    update_education,
    get_education_json,
    delete_education,
    toggle_star,
    register,
    login_user,
    logout_user,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("education/", show_education, name="show_education"),
    path("education/add/", create_education, name="create_education"),
    path("education/add-ajax/", create_education_ajax, name="create_education_ajax"),
    path("education/<uuid:education_id>/edit/", update_education, name="update_education"),
    path("education/<uuid:education_id>/delete/", delete_education, name="delete_education"),
    path("education/<uuid:education_id>/star/", toggle_star, name="toggle_star"),
    path("api/education/", get_education_json, name="get_education_json"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
]