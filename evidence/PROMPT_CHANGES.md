# Prompt Changes

## Baseline Behavior Preserved

The tutoring prompt was adjusted to improve reliability and JSON formatting while preserving the required tutoring flow.

## Changes Made

1. Added explicit JSON-only response instruction.
2. Added objective indexes using 0-based numbering.
3. Added instruction to ask exactly one guiding question at a time.
4. Added instruction to return `achieved_objective_index` only when the student's latest response clearly satisfies an objective.
5. Added short academic mini-lesson field after objective achievement.
6. Added already achieved objective indexes and current score into the system prompt to reduce duplicate scoring.

## Rationale

These changes were made to make the AI response easier to parse and to support objective-based scoring accurately.

## Expected Effect

- More consistent JSON responses.
- Fewer duplicate scores.
- Better alignment with activity terminology.
- More reliable one-question-at-a-time tutoring flow.