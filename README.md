# AI Governance Assessment: EU AI Act and NIST AI RMF

![tests](https://github.com/aadirani/ai-governance-assessment/actions/workflows/tests.yml/badge.svg)

What does the **EU AI Act** require of an AI system, and how do you manage its risks in practice? This repo assesses two AI systems at a **fictional** public hospital group, using the AI Act (with the 2026 amendments) and the **NIST AI Risk Management Framework**, and turns the risk register into something that's **checked automatically**.

> Not legal advice. A structured first-pass assessment and working method.

## The idea in one paragraph

The EU AI Act sorts AI systems by risk: some uses are banned, some are "high-risk" with heavy obligations, some only have to be transparent, and most have few rules. The **same AI model** can land in different tiers depending on what it's used for. Here, a staff assistant that answers questions about leave and procurement policies is in the **transparency** tier. A tool that suggests how urgently emergency patients need care is **high-risk** twice over. The assessment shows the reasoning, the obligations and deadlines, a scored risk register mapped to NIST's GOVERN / MAP / MEASURE / MANAGE functions, and the governance set-up that keeps it current.

## Try it

Needs Python 3.9+, nothing to install.

```bash
python -m governance classify     # EU AI Act tier and obligations for each system
python -m governance register     # validate and score the risk register, heat map
```

## Key findings

| | Staff policy assistant | Emergency triage assistant |
|---|---|---|
| EU AI Act tier | Transparency (Art. 50) | High-risk (MDR medical device + Annex III triage) |
| Main obligations from | 2 Aug 2026 | 2 Dec 2027 |
| Highest residual risk | 6 / 25: accepted | 10 / 25: needs board sign-off |

## What's inside

| Path | What it is |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Full assessment: classification flow, obligations, NIST mapping, risk register summary, governance model, 5 decisions, effort estimates, sources |
| [assessment/systems.json](assessment/systems.json) | Descriptions of the two systems, used as input to classification |
| [assessment/risk_register.csv](assessment/risk_register.csv) | 12 risks with inherent and residual scores, controls, owners, NIST function, AI Act references |
| [governance/](governance/) | The classifier and the register checker |
| [docs/code-walkthrough.md](docs/code-walkthrough.md) | Plain-language explanation |
