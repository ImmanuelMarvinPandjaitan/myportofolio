from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Select, DateInput
from django.utils.html import strip_tags

from main.models import Education


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