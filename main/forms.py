from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Textarea, Select, DateInput, URLInput
from django.utils.html import strip_tags

from main.models import Education, Experience


# form buat nambahin riwayat pendidikan lewat halaman web, bukan lewat shell lagi
class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = [
            "institution",
            "level",
            "major",
            "started_at",
            "ended_at",
        ]
        labels = {
            "institution": "Nama Institusi",
            "level": "Jenjang",
            "major": "Jurusan",
            "started_at": "Mulai",
            "ended_at": "Selesai (kosongkan kalau masih berlangsung)",
        }
        widgets = {
            "institution": TextInput(
                attrs={
                    "placeholder": "Universitas Indonesia",
                    "maxlength": 255,
                }
            ),
            "level": Select(),
            "major": TextInput(
                attrs={
                    "placeholder": "Ilmu Komputer (kosongkan kalau SD/SMP)",
                }
            ),
            "started_at": DateInput(attrs={"type": "date"}),
            "ended_at": DateInput(attrs={"type": "date"}),
        }

    # lapisan pertahanan kedua (Tutorial 05): buang tag HTML sejak data masuk.
    # Ini BUKAN pengganti escaping di JavaScript saat menampilkan data,
    # cuma tambahan supaya data yang tersimpan juga lebih bersih.
    def clean_institution(self):
        institution = strip_tags(self.cleaned_data["institution"]).strip()
        if not institution:
            raise ValidationError("Nama institusi tidak boleh hanya berisi tag HTML.")
        return institution

    def clean_major(self):
        return strip_tags(self.cleaned_data["major"]).strip()


# form buat nambahin pengalaman lewat halaman web (pola sama dengan EducationForm)
class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        # started_at tidak dimasukkan: field itu auto_now_add, diisi otomatis saat dibuat
        fields = ["title", "description", "category", "thumbnail", "ended_at"]
        labels = {
            "title": "Judul Pengalaman",
            "description": "Deskripsi",
            "category": "Kategori",
            "thumbnail": "URL Gambar (opsional)",
            "ended_at": "Selesai (kosongkan kalau masih berlangsung)",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "Asisten Dosen PBP", "maxlength": 255}),
            "description": Textarea(attrs={"rows": 4}),
            "category": Select(),
            "thumbnail": URLInput(attrs={"placeholder": "https://..."}),
            "ended_at": DateInput(attrs={"type": "date"}),
        }

    # lapisan pertahanan kedua (Tutorial 05): buang tag HTML sejak data masuk
    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Judul pengalaman tidak boleh hanya berisi tag HTML.")
        return title

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()