from main.models import Education

seen_levels = set()
for edu in Education.objects.order_by('started_at'):
    if edu.level in seen_levels:
        print("Menghapus:", edu.institution, "-", edu.level)
        edu.delete()
    else:
        seen_levels.add(edu.level)

print("Sisa data Education:")
for edu in Education.objects.order_by('started_at'):
    print("-", edu.institution, edu.level)
