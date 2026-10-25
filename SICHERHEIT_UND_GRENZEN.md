# SICHERHEIT, HAFTUNG UND GRENZEN — GRADweight/shared-lib

> **Kurz:** Offene Referenz von GRADweight GmbH. Kein Rechts- oder Beratungsgutachten. Alle Beispiele verwenden erfundene Referenzdaten, keine echten Kundendaten.

| Feld | Wert |
|---|---|
| Repo | `GRADweight/shared-lib` |
| Stand | 25.10.2026 |
| Lizenz | `MIT` — ein Satz: Wiederverwendbare Bausteine sollen offen einsetzbar sein (12 Tests). |
| Status | Intern geprüft, **noch NICHT public** (kein Visibility-Wechsel ohne ausdrückliche Owner-Freigabe). |

## 1. Sicherheitshinweise (Gemeinschaft)
- **Keine echten Kundendaten.** Alle Beispiele verwenden erfundene Referenzdaten (Marken-/Kundenwerte sind Platzhalter). Ueberprueft 25.10.2026: Grep nach AG/GmbH/Kundenamen lieferte nur Fachbegriffe.
- **Kein Rechts- oder Beratungsgutachten.** Dieses Repo ist eine technische Referenz, kein rechtsverbindliches Dokument. Vor einem konkreten Einsatzzweck eigene Pruefung / Fachberatung.
- **Versioniert, aber ohne Garantie.** Schildert den aktuellen Stand; keine SLA oder Aktualisierungspflicht. Vor Public erneut gegen HEAD pruefen.

## 2. Bekannte Fehler / offene Gaps (Repo-spezifisch)
- **localhost:11434 Defaults (Ollama)..** Publik-Default, kein Leak.
- **Nur 1 Test-Datei, 12 test-functions..** Genug für v0.1.1; Erweiterung optional.

## 3. Vor Public (Checkliste)
- [ ] Gegen HEAD pruefen: keine internen Pfade (/Users, ~/, /tmp), keine echten Kundendaten, keine Preise/Marge im Public-Text
- [ ] Interne Docs entfernt (OFFENE_PUNKTE, PROJEKT, ROADMAP, M-Module)
- [ ] Lizenz korrekt + ein-Satz-Erklaerung im README (s. oben)
- [ ] Sichtbarkeit erst nach **ausdruecklicher Owner-Freigabe** (kein automatischer Visibility-Wechsel)

_Grundlage: interner Forensic-Scan 25.10.2026; Werte aus /tmp/gwscan; nichts geschoben._
