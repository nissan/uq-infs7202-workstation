# Migration Plan for LearnMore Reborn

This document outlines the phased migration plan for moving features from the legacy `learnmore_plus` app into this new `learnmore-reborn` scaffold.

## 1. Audit & Alignment

- **Original Feature Inventory**: See `learnmore_plus/docs/CHECKPOINT.md` for the current feature set
planned for migration:
    - Course management system with CRUD operations
    - Course catalog with search and filtering
    - Course enrollment system
    - Learning interface with progress tracking
    - Quiz system with multiple question types and auto-grading
    - Consolidated student dashboard with progress tracking
    - Enhanced quiz system with pre-requisite surveys
    - Dual admin interfaces (System Admin Dashboard and Django Admin)
    - QR code generation system for courses and modules
    - AI Tutor system with LLM integration and RAG

## 2. Migration Phases
| Phase | Feature Area | Components Migrated |
|:-----:|:-------------|:-------------------|
| 1 | Core data & CRUD | Course & Progress models, admin, serializers, views, URLs, tests, docs |
| 2 | User auth & profiles | Custom User model, auth flows, profile views/edit, serializers, tests |
| 3 | Course catalog & enrollment | Course list/filter, enroll/un-enroll, UI pages, serializers, views, tests |
| 4 | Learning interface & progress tracking | Continue learning page, progress logic, templates, API, tests |
| 5 | Quiz system – basics | MCQ/T-F quizzes, auto-grading logic, forms/serializers/views, tests |
| 6 | Quiz system – advanced | Essay questions, time limits, pre-req surveys, detailed feedback, tests |
| 7 | Admin dashboards & analytics | System-admin & instructor dashboards, analytics views, tests |
| 8 | AI Tutor integration | LLM/RAG backend, tutor chat UI, conversation history, serializers/views, tests |
| 9 | QR code support | QR generation/scanning endpoints, admin UI, mobile-friendly templates, tests |
| 10 | UI/UX theming & accessibility | Design system integration, responsive templates, accessibility audit, tests |
| 11 | E2E, performance & docs polish | Playwright/e2e suites, performance benchmarks, update docs (README, HOWTOs) |
| 12 | Final cut-over & deployment | Data migrations, CI/CD settings, production rollout, stakeholder sign-off |

## 3. Phase Workflow Template

For each phase, follow a consistent slice-based approach:

1. Identify and migrate models → serializers/forms → views → URLs → templates → tests.
2. Update documentation (`README.md` or create `<PHASE>_CHECKLIST.md`).
3. Run and pass all relevant tests.
4. Commit to a feature branch named `phase-<N>-<feature-slug>`.
5. Open a pull request for stakeholder review and merge on approval.

## 4. Tracking & Tools

- **Issue board**: Create one ticket per phase (e.g. Phase 3: Course catalog & enrollment).
- **Branches**: `phase-1-core-crud`, `phase-2-auth`, etc.
- **CI**: Ensure tests pass before each merge.
- **Legacy cleanup**: Delete or archive migrated code in `learnmore_plus` as each phase completes.

## 5. Tips for a smooth migration

- Migrate one vertical slice at a time to keep the codebase runnable.
- Use common fixtures and seed data from `learnmore_plus/docs` when porting tests.
- Demo completed phases regularly to maintain stakeholder confidence.
- Keep the migration log up-to-date to avoid drift.