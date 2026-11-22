# Changelog

Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [0.2.0] – 2026-10-27

### Geändert
- Paket heisst neu `gradweight-shared-lib`; der Importname `gw_shared_lib` bleibt.
- Status Wartungsmodus. Nachfolger für Retrieval und Guard sind die Repositories
  `rag` und `guardrails`.
- Mindestversion Python 3.10.

### Behoben
- Das Paket liess sich nicht installieren (ungültiges Build-Backend).
- `Client.embed()` liess fehlgeschlagene Eingaben aus und verschob dadurch die
  Zuordnung von Vektoren zu Texten. Neu bleibt die Reihenfolge erhalten.
- `Client.embed()` erwartete vertauschte Antwortformate der Ollama-Endpunkte.
- `Client.chat()` verdoppelte `/v1` bei OpenAI-kompatiblen Basis-URLs und konnte
  Antworten der nativen Ollama-API nicht lesen.
- Zitate der RAG-Antwort enthalten wieder `access_level`; `is_confidential()` war
  dadurch wirkungslos.

### Entfernt
- Interne Arbeitsdokumente und der Zusatztext in der Lizenzdatei.
