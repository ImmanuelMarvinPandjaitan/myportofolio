from rest_framework.permissions import SAFE_METHODS, BasePermission


class ModelRolePermission(BasePermission):
    """
    Basis permission 4 peran Tugas 4 untuk API, memakai Django permission yang
    sama dengan view HTML (add_/change_/delete_<model>). Subclass cukup mengisi
    `model_name`, sehingga aturan peran ditulis sekali dan dipakai banyak model.

    - semua orang boleh membaca (GET/HEAD/OPTIONS)
    - POST -> add_<model>, PUT/PATCH -> change_<model>, DELETE -> delete_<model>
    - superuser otomatis lolos semua (has_perm); Editor (grup dengan izin
      change_<model> saja) hanya lolos PUT/PATCH; pengguna biasa tidak lolos apa pun
    """

    app_label = "main"
    model_name = None  # wajib diisi subclass, mis. "education"
    message = "Kamu tidak memiliki izin untuk melakukan tindakan ini."

    method_actions = {
        "POST": "add",
        "PUT": "change",
        "PATCH": "change",
        "DELETE": "delete",
    }

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        action = self.method_actions.get(request.method)
        user = request.user
        if action is None or not user.is_authenticated:
            return False
        return user.has_perm(f"{self.app_label}.{action}_{self.model_name}")


class IsEducationOwnerOrEditorOrReadOnly(ModelRolePermission):
    model_name = "education"


class IsExperienceOwnerOrEditorOrReadOnly(ModelRolePermission):
    model_name = "experience"