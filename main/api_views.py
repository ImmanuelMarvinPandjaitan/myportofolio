from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from main.models import Education, Experience
from main.permissions import (
    IsEducationOwnerOrEditorOrReadOnly,
    IsExperienceOwnerOrEditorOrReadOnly,
)
from main.serializers import EducationSerializer, ExperienceSerializer


# ======================= Education (Tutorial 07) =======================

@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsEducationOwnerOrEditorOrReadOnly])
def education_list(request):
    if request.method in ("GET", "HEAD"):
        educations = Education.objects.prefetch_related("stars").order_by("started_at", "id")
        institution = request.query_params.get("institution", "").strip()
        if institution:
            educations = educations.filter(institution__icontains=institution)

        serializer = EducationSerializer(
            educations, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = EducationSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsEducationOwnerOrEditorOrReadOnly])
def education_detail(request, education_id):
    education = get_object_or_404(
        Education.objects.prefetch_related("stars"), pk=education_id,
    )

    if request.method in ("GET", "HEAD"):
        serializer = EducationSerializer(education, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        education.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = EducationSerializer(
        education, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])  # semua akun login boleh star, bukan cuma pemilik/editor
def education_star(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    # akun yang memberi star selalu request.user, klien tidak bisa memilih akun lain
    if education.stars.filter(pk=request.user.pk).exists():
        education.stars.remove(request.user)
    else:
        education.stars.add(request.user)

    serializer = EducationSerializer(education, context={"request": request})
    return Response(serializer.data)


# ======================= Experience (Tugas 6) =======================

@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsExperienceOwnerOrEditorOrReadOnly])
def experience_list(request):
    if request.method in ("GET", "HEAD"):
        experiences = Experience.objects.prefetch_related("stars").order_by("started_at", "id")
        # pencarian dari Tugas 5 dipindahkan jadi parameter query: ?title=...
        title = request.query_params.get("title", "").strip()
        if title:
            experiences = experiences.filter(title__icontains=title)

        serializer = ExperienceSerializer(
            experiences, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ExperienceSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsExperienceOwnerOrEditorOrReadOnly])
def experience_detail(request, experience_id):
    experience = get_object_or_404(
        Experience.objects.prefetch_related("stars"), pk=experience_id,
    )

    if request.method in ("GET", "HEAD"):
        serializer = ExperienceSerializer(experience, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        experience.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ExperienceSerializer(
        experience, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def experience_star(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if experience.stars.filter(pk=request.user.pk).exists():
        experience.stars.remove(request.user)
    else:
        experience.stars.add(request.user)

    serializer = ExperienceSerializer(experience, context={"request": request})
    return Response(serializer.data)