from rest_framework import serializers
from .models import Client, IngestionBatch, RawRecord, EmissionRecord, Flag, AuditLog


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class IngestionBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionBatch
        fields = '__all__'


class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        fields = '__all__'


class EmissionRecordSerializer(serializers.ModelSerializer):
    flags = FlagSerializer(many=True, read_only=True)
    source_type = serializers.CharField(source='batch.source_type', read_only=True)

    class Meta:
        model = EmissionRecord
        fields = '__all__'


class AuditLogSerializer(serializers.ModelSerializer):
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'