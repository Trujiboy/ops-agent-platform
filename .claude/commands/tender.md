---
allowed-tools:
  - Bash
  - Write
---
Instrucciones:
1. Lee el archivo o URL pasado como argumento: $ARGUMENTS
2. Ejecuta: python -m modules.lead_finder.scorer --input "$ARGUMENTS" --vertical sicoops
3. Si score >= 70, pregunta: "Score: X/100. Iniciamos pipeline completo M2+M3+M4? (s/n)"
4. Si confirmado: lanza pipeline completo y avisa cuando este lista oferta_v0
5. Añade entrada a LEARNING_LOG.md: fecha, tender, score, decision
