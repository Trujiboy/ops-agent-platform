---
allowed-tools:
  - Bash
  - Write
---
Instrucciones:
1. Ejecuta: git diff --cached --stat
2. Si no hay nada staged: git add -A y muestra que se va a commitear
3. Genera commit message en formato convencional:
   type(scope): descripcion breve en espanol (max 72 chars)

   Types: feat|fix|docs|refactor|test|chore|perf
   Scopes: sicoops|pauops|trujillosales|shared|infra|upc

   Ejemplo: feat(sicoops): M2 DocDrafter genera memoria tecnica desde RAG

4. Ejecuta el commit
5. Añade entrada a LEARNING_LOG.md:
   ## [fecha y hora]
   **Commit:** [mensaje]
   **Que se construyo:** [1-2 lineas]
   **Proximo paso:** [1 linea]
   **Bloqueador si existe:** [o "ninguno"]
