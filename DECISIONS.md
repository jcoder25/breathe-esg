# Decisions

## SAP: Flat File CSV over IDoc/OData/BAPI

SAP supports multiple export mechanisms. I chose flat file CSV for 
these reasons:

1. IDocs are XML-based and designed for system-to-system integration.
   A sustainability analyst does not have an IDoc receiver set up.
2. OData and BAPI require live authenticated access to the SAP system.
   During client onboarding we would not have this.
3. Flat file exports via MB51 (material movements) or ME2M (purchase 
   orders) are what sustainability teams actually email to consultants.

What I handled: material movements with fuel materials (diesel, petrol,
natural gas). Plant codes, German-style dates (DD.MM.YYYY), and 
inconsistent units (L, LT, KG, M3, GAL).

What I ignored: cost center allocations, multi-currency procurement,
non-fuel materials, goods receipts vs goods issues distinction.

What I'd ask the PM: Do clients use MB51 or ME2M? Are plant codes 
mapped to locations somewhere, or do we need a lookup table?

## Utility: Portal CSV over PDF or API

1. PDF parsing is brittle — every utility formats bills differently.
   A regex that works for MSEDCL fails for BESCOM.
2. Green Button and UtilityAPI require OAuth and utility partnerships.
   Not realistic for a prototype.
3. Portal CSV exports are standard — every major utility portal 
   (Urjanet, utility websites) offers CSV download.

What I handled: meter ID, site name, billing period start/end, 
consumption in kWh (with MWh conversion), tariff code.

What I ignored: demand charges, power factor, time-of-use tariffs,
reactive power, multiple fuel types from the same meter.

What I'd ask the PM: Do all clients use the same utility portal, 
or do we need to handle multiple CSV formats?

## Travel: CSV Export over Concur/Navan API

1. Concur and Navan APIs require OAuth 2.0 with enterprise credentials.
   No realistic way to prototype this without a live account.
2. Both platforms support admin CSV exports of trip reports.
3. CSV export is what a travel manager would send us during onboarding.

What I handled: flights (with IATA code → Haversine distance 
calculation), hotels (per night), ground transport (per km).

What I ignored: rail travel, taxi/rideshare, meal expenses, 
class of travel (business vs economy has different emission factors).

What I'd ask the PM: Does the client use Concur or Navan? Do they 
have distance data in exports or only origin/destination?

## Review Workflow: pending → flagged → approved → locked

I chose a linear state machine over a free-form status field because:
- Auditors need a clear chain of custody
- Locked records cannot be edited -  this is non-negotiable for audit
- Flagging is automatic, approval is always human

## Emission Factors: DEFRA 2023

DEFRA publishes annual conversion factors used across UK carbon 
accounting. They are publicly auditable, versioned, and industry 
standard. I store the factor and source on every record so the 
calculation is independently verifiable.

Alternative considered: IPCC AR6 factors. Chose DEFRA because they 
are more granular for UK grid electricity and transport.