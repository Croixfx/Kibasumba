from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

LANGUAGE_CHOICES = [
    ("rw", "Kinyarwanda"),
    ("en", "English"),
]

ROLE_CHOICES = [
    ("woman", "Umubyeyi"),  # pregnant woman, Flutter app user
    ("midwife", "Umuganga/Umuforomo"),  # fills patient records
    ("chw", "Umujyanama w'Ubuzima"),  # community health worker
    ("admin", "Umuyobozi"),  # full system access
]


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Users must have a phone number")
        extra_fields.setdefault("role", "woman")
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_midwife(self, phone_number, password, **extra_fields):
        extra_fields["role"] = "midwife"
        extra_fields.setdefault("is_staff", True)
        return self.create_user(phone_number, password, **extra_fields)

    def create_chw(self, phone_number, password, **extra_fields):
        extra_fields["role"] = "chw"
        return self.create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields["role"] = "admin"
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=150, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    preferred_language = models.CharField(
        max_length=2, choices=LANGUAGE_CHOICES, default="rw"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="woman")
    is_phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # Required by AbstractBaseUser for Django admin access.
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.phone_number} ({self.role})"


class OTPCode(models.Model):
    # Not a FK — the OTP can exist before the user account does.
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def __str__(self):
        return f"{self.phone_number} - {self.code}"
