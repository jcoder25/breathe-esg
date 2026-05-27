# Breathe ESG — Emissions Ingestion & Review Platform

A deployed prototype built for the Breathe ESG Tech Intern Assignment.

This platform ingests emissions/activity data from multiple enterprise data sources, normalizes it into audit-ready emission records, and provides an analyst review workflow for approval before audit lock.

---

## Live Deployment

### Frontend
https://breathe-esg-1-o9is.onrender.com/

### Backend API
https://breathe-esg-e40y.onrender.com/

### Admin Console
https://breathe-esg-e40y.onrender.com/admin/

---

## Demo Credentials

**Username:** admin  
**Password:** admin123

---

## Problem Statement

Enterprise sustainability data arrives in inconsistent formats:

- SAP fuel/procurement exports
- Utility electricity exports
- Corporate travel platform reports

This system:

1. Ingests source files
2. Normalizes units and structures
3. Classifies Scope 1 / 2 / 3 emissions
4. Flags suspicious records
5. Enables analyst review
6. Locks approved rows for audit traceability

---

## Supported Sources

### 1. SAP Fuel & Procurement
Flat file CSV exports (MB51 / ME2M style)

Handles:
- Diesel
- Petrol
- Natural gas
- Unit normalization
- Plant-based source tracking

---

### 2. Utility Electricity
Portal CSV exports

Handles:
- Meter-based electricity consumption
- Billing period tracking
- kWh normalization
- Scope 2 classification

---

### 3. Corporate Travel
Concur/Navan style CSV exports

Handles:
- Flights
- Hotels
- Ground transport
- Distance normalization
- Scope 3 classification

---

## Core Features

### Data Ingestion
Upload source CSVs by client

### Multi-Tenant Architecture
Client-scoped records and batches

### Review Workflow
Pending → Flagged → Approved → Locked

### Audit Trail
Source-of-truth preservation via RawRecord + AuditLog

### Dashboard Analytics
Visual emissions breakdown by:

- Scope
- Source type
- Review status

---

## Tech Stack

### Backend
- Django
- Django REST Framework
- PostgreSQL
- WhiteNoise
- Render

### Frontend
- React
- Vite
- Axios
- Recharts

---

## Data Model

Core models:

- Client
- IngestionBatch
- RawRecord
- EmissionRecord
- AuditLog

Detailed rationale in:

- MODEL.md
- DECISIONS.md
- TRADEOFFS.md
- SOURCES.md

---

## Sample Test Data

Sample CSV files are included for evaluator testing.

Location:

sample-data/

Files:

- sap_sample.csv
- utility_sample.csv
- travel_sample.csv

These files represent realistic enterprise onboarding exports and can be uploaded directly through the deployed application to test ingestion, normalization, dashboard aggregation, and analyst review workflow.



## Local Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

cd frontend
npm install
npm run dev