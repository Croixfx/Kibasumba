from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsWoman

from .models import Pregnancy
from .pdf_generator import generate_ifishi_pdf
from .serializers import PregnancySerializer

ACTIVE_PREGNANCY_EXISTS_ERROR = (
    "Urashaka kwinjira inda nshya ariko ufite indi iracyahari"
)


def get_active_pregnancy(woman):
    return Pregnancy.objects.filter(woman=woman, is_active=True).first()


class CreatePregnancyView(APIView):
    permission_classes = [IsAuthenticated, IsWoman]

    def post(self, request):
        if get_active_pregnancy(request.user) is not None:
            return Response(
                {"error": ACTIVE_PREGNANCY_EXISTS_ERROR},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PregnancySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pregnancy = serializer.save(woman=request.user, is_active=True)
        return Response(
            PregnancySerializer(pregnancy).data, status=status.HTTP_201_CREATED
        )


class ActivePregnancyView(APIView):
    permission_classes = [IsAuthenticated, IsWoman]

    def get(self, request):
        pregnancy = get_active_pregnancy(request.user)
        if pregnancy is None:
            return Response(
                {"has_pregnancy": False}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(PregnancySerializer(pregnancy).data)


class UpdatePregnancyView(APIView):
    permission_classes = [IsAuthenticated, IsWoman]

    def patch(self, request):
        pregnancy = get_active_pregnancy(request.user)
        if pregnancy is None:
            return Response(
                {"has_pregnancy": False}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = PregnancySerializer(pregnancy, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        pregnancy = serializer.save()  # save() recalculates edd_date
        return Response(PregnancySerializer(pregnancy).data)


class DownloadCardView(APIView):
    """The woman downloads her official Ifishi as a PDF (Sprint 5)."""

    permission_classes = [IsAuthenticated, IsWoman]

    def get(self, request):
        pregnancy = get_active_pregnancy(request.user)
        if pregnancy is None:
            return Response(
                {"error": "Nta makuru y'inda aboneka"},
                status=status.HTTP_404_NOT_FOUND,
            )

        pdf_bytes = generate_ifishi_pdf(pregnancy, pregnancy.anc_visits.all())
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="ifishi_{request.user.phone_number}.pdf"'
        )
        return response
