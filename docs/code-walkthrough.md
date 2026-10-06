# Code walkthrough

A plain-language guide for explaining this project in an interview.

## Vocabulary

- **EU AI Act:** the EU law regulating AI by risk level. Amended in 2026 by the "AI Omnibus", which postponed the high-risk deadlines.
- **Provider:** whoever develops an AI system and puts it on the market or into service under their name. **Deployer:** whoever uses it professionally. A hospital that builds its own tool is both.
- **Annex I / Annex III:** the two routes to "high-risk". Annex I covers AI inside products already regulated by EU law (like medical devices). Annex III is a list of sensitive uses (like emergency triage, recruitment, credit scoring).
- **NIST AI RMF:** a US framework that organises AI risk work into GOVERN, MAP, MEASURE and MANAGE.
- **Inherent vs residual risk:** risk before controls vs risk after controls.

## `governance/classify.py`

`classify(system)` walks the same decision tree as the diagram in ARCHITECTURE.md:

1. A **prohibited practice** → stop, nothing else matters.
2. **Annex I product** needing third-party conformity assessment → high-risk, from 2 Aug 2028.
3. **Annex III use case** → high-risk, from 2 Dec 2027. If both routes apply, the **earlier** date wins.
4. **Interacts with people** or **generates content** → transparency duties (Art. 50), from 2 Aug 2026.
5. Nothing applies → minimal risk.
6. **Always:** AI literacy (Art. 4).

For high-risk systems it adds the provider obligations (Art. 9–17, 43, 72–73) or the deployer obligations (Art. 26–27), depending on the organisation's role. Notes cover things like *"the model vendor carries the general-purpose AI obligations"* and *"outside the EU this is a voluntary benchmark"*. The input is a simple description per system in `assessment/systems.json`.

## `governance/register.py`

- **`validate(rows)`** checks every risk has an id, owner, controls and NIST function, that scores are 1–5, that ids aren't duplicated, and that **residual ≤ inherent** (controls can't make risk worse).
- **`score(row)`** = likelihood × impact (1–25).
- **`appetite(score)`**: 1–8 accepted, 9–14 board sign-off, 15+ blocks go-live.
- **`heatmap(rows)`** counts risks in a 5×5 grid for the report.

`python -m governance register` prints the sorted register, the heat map and the risks needing sign-off. It **exits with an error** if the register is invalid or something blocks go-live, which is how CI enforces it.

## The tests

Classification: System A → transparency only, with the 2 Aug 2026 date. System B → high-risk by both routes with the 2 Dec 2027 date. Annex I alone → 2 Aug 2028. Prohibited and minimal cases. Register: the real register is valid, the appetite bands work, the triage risk R09 needs board sign-off, and validation catches missing owners, bad scores, duplicate ids, unknown NIST functions, and residual scores higher than inherent.

## Likely interview questions

- **"Is a chatbot high-risk under the AI Act?"** Usually not by itself. It's in the transparency tier, so people must know they're talking to an AI. It becomes high-risk when its *purpose* is in Annex III or it's part of a regulated product, like the triage example.
- **"When do the high-risk rules apply?"** After the 2026 AI Omnibus: 2 Dec 2027 for Annex III systems and 2 Aug 2028 for AI in regulated products. Transparency duties applied from 2 Aug 2026.
- **"How does NIST AI RMF relate to the AI Act?"** The Act is law and says *what*. NIST is a voluntary framework for *how*: governance, mapping context, measuring, managing. They complement each other (ADR-001).
- **"Why put a risk register in code?"** So it can't silently decay: every risk keeps an owner and valid scores, and go-live blockers are flagged automatically (ADR-003).
- **"Does this apply in Lebanon?"** Not directly, because the AI Act covers the EU market and outputs used in the EU. It's still a strong benchmark for any hospital working with international partners.
