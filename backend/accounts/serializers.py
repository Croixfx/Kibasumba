import re

from rest_framework import serializers

# Simple, deliberately loose Rwandan phone format: +250XXXXXXXXX (12 digits
# after the +) or 07XXXXXXXX (10 digits starting with 07).
PHONE_REGEX = re.compile(r"^(\+250\d{9}|07\d{8})$")


def validate_phone_number(value):
    if not PHONE_REGEX.match(value):
        raise serializers.ValidationError(
            "Enter a valid Rwandan phone number, e.g. +2507XXXXXXXX or 07XXXXXXXX."
        )
    return value


def validate_password_length(value):
    if len(value) < 6:
        raise serializers.ValidationError("Password must be at least 6 characters.")
    return value


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15, validators=[validate_phone_number]
    )


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15, validators=[validate_phone_number]
    )
    code = serializers.CharField(max_length=6)


class SetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15, validators=[validate_phone_number]
    )
    password = serializers.CharField(validators=[validate_password_length])


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15, validators=[validate_phone_number]
    )
    password = serializers.CharField()


class CreateWomanSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15, validators=[validate_phone_number]
    )
    full_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True, default=""
    )


class CreateStaffSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15, validators=[validate_phone_number]
    )
    # Women self-register via OTP; staff accounts are created here.
    role = serializers.ChoiceField(choices=["midwife", "chw", "admin"])
    full_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True, default=""
    )
