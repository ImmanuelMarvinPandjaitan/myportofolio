from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrEditorOrReadOnly(BasePermission):
    """
    Memetakan 4 peran Tugas 4 ke API tanpa mengubah aturannya:
    - semua orang boleh membaca (GET/HEAD/OPTIONS)
    - tulis memakai Django permission yang sama dengan view HTML Tugas 4:
        POST -> add_education, PUT/PATCH -> change_education, DELETE -> delete_education
    Superuser otomatis lolos semua (has_perm), Editor (grup dengan izin
    change_education saja) hanya lolos PUT/PATCH, pengguna biasa tidak lolos apa pun.
    """

    message = "Kamu tidak memiliki izin untuk melakukan tindakan ini."

    method_permissions = {
        "POST": "main.add_education",
        "PUT": "main.change_education",
        "PATCH": "main.change_education",
        "DELETE": "main.delete_education",
    }

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        required = self.method_permissions.get(request.method)
        user = request.user
        return bool(required and user.is_authenticated and user.has_perm(required))