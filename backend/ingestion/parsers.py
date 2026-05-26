import pandas as pd
from datetime import datetime, date
import math

# ---- Emission factors (DEFRA 2023) ----
EMISSION_FACTORS = {
    'diesel': 2.68,        # kgCO2e per litre
    'petrol': 2.31,        # kgCO2e per litre
    'natural_gas': 2.04,   # kgCO2e per kg
    'electricity': 0.233,  # kgCO2e per kWh (UK grid)
    'flight_short': 0.255, # kgCO2e per km per passenger
    'flight_long': 0.195,  # kgCO2e per km per passenger
    'hotel': 31.0,         # kgCO2e per night
    'car': 0.171,          # kgCO2e per km
}

# Airport coordinates for distance calculation
AIRPORT_COORDS = {
    'LHR': (51.477, -0.461), 'JFK': (40.641, -73.778),
    'DEL': (28.556, 77.100), 'BOM': (19.089, 72.868),
    'DXB': (25.253, 55.365), 'SIN': (1.350, 103.994),
    'CDG': (49.013, 2.550),  'FRA': (50.037, 8.562),
    'ORD': (41.978, -87.905),'LAX': (33.943, -118.408),
    'BLR': (13.198, 77.706), 'HYD': (17.231, 78.430),
    'MAA': (12.994, 80.171), 'CCU': (22.654, 88.447),
    'AMD': (23.077, 72.634), 'PNQ': (18.582, 73.919),
}


def haversine_km(coord1, coord2):
    """Calculate distance in km between two lat/long coordinates."""
    R = 6371
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def parse_sap_file(file):
    """
    Parse SAP flat file export (CSV).
    Expected columns: PLANT, MATERIAL, QUANTITY, UNIT, POSTING_DATE, MATERIAL_DESC
    """
    df = pd.read_csv(file, encoding='utf-8', sep=',')
    df = df.where(pd.notna(df), None)

    df.columns = [c.strip().upper() for c in df.columns]

    records = []
    errors = []

    UNIT_MAP = {'L': 'litre', 'LT': 'litre', 'KG': 'kg', 'M3': 'm3', 'GAL': 'gallon'}
    MATERIAL_FUEL_MAP = {
        'DIESEL': 'diesel', 'PETROL': 'petrol',
        'NATURAL GAS': 'natural_gas', 'GAS': 'natural_gas',
    }

    for i, row in df.iterrows():
        try:
            raw = row.to_dict()

            # Parse date - SAP often uses DD.MM.YYYY
            date_str = str(row.get('POSTING_DATE', ''))
            try:
                parsed_date = datetime.strptime(date_str, '%d.%m.%Y').date()
            except ValueError:
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            quantity = float(str(row.get('QUANTITY', '0')).replace(',', '.'))
            unit_raw = str(row.get('UNIT', 'L')).strip().upper()
            unit = UNIT_MAP.get(unit_raw, unit_raw.lower())

            material = str(row.get('MATERIAL_DESC', row.get('MATERIAL', ''))).upper()
            fuel_type = 'diesel'
            for key, val in MATERIAL_FUEL_MAP.items():
                if key in material:
                    fuel_type = val
                    break

            # Convert gallons to litres
            if unit == 'gallon':
                quantity = quantity * 3.785
                unit = 'litre'

            ef = EMISSION_FACTORS.get(fuel_type, EMISSION_FACTORS['diesel'])
            kgco2e = quantity * ef

            records.append({
                'raw': raw,
                'scope': 1,
                'category': 'fuel_combustion',
                'activity_value': quantity,
                'activity_unit': unit,
                'normalized_kgco2e': round(kgco2e, 4),
                'emission_factor': ef,
                'emission_factor_source': 'DEFRA 2023',
                'period_start': parsed_date,
                'period_end': parsed_date,
                'description': f"Plant: {row.get('PLANT','?')} | Material: {material}",
            })
        except Exception as e:
            errors.append({'row': i + 2, 'error': str(e), 'raw': row.to_dict()})

    return records, errors


