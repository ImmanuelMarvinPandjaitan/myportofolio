import uuid

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience


class ExperienceAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="visitor", password="test-password", email="visitor@example.com",
        )
        # peran Editor Tugas 4: grup dengan izin change_experience saja
        self.editor = User.objects.create_user(username="editor", password="test-password")
        group = Group.objects.create(name="Editor")
        group.permissions.add(Permission.objects.get(codename="change_experience"))
        self.editor.groups.add(group)

        self.experience = Experience.objects.create(
            title="Asisten Lab", description="Membantu praktikum.", category="part-time",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {
            "title": "Panitia OSKM", "description": "Membantu acara penyambutan.",
            "category": "volunteer", "thumbnail": "https://example.com/a.png",
            "ended_at": "2025-06-01",
        }

    # ---------- baca (publik) ----------
    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data[0]
        self.assertEqual(item["id"], str(self.experience.id))
        self.assertEqual(item["category_display"], "Part-Time")
        self.assertTrue(item["is_ongoing"])
        self.assertFalse(item["is_starred"])
        self.assertEqual(item["star_count"], 0)
        self.assertNotIn("fields", item)
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_api_does_not_leak_sensitive_data(self):
        self.experience.stars.add(self.visitor)
        response = self.client.get(self.list_url)
        self.assertNotIn("stars", response.data[0])
        for secret in ("visitor", "visitor@example.com", "password"):
            self.assertNotIn(secret, response.content.decode())

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "ASISTEN"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "tidak-ada"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_missing_experience(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    # ---------- pengunjung dan pengguna biasa ditolak (cek isi database) ----------
    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "X"}, format="json").status_code, 403)
            self.assertEqual(self.client.put(self.detail_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Lab")

    # ---------- Editor: boleh PATCH/PUT, ditolak create dan delete ----------
    def test_editor_can_update_but_not_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"description": "Deskripsi baru"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.description, "Deskripsi baru")
        self.assertEqual(self.experience.title, "Asisten Lab")  # PATCH: field lain tetap

        response = self.client.put(self.detail_url, {**self.payload, "title": "Judul PUT"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Judul PUT")

        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(Experience.objects.count(), 1)  # tidak ada data baru
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertTrue(Experience.objects.filter(pk=self.experience.pk).exists())  # tidak terhapus

    def test_editor_can_star(self):
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.experience.stars.count(), 1)

    def test_staff_without_permission_cannot_write(self):
        # is_staff saja tidak cukup: aturan portofolio memakai permission model
        self.visitor.is_staff = True
        self.visitor.save()
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ---------- pemilik: boleh create dan delete ----------
    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Experience.objects.get(pk=response.data["id"])
        self.assertEqual(created.title, "Panitia OSKM")
        self.assertFalse(response.data["is_ongoing"])  # ended_at terisi

    def test_ended_at_accepts_date_iso_and_null(self):
        self.client.force_authenticate(user=self.owner)
        for value, ongoing in [("2025-06-01", False), ("2025-06-01T10:30:00Z", False), (None, True)]:
            response = self.client.post(self.list_url, {**self.payload, "ended_at": value}, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, value)
            self.assertEqual(response.data["is_ongoing"], ongoing, value)

    def test_owner_can_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_owner_put_and_patch(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.put(self.detail_url, {"title": "Tidak lengkap"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # PUT: description wajib
        response = self.client.patch(self.detail_url, {"ended_at": None, "title": "Baru"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Baru")

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ---------- validasi input ----------
    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": " "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"description": "<b></b>"}, "description"),
            ({"category": "dukun"}, "category"),
            ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
            ({"ended_at": "bukan-tanggal"}, "ended_at"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, changes)
            self.assertIn(field, response.data)
        self.assertEqual(Experience.objects.count(), 1)  # tidak ada yang tersimpan

    def test_html_tags_are_stripped(self):
        self.client.force_authenticate(user=self.owner)
        payload = {**self.payload, "title": "<b>Panitia</b> OSKM", "description": "<i>Seru</i> sekali"}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Panitia OSKM")
        self.assertEqual(response.data["description"], "Seru sekali")

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        forged_id = str(uuid.uuid4())
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True, "is_ongoing": True,
            "id": forged_id, "started_at": "2000-01-01T00:00:00Z", "stars": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertFalse(response.data["is_ongoing"])
        self.assertNotEqual(response.data["id"], forged_id)
        self.assertFalse(response.data["started_at"].startswith("2000"))

    # ---------- star ----------
    def test_star_requires_login(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.stars.count(), 0)

    def test_star_toggles_per_account(self):
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        self.client.force_authenticate(user=self.editor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.data["star_count"], 2)
        response = self.client.post(self.star_url)  # editor membatalkan, visitor tetap
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)

    def test_star_get_not_allowed_and_missing(self):
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        url = reverse("api:experience-star", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(url).status_code, status.HTTP_404_NOT_FOUND)

    # ---------- CSRF (session sungguhan, bukan force_authenticate) ----------
    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)
        response = client.patch(self.detail_url, {"title": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Lab")

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")  # Browsable API memasang cookie CSRF
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.patch(self.detail_url, {"title": "Dengan token"}, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Dengan token")


class ExperiencePageUsesApiTest(TestCase):
    """Halaman /experience/ memakai API dan menjaga flag hak akses tiap peran."""

    def setUp(self):
        self.visitor = User.objects.create_user("visitor", password="test-password")
        self.editor = User.objects.create_user("editor", password="test-password")
        group = Group.objects.create(name="Editor")
        group.permissions.add(Permission.objects.get(codename="change_experience"))
        self.editor.groups.add(group)
        self.owner = User.objects.create_superuser("owner", password="test-password")
        self.url = reverse("main:show_experience")

    def test_anonymous(self):
        response = self.client.get(self.url)
        self.assertContains(response, reverse("api:experience-list"))
        self.assertContains(response, 'const CAN_ADD = "false"')
        self.assertContains(response, 'const CAN_CHANGE = "false"')
        self.assertContains(response, 'const CAN_DELETE = "false"')
        self.assertContains(response, 'const IS_AUTHENTICATED = "false"')
        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")
        self.assertNotContains(response, 'id="add-experience-modal"')
        self.assertNotContains(response, 'id="edit-experience-modal"')
        self.assertContains(response, "csrfmiddlewaretoken")  # cookie csrftoken tetap dibuat

    def test_regular_user(self):
        self.client.login(username="visitor", password="test-password")
        response = self.client.get(self.url)
        self.assertContains(response, 'const IS_AUTHENTICATED = "true"')
        self.assertContains(response, 'const CAN_CHANGE = "false"')
        self.assertNotContains(response, 'id="edit-experience-modal"')
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_editor_sees_edit_but_not_add_or_delete(self):
        self.client.login(username="editor", password="test-password")
        response = self.client.get(self.url)
        self.assertContains(response, 'const CAN_ADD = "false"')
        self.assertContains(response, 'const CAN_CHANGE = "true"')
        self.assertContains(response, 'const CAN_DELETE = "false"')
        self.assertContains(response, 'id="edit-experience-modal"')
        self.assertNotContains(response, 'id="add-experience-modal"')

    def test_owner_sees_everything(self):
        self.client.login(username="owner", password="test-password")
        response = self.client.get(self.url)
        self.assertContains(response, 'const CAN_ADD = "true"')
        self.assertContains(response, 'const CAN_CHANGE = "true"')
        self.assertContains(response, 'const CAN_DELETE = "true"')
        self.assertContains(response, 'id="add-experience-modal"')
        self.assertContains(response, 'id="edit-experience-modal"')