from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Education

class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")


class EducationTest(TestCase):
    def setUp(self):
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            level="kuliah",
            major="Ilmu Komputer",
            started_at="2025-08-01",
        )

    def test_education_url_is_accessible(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_json_shows_data(self):
        # sejak Tutorial 05, data pendidikan tidak lagi ada di HTML awal
        # (dimuat lewat AJAX), jadi kita periksa lewat endpoint JSON-nya
        response = self.client.get(reverse("main:get_education_json"))
        data = response.json()

        self.assertEqual(len(data), 1)
        fields = data[0]["fields"]
        self.assertEqual(fields["institution"], self.education.institution)
        self.assertEqual(fields["major"], self.education.major)
        self.assertEqual(fields["level_display"], "Kuliah")

    def test_empty_education_json(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:get_education_json"))

        self.assertEqual(response.json(), [])

    def test_education_page_shows_empty_state_markup(self):
        # halaman skeleton-nya harus tetap memuat teks kondisi kosong,
        # walau tampil/tidaknya baru ditentukan JavaScript di browser
        response = self.client.get(reverse("main:show_education"))
        self.assertContains(response, "Belum ada riwayat pendidikan yang ditambahkan.")

    def test_ongoing_education(self):
        self.assertTrue(self.education.is_ongoing)

# ---------- Tugas 4: autentikasi, otorisasi 4 peran, dan star ----------

from django.contrib.auth.models import Group, Permission, User


class EducationAccessTest(TestCase):
    def setUp(self):
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            level="kuliah",
            major="Ilmu Komputer",
            started_at="2025-08-01",
        )
        self.user = User.objects.create_user("biasa", password="pass12345")
        self.editor = User.objects.create_user("editor", password="pass12345")
        self.owner = User.objects.create_superuser("owner", password="pass12345")

        # peran Editor = grup dengan izin change_education saja (tanpa add/delete)
        group = Group.objects.create(name="Editor")
        group.permissions.add(Permission.objects.get(codename="change_education"))
        self.editor.groups.add(group)

        self.add_url = reverse("main:create_education")
        self.edit_url = reverse("main:update_education", args=[self.education.id])
        self.delete_url = reverse("main:delete_education", args=[self.education.id])
        self.star_url = reverse("main:toggle_star", args=[self.education.id])
        self.login_url = reverse("main:login")

    # --- pengunjung tanpa login ---
    def test_anonymous_can_read_list(self):
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        # sejak Tutorial 05 tombol dirakit oleh JavaScript, jadi yang diperiksa
        # adalah flag permission yang dikirim view lewat variabel JS di skeleton
        self.assertContains(response, 'const CAN_ADD = "false"')
        self.assertContains(response, 'const CAN_CHANGE = "false"')
        self.assertContains(response, 'const CAN_DELETE = "false"')
        self.assertContains(response, 'const IS_AUTHENTICATED = "false"')

    def test_anonymous_redirected_to_login(self):
        for url in (self.add_url, self.edit_url):
            response = self.client.get(url)
            self.assertRedirects(
                response, f"{self.login_url}?next={url}", fetch_redirect_response=False
            )
        for url in (self.delete_url, self.star_url):
            response = self.client.post(url)
            self.assertRedirects(
                response, f"{self.login_url}?next={url}", fetch_redirect_response=False
            )
        self.assertEqual(Education.objects.count(), 1)

    # --- pengguna biasa ---
    def test_regular_user_gets_403_on_create_update_delete(self):
        self.client.login(username="biasa", password="pass12345")
        self.assertEqual(self.client.get(self.add_url).status_code, 403)
        self.assertEqual(self.client.get(self.edit_url).status_code, 403)
        self.assertEqual(self.client.post(self.delete_url).status_code, 403)
        self.assertEqual(Education.objects.count(), 1)

    def test_regular_user_permission_flags(self):
        self.client.login(username="biasa", password="pass12345")
        response = self.client.get(reverse("main:show_education"))
        self.assertContains(response, 'const CAN_ADD = "false"')
        self.assertContains(response, 'const CAN_CHANGE = "false"')
        self.assertContains(response, 'const CAN_DELETE = "false"')
        self.assertContains(response, 'const IS_AUTHENTICATED = "true"')

    def test_star_toggle_max_one_per_user(self):
        self.client.login(username="biasa", password="pass12345")
        self.client.post(self.star_url)
        self.assertEqual(self.education.stars.count(), 1)
        self.client.post(self.star_url)  # kedua kali = batal
        self.assertEqual(self.education.stars.count(), 0)

    def test_star_rejects_get(self):
        self.client.login(username="biasa", password="pass12345")
        self.assertEqual(self.client.get(self.star_url).status_code, 405)

    def test_star_count_and_state_shown(self):
        # sejak Tutorial 05, jumlah dan status star dibaca lewat JSON, bukan HTML halaman
        self.education.stars.add(self.user, self.editor)
        self.client.login(username="biasa", password="pass12345")
        response = self.client.get(reverse("main:get_education_json"))
        fields = response.json()[0]["fields"]
        self.assertTrue(fields["is_starred"])
        self.assertEqual(fields["star_count"], 2)

    # --- editor ---
    def test_editor_can_update_but_not_create_or_delete(self):
        self.client.login(username="editor", password="pass12345")
        self.assertEqual(self.client.get(self.edit_url).status_code, 200)
        response = self.client.post(
            self.edit_url,
            {
                "institution": "UI Depok",
                "level": "kuliah",
                "major": "Ilmu Komputer",
                "started_at": "2025-08-01",
            },
        )
        self.assertRedirects(response, reverse("main:show_education"))
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "UI Depok")
        self.assertEqual(self.client.get(self.add_url).status_code, 403)
        self.assertEqual(self.client.post(self.delete_url).status_code, 403)

    def test_editor_permission_flags(self):
        self.client.login(username="editor", password="pass12345")
        response = self.client.get(reverse("main:show_education"))
        self.assertContains(response, 'const CAN_ADD = "false"')
        self.assertContains(response, 'const CAN_CHANGE = "true"')
        self.assertContains(response, 'const CAN_DELETE = "false"')

    def test_editor_can_star(self):
        self.client.login(username="editor", password="pass12345")
        self.client.post(self.star_url)
        self.assertEqual(self.education.stars.count(), 1)

    # --- pemilik (superuser) ---
    def test_owner_can_create_update_delete_and_star(self):
        self.client.login(username="owner", password="pass12345")
        self.assertEqual(self.client.get(self.add_url).status_code, 200)
        self.assertEqual(self.client.get(self.edit_url).status_code, 200)
        response = self.client.get(reverse("main:show_education"))
        self.assertContains(response, 'const CAN_ADD = "true"')
        self.assertContains(response, 'const CAN_CHANGE = "true"')
        self.assertContains(response, 'const CAN_DELETE = "true"')
        self.client.post(self.star_url)
        self.assertEqual(self.education.stars.count(), 1)
        self.client.post(self.delete_url)
        self.assertEqual(Education.objects.count(), 0)

    # --- login redirect + API ---
    def test_login_redirects_back_to_next(self):
        response = self.client.post(
            self.login_url,
            {"username": "owner", "password": "pass12345", "next": self.add_url},
        )
        self.assertRedirects(response, self.add_url, fetch_redirect_response=False)

    def test_login_ignores_external_next(self):
        response = self.client.post(
            self.login_url,
            {"username": "owner", "password": "pass12345", "next": "https://evil.example/"},
        )
        self.assertRedirects(response, reverse("main:show_main"), fetch_redirect_response=False)

    def test_json_api_public_and_does_not_leak_stars(self):
        self.education.stars.add(self.user)
        response = self.client.get(reverse("main:get_education_json"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Universitas Indonesia")
        self.assertNotContains(response, "stars")
        self.assertNotContains(response, "password")
        self.assertNotContains(response, "biasa")

# ---------- Tutorial 05: AJAX tambah pendidikan dan proteksi XSS ----------

class EducationAjaxTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("biasa2", password="pass12345")
        self.editor = User.objects.create_user("editor2", password="pass12345")
        group = Group.objects.create(name="Editor2")
        group.permissions.add(Permission.objects.get(codename="change_education"))
        self.editor.groups.add(group)
        self.owner = User.objects.create_superuser("owner2", password="pass12345")

        self.ajax_url = reverse("main:create_education_ajax")
        self.valid_payload = {
            "institution": "Universitas Indonesia",
            "level": "kuliah",
            "major": "Ilmu Komputer",
            "started_at": "2025-08-01",
        }

    def test_anonymous_forbidden(self):
        response = self.client.post(self.ajax_url, self.valid_payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Education.objects.count(), 0)

    def test_regular_user_forbidden(self):
        self.client.login(username="biasa2", password="pass12345")
        response = self.client.post(self.ajax_url, self.valid_payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Education.objects.count(), 0)

    def test_editor_forbidden(self):
        # Editor cuma boleh mengubah, bukan menambah
        self.client.login(username="editor2", password="pass12345")
        response = self.client.post(self.ajax_url, self.valid_payload)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Education.objects.count(), 0)

    def test_get_not_allowed(self):
        self.client.login(username="owner2", password="pass12345")
        response = self.client.get(self.ajax_url)
        self.assertEqual(response.status_code, 405)

    def test_owner_can_create(self):
        self.client.login(username="owner2", password="pass12345")
        response = self.client.post(self.ajax_url, self.valid_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Education.objects.count(), 1)
        self.assertIn("pk", response.json())

    def test_owner_invalid_data_returns_400(self):
        self.client.login(username="owner2", password="pass12345")
        payload = {**self.valid_payload, "institution": ""}
        response = self.client.post(self.ajax_url, payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("institution", response.json()["errors"])
        self.assertEqual(Education.objects.count(), 0)

    def test_html_tags_stripped_from_institution_and_major(self):
        # lapisan pertahanan kedua: tag HTML dibuang sejak data masuk (Tutorial 05)
        self.client.login(username="owner2", password="pass12345")
        payload = {
            **self.valid_payload,
            "institution": "<b>Universitas</b> Indonesia",
            "major": "<script>alert(1)</script>Ilmu Komputer",
        }
        self.client.post(self.ajax_url, payload)
        education = Education.objects.get()
        self.assertEqual(education.institution, "Universitas Indonesia")
        self.assertEqual(education.major, "alert(1)Ilmu Komputer")

    def test_institution_with_only_html_tags_rejected(self):
        self.client.login(username="owner2", password="pass12345")
        payload = {**self.valid_payload, "institution": "<img src=x onerror=alert(1)>"}
        response = self.client.post(self.ajax_url, payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Education.objects.count(), 0)