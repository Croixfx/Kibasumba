from rest_framework import serializers

from .models import ANCVisit, Pregnancy


class PregnancySerializer(serializers.ModelSerializer):
    current_week = serializers.IntegerField(read_only=True)

    class Meta:
        model = Pregnancy
        fields = [
            "id",
            "full_name",
            "age",
            "gravida",
            "parity",
            "lmp_date",
            "is_lmp_estimated",
            "edd_date",
            "is_active",
            "province",
            "district",
            "hospital",
            "health_centre",
            "health_post",
            "iron_folic_given",
            "iron_folic_date",
            "mebendazole_given",
            "mebendazole_date",
            "mms_given",
            "mms_date",
            "mosquito_net_given",
            "mosquito_net_date",
            "current_week",
            "created_at",
            "updated_at",
        ]
        # edd_date is always recalculated server-side from lmp_date.
        read_only_fields = ["id", "edd_date", "is_active", "created_at", "updated_at"]

    def validate_gravida(self, value):
        if value < 1:
            raise serializers.ValidationError("Gravida must be at least 1.")
        return value

    def validate(self, attrs):
        # On PATCH, fall back to the existing values for fields not sent.
        gravida = attrs.get("gravida", getattr(self.instance, "gravida", None))
        parity = attrs.get("parity", getattr(self.instance, "parity", None))
        if gravida is not None and parity is not None and parity >= gravida:
            raise serializers.ValidationError(
                {"parity": "Parity must be strictly less than gravida."}
            )
        return attrs


class ANCVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ANCVisit
        fields = [
            "id",
            "visit_number",
            "visit_date",
            "mother_weight_kg",
            "mother_height_cm",
            "fetal_position",
            "fetal_heartbeat",
            "next_visit_date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_visit_number(self, value):
        if not 1 <= value <= 8:
            raise serializers.ValidationError("Visit number must be 1-8.")
        return value
