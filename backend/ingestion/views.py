from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Client, IngestionBatch, RawRecord, EmissionRecord, Flag, AuditLog
from .serializers import ClientSerializer, IngestionBatchSerializer, EmissionRecordSerializer, AuditLogSerializer
from .parsers import parse_sap_file, parse_utility_file, parse_travel_file


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        print(f"Login attempt: {username}")  # debug
        user = authenticate(request, username=username, password=password)
        print(f"Auth result: {user}")  # debug
        if user:
            login(request, user)
            return Response({'message': 'Login successful', 'username': user.username})
        return Response({'error': 'Invalid credentials'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out'})


class MeView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response({'username': request.user.username, 'id': request.user.id})
        return Response({'username': '', 'id': None})

# ---- Client Views ----

class ClientListView(APIView):
    def get(self, request):
        clients = Client.objects.all()
        return Response(ClientSerializer(clients, many=True).data)

    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# ---- Ingestion Views ----

PARSER_MAP = {
    'sap': parse_sap_file,
    'utility': parse_utility_file,
    'travel': parse_travel_file,
}

FLAG_THRESHOLDS = {
    'fuel_combustion': 50000,
    'purchased_electricity': 100000,
    'business_travel_air': 10000,
    'business_travel_hotel': 5000,
    'business_travel_ground': 2000,
}


def auto_flag(emission_record):
    """Automatically flag suspicious records."""
    threshold = FLAG_THRESHOLDS.get(emission_record.category, 99999)
    if emission_record.normalized_kgco2e > threshold:
        Flag.objects.create(
            emission_record=emission_record,
            reason='high_value',
            detail=f'Value {emission_record.normalized_kgco2e:.2f} kgCO2e exceeds threshold {threshold}',
            auto_flagged=True,
        )
        emission_record.review_status = 'flagged'
        emission_record.save()


class IngestFileView(APIView):
    def post(self, request):
        source_type = request.data.get('source_type')
        client_id = request.data.get('client_id')
        file = request.FILES.get('file')

        if not all([source_type, client_id, file]):
            return Response({'error': 'source_type, client_id and file are required'}, status=400)

        if source_type not in PARSER_MAP:
            return Response({'error': 'Invalid source_type'}, status=400)

        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({'error': 'Client not found'}, status=404)

        # Create batch
        batch = IngestionBatch.objects.create(
            client=client,
            source_type=source_type,
            uploaded_by=request.user if request.user.is_authenticated else None,
            file_name=file.name,
            status='processing',
        )

        try:
            parser = PARSER_MAP[source_type]
            records, errors = parser(file)

            for i, rec in enumerate(records):
                raw = RawRecord.objects.create(
                    batch=batch,
                    row_number=i + 1,
                    raw_data=rec['raw'],
                    parse_status='ok',
                )
                emission = EmissionRecord.objects.create(
                    client=client,
                    batch=batch,
                    raw_record=raw,
                    scope=rec['scope'],
                    category=rec['category'],
                    activity_value=rec['activity_value'],
                    activity_unit=rec['activity_unit'],
                    normalized_kgco2e=rec['normalized_kgco2e'],
                    emission_factor=rec['emission_factor'],
                    emission_factor_source=rec['emission_factor_source'],
                    period_start=rec['period_start'],
                    period_end=rec['period_end'],
                    description=rec['description'],
                )
                auto_flag(emission)

            for err in errors:
                RawRecord.objects.create(
                    batch=batch,
                    row_number=err['row'],
                    raw_data=err.get('raw', {}),
                    parse_status='error',
                    parse_error=err['error'],
                )

            batch.status = 'completed'
            batch.row_count = len(records)
            batch.error_count = len(errors)
            batch.save()

            return Response({
                'batch_id': batch.id,
                'rows_ingested': len(records),
                'errors': len(errors),
            }, status=201)

        except Exception as e:
            batch.status = 'failed'
            batch.save()
            return Response({'error': str(e)}, status=500)


class BatchListView(APIView):
    def get(self, request):
        batches = IngestionBatch.objects.all().order_by('-uploaded_at')
        return Response(IngestionBatchSerializer(batches, many=True).data)


# ---- Review Views ----

class EmissionRecordListView(APIView):
    def get(self, request):
        import math
        qs = EmissionRecord.objects.all().order_by('-created_at')

        status_filter = request.query_params.get('status')
        client_filter = request.query_params.get('client_id')
        scope_filter = request.query_params.get('scope')
        source_filter = request.query_params.get('source_type')

        if status_filter:
            qs = qs.filter(review_status=status_filter)
        if client_filter:
            qs = qs.filter(client_id=client_filter)
        if scope_filter:
            qs = qs.filter(scope=scope_filter)
        if source_filter:
            qs = qs.filter(batch__source_type=source_filter)

        # Fix any NaN values before serializing
        data = EmissionRecordSerializer(qs, many=True).data
        for row in data:
            for key, val in row.items():
                if isinstance(val, float) and math.isnan(val):
                    row[key] = None

        return Response(data)


class EmissionRecordDetailView(APIView):
    def get(self, request, pk):
        try:
            record = EmissionRecord.objects.get(pk=pk)
            return Response(EmissionRecordSerializer(record).data)
        except EmissionRecord.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

    def patch(self, request, pk):
        try:
            record = EmissionRecord.objects.get(pk=pk)
        except EmissionRecord.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        if record.is_locked:
            return Response({'error': 'Record is locked and cannot be edited'}, status=403)

        # Track changes in audit log
        editable_fields = ['activity_value', 'activity_unit', 'normalized_kgco2e', 'description']
        for field in editable_fields:
            if field in request.data:
                old_value = str(getattr(record, field))
                new_value = str(request.data[field])
                if old_value != new_value:
                    AuditLog.objects.create(
                        emission_record=record,
                        changed_by=request.user,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                    )
                    setattr(record, field, request.data[field])
                    record.is_edited = True

        record.save()
        return Response(EmissionRecordSerializer(record).data)


class ApproveRecordView(APIView):
    def post(self, request, pk):
        try:
            record = EmissionRecord.objects.get(pk=pk)
        except EmissionRecord.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        if record.is_locked:
            return Response({'error': 'Already locked'}, status=403)

        record.review_status = 'approved'
        record.reviewed_by = request.user if request.user.is_authenticated else None
        record.reviewed_at = timezone.now()
        record.is_locked = True
        record.save()

        AuditLog.objects.create(
            emission_record=record,
            changed_by=request.user if request.user.is_authenticated else None,
            field_name='review_status',
            old_value='pending',
            new_value='approved',
        )

        return Response({'message': 'Record approved and locked'})


class RejectRecordView(APIView):
    def post(self, request, pk):
        try:
            record = EmissionRecord.objects.get(pk=pk)
        except EmissionRecord.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        record.review_status = 'rejected'
        record.reviewed_by = request.user if request.user.is_authenticated else None
        record.reviewed_at = timezone.now()
        record.save()

        return Response({'message': 'Record rejected'})

class DashboardStatsView(APIView):
    def get(self, request):
        try:
            from django.db.models import Sum, Count
            from django.db.models.functions import Coalesce
            from django.db.models import FloatField, Value

            total = EmissionRecord.objects.count()
            pending = EmissionRecord.objects.filter(review_status='pending').count()
            flagged = EmissionRecord.objects.filter(review_status='flagged').count()
            approved = EmissionRecord.objects.filter(review_status='approved').count()
            rejected = EmissionRecord.objects.filter(review_status='rejected').count()

            by_scope = list(
                EmissionRecord.objects.values('scope').annotate(
                    total_kgco2e=Coalesce(
                        Sum('normalized_kgco2e'),
                        Value(0.0),
                        output_field=FloatField()
                    ),
                    count=Count('id')
                )
            )

            by_source = list(
                EmissionRecord.objects.values('batch__source_type').annotate(
                    total_kgco2e=Coalesce(
                        Sum('normalized_kgco2e'),
                        Value(0.0),
                        output_field=FloatField()
                    ),
                    count=Count('id')
                )
            )

            return Response({
                'total': total,
                'pending': pending,
                'flagged': flagged,
                'approved': approved,
                'rejected': rejected,
                'by_scope': by_scope,
                'by_source': by_source,
            })

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=500)
        
        
class AuditLogView(APIView):
    def get(self, request, pk):
        logs = AuditLog.objects.filter(emission_record_id=pk).order_by('-changed_at')
        return Response(AuditLogSerializer(logs, many=True).data)