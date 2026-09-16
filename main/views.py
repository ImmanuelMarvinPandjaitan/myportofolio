from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import EducationForm
from main.models import Experience, Education


def show_main(request):
    context = {
        "name": "Immanuel Marvin Pandjaiatan",
        "npm": "2506623881",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Immanuel Marvin Pandjaiatan",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


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
        "name": "Immanuel Marvin Pandjaiatan",
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
        "name": "Immanuel Marvin Pandjaiatan",
        "form": form,
    }
    return render(request, "education_form.html", context)


def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Riwayat pendidikan berhasil dihapus!")
        return redirect("main:show_education")

    return redirect("main:show_education")