"""
ShieldSpam AI — scoring model (server-side).

Mirrors the client-side detection logic used in the browser prototype
(NativeParser.cs + the in-browser rule engine), so the backend is the single
source of truth for scoring. Ports over the fixes made along the way:
  - link counting matches whole URL tokens instead of double-counting
    substrings like "http" and "www." inside the same link
  - multi-word keyword phrases ("social security", "no risk") are matched
    against the raw text, not against single split words
  - phone numbers are checked for known fake/placeholder patterns:
    sequential digit runs, repeated digit blocks, and the NANP "555"
    reserved/fictional exchange
"""

import math
import re

PHONE_CANDIDATE_RE = re.compile(r"(?<!\w)(\+?\(?\d[\d\-.\s()]{5,}\d)(?!\w)")
URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
IP_URL_RE = re.compile(r"https?://(\d{1,3}\.){3}\d{1,3}", re.IGNORECASE)

SHORTENER_DOMAINS = [
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "buff.ly",
    "rebrand.ly", "cutt.ly", "shorturl.at", "rb.gy", "tiny.cc", "lnkd.in",
    "s.id", "bl.ink",
]
BAD_TLDS = [".xyz", ".top", ".click", ".loan", ".work", ".date", ".stream", ".download"]
HTML_TAGS = ["<a", "<b", "<html", "<div"]

# Multi-word phrases must be matched against the raw text — splitting the
# message into single words (below) can never match a two-word phrase.
KEYWORD_PHRASES = ["social security", "no risk"]
KEYWORDS = {
    "urgent", "free", "winner", "cash", "prize", "click", "verify", "account",
    "suspended", "limited", "offer", "subscribe", "unsubscribe", "credit",
    "card", "bank", "login", "password", "irs", "lottery", "exclusive",
    "guaranteed", "hidden", "confidential", "identity", "security", "locked",
}


def _is_sequential_digits(digits: str) -> bool:
    if len(digits) < 4:
        return False
    asc = desc = True
    for i in range(1, len(digits)):
        prev, cur = int(digits[i - 1]), int(digits[i])
        if cur != (prev + 1) % 10:
            asc = False
        if cur != (prev + 9) % 10:
            desc = False
    return asc or desc


def _has_sequential_run(digits: str, run_len: int = 4) -> bool:
    for i in range(0, len(digits) - run_len + 1):
        asc = desc = True
        for j in range(1, run_len):
            prev, cur = int(digits[i + j - 1]), int(digits[i + j])
            if cur != (prev + 1) % 10:
                asc = False
            if cur != (prev + 9) % 10:
                desc = False
        if asc or desc:
            return True
    return False


def _has_repeated_digit_block(digits: str, run_len: int = 3) -> bool:
    for i in range(0, len(digits) - run_len + 1):
        if len(set(digits[i:i + run_len])) == 1:
            return True
    return False


def _is_fake_nanp_exchange(digits: str) -> bool:
    d = digits
    if len(d) == 11 and d[0] == "1":
        d = d[1:]
    if len(d) != 10:
        return False
    return d[3:6] == "555"


def _count_occurrences(text: str, sub: str) -> int:
    count = pos = 0
    lower, sub_lower = text.lower(), sub.lower()
    while True:
        pos = lower.find(sub_lower, pos)
        if pos == -1:
            return count
        count += 1
        pos += len(sub)


def _count_links(text: str) -> int:
    # A single "http://www.example.com" contains both "http" and "www." —
    # matching whole URL tokens avoids counting one real link as two.
    return len(URL_RE.findall(text))


def _count_keywords(text: str) -> int:
    lower = text.lower()
    count = 0
    remaining = lower
    for phrase in KEYWORD_PHRASES:
        hits = _count_occurrences(remaining, phrase)
        count += hits
        if hits:
            # Strip matched phrases first so a phrase like "social security"
            # isn't double-counted again via its component word "security".
            remaining = remaining.replace(phrase, " ")
    words = re.split(r"[\s.,!?;:]+", remaining)
    count += sum(1 for w in words if w in KEYWORDS)
    return count


def _calc_entropy(text: str) -> float:
    if not text:
        return 0.0
    freq: dict = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    entropy = 0.0
    n = len(text)
    for c in freq.values():
        p = c / n
        entropy -= p * math.log2(p)
    return entropy


