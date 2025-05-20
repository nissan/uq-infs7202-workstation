# Question Types and Scoring Rules

This document explains the different question types available in the LearnMore quiz system and how they are scored.

## Question Types Overview

The LearnMore quiz system currently supports the following question types:

1. Multiple Choice (Single Answer)
2. Multiple Choice (Multiple Answers)
3. True/False

Each question type has specific configuration options and scoring rules.

## Multiple Choice Questions

### Single Answer Multiple Choice

In this question type, students must select exactly one answer from a list of options.

#### Configuration

- **Question Text**: The main question prompt
- **Points**: Number of points awarded for a correct answer
- **Choices**: A list of possible answers
  - **Text**: The answer text
  - **Correct**: One choice must be marked as correct
  - **Order**: Optional ordering of choices (if not randomized)
- **Allow Multiple**: Must be set to `false`
- **Feedback**: Optional feedback for correct and incorrect answers
- **Explanation**: Optional explanation of the correct answer

#### Scoring Rules

- If the student selects the correct answer, they receive full points
- If the student selects an incorrect answer, they receive zero points
- If the student selects multiple answers, the response is considered incorrect

#### Example

```
Question: What is the capital of France?
Points: 1
Choices:
  - London (incorrect)
  - Paris (correct)
  - Berlin (incorrect)
  - Madrid (incorrect)
```

If the student selects "Paris", they receive 1 point. Any other selection receives 0 points.

### Multiple Answer Multiple Choice

In this question type, students can select one or more answers from a list of options.

#### Configuration

- **Question Text**: The main question prompt
- **Points**: Number of points awarded for a completely correct answer
- **Choices**: A list of possible answers
  - **Text**: The answer text
  - **Correct**: One or more choices can be marked as correct
  - **Order**: Optional ordering of choices (if not randomized)
- **Allow Multiple**: Must be set to `true`
- **Feedback**: Optional feedback for correct and incorrect answers
- **Explanation**: Optional explanation of the correct answer

#### Scoring Rules

- If the student selects all correct choices and no incorrect choices, they receive full points
- If the student selects any incorrect choice or fails to select any correct choice, they receive zero points
- Partial credit is not awarded (it's all or nothing)

#### Example

```
Question: Which of the following are prime numbers?
Points: 2
Choices:
  - 2 (correct)
  - 4 (incorrect)
  - 7 (correct)
  - 9 (incorrect)
  - 11 (correct)
```

If the student selects "2", "7", and "11" (all correct choices and no incorrect ones), they receive 2 points. If they select any other combination, they receive 0 points.

## True/False Questions

In this question type, students must indicate whether a statement is true or false.

### Configuration

- **Question Text**: The statement to evaluate
- **Points**: Number of points awarded for a correct answer
- **Correct Answer**: Either `true` or `false`
- **Feedback**: Optional feedback for correct and incorrect answers
- **Explanation**: Optional explanation of the correct answer

### Scoring Rules

- If the student selects the correct answer (true or false), they receive full points
- If the student selects the incorrect answer, they receive zero points

### Example

```
Question: The Earth orbits around the Sun.
Points: 1
Correct Answer: True
```

If the student selects "True", they receive 1 point. If they select "False", they receive 0 points.

## Input Handling and Validation

### Multiple Choice Input

- **Single answer**: Stored as `selected_choice` with a single choice ID
- **Multiple answers**: Stored as `selected_choices` with an array of choice IDs

### True/False Input

The system accepts multiple formats for true/false input:
- Boolean values: `true`, `false`
- Strings: `"true"`, `"True"`, `"false"`, `"False"`
- Numbers: `1` (true), `0` (false)
- String numbers: `"1"` (true), `"0"` (false)

## Quiz Scoring

### Overall Score Calculation

1. Each question response is evaluated and assigned points
2. The total score is the sum of points earned from all responses
3. The maximum possible score is the sum of all question point values
4. The percentage score is calculated as: (total score / maximum possible score) * 100%

### Pass/Fail Determination

1. Each quiz has a passing score percentage (default: 70%)
2. A student passes the quiz if their percentage score equals or exceeds the passing percentage
3. For example, if a quiz has a passing score of 70%:
   - A student scoring 70% or higher passes
   - A student scoring below 70% fails

### Special Cases

1. **Unanswered Questions**: 
   - Receive zero points
   - Counted in the maximum possible score

2. **Timed Out Quizzes**:
   - Only answered questions are scored
   - Unanswered questions receive zero points

3. **Surveys**:
   - Even though answers are scored, surveys don't count toward module completion
   - There is no "passing" concept for surveys

## Future Question Types

The quiz system is designed to be extensible. Future versions may include additional question types such as:

1. Short Answer
2. Essay
3. Matching
4. Fill in the Blank
5. Numerical

Each new question type will implement the abstract `check_answer()` method with appropriate scoring rules.