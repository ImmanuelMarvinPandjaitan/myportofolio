import uuid
from datetime import date

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Education


class EducationAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="visitor", password="test-password", email="visitor@example.com",
        )
        # peran Editor Tugas 4: grup dengan izin change_education saja
        self.editor = User.objects.create_user(username="editor", password="test-password")
        group = Group.objects.create(name="Editor")
        group.permissions.add(Permission.objects.get(codename="change_education"))
        self.editor.groups.add(group)

        self.education = Education.objects.create(
            institution="Universitas Indonesia", level="kuliah",
            major="Ilmu Komputer", started_at=date(2025, 8, 1),
        )
        self.list_url = reverse("api:education-list")
        self.detail_url = reverse("api:education-detail", args=[self.education.id])
        self.star_url = reverse("api:education-star", args=[self.education.id])
        self.payload = {
            "institution": "SMA Labschool Cirendeu", "level": "sma", "major": "MIPA",
            "started_at": "2022-07-01", "ended_at": "2025-06-01",
        }

    # ---------- baca (publik) ----------
    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data[0]
        self.assertEqual(item["id"], str(self.education.id))
        self.assertEqual(item["level_display"], "Kuliah")
        self.assertTrue(item["is_ongoing"])
        self.assertFalse(item["is_starred"])
        self.assertNotIn("fields", item)  # kontrak baru: objek datar, bukan {"pk", "fields"}
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_api_does_not_leak_sensitive_data(self):
        self.education.stars.add(self.visitor)
        response = self.client.get(self.list_url)
        self.assertNotIn("stars", response.data[0])
        for secret in ("visitor", "visitor@example.com", "password"):
            self.assertNotIn(secret, response.content.decode())

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"institution": "UNIVERSITAS"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"institution": "tidak-ada"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_missing_education(self):
        url = reverse("api:education-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    # ---------- hak akses ----------
    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"institution": "X"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Education.objects.count(), 1)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Universitas Indonesia")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Education.objects.filter(pk=response.data["id"]).exists())

    def test_create_without_end_date_is_ongoing(self):
        self.client.force_authenticate(user=self.owner)
        payload = {**self.payload, "ended_at": None}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["is_ongoing"])

    def test_editor_can_update_but_not_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        response = self.client.patch(self.detail_url, {"major": "Sistem Informasi"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.major, "Sistem Informasi")
        full = {**self.payload, "institution": "UI Depok"}
        self.assertEqual(self.client.put(self.detail_url, full, format="json").status_code, 200)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Education.objects.count(), 1)

    def test_staff_without_permission_cannot_write(self):
        # is_staff saja tidak cukup: aturan portofolio memakai permission, bukan is_staff
        self.visitor.is_staff = True
        self.visitor.save()
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"institution": "X"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ---------- validasi ----------
    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"institution": " "}, "institution"),
            ({"institution": '<img src="x" onerror="alert(1)">'}, "institution"),
            ({"level": "doktor"}, "level"),
            ({"started_at": "bukan-tanggal"}, "started_at"),
            ({"ended_at": "2020-01-01"}, "ended_at"),  # sebelum started_at
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, changes)
            self.assertIn(field, response.data)
        self.assertEqual(Education.objects.count(), 1)

    def test_html_tags_are_stripped(self):
        self.client.force_authenticate(user=self.owner)
        payload = {**self.payload, "institution": "<b>SMA</b> Labschool", "major": "<i>MIPA</i>"}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["institution"], "SMA Labschool")
        self.assertEqual(response.data["major"], "MIPA")

    def test_patch_cannot_make_end_before_start(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"ended_at": "2020-01-01"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"institution": "UI"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "UI")
        self.assertEqual(self.education.major, "Ilmu Komputer")  # PATCH: field lain tetap

        response = self.client.put(self.detail_url, {"institution": "Tidak lengkap"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # PUT: field wajib
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Education.objects.filter(pk=self.education.id).exists())

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "is_ongoing": True, "id": str(uuid.uuid4()), "stars": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertFalse(response.data["is_ongoing"])  # dihitung dari ended_at, bukan dari klien
        self.assertNotEqual(response.data["id"], self.education.id)

    # ---------- star ----------
    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_star_get_not_allowed_and_each_user_counts_once(self):
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.client.post(self.star_url)
        self.client.force_authenticate(user=self.editor)
        response = self.client.post(self.star_url)
        self.assertEqual(response.data["star_count"], 2)
        self.assertTrue(response.data["is_starred"])  # status dihitung per akun yang melihat

    def test_star_missing_education(self):
        self.client.force_authenticate(user=self.visitor)
        url = reverse("api:education-star", args=[uuid.uuid4()])
        self.assertEqual(self.client.post(url).status_code, status.HTTP_404_NOT_FOUND)

    # ---------- CSRF (session sungguhan, bukan force_authenticate) ----------
    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Education.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")  # Browsable API memasang cookie CSRF
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EducationPageUsesApiTest(TestCase):
    """Halaman /education/ harus memakai endpoint DRF dan tetap menjaga flag hak akses."""

    def test_page_points_to_api_and_keeps_flags(self):
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("api:education-list"))
        self.assertContains(response, 'const CAN_ADD = "false"')
        self.assertContains(response, 'const CAN_CHANGE = "false"')
        self.assertContains(response, 'const CAN_DELETE = "false"')
        self.assertContains(response, 'const IS_AUTHENTICATED = "false"')
        self.assertContains(response, "Belum ada riwayat pendidikan yang ditambahkan.")
        self.assertContains(response, "csrfmiddlewaretoken")  # supaya cookie csrftoken selalu dibuat