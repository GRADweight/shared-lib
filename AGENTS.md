# AGENTS.md — GRADweight/shared-lib

## Zweck
Das gemeinsame technische Fundament (6 Bausteine) für alle GRADweight-
Prototypen (s. internal-kb/katalog, Nr. 1-20) und Prototypen-Repos.
Harte Abhängigkeit: keine (nur stdlib; numpy/pdfplumber/python-docx
optional). Lauffähig offline via ein StubClient.

## Layout (gw_shared_lib/)
- inference.py  — OpenAI-kompatibler Client (Ollama/vLLM/LiteLLM) +
                  StubClient (offline, bag-of-words, kein Netz)
- guard.py      — CANONICAL 16 Signaturen + Judge + GuardPipeline
                  (fail-closed)
- rag.py        — Chunk + retrieve + RAGPipeline (quelle-zitiert,
                  ehrliche Nicht-Antwort)
- parsers.py    — Text/Markdown (stdlib) + PDF/DOCX (optional,
                  graceful Degrade)
- config.py     — OS.environ + optionales .env (keine Secrets im Code)
- audit.py      — JSON-lines Audit-Trail (wer/was/wann/Grund/fall_id)
- __main__.py   — `python -m gw_shared_lib smoke` (offline Fundament-Check)
- tests/        — 9 pytest, stdlib, kein Netz

## Befehle
```bash
python3 -m gw_shared_lib smoke          # offline Fundament-Check
pip install -e .                       # ohne Extras (stdlib)
pip install -e ".[all]"               # + numpy/pdfplumber/python-docx
python3 -m pytest -q                   # 9 Tests grüns
```

## Konventionen
- **Sprache**: Schweizer Hochdeutsch, «ss», keine Gedankenstriche.
- **Secrets**: nur OS.environ / .env. .gitignore blockiert .env*.
- **Branch-Modell**: main = Approved State, Änderungen nur via Squash-PR
  nach Gründer-Freigabe.
- **Fail-closed**: der Judge blockt bei Fehler, nicht durchlässt.
- **CANONICAL**: guard.INJECTION_SIGNATURES ist die einzige Quelle im
  ganzen Org-Stack. Andere Repos (guardrails, rag) importieren hierher.

## Grenzen (ehrlich, dokumentiert)
- StubClient ist bag-of-words (Retrieval-Logik, KEINE semantische
  Äbnichkeit). Für Produktion: GW_INFER_URL + echtes Embedding-Modell.
- parsers.py: PDF/DOCX brauchen Optionals (pdfplumber/python-docx),
  falls nicht installiert: graceful Degradation, kein Crash.

## Status (10/2026)
- v0.1.0, 6 Bausteine, 9 Teste grüns, CI (ci.yml), Smoke GREEN
- Noch privat, launch 25.10.2026 nach Gründer-Entscheid.
