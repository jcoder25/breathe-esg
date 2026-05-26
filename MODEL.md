# Data Model

## Overview
The data model is designed around three concerns: multi-tenancy, 
source-of-truth preservation, and audit readiness. Every record 
traces back to the file that produced it, the client it belongs to, 
and every human decision made on it.

## Models

### Client
Represents an enterprise client onboarded to the platform.
Every other model links to Client via foreign key.
This is how multi-tenancy works - all queries are scoped by client_id.

### IngestionBatch
Created once per file upload. Tracks who uploaded what file, when,
for which client, and whether parsing succeeded or failed.
Purpose: if a bad file is uploaded, you delete the batch and all
its records together. You never hunt for individual rows.

Fields of note:
- source_type: sap | utility | travel
- status: processing → completed | failed
- row_count / error_count: how many rows parsed vs failed

### RawRecord
Stores the original row from the uploaded file as a JSONField,
untouched. This is the source of truth. If an auditor asks
"what did the original file say?", we show them this.
Parse errors are stored here too — a row that failed parsing
still gets a RawRecord with parse_status=error.

### EmissionRecord
The normalized, audit-ready version of a RawRecord.
One RawRecord produces exactly one EmissionRecord.

Key design decisions:
- activity_value + activity_unit: original measurement before conversion
  (e.g. 5000 litres, 45200 kWh, 1148 km)
- normalized_kgco2e: final emission in kg CO2 equivalent
- emission_factor + emission_factor_source: the multiplier used and
  where it came from (DEFRA 2023). Stored per-record so the
  calculation is always reproducible.
- period_start / period_end: billing period, not upload date.
  Utility bills span 28-35 days, not calendar months.
- review_status: pending → flagged → approved | rejected → locked
- is_locked: once True, no edits permitted. Set on approval.
- is_edited: True if a human changed any field after ingestion.

### Scope Classification
- Scope 1 (Direct): fuel combustion from SAP data
- Scope 2 (Indirect): purchased electricity from utility data  
- Scope 3 (Value chain): business travel from Concur/Navan data

### Flag
Auto-generated when a record exceeds category thresholds:
- fuel_combustion > 50,000 kgCO2e
- purchased_electricity > 100,000 kgCO2e  
- business_travel_air > 10,000 kgCO2e

Flags change review_status to 'flagged' automatically.
A human must resolve flagged records before approval.

### AuditLog
Every field change is recorded: who changed it, when, 
old value, new value. Append-only -  logs are never deleted.
Once a record is locked (approved), no new audit logs can be created.

## Multi-tenancy
All queries in views.py filter by client. The frontend passes 
client_id on every upload. In a production system this would be 
enforced at the ORM level via a base queryset.

## Unit Normalization
All emissions normalize to kgCO2e using DEFRA 2023 factors:
- Diesel: 2.68 kgCO2e/litre
- Petrol: 2.31 kgCO2e/litre  
- Natural Gas: 2.04 kgCO2e/kg
- Electricity: 0.233 kgCO2e/kWh (UK grid average)
- Short-haul flight (<3700km): 0.255 kgCO2e/km/passenger
- Long-haul flight (>3700km): 0.195 kgCO2e/km/passenger
- Hotel: 31.0 kgCO2e/night
- Car/ground: 0.171 kgCO2e/km