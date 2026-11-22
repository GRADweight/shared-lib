# gradweight-shared-lib

> **Status: Wartungsmodus.** Dieses Paket stammt aus der Frühphase von GRADweight
> und wird nicht mehr weiterentwickelt. Fehlerkorrekturen ja, neue Funktionen nein.
> Für neue Projekte: [`GRADweight/rag`](https://github.com/GRADweight/rag) für
> berechtigungsbewusstes Retrieval und [`GRADweight/guardrails`](https://github.com/GRADweight/guardrails)
> für die Erkennung von Prompt-Injection.

## In English

A small collection of zero-dependency helpers from GRADweight's early days: an
OpenAI-/Ollama-compatible HTTP client with an offline stub, simple document parsers,
environment-based configuration and a JSON-lines audit log. The package is in
maintenance mode. Its retrieval and guard components are deliberately simple and are
superseded by the dedicated `rag` and `guardrails` repositories.

## Inhalt

| Modul | Zweck | Einordnung |
|---|---|---|
| `inference` | Client für OpenAI-kompatible APIs und die native Ollama-API, dazu ein deterministischer `StubClient` für Tests | brauchbar |
| `parsers` | Text und Markdown (stdlib), PDF (`pdfplumber`), DOCX (`python-docx`) als optionale Extras | brauchbar |
| `config` | Konfiguration aus Umgebungsvariablen und optionaler `.env`-Datei | brauchbar |
| `audit` | Audit-Protokoll als JSON-Lines (wer, was, wann, Grund) | einfach, ohne Manipulationsschutz |
| `rag` | Kosinus-Suche über eine Liste im Speicher, Antwort als zitierte Textausschnitte, **ohne LLM-Generierung** | Demo-Niveau |
| `guard` | Abgleich gegen eine feste Liste englischer Phrasen | Demo-Niveau, leicht umgehbar |

## Installation

Das Paket liegt nicht auf PyPI. Installation direkt aus dem Repository:

```bash
pip install "gradweight-shared-lib @ git+https://github.com/GRADweight/shared-lib"
# mit optionalen Parsern
pip install "gradweight-shared-lib[all] @ git+https://github.com/GRADweight/shared-lib"
```

Offline-Rundgang ohne Netz und ohne API-Schlüssel:

```bash
python -m gw_shared_lib smoke
```

## Grenzen

- Der `StubClient` erzeugt Vektoren per Token-Hashing. Er ist für Tests gedacht und
  erfasst keine Bedeutungsähnlichkeit.
- `rag` setzt keine Zugriffsrechte durch. Das Feld `access_level` wird nur mitgeführt.
  Für Dokumente mit Personendaten oder vertraulichen Inhalten ungeeignet.
- `guard` erkennt nur englische Standardformulierungen und keine Varianten.
- Das Audit-Protokoll kann nachträglich verändert werden, ohne dass es auffällt.

## Entwicklung

```bash
uv venv && uv pip install -e ".[dev]"
python -m pytest -q
ruff check .
```

## Lizenz und Kontakt

MIT, siehe [LICENSE](LICENSE). Sicherheitsmeldungen: siehe [SECURITY.md](SECURITY.md).
Kontakt: mail@gradweight.ch
