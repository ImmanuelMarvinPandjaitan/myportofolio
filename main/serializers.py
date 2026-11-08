from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Education, Experience


class EducationSerializer(serializers.ModelSerializer):
    # field hanya-baca: dihitung server, tidak pernah diterima dari klien
    level_display = serializers.CharField(source="get_level_display", read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Education
        # daftar field ditulis eksplisit (whitelist): relasi "stars" mentah tidak
        # ikut diekspos, jadi id/akun pemberi star tidak bocor lewat API
        fields = [
            "id", "institution", "level", "level_display", "major",
            "started_at", "ended_at", "is_ongoing",
            "star_count", "is_starred",
        ]
        read_only_fields = ["id"]

    # padanan clean_institution / clean_major di EducationForm. Serializer tidak
    # menjalankan form, jadi aturan yang sama harus ditulis ulang di sini.
    def validate_institution(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Nama institusi tidak boleh kosong.")
        return value

    def validate_major(self, value):
        return strip_tags(value).strip()

    def validate(self, attrs):
        # pada PATCH salah satu tanggal bisa tidak dikirim, jadi ambil dari instance
        started_at = attrs.get("started_at", getattr(self.instance, "started_at", None))
        ended_at = attrs.get("ended_at", getattr(self.instance, "ended_at", None))
        if started_at and ended_at and ended_at < started_at:
            raise serializers.ValidationError(
                {"ended_at": "Tanggal selesai tidak boleh sebelum tanggal mulai."}
            )
        return attrs

    def get_star_count(self, obj):
        return len(obj.stars.all())

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return any(user.pk == request.user.pk for user in obj.stars.all())

    

class ExperienceSerializer(serializers.ModelSerializer):
    # field hanya-baca: dihitung server, tidak pernah diterima dari klien
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    # <input type="date"> mengirim "YYYY-MM-DD", sedangkan DateTimeField DRF bawaan
    # hanya menerima ISO 8601 lengkap. Terima keduanya; null = masih berlangsung.
    ended_at = serializers.DateTimeField(
        required=False, allow_null=True, input_formats=["iso-8601", "%Y-%m-%d"],
    )

    class Meta:
        model = Experience
        # whitelist eksplisit: relasi "stars" mentah (daftar id user) tidak diekspos
        fields = [
            "id", "title", "description", "category", "category_display",
            "thumbnail", "started_at", "ended_at", "is_ongoing",
            "star_count", "is_starred",
        ]
        # started_at auto_now_add: diisi saat dibuat, klien tidak boleh menentukannya
        read_only_fields = ["id", "started_at"]

    # padanan clean_title / clean_description di ExperienceForm (Tugas 5)
    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Judul pengalaman tidak boleh kosong.")
        return value

    def validate_description(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Deskripsi tidak boleh kosong.")
        return value

    def get_star_count(self, obj):
        return len(obj.stars.all())

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return any(user.pk == request.user.pk for user in obj.stars.all())