"""Midwife-facing endpoints backing the React admin (Sprint 4)."""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CustomUser
from accounts.permissions import IsMidwife

from .models import ANCVisit
from .serializers import ANCVisitSerializer, PregnancySerializer
from .views import get_active_pregnancy

WOMAN_NOT_FOUND_ERROR = "Nta mubyeyi ufite iyi nimero wabonetse."
NO_PREGNANCY_ERROR = "Uyu mubyeyi nta nda ifite yanditswe."


def find_woman(phone_number):
    return CustomUser.objects.filter(
        phone_number=phone_number, role="woman"
    ).first()


class WomanRecordView(APIView):
    """Everything the record panel needs for one woman, by phone number."""

    permission_classes = [IsAuthenticated, IsMidwife]

    def get(self, request):
        phone = request.query_params.get("phone", "").strip()
        woman = find_woman(phone)
        if woman is None:
            return Response(
                {"error": WOMAN_NOT_FOUND_ERROR}, status=status.HTTP_404_NOT_FOUND
            )

        pregnancy = get_active_pregnancy(woman)
        return Response(
            {
                "woman": {
                    "phone_number": woman.phone_number,
                    "full_name": woman.full_name,
                },
                "pregnancy": (
                    PregnancySerializer(pregnancy).data if pregnancy else None
                ),
                "anc_visits": ANCVisitSerializer(
                    pregnancy.anc_visits.all() if pregnancy else [], many=True
                ).data,
            }
        )


class CreateOrUpdatePregnancyView(APIView):
    """Save Section A of the record panel: create the woman's active
    pregnancy if she has none, update it otherwise."""

    permission_classes = [IsAuthenticated, IsMidwife]

    def post(self, request):
        data = request.data.copy()
        woman = find_woman(data.pop("phone_number", ""))
        if woman is None:
            return Response(
                {"error": WOMAN_NOT_FOUND_ERROR}, status=status.HTTP_404_NOT_FOUND
            )

        pregnancy = get_active_pregnancy(woman)
        serializer = PregnancySerializer(
            pregnancy, data=data, partial=pregnancy is not None
        )
        serializer.is_valid(raise_exception=True)
        saved = serializer.save(woman=woman, is_active=True)
        return Response(
            PregnancySerializer(saved).data,
            status=status.HTTP_200_OK if pregnancy else status.HTTP_201_CREATED,
        )


class ANCVisitUpsertView(APIView):
    """Save one row of the ANC visits table. Saving the same visit_number
    again updates the existing row instead of duplicating it."""

    permission_classes = [IsAuthenticated, IsMidwife]

    def post(self, request):
        data = request.data.copy()
        woman = find_woman(data.pop("phone_number", ""))
        if woman is None:
            return Response(
                {"error": WOMAN_NOT_FOUND_ERROR}, status=status.HTTP_404_NOT_FOUND
            )
        pregnancy = get_active_pregnancy(woman)
        if pregnancy is None:
            return Response(
                {"error": NO_PREGNANCY_ERROR}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ANCVisitSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        fields = dict(serializer.validated_data)
        visit_number = fields.pop("visit_number")
        visit, created = ANCVisit.objects.update_or_create(
            pregnancy=pregnancy, visit_number=visit_number, defaults=fields
        )
        return Response(
            ANCVisitSerializer(visit).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
