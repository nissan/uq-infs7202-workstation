# Quiz Creation and Management Guide

This guide provides step-by-step instructions for instructors on how to create, configure, and manage quizzes in the LearnMore LMS.

## Getting Started

To manage quizzes, you must have instructor privileges in the system. Quizzes are always associated with a specific module within a course.

## Creating a Quiz

### Step 1: Navigate to the Module Page

First, navigate to the course page and select the module where you want to add the quiz.

### Step 2: Create a New Quiz

1. Click the "Add Quiz" button in the module management area.
2. Fill in the basic information:
   - **Title**: A descriptive name for the quiz
   - **Description**: A brief overview of the quiz content
   - **Instructions**: Detailed instructions for students taking the quiz

### Step 3: Configure Quiz Settings

Configure the following settings for your quiz:

1. **Time Limit**: Set an optional time limit in minutes (leave empty for unlimited time)
2. **Passing Score**: Set the percentage required to pass (default: 70%)
3. **Attempt Settings**:
   - **Allow Multiple Attempts**: Enable or disable multiple attempts
   - **Maximum Attempts**: Set the maximum number of attempts (0 for unlimited)
4. **Randomization**: Choose whether to randomize question order
5. **Quiz Type**: 
   - **Standard Quiz**: Counts toward grades and progress
   - **Survey**: For gathering opinions or feedback (not graded)

### Step 4: Save the Quiz

Click "Save" to create the quiz. At this point, the quiz is saved but not yet published.

## Adding Questions

### Step 1: Navigate to the Quiz Editor

From the quiz details page, click "Edit Questions" to open the question editor.

### Step 2: Add a Multiple Choice Question

1. Click "Add Question" and select "Multiple Choice"
2. Fill in the question text
3. Set the points value for this question
4. Choose whether multiple answers are allowed
5. Add answer choices:
   - Enter the text for each choice
   - Mark the correct choice(s)
   - Set the order if desired
6. Optionally add:
   - **Explanation**: Detailed explanation of the answer
   - **Feedback**: Specific feedback for correct and incorrect answers
7. Click "Save Question"

### Step 3: Add a True/False Question

1. Click "Add Question" and select "True/False"
2. Fill in the question text
3. Set the points value for this question
4. Select the correct answer (True or False)
5. Optionally add:
   - **Explanation**: Detailed explanation of the answer
   - **Feedback**: Specific feedback for correct and incorrect answers
6. Click "Save Question"

### Step 4: Arrange Questions

1. On the questions list page, you can:
   - Drag and drop questions to change their order
   - Edit existing questions
   - Delete questions

## Managing Quizzes

### Publishing a Quiz

1. From the quiz details page, toggle the "Published" switch to ON
2. Only published quizzes are visible to students

### Editing a Quiz

1. Navigate to the quiz details page
2. Click "Edit Quiz" to modify basic information and settings
3. Click "Edit Questions" to modify questions

### Viewing Quiz Results

1. Navigate to the quiz details page
2. Click "View Results" to see:
   - Overview statistics (average score, completion rate, etc.)
   - Individual student attempts
   - Question-level analytics (which questions were most commonly missed)

### Deleting a Quiz

1. Navigate to the quiz details page
2. Click "Delete Quiz"
3. Confirm deletion
4. Note: Deleting a quiz will remove all student attempt data

## Best Practices

### Quiz Design

1. **Clear Instructions**: Provide clear instructions about the quiz purpose and how to complete it
2. **Appropriate Difficulty**: Ensure questions align with the material taught
3. **Question Variety**: Use a mix of question types
4. **Balanced Scoring**: Assign points based on question difficulty and importance
5. **Helpful Feedback**: Provide constructive feedback for both correct and incorrect answers

### Question Writing

1. **Clarity**: Write clear, unambiguous questions
2. **Focused Questions**: Each question should test one concept
3. **Plausible Distractors**: For multiple choice, all options should be plausible
4. **Avoid Negative Questions**: Avoid using "not" or "except" in questions
5. **Use Images When Helpful**: Include diagrams or images when they clarify the question

### Quiz Administration

1. **Test Your Quiz**: Always preview the quiz before publishing
2. **Set Appropriate Time Limits**: Ensure time limits allow for thoughtful responses
3. **Consider Attempt Limits**: Set attempt limits based on the quiz purpose
4. **Use Randomization**: Enable question randomization for high-stakes assessments
5. **Monitor Results**: Review analytics to identify areas where students struggle

## Troubleshooting

### Common Issues

1. **Quiz Not Visible to Students**:
   - Check that the quiz is published
   - Verify course enrollment for the students
   - Check any release date/time settings

2. **Scoring Issues**:
   - Verify correct answers are properly marked
   - Check that point values are assigned correctly
   - Review any custom scoring rules

3. **Time Limit Problems**:
   - Ensure time limits are reasonable for the number of questions
   - Check if students reported any technical issues during the quiz

### Getting Help

For additional assistance with quiz management:
1. Review the API documentation for programmatic quiz management
2. Contact technical support for system-related issues