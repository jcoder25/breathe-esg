# Tradeoffs — Three Things I Deliberately Did Not Build

## 1. Role-based access control (RBAC)

I did not build separate roles for uploaders vs reviewers vs auditors.
Currently any logged-in user can upload and approve.

Why not: Implementing RBAC correctly requires careful permission 
modeling. A half-built RBAC is worse than none — it gives false 
confidence. The data model supports it (uploaded_by and reviewed_by 
are separate fields) so it can be added without schema changes.

What I'd build next: An uploader role cannot approve their own uploads.
An auditor role gets read-only access to locked records only.

## 2. Duplicate detection

I did not build logic to detect if the same file is uploaded twice,
or if rows overlap with existing records for the same period.

Why not: Duplicate detection requires defining what "same" means —
same meter ID + same period? Same plant + same material + same date?
This varies per source type and needs PM input on business rules.
Getting it wrong silently drops valid data, which is worse than 
flagging it for human review.

What I'd build next: A hash of (client_id + source_type + period + 
key identifier) checked on ingest, with duplicate flagging rather 
than silent rejection.

## 3. Supplier-specific emission factors

I used DEFRA 2023 grid average for electricity instead of 
location-specific or supplier-specific factors.

Why not: A client in Karnataka uses BESCOM power which has a 
different grid intensity than UK average. Getting accurate 
location-specific factors requires either a factors database or 
client configuration. This is a significant data problem.

What I'd build next: An EmissionFactor table per client with 
effective dates, allowing overrides at the meter or plant level.