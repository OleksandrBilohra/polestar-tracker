"""
Simulated AI verification for OEM parts.

Checks whether a submitted part number looks like a real Volvo / Polestar
OEM part and returns a verdict with availability hints.  The logic is
intentionally kept lightweight so the module can later be swapped for a
real AI / parts-database API without touching the rest of the codebase.
"""

import re

# ── Known Volvo / Polestar OEM part-number prefixes and patterns ─────────
# Real Volvo parts typically follow patterns like:
#   31XXX-XXX  (five digits, dash, three chars)
#   30XXX-XXX
#   8XXXXXXX   (eight-digit numeric)
#   6XXXXXXX
# Polestar-specific upgrade parts often start with 31 or carry a
# "Polestar" prefix in aftermarket catalogues.

_VOLVO_PATTERNS = [
    re.compile(r'^3[01]\d{3,5}[- ]?\d{0,4}$', re.IGNORECASE),
    re.compile(r'^[0-9]{7,10}$'),
    re.compile(r'^VOL[A-Z0-9\- ]{4,}$', re.IGNORECASE),
]

# Categories that are common for Polestar OEM upgrades
_KNOWN_CATEGORIES = {
    'engine', 'brakes', 'suspension', 'drivetrain', 'exhaust',
    'turbo', 'intake', 'ecu', 'body', 'interior', 'electrical',
    'cooling', 'fuel', 'transmission', 'wheels', 'steering',
}

_TRUSTED_SHOPS = [
    'FCP Euro (fcpeuro.com)',
    'Skandix (skandix.de)',
    'Volvo Parts Webstore (volvopartswebstore.com)',
    'IPD (ipdusa.com)',
    'eEuroparts (eeuroparts.com)',
]


def verify_oem_part(part_number: str, part_name: str,
                    description: str, model: str,
                    category: str) -> dict:
    """Return an AI-style verification result.

    Returns
    -------
    dict  with keys:
        verified : bool   – whether the part appears genuine
        verdict  : str    – human-readable explanation
    """
    part_number = (part_number or '').strip()
    part_name = (part_name or '').strip()
    category_lower = (category or '').strip().lower()

    issues: list[str] = []
    tips: list[str] = []

    # 1. Part-number format check
    number_looks_valid = any(p.match(part_number) for p in _VOLVO_PATTERNS)
    if not number_looks_valid:
        issues.append(
            f'The part number "{part_number}" does not match common '
            'Volvo/Polestar OEM formats (e.g. 31400-123 or 8-digit numeric).'
        )
    else:
        tips.append(
            f'Part number "{part_number}" matches a known Volvo OEM format.'
        )

    # 2. Category plausibility
    if category_lower not in _KNOWN_CATEGORIES:
        issues.append(
            f'Category "{category}" is uncommon for Polestar OEM parts. '
            'Double-check that this is an authentic OEM category.'
        )

    # 3. Name / description sanity
    if len(part_name) < 3:
        issues.append('Part name is too short to verify.')
    if len(description) < 10:
        issues.append('Description is too brief for a meaningful check.')

    # 4. Model compatibility
    valid_models = {'S60 Polestar', 'V60 Polestar'}
    if model not in valid_models:
        issues.append(
            f'Model "{model}" is not in the verified Polestar roster '
            f'({", ".join(sorted(valid_models))}).'
        )

    # 5. Build verdict
    verified = len(issues) == 0
    lines: list[str] = []

    if verified:
        lines.append('✅ This part looks like a genuine Volvo/Polestar OEM part.')
        lines.append('')
        lines.append('Where to buy:')
        for shop in _TRUSTED_SHOPS:
            lines.append(f'  • {shop}')
        lines.append('')
        lines.append(
            'Tip: Always cross-reference the part number in your Volvo '
            'dealer\'s EPC (Electronic Parts Catalogue) to confirm fitment '
            'for your specific VIN.'
        )
    else:
        lines.append('⚠️ Verification could not fully confirm this part.')
        lines.append('')
        lines.append('Issues found:')
        for issue in issues:
            lines.append(f'  • {issue}')
        if tips:
            lines.append('')
            lines.append('Positive signals:')
            for tip in tips:
                lines.append(f'  • {tip}')
        lines.append('')
        lines.append(
            'Suggestion: Verify the part number directly with a Volvo '
            'dealer or check FCP Euro / Skandix catalogues before purchasing.'
        )

    return {
        'verified': verified,
        'verdict': '\n'.join(lines),
    }