def parse_utility_file(file):
    """
    Parse utility portal CSV export.
    Expected columns: METER_ID, SITE, PERIOD_START, PERIOD_END, CONSUMPTION_KWH, TARIFF
    """
    df = pd.read_csv(file, encoding='utf-8')
    df = df.where(pd.notna(df), None)

    df.columns = [c.strip().upper() for c in df.columns]

    records = []
    errors = []

    for i, row in df.iterrows():
        try:
            raw = row.to_dict()

            consumption = float(str(row.get('CONSUMPTION_KWH', 0)).replace(',', ''))

            # Handle MWh if present
            unit_col = str(row.get('UNIT', 'KWH')).upper()
            if unit_col == 'MWH':
                consumption = consumption * 1000

            period_start = pd.to_datetime(row.get('PERIOD_START')).date()
            period_end = pd.to_datetime(row.get('PERIOD_END')).date()

            ef = EMISSION_FACTORS['electricity']
            kgco2e = consumption * ef

            records.append({
                'raw': raw,
                'scope': 2,
                'category': 'purchased_electricity',
                'activity_value': consumption,
                'activity_unit': 'kWh',
                'normalized_kgco2e': round(kgco2e, 4),
                'emission_factor': ef,
                'emission_factor_source': 'DEFRA 2023',
                'period_start': period_start,
                'period_end': period_end,
                'description': f"Meter: {row.get('METER_ID','?')} | Site: {row.get('SITE','?')}",
            })
        except Exception as e:
            errors.append({'row': i + 2, 'error': str(e), 'raw': row.to_dict()})

    return records, errors


def parse_travel_file(file):
    import numpy as np
    df = pd.read_csv(file, encoding='utf-8')
    df.columns = [c.strip().upper() for c in df.columns]
    df = df.where(pd.notna(df), other=None)

    records = []
    errors = []

    for i, row in df.iterrows():
        try:
            raw = {}
            for k, v in row.to_dict().items():
                if v is None:
                    raw[k] = None
                elif isinstance(v, float) and math.isnan(v):
                    raw[k] = None
                else:
                    raw[k] = v

            travel_type = str(row.get('TRAVEL_TYPE', '') or '').lower().strip()
            travel_date = pd.to_datetime(row.get('TRAVEL_DATE')).date()

            if 'air' in travel_type or 'flight' in travel_type:
                origin = str(row.get('ORIGIN', '') or '').upper().strip()
                dest = str(row.get('DESTINATION', '') or '').upper().strip()

                dist_raw = row.get('DISTANCE_KM')
                if dist_raw is None or dist_raw == '' or (isinstance(dist_raw, float) and math.isnan(dist_raw)):
                    if origin in AIRPORT_COORDS and dest in AIRPORT_COORDS:
                        calc_distance = haversine_km(AIRPORT_COORDS[origin], AIRPORT_COORDS[dest])
                    else:
                        calc_distance = 1000.0
                else:
                    calc_distance = float(dist_raw)

                ef_key = 'flight_long' if calc_distance > 3700 else 'flight_short'
                ef = EMISSION_FACTORS[ef_key]
                kgco2e = round(calc_distance * ef, 4)
                category = 'business_travel_air'
                activity_value = round(float(calc_distance), 2)
                activity_unit = 'km'
                description = f"Flight: {origin} → {dest} | Traveler: {row.get('TRAVELER','?')}"

            elif 'hotel' in travel_type or 'accommodation' in travel_type:
                nights = float(row.get('NIGHTS') or 1)
                ef = EMISSION_FACTORS['hotel']
                kgco2e = round(nights * ef, 4)
                category = 'business_travel_hotel'
                activity_value = float(nights)
                activity_unit = 'nights'
                description = f"Hotel: {row.get('DESTINATION','?')} | Traveler: {row.get('TRAVELER','?')}"

            else:
                dist_raw = row.get('DISTANCE_KM')
                calc_distance = float(dist_raw) if dist_raw is not None else 50.0
                ef = EMISSION_FACTORS['car']
                kgco2e = round(calc_distance * ef, 4)
                category = 'business_travel_ground'
                activity_value = float(calc_distance)
                activity_unit = 'km'
                description = f"Ground: {row.get('ORIGIN','?')} → {row.get('DESTINATION','?')}"

            records.append({
                'raw': raw,
                'scope': 3,
                'category': category,
                'activity_value': activity_value,
                'activity_unit': activity_unit,
                'normalized_kgco2e': kgco2e,
                'emission_factor': ef,
                'emission_factor_source': 'DEFRA 2023',
                'period_start': travel_date,
                'period_end': travel_date,
                'description': description,
            })
        except Exception as e:
            errors.append({'row': i + 2, 'error': str(e), 'raw': {k: str(v) for k, v in row.to_dict().items()}})

    return records, errors