def extract_signals(text: str) -> dict:
    text = text or ""
    lower = text.lower()
    s: dict = {}

    s["linkCount"] = _count_links(text)

    phone_numbers = []
    has_suspicious_phone_pattern = False
    for m in PHONE_CANDIDATE_RE.finditer(text):
        digits_only = re.sub(r"\D", "", m.group(1))
        if len(digits_only) < 7 or len(digits_only) > 15:
            continue
        phone_numbers.append(m.group(1).strip())
        all_same = len(set(digits_only)) == 1
        if (
            all_same
            or _is_sequential_digits(digits_only)
            or _has_sequential_run(digits_only)
            or _has_repeated_digit_block(digits_only)
            or _is_fake_nanp_exchange(digits_only)
        ):
            has_suspicious_phone_pattern = True
    s["phoneCount"] = len(phone_numbers)
    s["hasSuspiciousPhonePattern"] = has_suspicious_phone_pattern

    s["shortenerCount"] = sum(1 for d in SHORTENER_DOMAINS if d in lower)
    s["ipUrlCount"] = len(IP_URL_RE.findall(text))
    s["emailCount"] = _count_occurrences(text, "@")
    s["exclamationCount"] = text.count("!")

    letters = len(text)
    capital_count = sum(1 for c in text if c.isupper())
    s["capsRatio"] = (capital_count / letters) if letters else 0.0

    s["wordCount"] = len(re.findall(r"[A-Za-z]+", text))
    s["keywordCount"] = _count_keywords(text)
    s["entropy"] = _calc_entropy(text)
    s["hasSuspiciousTLD"] = any(tld in lower for tld in BAD_TLDS)
    s["hasHTML"] = any(tag in lower for tag in HTML_TAGS)
    s["exclamationRatio"] = (s["exclamationCount"] / letters) if letters else 0.0

    return s


def rule_score(sig: dict) -> int:
    score = 0
    if sig["linkCount"] > 0 and sig["keywordCount"] >= 2:
        score += 35
    if sig["linkCount"] > 0 and sig["keywordCount"] >= 3:
        score += 10
    if sig["linkCount"] > 0 and sig["keywordCount"] >= 5:
        score += 10
    if sig["hasSuspiciousTLD"]:
        score += 30
    if sig["linkCount"] > 0 and sig["phoneCount"] > 0:
        score += 35
    if sig["phoneCount"] > 0 and sig["linkCount"] == 0:
        score += 12
        if sig["keywordCount"] >= 2:
            score += 25
    if sig["phoneCount"] >= 2:
        score += 15
    if sig["hasSuspiciousPhonePattern"]:
        score += 30
    if sig["entropy"] > 4.5:
        score += 20
    if sig["capsRatio"] > 0.20:
        score += 15
    if sig["exclamationRatio"] > 0.02:
        score += 15
    if sig["keywordCount"] > 5:
        score += 30
    elif sig["keywordCount"] > 3:
        score += 20
    elif sig["keywordCount"] > 1 and sig["linkCount"] > 0:
        score += 10
    if sig["shortenerCount"] > 0:
        score += 25
    if sig["ipUrlCount"] > 0:
        score += 30
    return min(score, 100)


def build_reasons(sig: dict, score: int) -> list:
    reasons = []
    if sig["linkCount"] > 0:
        reasons.append("Contains external links")
    if sig["shortenerCount"] > 0:
        reasons.append("Uses a link-shortening service")
    if sig["ipUrlCount"] > 0:
        reasons.append("Link points to a raw IP address")
    if sig["hasSuspiciousTLD"]:
        reasons.append("Suspicious URL extension")
    if sig["phoneCount"] > 0 and sig["linkCount"] > 0:
        reasons.append("Phone + Link scam pattern")
    elif sig["phoneCount"] > 0 and sig["keywordCount"] >= 2:
        reasons.append("Phone number with urgency/scam keywords")
    elif sig["phoneCount"] > 0:
        reasons.append("Contains a phone number")
    if sig["phoneCount"] >= 2:
        reasons.append("Multiple phone numbers listed")
    if sig["hasSuspiciousPhonePattern"]:
        reasons.append("Phone number matches a known fake/placeholder pattern (sequential, repeated block, or 555 exchange)")
    if sig["keywordCount"] > 5:
        reasons.append("Multiple spam keywords")
    elif sig["keywordCount"] > 3:
        reasons.append("Several spam keywords")
    elif sig["keywordCount"] > 1 and sig["linkCount"] > 0:
        reasons.append("Link with suspicious keywords")
    if sig["entropy"] > 4.5:
        reasons.append("Unnatural text randomness")
    if sig["capsRatio"] > 0.20:
        reasons.append("Excessive uppercase letters")
    if not reasons and score > 50:
        reasons.append("Suspicious pattern detected")
    return reasons


def score_text(text: str) -> dict:
    sig = extract_signals(text)
    score = rule_score(sig)
    tier = "spam" if score >= 60 else ("suspicious" if score >= 30 else "safe")
    reasons = build_reasons(sig, score) or ["No red flags detected"]
    return {
        "score": score,
        "tier": tier,
        "reasons": reasons,
        "signals": sig,
    }
