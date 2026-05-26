# Sources Research

## SAP Fuel & Procurement

**Format researched:** SAP flat file export via transaction MB51 
(material document list) and ME2M (purchase orders by material).

**What I learned:**
- SAP uses numeric plant codes (1000, 2000) that map to physical 
  locations only via a plant master table
- Default date format is DD.MM.YYYY (European)
- Units use SAP internal codes: L (litre), KG (kilogram), M3 (cubic 
  metre), with some configurations using German abbreviations
- Material numbers are internal codes — descriptions come from a 
  separate material master
- Exports can have German column headers depending on system language

**Sample data rationale:**
Plants 1000, 2000, 3000 represent a head office, warehouse, and 
factory. Materials are diesel, petrol, and natural gas — the most 
common fuel types in procurement. Quantities are realistic for 
monthly industrial consumption (1000-8500 litres). One row has 
120,000 litres — intentionally unrealistic to trigger auto-flagging 
and demonstrate the review workflow.

**What would break in production:**
- Plant codes need a lookup table to map to real locations
- Non-fuel materials (lubricants, chemicals) would need filtering
- Multi-currency procurement needs exchange rate handling
- Some SAP configs export with semicolon delimiters not commas

## Utility Electricity

**Format researched:** Portal CSV export from utility management 
platforms like Urjanet, and direct utility portal exports (MSEDCL, 
BESCOM, TATA Power portals).

**What I learned:**
- Billing periods are 28-35 days, rarely aligned to calendar months
- Large consumers (factories) often have multiple meters per site
- Units are usually kWh but some industrial exports use MWh
- Tariff codes (B1, B2, HT, C1) indicate consumer category and 
  affect pricing but not emission calculation
- Some portals export demand (kW) alongside consumption (kWh)

**Sample data rationale:**
4 meters across different site types: head office (~45,000 kWh/month),
warehouse (~30,000), factory (~100,000), branch office (~18,000).
These reflect realistic consumption ratios. Factory Pune at 100,000 
kWh is the largest consumer as expected for manufacturing.

**What would break in production:**
- Different utilities use different column names and date formats
- Some portals export multiple months in one file, some one month
- PDF bills would need OCR — completely different pipeline
- Location-specific grid emission factors not implemented

## Corporate Travel

**Format researched:** Concur Travel & Expense CSV export (Trip 
Report extract) and Navan admin export format.

**What I learned:**
- Concur exports include trip segments, not just bookings
- Origin/destination are IATA airport codes for flights, 
  city names for hotels and ground
- Distance is not always included — must be calculated from 
  airport coordinates using Haversine formula
- Hotels export as nights stayed, not check-in/check-out dates
- Ground transport may have distance or only origin/destination

**Sample data rationale:**
Mix of domestic India flights (DEL-BOM ~1148km, short-haul) and 
international (BOM-LHR ~7200km, long-haul) to show different 
emission factors apply. Hotel stays in Mumbai and London show 
realistic business travel patterns. Ground transport includes 
both short city trips (Delhi-Gurgaon 45km) and longer intercity 
(Mumbai-Pune 148km).

**What would break in production:**
- Airport codes not in our lookup table default to 1000km — wrong
- Class of travel (business vs economy) has 2-3x emission factor 
  difference — not implemented
- Rail travel not handled at all
- Concur and Navan have slightly different column names