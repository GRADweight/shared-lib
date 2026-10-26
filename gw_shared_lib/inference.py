"""Schicht 0: Inferenz-Client (OpenAI-kompatibel).

Inferenzschicht: OpenAI-kompatibler Client und native Ollama-API.
Ersetzt die zersplitterten Versionen (rag/retrieve.ollama_embed,
platforms/stack/minimal/rag.py embed/chat) im ganzen Org.

Zwei Client-Klassen:
  - Client       : HTTP-Client gegen einen OpenAI-kompatiblen
                   Endpoint (/v1/embeddings, /v1/chat/completions).
                   Lauffähig gegen Ollama, vLLM, LiteLLM-Gateway.
  - StubClient   : Offline-Client für Tests und Demo (deterministisch).
                   Kein Netz, kein Crash. Liefert bag-of-words-Vektor
                   via SHA-256-Hash-basierte Token-Segregation.

Wenn die HTTP-Calls fehlschlagen, fällt `embed_texts` bzw. `chat`
auf `StubClient` zurück — fail-soft, keine Erfindung.
"""
from __future__ import annotations

import json
import logging
import os
import math
import re
import hashlib
import urllib.request
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_URL = os.environ.get("GW_INFER_URL", "http://localhost:11434")
DEFAULT_EMBED = os.environ.get("GW_INFER_EMBED", "nomic-embed-text")
DEFAULT_CHAT = os.environ.get("GW_INFER_CHAT", "llama3.2:3b")


