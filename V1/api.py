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


def extract_data(payload: Dict[str, Any], show_pos_tags: bool = False) -> Dict[str, str]:
    """
    Extract structured data from API response
    
    JSON structure from ENVI API:
    {
        "word": "word",
        "pron": "wɜːd",
        "pos": "noun",
        "def": "a single distinct meaningful element of speech or writing",
        "mean": [
            {
                "m": "His [word] carried a lot of weight in the discussion",
                "e": "Lời nói của anh ấy có nhiều trọng lượng trong cuộc thảo luận",
                "v": "từ"
            },
            {
                "m": "Can you use the word in a sentence?",
                "e": "Bạn có thể dùng từ này trong một câu không?",
                "v": "từ ngữ"
            }
        ]
    }
    
    Where:
    - m: English example sentence (may contain [word] placeholder)
    - e: Vietnamese translation of the example sentence
    - v: Vietnamese meaning of the word
    
    Returns:
        Dictionary with keys: definition, pronunciation, pos, meanings, examples
    """
    result = {
        "definition": "",
        "pronunciation": "",
        "pos": "",
        "meanings": "",
        "examples": ""
    }
    
    # Extract definition
    definition = (payload.get("def") or "").strip()
    result["definition"] = definition
    
    # Extract pronunciation
    pron = (payload.get("pron") or "").strip()
    if pron:
        # Format as IPA notation if needed
        if "/" not in pron:
            pron = f"/{pron}/"
    result["pronunciation"] = pron
    
    # Extract POS (Part of Speech)
    pos = (payload.get("pos") or "").strip()
    result["pos"] = pos

    # Optionally prepend POS tag into meanings for display
    pos_prefix = f"[{pos}] " if (show_pos_tags and pos) else ""
    
    # Extract meanings and examples from 'mean' array
    mean = payload.get("mean")
    if isinstance(mean, list) and mean:
        meanings_list = []
        examples_list = []
        seen_meanings = set()  # To avoid duplicates
        
        for item in mean:
            if not isinstance(item, dict):
                continue
            
            # Get fields
            m = (item.get("m") or "").strip()  # English example sentence
            e = (item.get("e") or "").strip()  # Vietnamese translation of example
            v = (item.get("v") or "").strip()  # Vietnamese meaning
            
            # Add Vietnamese meaning (avoid duplicates)
            if v and v not in seen_meanings:
                meanings_list.append(v)
                seen_meanings.add(v)
            
            # Add example pair (English sentence + Vietnamese translation)
            if m and e:
                # Replace [word] placeholder with actual word if present
                word = payload.get("word", "")
                if word and "[word]" in m.lower():
                    m = m.replace("[word]", word).replace("[Word]", word.capitalize())
                
                examples_list.append(f"{m}\n{e}")
        
        # Join meanings (one per line)
        result["meanings"] = "\n".join([(pos_prefix + m) if (i==0 and pos_prefix) else m for i, m in enumerate(meanings_list)])
        
        # Join examples (separated by blank line for clarity)
        result["examples"] = "\n\n".join(examples_list)
    
    return result
