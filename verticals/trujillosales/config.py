"""
TrujilloSales vertical configuration.
Comercial biometano EU para Verdemobil Espana.
"""
ORG_SLUG = "trujillosales"
ORG_NAME = "Verdemobil Espana"

# Target geography (paises con plantas biometano activas)
TARGET_COUNTRIES = [
    "ES", "FR", "DE", "NL", "BE", "IT", "DK", "SE",
]

# Plant capacity filter (solo plantas con potencial real)
MIN_CAPACITY_NM3H = 100

# Lead scoring thresholds
SCORE_HOT = 75
SCORE_WARM = 50

# Outreach sequence (dias entre contactos)
OUTREACH_SEQUENCE_DAYS = [0, 7, 14, 30]

# Non-compete sectors (Verdemobil exclusivos — NO tocar desde Sicoenginy)
NONCOMPETE_SECTORS = [
    "biogas", "biometano", "upgrading", "digestión anaerobia",
]