@dataclass
class Client:
    """OpenAI-kompatibler HTTP-Client.

    `url`       : Basis-URL (z.B. http://localhost:11434/v1)
    `embed_model` : Standard-Embedding-Modell
    `chat_model`  : Standard-Chat-Modell
    `timeout`    : HTTP-Timeout in Sekunden
    """
    url: str = DEFAULT_URL
    embed_model: str = DEFAULT_EMBED
    chat_model: str = DEFAULT_CHAT
    timeout: float = 120.0

    def _post(self, path: str, payload: dict) -> dict:
        full = self.url.rstrip("/") + path
        req = urllib.request.Request(
            full,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def embed(self, texts, model: Optional[str] = None) -> list[list[float]]:
        """Embeddings für `texts` (str oder list[str]).

        Rückgabe: Liste von Vektoren, immer in derselben Reihenfolge.
        Versucht je einen native-Ollama- und einen OpenAI-kompatiblen
        Endpoint pro Input (fail-soft; leere Vektoren = nächster Versuch).
        v0.1.1: URL-aware — bei `/v1`-Basis wird `/v1/embeddings` NICHT zum
        doppelten `.../v1/v1/embeddings`; native Ollama läuft zuerst, dann
        OpenAI-kompatibel. (Regression-Test: test_embed_is_url_aware)
        """
        model = model or self.embed_model
        single = isinstance(texts, str)
        inputs = [texts] if single else list(texts)
        out: list[list[float]] = []
        is_v1 = self.url.rstrip("/").endswith("/v1")
        for t in inputs:
            # native Ollama zuerst, dann OpenAI-kompatibel.
            # Endpoint-Pfade werden URL-aware gesetzt (/v1 wird nicht doppelt).
            openai_ep = "/embeddings" if is_v1 else "/v1/embeddings"
            # Formate (Ollama-Doku): /api/embed {"input"} -> {"embeddings": [[...]]},
            # /api/embeddings (alt) {"prompt"} -> {"embedding": [...]},
            # OpenAI-kompatibel /v1/embeddings -> {"data": [{"embedding": [...]}]}.
            attempts = [
                (openai_ep, {"model": model, "input": [t]},
                 lambda d: (d.get("data") or [{}])[0].get("embedding")),
                ("/api/embed", {"model": model, "input": t},
                 lambda d: (d.get("embeddings") or [None])[0]),
                ("/api/embeddings", {"model": model, "prompt": t},
                 lambda d: d.get("embedding")),
            ]
            # Basis-URL ohne /v1: zuerst die nativen Ollama-Endpunkte
            if not is_v1:
                attempts = attempts[1:] + attempts[:1]
            else:
                attempts = attempts[:1]
            vec_out: list[float] = []
            for path, body, parse in attempts:
                try:
                    data = self._post(path, body)
                    vec = parse(data or {})
                except Exception as exc:  # noqa: BLE001 - nächster Endpoint
                    logger.debug("Embedding über %s fehlgeschlagen: %s", path, exc)
                    continue
                if isinstance(vec, list) and vec and all(
                    isinstance(x, (int, float)) for x in vec
                ):
                    vec_out = [float(x) for x in vec]
                    break
            if not vec_out:
                logger.warning("Kein Embedding für Eingabe %d erhalten", len(out))
            # Platzhalter statt Auslassen: Reihenfolge und Länge bleiben erhalten.
            out.append(vec_out)
        return out

    def chat(self, messages: list[dict], model: Optional[str] = None,
             temperature: float = 0.2, max_tokens: int = 400) -> str:
        """Eine Chat-Request über /chat/completions. Gibt den Text
        zurück. Fail-soft: '' bei Fehler (der Aufrufer muss
        die Antwort validieren — RAG-Pipeline tut es).
        """
        model = model or self.chat_model
        body = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        is_v1 = self.url.rstrip("/").endswith("/v1")
        openai_ep = "/chat/completions" if is_v1 else "/v1/chat/completions"
        native_body = {**body, "stream": False}
        for ep, payload in ((openai_ep, body), ("/api/chat", native_body)):
            if is_v1 and ep == "/api/chat":
                continue  # native Ollama-API liegt nicht unter /v1
            try:
                data = self._post(ep, payload) or {}
            except Exception as exc:  # noqa: BLE001 - nächster Endpoint
                logger.debug("Chat über %s fehlgeschlagen: %s", ep, exc)
                continue
            choices = data.get("choices") or []
            if choices:  # OpenAI-kompatibel
                return str((choices[0].get("message") or {}).get("content", ""))
            message = data.get("message")
            if isinstance(message, dict):  # native Ollama /api/chat
                return str(message.get("content", ""))
        return ""


@dataclass
class StubClient(Client):
    """Deterministischer Offline-Client für Tests und Demos.

    Kein HTTP, kein Netz. Liefert:
      - embed()   : bag-of-words-Vektor via Token-Hashing
                    (gleiche Text -> gleiche Vektor, ähnliche Texte
                     haben höheren Übereinstimmungs-Wert —
                      kein ML, kein Netz, aber ehrlicher als ein
                      SHA-256-Whole-Text-Hash, der keine
                      Semantik versteht).
      - chat()    : ein fester Antwort-Text
                    "Offline (StubClient)."
    """
    embed_model: str = "stub"
    chat_model: str = "stub"
    _dim: int = 128
    _chat_reply: str = "Offline (StubClient). Für Produktion: setze GW_INFER_URL."

    def embed(self, texts, model: Optional[str] = None) -> list[list[float]]:
        single = isinstance(texts, str)
        inputs = [texts] if single else list(texts)
        out = [_stub_vec(t, self._dim) for t in inputs]
        return out[0:1] if single else out

    def chat(self, messages, model=None, temperature=0.2,
             max_tokens=400) -> str:
        return self._chat_reply


def _stub_vec(text: str, dim: int = 128) -> list[float]:
    """Offlin-Ersetzer für einen Embedding-Server.

    **Ehrlich:** Dies ist KEIN semantisches Embedding.
    Es ist ein bag-of-words-Vektor: die Tokens des Textes
    werden per SHA-256 auf `dim` Dimensionen gehasht und
    gezählt. Ähnlichkeit = Übereinstimmung der Tokens (Wort-
    Overlap, nicht Bedeutung-Ähnlichkeit).

    Das ist **genug** für die Retrievall-Logik (welche Chunk
    ist am nächsten?), aber **nicht** für echte semantische
    Ähnlichkeit (dafür braucht man ein echtes Embedding-Modell,
    z.B. nomic-embed-text). Der Aufrufer muss wissen, dass
    `StubClient.cosine(a,b)` ≈ 0 bedeutet "keine Wort-Über-
    einstimmung", aber nicht "verschiedene Bedeutung".

    Kein externer Abhäng (nur stdlib re + hashlib).
    """
    dim = max(dim, 32)
    vec = [0.0] * dim
    tokens = [t for t in re.findall(r"\w+", text.lower())
              if len(t) > 1]  # keine 1-zeiger
    n = len(tokens)
    if n == 0:
        return [0.0] * dim
    for tok in tokens:
        h = hashlib.sha256(tok.encode()).digest()
        idx = int.from_bytes(h[:4], "big") % dim
        vec[idx] += 1.0
    norm = sum(x * x for x in vec) ** 0.5
    if norm > 1e-9:
        vec = [x / norm for x in vec]
    return vec


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Deterministische cosine-Similarität (reines Python, kein
    numpy nötig). 0..1 (nur positive, wenn beide Vektoren
    identisch) oder -1..1 für generelle Vektoren."""
    if not a or not b or len(a) != len(b):
        return 0.0  # leere Platzhalter oder unterschiedliche Modelle
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def embed_texts(texts, *, client: Optional[Client] = None,
                fallback_stub: bool = True) -> list[list[float]]:
    """Bequemer Wrapper: versucht HTTP-Client, fällt auf StubClient
    zurück wenn `fallback_stub=True` und HTTP fehlschlägt.

    Für RAG-Integrationen: wenn der Embedding-Server (Ollama/vLLM)
    nicht erreichbar ist, kein Crash, sondern ein "kein Treffer"
    Zustand, der von der RAG-Pipeline als "keine Angaben" behandelt
    wird.
    """
    client = client or Client()
    try:
        out = client.embed(texts)
    except Exception:
        if fallback_stub:
            out = StubClient().embed(texts)
        else:
            raise
    return out


def chat(messages, *, client: Optional[Client] = None,
         fallback_stub: bool = True) -> str:
    client = client or Client()
    try:
        return client.chat(messages)
    except Exception:
        if fallback_stub:
            return StubClient().chat(messages)
        raise
