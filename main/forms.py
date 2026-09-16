from django.forms import ModelForm, TextInput, Select, DateInput

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