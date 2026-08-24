from __future__ import annotations

import re
from dataclasses import dataclass

from .fashion_flat import DressSpec


class PromptParseError(ValueError):
    """Raised when natural language cannot be mapped without guessing."""


@dataclass(frozen=True)
class PromptParseResult:
    garment: str
    spec: DressSpec
    matched: dict[str, str]


_ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
    "garment": {
        "dress": (r"\bdress\b", r"連衣裙", r"连衣裙"),
    },
    "neckline": {
        "round": (r"\bround[ -]?neck(?:line)?\b", r"圓領", r"圆领"),
        "v": (r"\bv[ -]?neck(?:line)?\b", r"V領", r"v領", r"V领", r"v领"),
    },
    "sleeve": {
        "sleeveless": (r"\bsleeveless\b", r"無袖", r"无袖"),
        "short": (r"\bshort[ -]?sleeve(?:d)?\b", r"短袖"),
    },
    "silhouette": {
        "a_line": (r"\ba[ -]?line\b", r"A字", r"a字"),
        "straight": (r"\bstraight(?:[ -]?(?:cut|silhouette))?\b", r"直筒"),
    },
    "length": {
        "mini": (r"\bmini\b", r"迷你裙"),
        "knee": (r"\bknee[ -]?length\b", r"及膝"),
        "midi": (r"\bmidi\b", r"中長", r"中长"),
        "maxi": (r"\bmaxi\b", r"及踝", r"長款", r"长款"),
    },
}

# These phrases are deliberately rejected rather than silently simplified to a
# supported v0.1 option.
_UNSUPPORTED = (
    r"\blong[ -]?sleeve(?:d)?\b",
    r"\bpuff[ -]?sleeve(?:d)?\b",
    r"\bcap[ -]?sleeve(?:d)?\b",
    r"\boff[ -]?(?:the[ -]?)?shoulder\b",
    r"\bhalter\b",
    r"\bstrapless\b",
    r"長袖",
    r"长袖",
    r"泡泡袖",
    r"一字肩",
    r"掛頸",
    r"挂脖",
    r"抹胸",
)


def _matches(text: str, category: str) -> list[str]:
    found: list[str] = []
    for value, patterns in _ALIASES[category].items():
        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns):
            found.append(value)
    return found


def parse_prompt(text: str) -> PromptParseResult:
    """Map a garment prompt to the v0.1 DressSpec without hidden defaults.

    Every required semantic category must be stated explicitly. Conflicting or
    unsupported language safe-stops instead of choosing one interpretation.
    """
    normalized = " ".join(text.strip().split())
    if not normalized:
        raise PromptParseError("prompt is empty")

    unsupported = [pattern for pattern in _UNSUPPORTED if re.search(pattern, normalized, flags=re.IGNORECASE)]
    if unsupported:
        raise PromptParseError("prompt contains a garment feature unsupported by v0.1")

    resolved: dict[str, str] = {}
    for category in ("garment", "neckline", "sleeve", "silhouette", "length"):
        found = _matches(normalized, category)
        if len(found) > 1:
            raise PromptParseError(f"ambiguous {category}: {', '.join(found)}")
        if not found:
            raise PromptParseError(f"missing explicit {category}")
        resolved[category] = found[0]

    if resolved["garment"] != "dress":
        raise PromptParseError(f"unsupported garment: {resolved['garment']}")

    spec = DressSpec(
        neckline=resolved["neckline"],
        sleeve=resolved["sleeve"],
        silhouette=resolved["silhouette"],
        length=resolved["length"],
    )
    return PromptParseResult(garment="dress", spec=spec, matched=resolved)
