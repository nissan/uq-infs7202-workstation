// @ts-check

/**
 * QuizAdminPage class representing the quiz administration pages
 * Used by instructors/admin to create and manage quizzes
 */
class QuizAdminPage {
  /**
   * @param {import('@playwright/test').Page} page 
   */
  constructor(page) {
    this.page = page;
    this.quizTitleInput = page.locator('#id_title');
    this.quizDescriptionInput = page.locator('#id_description');
    this.quizPassingScoreInput = page.locator('#id_passing_score');
    this.quizTimeInput = page.locator('#id_time_limit');
    this.saveButton = page.locator('button[type="submit"]:has-text("Save"), input[type="submit"]');
    this.addQuestionButton = page.locator('button:has-text("Add Question"), a:has-text("Add Question")');
    this.questionTextInput = page.locator('#id_text, #id_question_text');
    this.questionTypeSelect = page.locator('#id_question_type');
    this.questionPointsInput = page.locator('#id_points');
    this.addAnswerButton = page.locator('button:has-text("Add Answer"), a:has-text("Add Answer")');
    this.answerTextInputs = page.locator('.answer-text, input[name*="answer_text"]');
    this.correctAnswerCheckboxes = page.locator('.correct-answer, input[name*="is_correct"]');
    this.backToQuizButton = page.locator('a:has-text("Back to Quiz")');
    this.quizList = page.locator('.quiz-list, table:has(.quiz)');
  }

  /**
   * Navigate to quiz creation page
   * @param {string} courseId 
   */
  async gotoCreateQuiz(courseId) {
    await this.page.goto(`/courses/course/${courseId}/quiz/create/`);
  }

  /**
   * Navigate to quiz edit page
   * @param {string} quizId 
   */
  async gotoEditQuiz(quizId) {
    await this.page.goto(`/courses/quiz/${quizId}/edit/`);
  }

  /**
   * Navigate to quiz list
   * @param {string} courseId 
   */
  async gotoQuizList(courseId) {
    await this.page.goto(`/courses/course/${courseId}/quizzes/`);
  }

  /**
   * Create a new quiz
   * @param {Object} quizData 
   * @param {string} quizData.title
   * @param {string} quizData.description
   * @param {number} quizData.passingScore
   * @param {number} quizData.timeLimit
   */
  async createQuiz(quizData) {
    await this.quizTitleInput.fill(quizData.title);
    await this.quizDescriptionInput.fill(quizData.description);
    await this.quizPassingScoreInput.fill(quizData.passingScore.toString());
    
    if (quizData.timeLimit) {
      await this.quizTimeInput.fill(quizData.timeLimit.toString());
    }
    
    await this.saveButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Add a multiple choice question to a quiz
   * @param {Object} questionData 
   * @param {string} questionData.text
   * @param {number} questionData.points
   * @param {Array<Object>} questionData.answers
   * @param {string} questionData.answers[].text
   * @param {boolean} questionData.answers[].isCorrect
   */
  async addMultipleChoiceQuestion(questionData) {
    // Click add question button
    await this.addQuestionButton.click();
    await this.page.waitForLoadState('networkidle');
    
    // Fill in question details
    await this.questionTextInput.fill(questionData.text);
    
    // Select multiple choice type
    try {
      await this.questionTypeSelect.selectOption('multiple_choice');
    } catch (error) {
      console.log('Question type select not found or not needed');
    }
    
    // Set points
    await this.questionPointsInput.fill(questionData.points.toString());
    
    // Add answers
    for (let i = 0; i < questionData.answers.length; i++) {
      if (i > 0) {
        // Add another answer option if needed
        await this.addAnswerButton.click();
        await this.page.waitForLoadState('domcontentloaded');
      }
      
      // Fill in answer text
      const answerInputs = await this.answerTextInputs.all();
      if (i < answerInputs.length) {
        await answerInputs[i].fill(questionData.answers[i].text);
      } else {
        console.log(`Answer input ${i} not found`);
      }
      
      // Mark as correct if needed
      const correctCheckboxes = await this.correctAnswerCheckboxes.all();
      if (i < correctCheckboxes.length && questionData.answers[i].isCorrect) {
        await correctCheckboxes[i].check();
      }
    }
    
    // Save the question
    await this.saveButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Create a complete test quiz with sample questions
   * @param {string} courseId 
   * @returns {Promise<string>} The ID of the created quiz
   */
  async createTestQuiz(courseId) {
    // Navigate to quiz creation page
    await this.gotoCreateQuiz(courseId);
    
    // Create basic quiz
    const quizData = {
      title: `Test Quiz ${new Date().toISOString().split('T')[0]}`,
      description: 'This is an automated test quiz created with Playwright',
      passingScore: 60,
      timeLimit: 10
    };
    
    await this.createQuiz(quizData);
    
    // Get the quiz ID from the URL
    const url = this.page.url();
    const quizId = url.split('/quiz/')[1]?.split('/')[0];
    
    if (!quizId) {
      throw new Error('Could not determine quiz ID from URL');
    }
    
    // Add a few sample questions
    const questions = [
      {
        text: 'What is the purpose of automated testing?',
        points: 10,
        answers: [
          { text: 'To catch bugs early in the development cycle', isCorrect: true },
          { text: 'To make the application run faster', isCorrect: false },
          { text: 'To replace manual testing completely', isCorrect: false },
          { text: 'To create more work for developers', isCorrect: false }
        ]
      },
      {
        text: 'Which of the following are benefits of Playwright?',
        points: 10,
        answers: [
          { text: 'Cross-browser testing', isCorrect: true },
          { text: 'Auto-waiting capabilities', isCorrect: true },
          { text: 'Network interception', isCorrect: true },
          { text: 'Making coffee automatically', isCorrect: false }
        ]
      },
      {
        text: 'What is the correct way to wait for an element in Playwright?',
        points: 10,
        answers: [
          { text: 'page.waitForSelector(selector)', isCorrect: true },
          { text: 'page.sleep(1000)', isCorrect: false },
          { text: 'page.waitUntil(() => {})', isCorrect: false },
          { text: 'page.waitForPageLoad()', isCorrect: false }
        ]
      }
    ];
    
    for (const question of questions) {
      await this.addMultipleChoiceQuestion(question);
    }
    
    return quizId;
  }

  /**
   * Get all quizzes in a course
   * @param {string} courseId 
   * @returns {Promise<Array<{id: string, title: string}>>}
   */
  async getQuizzes(courseId) {
    await this.gotoQuizList(courseId);
    
    const quizLinks = this.page.locator('a[href*="/quiz/"]');
    const count = await quizLinks.count();
    
    const quizzes = [];
    
    for (let i = 0; i < count; i++) {
      const link = quizLinks.nth(i);
      const href = await link.getAttribute('href');
      const title = await link.innerText();
      
      if (href) {
        const match = href.match(/\/quiz\/(\d+)/);
        if (match && match[1]) {
          quizzes.push({
            id: match[1],
            title: title
          });
        }
      }
    }
    
    return quizzes;
  }
}

module.exports = { QuizAdminPage };