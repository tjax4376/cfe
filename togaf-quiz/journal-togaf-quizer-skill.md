# Journal: TOGAF Quizer Skill

## Context Description

User requested online search for TOGAF 9.2 or TOGAF 10 quizzes, then creation of a `SKILL.md` file for a `togaf-quizer` skill that helps user build knowledge for passing TOGAF exam.

## Discussion Points

- Collected current TOGAF 10 quiz/practice sources, with official and unofficial options.
- Collected TOGAF 9.2 practice sources, including official exam/practice references.
- Applied source-quality rule: official-first, unofficial clearly labeled, avoid treating dumps as trusted prep.
- Designed skill workflow around baseline quiz, weak-domain loops, timed mocks, and readiness gate.

## Summary of Code Changed

- Added project skill file: `.cursor/skills/togaf-quizer/SKILL.md`
  - Defines `togaf-quizer` metadata and trigger description.
  - Adds verified source list for TOGAF 9.2 and TOGAF 10 prep.
  - Adds stepwise coaching workflow and response format.
- Added journal file: `journal-togaf-quizer-skill.md`.
- Added alias skill file for explicit command naming: `.cursor/skills/togaf-quizer-skill/SKILL.md`
  - Uses requested skill name `togaf-quizer-skill`.
  - Keeps same exam-prep workflow and source guardrails.
- Updated quiz interaction model in both skill files:
  - `.cursor/skills/togaf-quizer/SKILL.md`
  - `.cursor/skills/togaf-quizer-skill/SKILL.md`
  - Enforced strict single-question mode: one question asked, wait for answer, immediate feedback, running score, then next question.
  - Added explicit rule to never send multiple unanswered questions in one message.
