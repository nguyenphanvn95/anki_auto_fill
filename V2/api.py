# -*- coding: utf-8 -*-
"""
ENVI API integration - Updated based on actual JSON structure
"""

import json
import urllib.parse
import urllib.request
from typing import Any, Dict, List


API_BASE = "https://en.jpdictionary.com/api/"


def _build_flip_map() -> Dict[str, str]:
    """Build character flip map for decoding"""
    m: Dict[str, str] = {}
    for aa in range(32, 127):
        m[chr(aa)] = chr(158 - aa)
    return m


_FLIP_MAP = _build_flip_map()


def _swap_pairs(chars: List[str]) -> List[str]:
    """Swap adjacent pairs of characters"""
    for i in range(0, len(chars) - 1, 2):
        chars[i], chars[i + 1] = chars[i + 1], chars[i]
    return chars


def decode_obfuscated(s: Any) -> Any:
    """Decode obfuscated string from ENVI API"""
    if not isinstance(s, str):
        return s
    n = len(s)
    chars = list(s)
    for i, c in enumerate(chars):
        if c in _FLIP_MAP:
            chars[i] = _FLIP_MAP[c]
    mod = n % 3
    if mod == 0:
        chars.reverse()
    elif mod == 1:
        chars = _swap_pairs(chars)
    else:
        chars = _swap_pairs(chars)
        chars.reverse()
    return "".join(chars)


def post_form(url: str, params: Dict[str, str], timeout: int = 12) -> Dict[str, Any]:
    """Make POST request to API"""
    body = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "User-Agent": "Anki-ENVI-Auto-Fill/1.0.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)


def decode_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Decode API response payload"""
    if not isinstance(payload, dict):
        return payload

    if isinstance(payload.get("def"), str):
        payload["def"] = decode_obfuscated(payload["def"])

    mean = payload.get("mean")
    if isinstance(mean, str):
        try:
            mean = json.loads(mean)
        except Exception:
            mean = None

    if isinstance(mean, list):
        decoded = []
        for item in mean:
            if isinstance(item, dict):
                item = dict(item)
                item["m"] = decode_obfuscated(item.get("m"))
                item["e"] = decode_obfuscated(item.get("e"))
                item["v"] = decode_obfuscated(item.get("v"))
            decoded.append(item)
        payload["mean"] = decoded

    return payload


def search_english(word: str) -> Dict[str, Any]:
    """Search for English word"""
    data = post_form(API_BASE + "search/e", {"w": word})
    return decode_result(data)


def extract_data(payload, show_pos_tags=False):
    """
    Parse raw JSON from ENVI lookup
    Return dict ready to write into Anki fields
    """
    if not payload:
        return {}

    word = (payload.get("word") or "").strip()
    pron = (payload.get("pron") or "").strip()
    pos = (payload.get("pos") or "").strip()
    def_text = (payload.get("def") or "").strip()
    mean_data = payload.get("mean") or []

    # ---------- Meanings (Definition_VI) ----------
    meanings = []
    for item in mean_data:
        if isinstance(item, dict):
            m = (item.get("m") or "").strip()
            if m:
                meanings.append(m)

    # mỗi nghĩa 1 dòng (HTML <br>)
    meanings_text = "<br>".join(meanings)

    # ---------- Examples ----------
    examples = []
    for item in mean_data:
        if isinstance(item, dict):
            e = (item.get("e") or "").strip()
            v = (item.get("v") or "").strip()
            if e and v:
                examples.append(f"{e}<br>{v}")

    # mỗi cặp EN–VI cách nhau 1 dòng trống
    examples_text = "<br><br>".join(examples)

    # Nếu muốn show POS tag trong meanings (tuỳ chọn)
    if show_pos_tags and pos and meanings_text:
        meanings_text = f"[{pos}]<br>" + meanings_text

    # --- TRẢ NHIỀU KEY ĐỂ TƯƠNG THÍCH PROCESSOR + MAPPING ---
    result = {
        "word": word,

        # IPA / Pronunciation
        "pronunciation": pron,
        "ipa": pron,
        "IPA": pron,

        # Part of speech
        "part_of_speech": pos,
        "pos": pos,
        "partOfSpeech": pos,

        # Definition / Sources (từ payload["def"])
        "definition": def_text,
        "def": def_text,
        "sources": def_text,
        "Sources": def_text,

        # Meanings + Examples
        "meanings": meanings_text,
        "examples": examples_text,
    }

    return result
