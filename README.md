# ORIE 5355 Project 2026

[Project instructions](https://docs.google.com/document/d/1MSqzgD7nfi8dm48dM6qNIZkDNmIZmcag6WWIjUcZ0O4)

Use this one repository for all project parts.

## Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run these commands from this folder:

```bash
uv venv --python 3.13
uv pip install --python .venv -r requirements.txt
uv pip install --python .venv ipykernel
uv pip check --python .venv
```

Select `.venv` as the notebook kernel in VS Code. Do not submit `.venv`.

## Shared coding-agent guidance

The repository's coding assistant instructions are in [AGENTS.md](AGENTS.md). This is a shared instruction file for teammates and coding tools, separate from the Python pricing agents used by the simulator. Tools that support `AGENTS.md` should read it from the repository root; otherwise, explicitly provide it as project instructions before asking for code changes.

| File or folder | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Shared coding rules, course policy, permitted data, runtime constraints, collaboration, and migration guidance. |
| [docs/course-knowledge.md](docs/course-knowledge.md) | Concise class-derived notes, original lecture links, PDF page references, and assignment source mapping. |
| [docs/part1-step1-plan.md](docs/part1-step1-plan.md) | Demand-estimation implementation plan; separates requirements, recommendations, acceptance checks, and later steps. |
| [course_materials/INDEX.md](course_materials/INDEX.md) | Human-readable inventory of local PDFs, source links, download coverage, hashes, and limitations. |
| [course_materials/sources.json](course_materials/sources.json) | Machine-readable source and verification metadata. |
| `agents/agent_part1.py`, `agents/agent_part2.py` | Executable pricing agents; preserve required names and interfaces. |
| `model_training/` | Training, preprocessing, and feature-construction code. |
| `agents/helper_files_here/` | Saved models and other required runtime artifacts. |

### Verify original sources

Start with the [living assignment](https://docs.google.com/document/d/1MSqzgD7nfi8dm48dM6qNIZkDNmIZmcag6WWIjUcZ0O4) and [current course lectures](https://orie5355.github.io/Fall_2026/lectures/). Course announcements and updated assignment instructions take precedence over our snapshot and notes. The course reference uses 1-based PDF page numbers; verify a method against the linked original before attributing it to class. Notes and engineering recommendations do not replace the assignment.

The assignment allows AI assistance for coding but prohibits LLM use for every component of the Project Report. All teammates must understand and be able to explain submitted code. These instructions and the Step 1 plan support development work; they are not report content.

### Local PDFs and portable paths

Course PDFs are local resources and are intentionally absent from public Git. The initial inventory contains 10 lecture slide decks, 2 handwritten notes, and 6 linked readings, plus a separately retained project-assignment snapshot. Seven existing readable slide PDFs were reused; their bytes were not refreshed against the live URLs. The source index records retrieval status, size, page count, SHA256, and coverage limits. Guest or future lectures without posted slides, HTML articles, Colab notebooks, and private homework materials are not represented as downloaded PDFs.

After cloning on another computer:

1. Open [the source index](course_materials/INDEX.md) and retrieve the PDFs from its original-source URLs into the listed relative locations under `course_materials/slides/`, `course_materials/notes/`, and `course_materials/readings/`.
2. Download the assignment's [PDF export](https://docs.google.com/document/d/1MSqzgD7nfi8dm48dM6qNIZkDNmIZmcag6WWIjUcZ0O4/export?format=pdf) to `docs/assignment/project-instructions.pdf`. Create the directory if needed. Existing local links to this snapshot work after that step; on GitHub, use the living assignment link above.
3. Check file hashes against `course_materials/sources.json` when reproducing this snapshot. A changed hash may reflect an updated source or export; review it rather than silently treating it as the same version.
4. Keep PDF bytes local. Narrow `.gitignore` rules exclude PDFs in `course_materials/` and `docs/assignment/`; do not force-add them. The indexes and concise derived notes are shared, not full course materials.

Code and documentation use paths relative to the repository. Run notebook setup from this project folder, follow each notebook's path initialization, and keep fitted preprocessing with its model. Runtime agents must not depend on local course PDFs, a personal filesystem path, or internet access.

### Team collaboration and eventual migration

This public working fork supports preparation while the Classroom50 group repository is pending. The starter instruction to use one repository for all parts applies to the eventual shared team submission repository; this fork is not automatically that destination.

Each teammate should follow the existing environment setup above, read `AGENTS.md`, and check the assignment and source index. Inspect Git status before editing, preserve other teammates' changes, make understandable incremental commits, and review the exact files before pushing. Keep personal notes, credentials, local environments, and course PDFs out of public commits. No existing setup document guarantees autograder compatibility or pricing performance.

When the group repository is ready, confirm the assigned repository and team access, compare its starter code and instructions, and transfer reviewed changes without overwriting teammates' work. Preserve relative paths and required agent filenames, reproduce the local PDF layout where useful, and re-run the relevant environment and submission checks there. Verify its visibility and course-material permissions before changing sharing or publishing additional files. Do not rename this fork or change its remote as an automatic migration step.
