import calendar
from datetime import date, timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Pregnancy(models.Model):
    # A pregnancy belongs to a woman, not generically to a user.
    woman = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pregnancies",
        limit_choices_to={"role": "woman"},
    )
    full_name = models.CharField(max_length=150)
    age = models.PositiveSmallIntegerField()
    gravida = models.PositiveSmallIntegerField()
    parity = models.PositiveSmallIntegerField()
    lmp_date = models.DateField()
    is_lmp_estimated = models.BooleanField(default=False)
    # Always derived from lmp_date on save; never accepted from the client.
    edd_date = models.DateField()
    is_active = models.BooleanField(default=True)

    # Facility fields are plain text for the MVP. They are chosen from
    # hardcoded lists on the client; once MINISANTE integration is approved
    # these become references to their facility registry.
    province = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    hospital = models.CharField(max_length=150, blank=True)
    health_centre = models.CharField(max_length=150, blank=True)
    health_post = models.CharField(max_length=150, blank=True)

    # Provisions handed out at ANC visits (filled by the midwife from the
    # React admin; read-only in the Flutter app).
    iron_folic_given = models.BooleanField(default=False)
    iron_folic_date = models.DateField(null=True, blank=True)
    mebendazole_given = models.BooleanField(default=False)
    mebendazole_date = models.DateField(null=True, blank=True)
    mms_given = models.BooleanField(default=False)
    mms_date = models.DateField(null=True, blank=True)
    mosquito_net_given = models.BooleanField(default=False)
    mosquito_net_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def calculate_edd(lmp_date):
        """
        Naegele's rule: LMP + 7 days, then month +9 (same year) if the
        result falls in Jan-Mar, otherwise month -3 and year +1.
        """
        base = lmp_date + timedelta(days=7)
        if base.month <= 3:
            month, year = base.month + 9, base.year
        else:
            month, year = base.month - 3, base.year + 1
        # Clamp the day for shorter target months (e.g. 31 Dec + 7 days
        # would otherwise produce 31 Sep, which does not exist).
        day = min(base.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    @property
    def current_week(self):
        return (timezone.localdate() - self.lmp_date).days // 7

    def save(self, *args, **kwargs):
        self.edd_date = self.calculate_edd(self.lmp_date)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.woman.phone_number})"


class ANCVisit(models.Model):
    """One row of the paper ANC card: up to 8 visits per pregnancy."""

    pregnancy = models.ForeignKey(
        Pregnancy,
        on_delete=models.CASCADE,
        related_name="anc_visits",
    )
    visit_number = models.PositiveSmallIntegerField()  # 1-8
    visit_date = models.DateField(null=True, blank=True)
    mother_weight_kg = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    mother_height_cm = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    fetal_position = models.CharField(max_length=100, blank=True)
    fetal_heartbeat = models.CharField(max_length=50, blank=True)
    next_visit_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("pregnancy", "visit_number")
        ordering = ["visit_number"]

    def __str__(self):
        return f"Visit {self.visit_number} of {self.pregnancy}"
