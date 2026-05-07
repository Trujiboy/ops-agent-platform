"""
Shared Supabase client. Multi-tenant por org_id.
Cada tabla tiene org_id FK a organizations.
RLS activado en todas las tablas — service_role_key para backend.
"""
import os
from functools import lru_cache
from supabase import create_client, Client
from loguru import logger


@lru_cache(maxsize=1)
def get_client() -> Client:
    """Singleton Supabase client (service role para operaciones backend)."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required")

    return create_client(url, key)


def get_org_id(slug: str) -> str:
    """Get organization UUID by slug ('sicoops', 'pauops', 'trujillosales')."""
    client = get_client()
    result = (
        client.table("organizations")
        .select("id")
        .eq("slug", slug)
        .single()
        .execute()
    )
    if not result.data:
        raise ValueError(f"Organization not found: {slug}")
    return result.data["id"]


def upsert_organization(name: str, slug: str) -> str:
    """Create organization if not exists. Returns UUID."""
    client = get_client()
    result = (
        client.table("organizations")
        .upsert({"name": name, "slug": slug}, on_conflict="slug")
        .execute()
    )
    return result.data[0]["id"]


def seed_organizations() -> None:
    """Run once on setup to create the 3 tenant organizations."""
    orgs = [
        {"name": "Sicoenginy SL",     "slug": "sicoops"},
        {"name": "Transports Pau",    "slug": "pauops"},
        {"name": "Verdemobil España", "slug": "trujillosales"},
    ]
    for org in orgs:
        org_id = upsert_organization(org["name"], org["slug"])
        logger.info(f"Organization ready: {org['slug']} → {org_id}")


if __name__ == "__main__":
    seed_organizations()
    print("Organizations seeded")
