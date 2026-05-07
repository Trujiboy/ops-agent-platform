# OPS-AGENT Platform

Plataforma de agentes operativos para 3 verticales — construida en 6 semanas (mayo–junio 2026).

## Verticales

| Vertical | Empresa | Objetivo |
|----------|---------|---------|
| **SicoOps** | Sicoenginy SL | Pipeline tenders semi-autopilot |
| **PauOps** | Transports Pau | Gestion logistica 10 camiones |
| **TrujilloSales** | Verdemobil España | Leads biometano EU |

## Stack

- **AI:** Anthropic API — claude-sonnet-4-6 + claude-haiku-4-5 + prompt caching
- **DB:** Supabase (Postgres + pgvector + Storage)
- **Orquestacion:** n8n en Railway
- **Integraciones:** Twilio WhatsApp · Google Maps Routes API · Firecrawl
- **Frontend:** Next.js 15 + Vercel (pendiente semana 4)

## Modulos (8)

```
M1 LeadFinder     → Detecta tenders y leads en fuentes publicas
M2 DocDrafter     → Genera Word/PDF desde RAG + templates
M3 ExcelFactory   → Presupuestos y P&L con formulas
M4 LegalChecker   → Valida solvencia y compliance vs pliego
M5 CommEngine     → Mensajes multicanal (email, WhatsApp, LinkedIn)
M6 Scheduler      → Rutas diarias, reuniones, agendamiento
M7 CRMLite        → Pipeline + contactos + estados
M8 Analytics      → Dashboards y metricas
```

## Setup

```bash
git clone https://github.com/Trujiboy/ops-agent-platform.git
cd ops-agent-platform
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con API keys reales
```

## Uso rapido — M1 Scorer

```bash
python -m modules.lead_finder.scorer --quick "Consultoria eficiencia energetica industria quimica 15000 EUR plazo 20 dias"
```

## Slash commands Claude Code

- `/tender <url-o-path>` — Score + pipeline completo de licitacion
- `/audit` — Reporte semanal metricas y commits
- `/commit` — Commit convencional + LEARNING_LOG update

---

*Build period: 6 mayo – 14 junio 2026 · Owner: Luis Trujillo · Barcelona*
