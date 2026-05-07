"""
SicoOps vertical configuration.
Data sources, CPV codes, scoring thresholds, org identity.
"""
ORG_SLUG = "sicoops"
ORG_NAME = "Sicoenginy SL"

# CPV codes prioritarios (Clasificacion de Productos por Actividades)
CPV_CODES = [
    "71300000-1",  # Ingenieria
    "71314000-2",  # Energia
    "71314300-5",  # Eficiencia energetica
    "71621000-7",  # Analisis tecnico
    "73220000-0",  # Consultoria desarrollo
    "71241000-9",  # Estudios de viabilidad
    "71313000-5",  # Consultoria ambiental
]

# Sectores excluidos (non-compete Verdemobil)
EXCLUDED_KEYWORDS = [
    "biogas", "biometano", "upgrading", "digestion anaerobia",
    "biometane", "anaerobic", "CO2 biogenico",
]

# Budget thresholds (EUR)
BUDGET_MIN = 8_000
BUDGET_MAX = 150_000
BUDGET_OPTIMAL_MIN = 10_000
BUDGET_OPTIMAL_MAX = 20_000

# Scoring thresholds
SCORE_GO_THRESHOLD = 70       # Auto-GO si score >= 70
SCORE_DEEP_THRESHOLD = 70     # Usar Sonnet si Haiku da >= 70
SCORE_MIN_VIABLE = 50         # Por debajo = NO GO automatico

# Prep time budget (horas)
MAX_PREP_HOURS = 40           # Si estimado > 40h → revisar con Laura

# Data sources
SOURCES = {
    "contractaciopublica": "https://api.contractaciopublica.cat",
    "ted": "https://api.ted.europa.eu/v3/notices/search",
    "boe": "https://boe.es/diario_boe/xml.php",
}
