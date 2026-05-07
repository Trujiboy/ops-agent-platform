-- OPS-AGENT Platform · Supabase Schema
-- Ejecutar en: dashboard → SQL Editor → New query → pegar y Run
-- Orden: extensiones → tablas → índices → seed

-- ─── Extensiones ──────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── Organizations (multi-tenant root) ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS organizations (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name       TEXT NOT NULL,
  slug       TEXT UNIQUE NOT NULL,  -- 'sicoops' | 'pauops' | 'trujillosales'
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Tenders (SicoOps) ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tenders (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id      UUID REFERENCES organizations(id) ON DELETE CASCADE,
  source      TEXT,                 -- 'contractaciopublica' | 'ted' | 'boe'
  external_id TEXT,
  title       TEXT,
  budget_min  NUMERIC,
  budget_max  NUMERIC,
  deadline    DATE,
  cpv_codes   TEXT[],
  score       NUMERIC,              -- M1 LeadFinder score (0-100)
  status      TEXT DEFAULT 'detected'
              CHECK (status IN ('detected','analyzing','drafting','submitted','won','lost')),
  full_text   TEXT,
  embedding   vector(1536),         -- pgvector · Voyage AI voyage-large-2
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Offer Documents (SicoOps) ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS offer_documents (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tender_id           UUID REFERENCES tenders(id) ON DELETE CASCADE,
  type                TEXT,  -- 'memoria_tecnica' | 'propuesta_economica' | 'excel_presupuesto'
  storage_path        TEXT,
  generation_tokens   INT,
  generation_cost_eur NUMERIC,
  laura_approved      BOOLEAN DEFAULT FALSE,
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Bid Corpus RAG (SicoOps) ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sicoops_bid_corpus (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id     UUID REFERENCES organizations(id) ON DELETE CASCADE,
  title      TEXT NOT NULL,
  content    TEXT NOT NULL,
  doc_type   TEXT,  -- 'memoria_ganada' | 'pliego_referencia' | 'propuesta_economica'
  won        BOOLEAN DEFAULT FALSE,
  embedding  vector(1536),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Orders (PauOps) ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS orders (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id       UUID REFERENCES organizations(id) ON DELETE CASCADE,
  raw_message  TEXT,
  origin       TEXT,
  destination  TEXT,
  cargo_type   TEXT,
  weight_kg    NUMERIC,
  pickup_date  DATE,
  client_name  TEXT,
  client_phone TEXT,
  status       TEXT DEFAULT 'received'
               CHECK (status IN ('received','assigned','in_transit','delivered','billed')),
  driver_id    UUID,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Deliveries / Albaranes (PauOps) ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS deliveries (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id         UUID REFERENCES orders(id) ON DELETE CASCADE,
  storage_path     TEXT,   -- Supabase Storage: delivery-photos bucket
  delivered_at     TIMESTAMPTZ,
  driver_signature BOOLEAN DEFAULT FALSE,
  created_at       TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Biogas Leads (TrujilloSales) ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS biogas_leads (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id              UUID REFERENCES organizations(id) ON DELETE CASCADE,
  company             TEXT,
  country             TEXT,
  plant_capacity_nm3h NUMERIC,
  contact_name        TEXT,
  contact_linkedin    TEXT,
  contact_email       TEXT,
  score               NUMERIC,
  status              TEXT DEFAULT 'identified'
                      CHECK (status IN ('identified','contacted','replied','meeting','proposal','closed')),
  notes               TEXT DEFAULT '',
  embedding           vector(1536),
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Índices ──────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_tenders_org_id     ON tenders(org_id);
CREATE INDEX IF NOT EXISTS idx_tenders_status     ON tenders(status);
CREATE INDEX IF NOT EXISTS idx_tenders_score      ON tenders(score DESC);
CREATE INDEX IF NOT EXISTS idx_orders_org_id      ON orders(org_id);
CREATE INDEX IF NOT EXISTS idx_orders_status      ON orders(status);
CREATE INDEX IF NOT EXISTS idx_leads_org_id       ON biogas_leads(org_id);
CREATE INDEX IF NOT EXISTS idx_leads_status       ON biogas_leads(status);

-- Vector similarity search indexes
CREATE INDEX IF NOT EXISTS idx_tenders_embedding
  ON tenders USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_corpus_embedding
  ON sicoops_bid_corpus USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_leads_embedding
  ON biogas_leads USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- ─── Seed: 3 organizaciones ───────────────────────────────────────────────────
INSERT INTO organizations (name, slug) VALUES
  ('Sicoenginy SL',     'sicoops'),
  ('Transports Pau',    'pauops'),
  ('Verdemobil España', 'trujillosales')
ON CONFLICT (slug) DO NOTHING;

-- ─── Verificación ─────────────────────────────────────────────────────────────
SELECT slug, name FROM organizations ORDER BY slug;
