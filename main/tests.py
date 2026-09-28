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

    def test_education_page_shows_data(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, self.education.institution)
        self.assertContains(response, self.education.major)
        self.assertContains(response, "Kuliah")

    def test_empty_education_page(self):
        Education.objects.all().delete()
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
        self.assertNotContains(response, self.add_url)
        self.assertNotContains(response, self.edit_url)
        self.assertNotContains(response, self.delete_url)

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

    def test_regular_user_buttons_hidden_but_star_visible(self):
        self.client.login(username="biasa", password="pass12345")
        response = self.client.get(reverse("main:show_education"))
        self.assertNotContains(response, self.add_url)
        self.assertNotContains(response, self.edit_url)
        self.assertNotContains(response, self.delete_url)
        self.assertContains(response, self.star_url)

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
        self.education.stars.add(self.user, self.editor)
        self.client.login(username="biasa", password="pass12345")
        response = self.client.get(reverse("main:show_education"))
        self.assertContains(response, "Batalkan star")
        self.assertContains(response, "(2)")

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

    def test_editor_sees_only_edit_button(self):
        self.client.login(username="editor", password="pass12345")
        response = self.client.get(reverse("main:show_education"))
        self.assertContains(response, self.edit_url)
        self.assertNotContains(response, self.add_url)
        self.assertNotContains(response, self.delete_url)

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
        self.assertContains(response, self.add_url)
        self.assertContains(response, self.edit_url)
        self.assertContains(response, self.delete_url)
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