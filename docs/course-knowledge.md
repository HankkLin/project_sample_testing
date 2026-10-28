# Course knowledge reference

Concise notes derived from Nikhil Garg's ORIE 5355 Fall 2026 lecture slides. Page references below are 1-based PDF pages, not notebook cells. Full slides remain at the [course lecture page](https://orie5355.github.io/Fall_2026/lectures/); they are not included here. Notes were verified against local copies of Lectures 2–8, with the pricing pages below read directly.

| Source | Pages | Concept and project use |
| --- | --- | --- |
| [Lecture 7: Introduction to Algorithmic Pricing](https://orie5355.github.io/Fall_2026/static_files/lectures/Lecture7_AlgorithmicPricing_Intro.pdf#page=11) | 11–13 | A buyer purchases when valuation meets the offered price. Pricing at a point estimate of valuation ignores asymmetric revenue consequences of estimation error. Step 1 should estimate purchase probability, not reconstruct private valuations. |
| [Lecture 7](https://orie5355.github.io/Fall_2026/static_files/lectures/Lecture7_AlgorithmicPricing_Intro.pdf#page=16) | 16–20 | Demand is the probability of purchasing at a price; unconstrained expected revenue is price times demand. With customer covariates, estimate conditional demand. Revenue maximization is Step 2, downstream of Step 1. |
| [Lecture 7](https://orie5355.github.io/Fall_2026/static_files/lectures/Lecture7_AlgorithmicPricing_Intro.pdf#page=23) | 23–25 | Historical observations are offered prices and purchase decisions, not valuations. Estimate demand empirically as purchases divided by offers in price bins; fine bins and covariate strata need many observations. Useful diagnostic baseline. |
| [Lecture 7](https://orie5355.github.io/Fall_2026/static_files/lectures/Lecture7_AlgorithmicPricing_Intro.pdf#page=26) | 26–28 | Logistic regression models purchase decisions using price, covariates, and possible interactions, borrowing information across prices and groups. Historical coverage of candidate prices is a major limitation. This motivates the recommended Step 1 comparator. |
| [Lecture 8: Algorithmic pricing: capacity, price differentiation, and competition](https://orie5355.github.io/Fall_2026/static_files/lectures/Lecture8_AlgorithmicPricing_Complications.pdf#page=9) | 9–19 | Limited inventory and future buyers couple today's price to later decisions. Work backward, then generalize the Bellman state to remaining inventory. Relevant to Step 3, not a requirement for Step 1. |
| [Lecture 8](https://orie5355.github.io/Fall_2026/static_files/lectures/Lecture8_AlgorithmicPricing_Complications.pdf#page=20) | 20–22 | Approximate future inventory value when full dynamic programming is impractical; interpret future value as opportunity cost. A later strategy option. |
| [Lecture 6: Recommendations—from predictions to decisions](https://orie5355.github.io/Fall_2026/static_files/lectures/Lecture6_Recommendations_FromPredictionsToDecisions.pdf#page=5) | 5–11 | Prediction and constrained decision-making are distinct tasks. Transfer that distinction to demand estimation versus pricing; this is not a recommender-system implementation task. |

## Assignment authority

[Living assignment](https://docs.google.com/document/d/1MSqzgD7nfi8dm48dM6qNIZkDNmIZmcag6WWIjUcZ0O4) and [unchanged PDF snapshot](assignment/project-instructions.pdf), retrieved 2026-10-27.

The snapshot is the original [PDF export](https://docs.google.com/document/d/1MSqzgD7nfi8dm48dM6qNIZkDNmIZmcag6WWIjUcZ0O4/export?format=pdf), saved without content modifications: 17 pages, 414,078 bytes, SHA256 `c408262cfc6ec39d86731d2a9d05148b64084f3053b6a71fa227a2ac4e06d232`. The live document can change; page references in these notes refer to this snapshot.

| Snapshot pages | What they establish |
| --- | --- |
| 1, 7, 12 | Coding assistance allowed; LLM use forbidden for every component of the Project Report; team must understand its work and keep incremental commits. |
| 3 | Step 1 input, training and artifact locations, held-out evaluation, and no separately numerical Step 1 assessment. |
| 4–5 | Allowed learning sources; static-price output and capacity-control steps are separate. |
| 7–8, 12–13 | Runtime restrictions, permitted packages, portable paths, required filenames, and simulator integrity. |
| 9–11 | Classroom50 shared team repository and submission process. Do not assume a personal starter/practice repository is the graded destination. |
| 14–15 | Suggested logistic demand estimation, later static-price maximization, and later dynamic programming. These are strategy suggestions rather than mandatory algorithms. |

## Recommendations beyond the slides

Stratified fixed holdouts, Brier score, log loss, calibration plots, fitted preprocessing pipelines, and serialization checks are engineering recommendations for reliable implementation. They are not asserted here as assignment mandates or explicitly taught slide content. A monotonicity diagnostic checks whether predicted demand increases implausibly with price; unconstrained logistic interactions do not guarantee monotonic demand everywhere.
