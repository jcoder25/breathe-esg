from django.contrib import admin
from .models import Client, IngestionBatch, RawRecord, EmissionRecord, Flag, AuditLog

admin.site.register(Client)
admin.site.register(IngestionBatch)
admin.site.register(RawRecord)
admin.site.register(EmissionRecord)
admin.site.register(Flag)
admin.site.register(AuditLog)