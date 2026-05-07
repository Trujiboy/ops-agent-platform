"""
M1 LeadFinder — Scorer
Scorea licitaciones para Sicoenginy SL usando Claude.
Haiku para batch (coste bajo), Sonnet para analisis profundo de top candidatos.

Uso:
    python -m modules.lead_finder.scorer --quick "texto de licitacion"
    python -m modules.lead_finder.scorer --input ruta/al/pliego.txt
"""
from __future__ import annotations
import json
import argparse
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field
from loguru import logger

from shared.anthropic_client import create_structured_message, HAIKU, SONNET


# ─── Pydantic Models ─────────────────────────────────────────────────────────

class TenderScore(BaseModel):
    score: int = Field(ge=0, le=100, description="Score 0-100")
    go: bool = Field(description="Presentar oferta?")
    reason_go: str | None = Field(default=None, description="Razon si go=True (max 50 palabras)")
    reason_no: str | None = Field(default=None, description="Razon si go=False (max 30 palabras)")
    estimated_prep_hours: float = Field(description="Horas estimadas de preparacion")
    risk_flag: str | None = Field(default=None, description="Riesgo especifico si existe")
    key_requirement_gap: str | None = Field(default=None, description="Que falta para ganar")


# ─── System Prompts ───────────────────────────────────────────────────────────

SICOOPS_SCORING_PROMPT = """Eres un evaluador de licitaciones publicas para Sicoenginy SL,
consultora de ingenieria energetica en Cataluna. Evalua si la siguiente licitacion es adecuada.

CRITERIOS DE EVALUACION:
1. Sector: H2, BESS, eficiencia energetica industrial, auditoria energetica,
   data centers, ingenieria de redes, NCRfG compliance, consultoria ambiental
   EXCLUIR COMPLETAMENTE: biogas, biometano, upgrading, digestion anaerobia
2. Presupuesto: 8000-150000 EUR (optimo 10000-20000 EUR)
3. Capacidad real: Sicoenginy = 2 personas (abogada/economista + ingeniero senior EPC)
   + colaborador tecnico ocasional. No podemos ganar contratos que requieran equipo de 10+
4. Solvencia tipica requerida: facturacion 150k/anyo ultimos 3, experiencia proporcional
5. Plazo minimo: 10 dias habiles desde hoy para preparar oferta

PERFIL EQUIPO:
- Laura Bastons: abogada + economista, experiencia en licitaciones publicas y contratos
- Luis Trujillo: ingeniero industrial senior, 8 anyos EPC 100M+, H2, energia
- Joan (colaborador): ingenieria ambiental, firma tecnica externa

CALIBRACION:
85-100: Perfil exacto, presupuesto optimo, sin gap de solvencia -> GO inmediato
70-84:  Buena oportunidad, 1-2 puntos a verificar -> GO con analisis
50-69:  Posible pero con trade-offs -> Laura decide
0-49:   No encaja -> NO GO automatico

Responde UNICAMENTE con JSON valido siguiendo el schema exacto proporcionado."""


# ─── Core Functions ───────────────────────────────────────────────────────────

def score_tender(
    tender_text: str,
    vertical: Literal["sicoops"] = "sicoops",
    deep: bool = False,
) -> TenderScore:
    """
    Score a tender using Claude.

    Args:
        tender_text: Full tender description/pliego text
        vertical:    Which vertical config to use (only sicoops for now)
        deep:        True = Sonnet (deeper, 10x cost). False = Haiku (batch screening)

    Cost estimate:
        Haiku quick:  ~0.0003 EUR/call
        Sonnet deep:  ~0.003  EUR/call
        Use Haiku for batch, Sonnet only for score > 70
    """
    if vertical != "sicoops":
        raise NotImplementedError(f"Vertical {vertical} not yet implemented")

    model = SONNET if deep else HAIKU
    logger.debug(f"Scoring tender with {model} (deep={deep})")

    raw = create_structured_message(
        system_prompt=SICOOPS_SCORING_PROMPT,
        user_content=f"Evalua esta licitacion:\n\n{tender_text}",
        model=model,
        max_tokens=512,
    )

    try:
        return TenderScore(**json.loads(raw))
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"Failed to parse scoring response: {e}\nRaw: {raw[:200]}")
        raise


def score_batch(
    tenders: list[dict],
    vertical: str = "sicoops",
    deep_threshold: int = 70,
) -> list[dict]:
    """
    Two-pass batch scoring.
    Pass 1: All tenders with Haiku (cheap).
    Pass 2: Candidates >= deep_threshold with Sonnet (deep analysis).

    Args:
        tenders:         List of {"id", "title", "text", "budget"}
        deep_threshold:  Score above which to run Sonnet deep analysis

    Returns:
        List sorted by final_score descending, each item has "go" bool
    """
    results = []

    for tender in tenders:
        text = (
            f"TITULO: {tender.get('title', '')}\n"
            f"PRESUPUESTO: {tender.get('budget', 0):,.0f} EUR\n"
            f"DESCRIPCION:\n{tender.get('text', '')}"
        )

        score = score_tender(text, vertical=vertical, deep=False)
        tender["score"] = score.model_dump()

        if score.score >= deep_threshold:
            logger.info(
                f"'{tender.get('title', '')[:50]}' → {score.score}, running deep analysis"
            )
            score_deep = score_tender(text, vertical=vertical, deep=True)
            tender["score_deep"]  = score_deep.model_dump()
            tender["final_score"] = score_deep.score
            tender["go"]          = score_deep.go
        else:
            tender["final_score"] = score.score
            tender["go"]          = score.go

        decision = "GO" if tender["go"] else "NO GO"
        logger.info(f"'{tender.get('title', '')[:40]}' → {tender['final_score']}/100 {decision}")
        results.append(tender)

    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="M1 LeadFinder Scorer")
    parser.add_argument("--input", help="Path to tender text file")
    parser.add_argument("--quick", help="Quick score of text input directly")
    parser.add_argument("--vertical", default="sicoops", choices=["sicoops"])
    args = parser.parse_args()

    if args.quick:
        score = score_tender(args.quick, vertical=args.vertical, deep=False)
        print(f"\nScore: {score.score}/100")
        print(f"Decision: {'GO' if score.go else 'NO GO'}")
        print(f"Reason: {score.reason_go or score.reason_no}")
        print(f"Prep: ~{score.estimated_prep_hours}h")
        if score.risk_flag:
            print(f"Risk: {score.risk_flag}")

    elif args.input:
        path = Path(args.input)
        text = path.read_text(encoding="utf-8") if path.exists() else args.input
        score = score_tender(text, vertical=args.vertical, deep=True)
        print(f"\n{'='*50}")
        print(f"SCORE: {score.score}/100")
        print(f"DECISION: {'GO' if score.go else 'NO GO'}")
        print(f"Reason: {score.reason_go or score.reason_no}")
        print(f"Prep: {score.estimated_prep_hours}h")
        if score.risk_flag:
            print(f"Risk: {score.risk_flag}")
        if score.key_requirement_gap:
            print(f"Gap: {score.key_requirement_gap}")
        print("=" * 50)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
