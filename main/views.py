import datetime
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.models import Education, Experience
from main.forms import EducationForm

def show_main(request):
    last_login = request.COOKIES.get(
        "last_login", "Belum ada sesi login / Cookie tidak ditemukan"
    )
    context = {
        "name": "Immanuel Marvin Pandjaitan",
        "npm": "2506623881",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Immanuel Marvin Pandjaitan",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

# bonus: ambil data Experience dalam format JSON juga, pola sama kayak get_education_json
def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experience_qs = Experience.objects.all()

    if title_query:
        experience_qs = experience_qs.filter(title__icontains=title_query)

    experience_json = serializers.serialize("json", experience_qs)
    return HttpResponse(experience_json, content_type="application/json")


# ambil data Education dalam format JSON, dipakai juga sama show_education di bawah
def get_education_json(request):
    institution_query = request.GET.get("institution", "").strip()
    education_qs = Education.objects.all().order_by("started_at")

    if institution_query:
        education_qs = education_qs.filter(institution__icontains=institution_query)

    education_json = serializers.serialize("json", education_qs)
    return HttpResponse(education_json, content_type="application/json")


# nampilin daftar riwayat pendidikan, sekarang lewat JSON dulu baru di-deserialize
# (memang keliatan muter-muter, tapi ini contoh alur data delivery dari Tutorial 03)
def show_education(request):
    json_response = get_education_json(request)
    education_objects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    education_list = [item.object for item in education_objects]

    institution_query = request.GET.get("institution", "").strip()

    context = {
        "name": "Immanuel Marvin Pandjaitan",
        "education_list": education_list,
        "institution_query": institution_query,
    }
    return render(request, "education.html", context)


# form buat nambahin riwayat pendidikan baru lewat halaman web
def create_education(request):
    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan baru berhasil ditambahkan!")
        return redirect("main:show_education")

    context = {
        "name": "Immanuel Marvin Pandjaitan",
        "form": form,
    }
    return render(request, "education_form.html", context)

# form buat ngedit riwayat pendidikan yang udah ada, pakai form yang sama kayak create
# bedanya form-nya di-passing instance= biar ke-prefill data lama
def update_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    form = EducationForm(request.POST or None, instance=education)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Riwayat pendidikan berhasil diperbarui!")
        return redirect("main:show_education")

    context = {
        "name": "Immanuel Marvin Pandjaitan",
        "form": form,
        "education": education,
    }
    return render(request, "education_form.html", context)

def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Riwayat pendidikan berhasil dihapus!")
        return redirect("main:show_education")

    return redirect("main:show_education")

# ---------- Autentikasi (Tutorial 04, Bagian 1) ----------

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Immanuel Marvin Pandjaitan",
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        response = redirect("main:show_main")
        response.set_cookie(
            "last_login", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        return response

    context = {
        "name": "Immanuel Marvin Pandjaitan",
        "form": form,
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response