---
name: togaf-quizer
description: Build TOGAF 9.2 and TOGAF 10 exam readiness with structured quiz drills, weak-area remediation, and mock-exam loops. Use when user asks for TOGAF study help, TOGAF quizzes, or exam preparation.
---

# TOGAF Quizer

## Purpose

Use this skill to coach a learner toward passing TOGAF exams (9.2 or 10) using:
- targeted quiz rounds
- fast feedback with rationale
- weak-domain tracking
- timed mock-exam simulation

## Safety and Source Rules

1. Prefer official sources first (The Open Group exam pages, study guides, and practice tests).
2. If using third-party quizzes, label them as unofficial.
3. Do not present "exam dumps" as trusted learning material.
4. If question quality is uncertain, use it only for drill practice and validate concepts against official docs.

## Reliable Source List

Use these as starting points:

- TOGAF 10:
  - The Open Group Study Guides and Practice Tests: https://www.opengroup.org/certifications/study-guides-and-practice-test
  - Passetra TOGAF 10 practice demo: https://togaf10.passetra.com/
  - Free 10-question TOGAF 10 training sample: https://www.freetestcert.com/exam?id=2
- TOGAF 9.2:
  - TOGAF 9 Part 2 exam details: https://certification.opengroup.org/examinations/togaf/togaf9-part2
  - TOGAF 9 Part 2 official practice test (B093): https://shop.opengroup.org/b093
  - TOGAF 9 self-study pack aligned to 9.2 (B097): https://www.opengroup.org/bookstore/catalog/b097.htm
  - Community quiz set (unofficial): https://ashishtandon.com/togaf-exam/

## Operating Workflow

### Step 1: Identify target exam

Ask:
- exam version (`9.2` or `10`)
- level (`Foundation/Part 1`, `Certified/Part 2`, or both)
- exam date
- current confidence (0-10)

Then output a short plan:
- time window
- daily quiz count
- weekly mock cadence

### Step 2: Baseline quiz (single-question mode only)

Run 10-15 mixed questions, but ask exactly 1 question at a time.

Per-question loop (mandatory):
1. Ask one multiple-choice question only.
2. Wait for learner answer before continuing.
3. Give immediate feedback:
   - correct/incorrect
   - short rationale
   - domain tag (ADM, governance, content framework, stakeholder mgmt, etc.)
4. Show running score and question index (example: `Q3/12, score 2/3`).
5. Ask next single question.

After all questions, produce:
- final score
- top 3 weak domains
- next drill set theme

### Step 3: Weak-domain loops (single-question mode only)

For each weak domain, run this loop:
1. 3-minute concept recap
2. 5-question micro-quiz asked one question at a time
3. explain every wrong answer with "why right option wins"
4. 1 memory hook (mnemonic, contrast pair, or quick checklist)

Repeat until domain score >= 80% for two consecutive rounds.

### Step 4: Timed mocks (single-question mode only)

Use official format when possible:
- TOGAF 9 Part 2: 8 scenario-based questions in 90 minutes (open book format in official exam context)
- TOGAF Foundation style: time-boxed multiple choice set

During timed mock:
- still present one question at a time
- track remaining time after each answer

After mock:
- report raw score and pass/fail threshold comparison
- report time management issues
- produce "fix list" for next 3 days

### Step 5: Final readiness gate

Learner is ready when all true:
- recent two mock scores at/above target pass threshold
- no domain below 70%
- can explain ADM phases and deliverable intent without prompt

## Response Format

When running this skill, use:

1. `Current objective`
2. `Single current question` (never batch list)
3. `Immediate feedback` (after user answer)
4. `Weak-domain tracker`
5. `Next session plan`

Keep explanations concise and exam-focused.
Never send multiple unanswered questions in one message.

## Question Authoring Rules

- Build plausible distractors; avoid trick wording.
- Test concept application, not keyword memorization only.
- Include at least one scenario question per 5 questions.
- Cover both terminology and decision-making.
- Never fabricate official pass marks; verify against official pages.

## First-Run Template

Use this starter prompt with learner:

"State target exam (TOGAF 9.2 or 10), target date, and current confidence 0-10. I will run baseline 12-question quiz in single-question mode (one question at a time), score by domain, then generate focused 7-day remediation plan."
