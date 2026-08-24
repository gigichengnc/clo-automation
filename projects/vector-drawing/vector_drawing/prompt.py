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
    "back_neckline": {
        "same_as_front": (
            r"\bback[ -]?neck(?:line)?[ -]same[ -]as[ -]front\b",
            r"\bsame[ -]front[ -]and[ -]back[ -]?neck(?:line)?\b",
            r"前後領相同",
            r"前后领相同",
        ),
        "shallow_round": (
            r"\bshallow[ -]round[ -]back[ -]?neck(?:line)?\b",
            r"\bshallow[ -]back[ -]?neck(?:line)?\b",
            r"淺圓後領",
            r"浅圆后领",
            r"淺後領",
            r"浅后领",
        ),
    },
    "back_closure": {
        "none": (
            r"\bno[ -]back[ -](?:closure|zip|zipper)\b",
            r"\bback[ -]closure[ -]none\b",
            r"後背無拉鏈",
            r"后背无拉链",
            r"無後開合",
            r"无后开合",
        ),
        "centre_zip": (
            r"\b(?:centre|center)[ -]?back[ -]?(?:zip|zipper)\b",
            r"\bback[ -](?:centre|center)[ -]?(?:zip|zipper)\b",
            r"後中拉鏈",
            r"后中拉链",
        ),
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


def _resolve_category(text: str, category: str, *, required: bool) -> str | None:
    found = _matches(text, category)
    if len(found) > 1:
        raise PromptParseError(f"ambiguous {category}: {', '.join(found)}")
    if not found:
        if required:
            raise PromptParseError(f"missing explicit {category}")
        return None
    return found[0]


def parse_prompt(text: str, *, require_back: bool = False) -> PromptParseResult:
    """Map a garment prompt to the v0.1 DressSpec without hidden defaults.

    Front semantic categories must always be explicit. Back categories become
    mandatory only when a caller requests a back technical flat. Back language
    is still parsed when present for front requests so contradictions are not
    silently ignored.
    """
    normalized = " ".join(text.strip().split())
    if not normalized:
        raise PromptParseError("prompt is empty")

    unsupported = [pattern for pattern in _UNSUPPORTED if re.search(pattern, normalized, flags=re.IGNORECASE)]
    if unsupported:
        raise PromptParseError("prompt contains a garment feature unsupported by v0.1")

    resolved: dict[str, str] = {}
    for category in ("garment", "neckline", "sleeve", "silhouette", "length"):
        value = _resolve_category(normalized, category, required=True)
        assert value is not None
        resolved[category] = value

    if resolved["garment"] != "dress":
        raise PromptParseError(f"unsupported garment: {resolved['garment']}")

    back_neckline = _resolve_category(normalized, "back_neckline", required=require_back)
    back_closure = _resolve_category(normalized, "back_closure", required=require_back)
    if back_neckline is not None:
        resolved["back_neckline"] = back_neckline
    if back_closure is not None:
        resolved["back_closure"] = back_closure

    spec = DressSpec(
        neckline=resolved["neckline"],
        sleeve=resolved["sleeve"],
        silhouette=resolved["silhouette"],
        length=resolved["length"],
        back_neckline=back_neckline,
        back_closure=back_closure,
    )
    return PromptParseResult(garment="dress", spec=spec, matched=resolved)
