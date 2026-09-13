from django.shortcuts import render

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


# nampilin daftar riwayat pendidikan, diambil dari model Education (dulunya hardcode di index.html)
def show_education(request):
    context = {
        "name": "Immanuel Marvin Pandjaiatan",
        "education_list": Education.objects.all().order_by('started_at'),
    }
    return render(request, "education.html", context)