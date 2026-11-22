"""gradweight-shared-lib: kleine Hilfsbausteine aus der Frühphase von GRADweight.

Status: Wartungsmodus. Für Retrieval mit Zugriffskontrolle siehe das Repository
``GRADweight/rag``, für die Erkennung von Prompt-Injection ``GRADweight/guardrails``.

Module:

  inference  OpenAI-kompatibler Client und native Ollama-API, dazu ein
             deterministischer StubClient für Tests (kein Netz).
  guard      Einfache Phrasenliste (Demo-Niveau, leicht umgehbar).
  rag        Kosinus-Suche über eine Liste im Speicher, Antwort als zitierte
             Textausschnitte, ohne LLM-Generierung und ohne Rechteprüfung.
  parsers    Text und Markdown; PDF (pdfplumber) und DOCX (python-docx) optional.
  config     Konfiguration aus Umgebungsvariablen und optionaler .env-Datei.
  audit      Audit-Protokoll als JSON-Lines, ohne Manipulationsschutz.

Keine harte Laufzeitabhängigkeit; numpy, pdfplumber und python-docx sind optional.
"""
from __future__ import annotations

__version__ = "0.2.0"

# Kern-Importe (funktionieren ohne jede optionale Abhängigkeit) —
# die hier gezeigten Symbole sind die öffentliche API.
from . import inference, guard, rag, parsers, config, audit
from .inference import Client, StubClient, embed_texts, chat
from .guard import (
    INJECTION_SIGNATURES, INJECTION_CATEGORIES,
    GuardResult, Judge, DummyJudge, GuardPipeline,
    analyse, detect,
)
from .rag import Chunk, RAGPipeline, RAGResult
from .config import Config, load_config
from .audit import AuditLog, audit_action
from .parsers import parse_text, parse_file, to_chunks

__all__ = [
    "__version__",
    # inference
    "Client", "StubClient", "embed_texts", "chat",
    # guard
    "INJECTION_SIGNATURES", "INJECTION_CATEGORIES",
    "GuardResult", "Judge", "DummyJudge", "GuardPipeline",
    "analyse", "detect",
    # rag
    "Chunk", "RAGPipeline", "RAGResult",
    # config
    "Config", "load_config",
    # audit
    "AuditLog", "audit_action",
    # parsers
    "parse_text", "parse_file", "to_chunks",
    # submodules
    "inference", "guard", "rag", "parsers", "config", "audit",
]
