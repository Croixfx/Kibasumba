import random
import secrets
import string
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser, OTPCode
from .permissions import IsAdmin, IsMidwife
from .serializers import (
    CreateStaffSerializer,
    CreateWomanSerializer,
    LoginSerializer,
    RequestOTPSerializer,
    SetPasswordSerializer,
    VerifyOTPSerializer,
)
from .sms import send_sms


def generate_temp_password():
    return "".join(
        secrets.choice(string.ascii_letters + string.digits) for _ in range(8)
    )

OTP_VALIDITY_MINUTES = 5
OTP_RATE_LIMIT_WINDOW_MINUTES = 10
OTP_RATE_LIMIT_MAX = 3


class RequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]

        window_start = timezone.now() - timedelta(minutes=OTP_RATE_LIMIT_WINDOW_MINUTES)
        recent_count = OTPCode.objects.filter(
            phone_number=phone_number, created_at__gte=window_start
        ).count()
        if recent_count >= OTP_RATE_LIMIT_MAX:
            return Response(
                {"error": "Too many OTP requests. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        code = f"{random.randint(0, 999999):06d}"
        now = timezone.now()
        OTPCode.objects.create(
            phone_number=phone_number,
            code=code,
            expires_at=now + timedelta(minutes=OTP_VALIDITY_MINUTES),
        )
        send_sms(phone_number, f"Your kibasumba verification code is {code}. It expires in 5 minutes.")

        return Response({"message": "OTP sent"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]

        otp = (
            OTPCode.objects.filter(phone_number=phone_number, code=code, is_used=False)
            .order_by("-created_at")
            .first()
        )
        if otp is None or not otp.is_valid():
            return Response(
                {"error": "Invalid or expired OTP code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        # Self-registering users via OTP are always women.
        woman, _ = CustomUser.objects.get_or_create(
            phone_number=phone_number, defaults={"role": "woman"}
        )
        if not woman.is_phone_verified:
            woman.is_phone_verified = True
            woman.save(update_fields=["is_phone_verified"])

        return Response(
            {"message": "Phone verified", "phone_number": phone_number},
            status=status.HTTP_200_OK,
        )


class SetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        password = serializer.validated_data["password"]

        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if user is None or not user.is_phone_verified:
            return Response(
                {"error": "Phone number is not verified yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(password)
        user.save(update_fields=["password"])

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "phone_number": phone_number},
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        password = serializer.validated_data["password"]

        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if user is None or not user.check_password(password):
            return Response(
                {"error": "Invalid phone number or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "phone_number": phone_number},
            status=status.HTTP_200_OK,
        )


class CreateStaffView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = CreateStaffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        role = serializer.validated_data["role"]
        full_name = serializer.validated_data["full_name"]

        if CustomUser.objects.filter(phone_number=phone_number).exists():
            return Response(
                {"error": "A user with this phone number already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        temp_password = generate_temp_password()
        create_by_role = {
            "midwife": CustomUser.objects.create_midwife,
            "chw": CustomUser.objects.create_chw,
            "admin": CustomUser.objects.create_superuser,
        }
        create_by_role[role](
            phone_number,
            temp_password,
            full_name=full_name,
            is_phone_verified=True,
        )

        send_sms(
            phone_number,
            f"Konti yawe ya kibasumba yakozwe. Ijambo ry'ibanga ry'agateganyo: "
            f"{temp_password}",
        )

        # The temp password travels only by SMS, never in the response.
        return Response(
            {
                "message": "Staff account created",
                "phone_number": phone_number,
                "role": role,
            },
            status=status.HTTP_201_CREATED,
        )


class CreateWomanView(APIView):
    """Midwife registers a woman at the clinic (Sprint 4 React admin)."""

    permission_classes = [IsAuthenticated, IsMidwife]

    def post(self, request):
        serializer = CreateWomanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        full_name = serializer.validated_data["full_name"]

        existing = CustomUser.objects.filter(phone_number=phone_number).first()
        if existing is not None:
            if existing.role != "woman":
                return Response(
                    {"error": "Iyi nimero ni iy'umukozi w'ubuzima, si umubyeyi."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return Response(
                {
                    "already_exists": True,
                    "phone_number": existing.phone_number,
                    "full_name": existing.full_name,
                },
                status=status.HTTP_200_OK,
            )

        temp_password = generate_temp_password()
        CustomUser.objects.create_user(
            phone_number,
            temp_password,
            full_name=full_name,
            is_phone_verified=True,
        )
        send_sms(
            phone_number,
            f"Konti yawe ya kibasumba yakozwe n'umuganga. "
            f"Ijambo ry'ibanga ry'agateganyo: {temp_password}",
        )

        # The temp password travels only by SMS, never in the response.
        return Response(
            {
                "already_exists": False,
                "phone_number": phone_number,
                "full_name": full_name,
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "phone_number": user.phone_number,
                "full_name": user.full_name,
                "role": user.role,
                "preferred_language": user.preferred_language,
                "is_phone_verified": user.is_phone_verified,
            }
        )
