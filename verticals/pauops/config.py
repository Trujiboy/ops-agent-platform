"""
PauOps vertical configuration.
Transports Pau — 10 trucks, B2B Spain.
"""
ORG_SLUG = "pauops"
ORG_NAME = "Transports Pau"

# Fleet
FLEET_SIZE = 10

# Route planning
ROUTE_DISPATCH_TIME = "06:30"   # Hojas de ruta enviadas a conductores
ROUTE_PREP_CRON = "22:00"       # n8n genera rutas del dia siguiente

# WhatsApp bot
WHATSAPP_FALLBACK_RESPONSE = {
    "type": "human_needed",
    "message": "Este pedido necesita confirmacion manual. Laura sera notificada.",
}

# Billing milestones (dias despues de entrega)
BILLING_DAYS = 3

# Google Maps
MAPS_OPTIMIZATION = "TRAFFIC_AWARE"   # Routes API mode
