# Shared project guidance

This repository supports the ORIE 5355 Fall 2026 pricing project. Read the [assignment snapshot](docs/assignment/project-instructions.pdf), [course reference](docs/course-knowledge.md), and [Part 1 Step 1 plan](docs/part1-step1-plan.md) before making changes. The linked living assignment and course announcements take precedence over this dated snapshot; flag conflicts explicitly.

## Course policy and scope

- AI assistance is allowed for coding, but every teammate must understand and be able to explain submitted work. Do not generate, rewrite, outline, or otherwise assist with any component of the Project Report: the assignment forbids LLM use for that report (assignment pp. 1, 7, 12). Development plans here are for coding work, not report material.
- Prefer class-taught ideas and explain their connection to the task. Distinguish assignment requirements, lecture concepts, and our engineering recommendations. Do not describe optional model choices or starter defaults as requirements.
- Learn only from supplied offered prices, purchase decisions, customer covariates, and permitted simulator feedback. Do not train on hidden valuations or simulator internals, including valuation files present in the starter. Use the supplied evaluation helpers as intended; do not extract hidden targets from them.
- Do not alter simulator execution context or internal state, or access or modify another agent's files or private variables. Do not rely on modifications to supplied simulator/helper code.

## Coding and collaboration

- Preserve teammates' changes. Inspect Git status and relevant code before editing; avoid overwriting work or broad notebook output churn. Make incremental, understandable changes and record how they were checked.
- Keep training, preprocessing, and feature construction in `model_training/`; save required model artifacts in `agents/helper_files_here/`. Preserve the names `agents/agent_part1.py`, `agents/agent_part2.py`, and `agents/helper_files_here/`, and required method names.
- Use Python 3.13, the pinned `requirements.txt`, and the standard library. Follow the existing README for environment setup. Runtime code must be self-contained in the repository and approved packages, with no internet/API dependencies, no multiprocessing, and one CPU core. Respect the assignment's average 0.5-second decision limit.
- Use relative, portable paths. Keep secrets, personal notes, local environment files, and machine-specific assumptions out of shared code and documentation. Do not copy complete course slide PDFs into this repository; link and cite concise derived notes instead.
- Preserve the model's probability contract: current starter code calls `predict()` and clips regression output. A classifier requires the probability column corresponding to purchase label 1, not its predicted class label. Serialize fitted preprocessing with the estimator and verify save/reload agreement before integrating.
- Validate held-out purchase probabilities before optimizing prices. Do not confuse prediction quality with pricing revenue. Keep the Step 1 demand-model work separate from Step 2 static pricing, Step 3 inventory control, Part 2 competition, and the fairness bonus.
- Explain results and limits without fabricating runs or scores. Before publishing or pushing, verify the intended team repository, visibility, authorization, and permission to distribute included course material. A local edit does not authorize a push or remote-sharing change.

## Knowledge entry points

Lecture 7 supplies the main Step 1 method: estimate `Pr(purchase = 1 | price, covariates)` from observed offers and decisions, with empirical price bins or logistic regression (pp. 23–28). Its revenue objective `price * demand(price, covariates)` belongs to the later pricing step (pp. 17–18). Lecture 8 introduces backward induction and inventory opportunity cost for the later capacity step (pp. 12–21). See the [linked page mapping](docs/course-knowledge.md) before attributing a technique to class.

## Moving to the team repository

When the Classroom50 group repository becomes available, confirm its destination and access with the team, compare its current starter and instructions, and transfer reviewed changes without replacing teammates' work. Preserve this relative directory layout, re-run relevant checks in the new checkout, and follow its existing instructions. Do not assume the working repository is the graded submission destination or change remotes or publish files without authorization.
