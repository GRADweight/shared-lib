# GRADweight — shared-lib

**Das gemeinsame technische Fundament** des ganzen GRADweight-Stacks.
Sechs lauffähige Bausteine, aus denen alle Prototypen (1–20,
[`internal-kb/katalog`](../internal-kb/katalog/)) und Prototypen-Repos
aufgebaut werden.

> **Der Unterschied ist nicht das Versprechen — es ist, was wir zeigen.**
> Dieses Repo ist lauffähig **ohne** Setup: keine API-Keys, keine Cloud,
> kein Netz. `python -m gw_shared_lib smoke` läuft offline und zeigt die
> Kette Inferenz → Guard → RAG → Config → Audit.

## Für wen

**Entwickler im GRADweight-Stack (und jeder, der nachbauen will)** — das
gemeinsame Fundament, aus dem Prototypen 1–20 aufgebaut werden.  Nutzt es
als Ausgangspunkt: kein Framework, das installiert werden muss, sondern
Bausteine, die in jedes KMU-Projekt reinlaufen.

---

## Die sechs Bausteine

| Baustein | Was es leistet | Lauffähig |
|---|---|---|
| **inference** | OpenAI-kompatibler Client für Ollama / vLLM / LiteLLM-Gateway **+** ein offline `StubClient` (bag-of-words, kein Netz) | stdlib nur |
| **guard** | **CANONICAL** Signatur-Schicht (16 Signaturen, 6 Kategorien) + pluggbarer `Judge` + `GuardPipeline` (fail-closed) | stdlib nur |
| **rag** | `Chunk` + `retrieve` (cosine) + `RAGPipeline` (Guard → Retrieve → **quelle-zitierte Antwort**, ehrliche Nicht-Antwort statt Halluzination) | stdlib + optional numpy |
| **parsers** | Text/Markdown (stdlib), PDF (`pdfplumber`), DOCX (`python-docx`) — mit graceful Degradation | stdlib + optional |
| **config** | Config aus `OS.environ` + optionalem `.env` — **keine Secrets im Code** (DSG) | stdlib nur |
| **audit** | Audit-Trail als JSON-lines (wer / was / wann / Grund / `fall_id`) | stdlib nur |

**Harte Abhängigkeit: keine.** `numpy`, `pdfplumber`, `python-docx` sind
optional und werden graceful ausgelastet, falls nicht installiert.

---

## Lauffähig ohne Setup

```bash
# Offline — zeigt den ganzen Stack (keine API, kein Netz)
python3 -m gw_shared_lib smoke

# Eigener Build (Optiona: numpy/pdf/docx)
pip install gw-shared-lib            # ohne Extras
pip install gw-shared-lib[all]       # mit numpy + pdfplumber + python-docx
```

### Ein Prototyp nutzt den Fundament

```python
from gw_shared_lib import RAGPipeline, GuardPipeline, Chunk, load_config

cfg = load_config()                   # Secrets aus .env / OS, nie im Code
corpus = [Chunk(content="Ferientage im 1. Dienstjahr: 25 Tage.",
                source="reglement/urlaub.md#3.1", confidence=0.84,
                access_level="internal")]
pipe = RAGPipeline(corpus=corpus, guard=GuardPipeline())
res = pipe.answer("Wie viele Ferientage habe ich im ersten Dienstjahr?")
print(res.answer)        # quell-zitierte Antwort
print(res.citations)     # Quelle + Confidence
print(res.guard_blocked) # False (kein Injection)
```

## CANONICAL — die Signaturliste

`gw_shared_lib.guard.INJECTION_SIGNATURES` ist die **einzelne Quelle** der
16 Injection-Signaturen für den ganzen Org-Stack. Die früheren Kopien in
`guardrails/guard/core.py` und `rag/rag/guard.py` sollen per
`from gw_shared_lib.guard import INJECTION_SIGNATURES` hierher synchronisiert
werden.

## Ehrliche Grenzen (was `StubClient` leistet — und was nicht)

Der offline `StubClient` ist ein **bag-of-words-Ersetzer** (Token-Overlap,
via SHA-256-Hash, stdlib). Er leistet *Retrieval-Logik* (welcher Chunk ist
nächster?), aber **keine** semantische Ähnlichkeit (welcher Chunk meint
das Gleiche?). Für Produktion: `GW_INFER_URL=http://localhost:11434` und
ein echtes Embedding-Modell (`nomic-embed-text`). Diese Grenze ist bewusst
dokumentiert — wir zeigen sie, statt sie zu verdecken.

## Konventionen

- **Sprache**: Schweizer Hochdeutsch, «ss», keine Gedankenstriche — auch in
  Commits und Code.
- **Secrets**: nur via `OS.environ` / `.env` (`.gitignore` blockiert `.env*`).
  Nie in Code, nie in Logs.
- **Branch-Modell**: `main` = Approved State, Änderungen nur via Squash-PR
  nach Gründer-Freigabe.
- **Fail-closed**: der `Judge` blockt bei Fehler, nicht durchlässt.

## Status / Tests

- v0.1.0 — 6 Bausteine, lauffähig offline
- `tests/` — 9 pytest grüns (stdlib, kein Netz), CI: `ci.yml` (Py 3.9/3.11/3.12)
- `python -m gw_shared_lib smoke` → GREEN

**Kontakt:** edin@gradweight.ch · gradweight.ch
