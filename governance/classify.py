"""Simplified EU AI Act triage: which risk tier(s) and obligations apply to an AI system.

A first-pass screening aid for a governance team, NOT legal advice. It encodes the main
decision points of Regulation (EU) 2024/1689 as amended by the AI Omnibus,
Regulation (EU) 2026/1744 (in force 27 July 2026). Confirm every result with legal counsel.
"""

ANNEX_III_DATE = "2027-12-02"   # stand-alone high-risk systems (deferred by the AI Omnibus)
ANNEX_I_DATE = "2028-08-02"     # high-risk AI in products under EU product legislation, e.g. medical devices
TRANSPARENCY_DATE = "2026-08-02"

HIGH_RISK_PROVIDER = [
    ("Art. 9", "Risk management system across the lifecycle"),
    ("Art. 10", "Data and data governance (relevant, representative, examined for bias)"),
    ("Art. 11", "Technical documentation"),
    ("Art. 12", "Automatic record-keeping (logs)"),
    ("Art. 13", "Transparency and instructions for use for deployers"),
    ("Art. 14", "Human oversight by design"),
    ("Art. 15", "Accuracy, robustness and cybersecurity"),
    ("Art. 17", "Quality management system"),
    ("Art. 43", "Conformity assessment before placing on the market"),
    ("Art. 72-73", "Post-market monitoring and serious-incident reporting"),
]
HIGH_RISK_DEPLOYER = [
    ("Art. 26", "Use per instructions, competent human oversight, monitoring, keep logs (at least 6 months)"),
    ("Art. 27", "Fundamental rights impact assessment, for public bodies and providers of public services "
                "(Annex III systems; confirm applicability)"),
]


def classify(system):
    """Return {"tiers": [...], "obligations": [{"ref", "text", "applies_from"}], "notes": [...]}."""
    tiers, obligations, notes = [], [], []

    def add(ref, text, date):
        obligations.append({"ref": ref, "text": text, "applies_from": date})

    if system.get("prohibited_practice"):
        return {"tiers": ["prohibited"],
                "obligations": [{"ref": "Art. 5", "text": f"Prohibited practice: {system['prohibited_practice']}. "
                                 "Must not be placed on the market or used.", "applies_from": "2025-02-02"}],
                "notes": ["Stop: redesign the use case."]}

    roles = system.get("roles", [])
    high_risk_date = None
    if system.get("annex_I_product") and system.get("third_party_conformity_assessment"):
        tiers.append("high-risk (Art. 6(1), Annex I product)")
        high_risk_date = ANNEX_I_DATE
        notes.append("As a regulated product, sector conformity rules (e.g. EU MDR for medical devices) "
                     "also apply; the AI Act requirements are assessed within that procedure.")
    if system.get("annex_III_area"):
        tiers.append(f"high-risk (Art. 6(2), Annex III: {system['annex_III_area']})")
        high_risk_date = min(filter(None, [high_risk_date, ANNEX_III_DATE]))
        if system.get("profiling"):
            notes.append("Profiling of natural persons: the Art. 6(3) exemption can't be used.")

    if high_risk_date:
        if "provider" in roles:
            for ref, text in HIGH_RISK_PROVIDER:
                add(ref, text, high_risk_date)
        if "deployer" in roles:
            for ref, text in HIGH_RISK_DEPLOYER:
                add(ref, text, high_risk_date)

    if system.get("interacts_with_natural_persons"):
        tiers.append("transparency (Art. 50)")
        add("Art. 50(1)", "Inform people that they are interacting with an AI system, unless obvious",
            TRANSPARENCY_DATE)
    if system.get("generates_synthetic_content"):
        if "transparency (Art. 50)" not in tiers:
            tiers.append("transparency (Art. 50)")
        add("Art. 50(2)", "Mark AI-generated content in a machine-readable way (confirm scope for internal "
            "text tools; systems on the market before 2 Aug 2026 have until 2 Dec 2026)", TRANSPARENCY_DATE)

    if not tiers:
        tiers.append("minimal risk")
        notes.append("No specific AI Act obligations beyond AI literacy; voluntary codes of conduct encouraged.")

    add("Art. 4", "Take measures to support sufficient AI literacy of staff dealing with the system",
        "2025-02-02")
    if system.get("uses_gpai_model"):
        notes.append("General-purpose AI model obligations (Art. 53-55) sit with the model provider; "
                     "do vendor due diligence and keep their documentation.")
    if system.get("outside_eu"):
        notes.append("The AI Act applies to systems placed on the EU market or whose output is used in "
                     "the EU; elsewhere this assessment serves as a voluntary benchmark.")
    return {"tiers": tiers, "obligations": obligations, "notes": notes}
