import datetime
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from main.models import Education, Experience
from main.forms import EducationForm, ExperienceForm

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


# cuma nampilin kerangka halaman; datanya diambil terpisah lewat AJAX (Tutorial 05/Tugas 5)
def show_experience(request):
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Immanuel Marvin Pandjaitan",
        "title_query": title_query,
        "form": ExperienceForm(),
    }
    return render(request, "experience.html", context)


# JSON dirakit manual (bukan serializers.serialize) supaya bisa menyisipkan
# info star per pengguna, pola sama persis seperti get_education_json
def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experience_qs = Experience.objects.all().order_by("started_at")

    if title_query:
        experience_qs = experience_qs.filter(title__icontains=title_query)

    starred_ids = set()
    if request.user.is_authenticated:
        starred_ids = set(request.user.starred_experiences.values_list("pk", flat=True))

    data = []
    for experience in experience_qs:
        data.append({
            "pk": str(experience.pk),
            "fields": {
                "title": experience.title,
                "description": experience.description,
                "category": experience.category,
                "category_display": experience.get_category_display(),
                "thumbnail": experience.thumbnail,
                "is_ongoing": experience.is_ongoing,
                "star_count": experience.stars.count(),
                "is_starred": experience.pk in starred_ids,
            },
        })

    return JsonResponse(data, safe=False)

# ambil data Education dalam format JSON, dirakit manual (Tutorial 05) supaya
# bisa menyisipkan info star (is_starred tergantung siapa yang sedang login,
# jadi tidak bisa dilakukan serializers.serialize bawaan seperti sebelumnya)
def get_education_json(request):
    institution_query = request.GET.get("institution", "").strip()
    education_qs = Education.objects.all().order_by("started_at")

    if institution_query:
        education_qs = education_qs.filter(institution__icontains=institution_query)

    starred_ids = set()
    if request.user.is_authenticated:
        starred_ids = set(request.user.starred_educations.values_list("pk", flat=True))

    data = []
    for education in education_qs:
        data.append({
            "pk": str(education.pk),
            "fields": {
                # field "stars" (daftar id user) sengaja TIDAK ikut diekspos
                "institution": education.institution,
                "level": education.level,
                "level_display": education.get_level_display(),
                "major": education.major,
                "started_year": education.started_at.year,
                "ended_year": education.ended_at.year if education.ended_at else None,
                "is_ongoing": education.is_ongoing,
                "star_count": education.stars.count(),
                "is_starred": education.pk in starred_ids,
            },
        })

    return JsonResponse(data, safe=False)


# cuma nampilin kerangka halaman; datanya diambil terpisah lewat AJAX (Tutorial 05)
def show_education(request):
    institution_query = request.GET.get("institution", "").strip()

    context = {
        "name": "Immanuel Marvin Pandjaitan",
        "institution_query": institution_query,
        "form": EducationForm(),
    }
    return render(request, "education.html", context)


# form buat nambahin riwayat pendidikan baru lewat halaman web
@login_required  # belum login -> redirect ke LOGIN_URL
@permission_required("main.add_education", raise_exception=True)  # login tapi tidak berhak -> 403
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
@login_required
@permission_required("main.change_education", raise_exception=True)
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

@login_required
@permission_required("main.delete_education", raise_exception=True)
def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Riwayat pendidikan berhasil dihapus!")
        return redirect("main:show_education")

    return redirect("main:show_education")


# ---------- AJAX tambah pendidikan (Tutorial 05) ----------

@require_POST
def create_education_ajax(request):
    # bukan @login_required: fetch akan ikut redirect ke halaman login (200 HTML)
    # kalau pakai itu, jadi JS tidak bisa mengenali kegagalannya. AnonymousUser
    # otomatis has_perm False juga, jadi satu pengecekan ini menolak pengunjung
    # anonim maupun pengguna yang tidak berhak, dengan respons JSON yang jelas.
    if not request.user.has_perm("main.add_education"):
        return JsonResponse(
            {"message": "Kamu tidak berhak menambahkan riwayat pendidikan."},
            status=403,
        )

    form = EducationForm(request.POST)
    if form.is_valid():
        education = form.save()
        return JsonResponse(
            {"message": "Riwayat pendidikan berhasil ditambahkan.", "pk": str(education.id)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


# ---------- Star (Tugas 4) ----------

@login_required
@require_POST  # toggle mengubah data, jadi hanya boleh lewat POST (+ csrf_token di form)
def toggle_star(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if education.stars.filter(pk=request.user.pk).exists():
        education.stars.remove(request.user)
    else:
        education.stars.add(request.user)

    return redirect("main:show_education")

# ---------- CRUD + AJAX untuk Experience (Tugas 5, pola sama dengan Education) ----------

@login_required
@permission_required("main.add_experience", raise_exception=True)
def create_experience(request):
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Immanuel Marvin Pandjaitan",
        "form": form,
    }
    return render(request, "experience_form.html", context)


@login_required
@permission_required("main.change_experience", raise_exception=True)
def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": "Immanuel Marvin Pandjaitan",
        "form": form,
        "experience": experience,
    }
    return render(request, "experience_form.html", context)


@login_required
@permission_required("main.delete_experience", raise_exception=True)
def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Pengalaman berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")


@login_required
@require_POST
def toggle_star_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if experience.stars.filter(pk=request.user.pk).exists():
        experience.stars.remove(request.user)
    else:
        experience.stars.add(request.user)

    return redirect("main:show_experience")


@require_POST
def create_experience_ajax(request):
    if not request.user.has_perm("main.add_experience"):
        return JsonResponse(
            {"message": "Kamu tidak berhak menambahkan pengalaman."},
            status=403,
        )

    form = ExperienceForm(request.POST)
    if form.is_valid():
        experience = form.save()
        return JsonResponse(
            {"message": "Pengalaman berhasil ditambahkan.", "pk": str(experience.id)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

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

        next_url = request.POST.get("next") or request.GET.get("next")
        if not next_url or not url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            next_url = "main:show_main"

        response = redirect(next_url)
        response.set_cookie(
            "last_login", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        return response

    context = {
        "name": "Immanuel Marvin Pandjaitan",
        "form": form,
        "next": request.GET.get("next", ""),
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response