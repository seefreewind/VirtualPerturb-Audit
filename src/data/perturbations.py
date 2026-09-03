from __future__ import annotations


CONTROL_LABELS = {"ctrl", "control", "non-targeting", "non_targeting", "ntc", "safe-targeting"}


def is_control_label(label: str) -> bool:
    return str(label).strip().lower() in CONTROL_LABELS


def normalize_condition(label: str) -> str:
    """Canonicalize single/combinatorial perturbation labels without inventing targets."""
    text = str(label).strip()
    if not text or text.lower() in {"nan", "none", "na"}:
        return "NA"
    parts = []
    for raw in text.replace("|", "+").replace("_", "+").split("+"):
        token = raw.strip()
        if not token or is_control_label(token):
            continue
        parts.append(token.upper())
    if not parts:
        return "ctrl"
    return "+".join(sorted(parts))


def target_fields(label: str) -> tuple[str, str]:
    normalized = normalize_condition(label)
    if normalized == "ctrl" or normalized == "NA":
        return "NA", "NA"
    parts = normalized.split("+")
    first = parts[0] if len(parts) >= 1 else "NA"
    second = parts[1] if len(parts) >= 2 else "NA"
    return first, second
