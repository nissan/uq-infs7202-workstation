#!/usr/bin/env python
"""
Script to create rich demo content for courses with detailed materials for RAG integration.
This script creates comprehensive course content including markdown lectures, code examples,
and diverse quiz types that can be used to demonstrate the platform's capabilities.

Usage:
    python manage.py shell < create_demo_rag_content.py
"""

import os
import django
import random
from datetime import timedelta
from django.db import transaction
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learnmore.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import UserProfile
from courses.models import (
    Course, Module, Quiz, Question, MultipleChoiceQuestion, 
    TrueFalseQuestion, EssayQuestion, Choice, Enrollment
)

User = get_user_model()

# Rich course content examples
PYTHON_INTRO_CONTENT = """
# Introduction to Python Programming

Python is a high-level, interpreted programming language known for its readability and versatility. Created by Guido van Rossum and first released in 1991, Python has become one of the most popular programming languages in the world.

## Key Features of Python

- **Easy to Learn and Use**: Python's syntax is designed to be readable and straightforward.
- **Versatile**: Python can be used for web development, data analysis, artificial intelligence, scientific computing, and more.
- **Large Standard Library**: Python comes with a comprehensive standard library that supports many common programming tasks.
- **Extensive Third-Party Packages**: Python has a vast ecosystem of third-party packages for various specialized tasks.
- **Cross-Platform**: Python runs on various operating systems including Windows, macOS, and Linux.

## Python Syntax Basics

Here's a simple Python program:

```python
# This is a comment
print("Hello, World!")  # This prints a greeting

# Variables and basic data types
name = "Alice"  # String
age = 30        # Integer
height = 5.7    # Float
is_student = True  # Boolean

# Simple conditional statement
if age >= 18:
    print(f"{name} is an adult.")
else:
    print(f"{name} is a minor.")

# Basic loop
for i in range(5):
    print(f"Count: {i}")
```

## Variables and Data Types

Python has several built-in data types:

1. **Numeric Types**:
   - `int`: Integer numbers (e.g., `42`, `-7`)
   - `float`: Floating-point numbers (e.g., `3.14`, `-2.5`)
   - `complex`: Complex numbers (e.g., `3+4j`)

2. **Sequence Types**:
   - `str`: String of characters (e.g., `"Hello"`)
   - `list`: Ordered, mutable sequence (e.g., `[1, 2, 3]`)
   - `tuple`: Ordered, immutable sequence (e.g., `(1, 2, 3)`)

3. **Mapping Type**:
   - `dict`: Key-value pairs (e.g., `{"name": "Alice", "age": 30}`)

4. **Set Types**:
   - `set`: Unordered collection of unique elements (e.g., `{1, 2, 3}`)
   - `frozenset`: Immutable version of a set

5. **Boolean Type**:
   - `bool`: Either `True` or `False`

6. **None Type**:
   - `None`: Represents the absence of a value

## Next Steps

In the following modules, we'll explore these concepts in more depth and introduce additional Python features.
"""

WEB_DEV_CONTENT = """
# Introduction to Web Development

Web development encompasses the creation and maintenance of websites and web applications. It involves various technologies, skills, and disciplines focused on creating engaging, functional, and user-friendly web experiences.

## Front-End Development

Front-end development focuses on what users see and interact with in a web browser.

### Key Front-End Technologies:

1. **HTML (HyperText Markup Language)**
   - The standard markup language for documents designed to be displayed in a web browser
   - Defines the structure and content of web pages

   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>My First Web Page</title>
   </head>
   <body>
       <h1>Hello, World!</h1>
       <p>This is a paragraph of text.</p>
   </body>
   </html>
   ```

2. **CSS (Cascading Style Sheets)**
   - Used to style and layout web pages
   - Controls colors, fonts, spacing, and more

   ```css
   body {
       font-family: Arial, sans-serif;
       background-color: #f0f0f0;
       margin: 0;
       padding: 20px;
   }
   
   h1 {
       color: #333;
       text-align: center;
   }
   
   p {
       line-height: 1.6;
       color: #666;
   }
   ```

3. **JavaScript**
   - Programming language that allows for interactive web pages
   - Enables dynamic content and user interactions

   ```javascript
   // Simple JavaScript example
   document.addEventListener('DOMContentLoaded', function() {
       const button = document.querySelector('#myButton');
       
       button.addEventListener('click', function() {
           alert('Button was clicked!');
       });
   });
   ```

## Back-End Development

Back-end development focuses on server-side logic, databases, and application integration.

### Key Back-End Technologies:

1. **Server-Side Languages**:
   - Python (Django, Flask)
   - JavaScript (Node.js, Express)
   - PHP
   - Ruby (Ruby on Rails)
   - Java
   - C# (.NET)

2. **Databases**:
   - Relational: MySQL, PostgreSQL, SQLite
   - NoSQL: MongoDB, Firebase, Cassandra

3. **APIs (Application Programming Interfaces)**:
   - RESTful APIs
   - GraphQL
   - Web Services

## Full-Stack Development

Full-stack development combines both front-end and back-end skills. A full-stack developer understands all aspects of web development and can work on both client and server sides.

## Web Development Workflow

1. **Planning**: Define goals, audience, content, and features
2. **Design**: Create wireframes and mockups
3. **Development**: Write code for both front-end and back-end
4. **Testing**: Ensure functionality and responsiveness
5. **Deployment**: Publish the website to a server
6. **Maintenance**: Update content, fix bugs, and implement new features

## Modern Web Development Trends

- **Responsive Design**: Websites that work well on all devices
- **Progressive Web Apps (PWAs)**: Web applications that offer a native app-like experience
- **Single Page Applications (SPAs)**: Web apps that load a single HTML page and dynamically update content
- **JAMstack**: JavaScript, APIs, and Markup architecture
- **Serverless Architecture**: Cloud-based services that eliminate server management
- **AI and Machine Learning Integration**: Smart features and personalization

## Next Steps

In the following modules, we'll dive deeper into each aspect of web development and build practical projects to apply these concepts.
"""

DATA_SCIENCE_CONTENT = """
# Introduction to Data Science

Data Science is an interdisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge and insights from structured and unstructured data. It combines expertise from statistics, mathematics, computer science, and domain knowledge.

## The Data Science Process

1. **Ask Questions**: Define the problem to solve or questions to answer with data
2. **Get Data**: Collect data from various sources
3. **Clean Data**: Preprocess and prepare data for analysis
4. **Explore Data**: Perform exploratory data analysis (EDA)
5. **Model Data**: Apply statistical models and machine learning algorithms
6. **Interpret Results**: Extract insights and draw conclusions
7. **Communicate Findings**: Present results through visualizations and reports

## Essential Python Libraries for Data Science

### Data Manipulation and Analysis

1. **NumPy**: Fundamental package for scientific computing
   
   ```python
   import numpy as np
   
   # Create a numpy array
   arr = np.array([1, 2, 3, 4, 5])
   
   # Basic operations
   print(arr.mean())  # Mean
   print(arr.std())   # Standard deviation
   print(arr * 2)     # Element-wise multiplication
   ```

2. **Pandas**: Data analysis and manipulation tool
   
   ```python
   import pandas as pd
   
   # Create a DataFrame
   data = {
       'Name': ['Alice', 'Bob', 'Charlie'],
       'Age': [25, 30, 35],
       'City': ['New York', 'San Francisco', 'Chicago']
   }
   
   df = pd.DataFrame(data)
   print(df.head())
   
   # Basic analysis
   print(df['Age'].mean())
   print(df.describe())
   ```

### Data Visualization

1. **Matplotlib**: Comprehensive library for creating static visualizations
   
   ```python
   import matplotlib.pyplot as plt
   
   # Create a simple line plot
   x = [1, 2, 3, 4, 5]
   y = [10, 20, 25, 30, 45]
   
   plt.figure(figsize=(8, 5))
   plt.plot(x, y, marker='o')
   plt.title('Sample Line Plot')
   plt.xlabel('X-axis')
   plt.ylabel('Y-axis')
   plt.grid(True)
   plt.show()
   ```

2. **Seaborn**: Statistical data visualization based on matplotlib
   
   ```python
   import seaborn as sns
   
   # Create a dataset
   tips = sns.load_dataset('tips')
   
   # Create a visualization
   plt.figure(figsize=(10, 6))
   sns.scatterplot(x='total_bill', y='tip', hue='sex', data=tips)
   plt.title('Tips vs. Total Bill by Gender')
   plt.show()
   ```

### Machine Learning

1. **Scikit-learn**: Simple and efficient tools for data analysis and modeling
   
   ```python
   from sklearn.model_selection import train_test_split
   from sklearn.linear_model import LinearRegression
   from sklearn.metrics import mean_squared_error
   import numpy as np
   
   # Generate sample data
   X = np.random.rand(100, 1) * 10
   y = 2 * X + 1 + np.random.randn(100, 1)
   
   # Split data
   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
   
   # Train model
   model = LinearRegression()
   model.fit(X_train, y_train)
   
   # Make predictions
   y_pred = model.predict(X_test)
   
   # Evaluate model
   mse = mean_squared_error(y_test, y_pred)
   print(f'Slope: {model.coef_[0][0]:.2f}')
   print(f'Intercept: {model.intercept_[0]:.2f}')
   print(f'Mean Squared Error: {mse:.2f}')
   ```

## Types of Data Science Problems

1. **Classification**: Predicting categories (e.g., spam detection, disease diagnosis)
2. **Regression**: Predicting continuous values (e.g., housing prices, temperature)
3. **Clustering**: Grouping similar items (e.g., customer segmentation)
4. **Anomaly Detection**: Identifying unusual patterns (e.g., fraud detection)
5. **Recommendation Systems**: Suggesting items to users (e.g., product recommendations)
6. **Natural Language Processing**: Analyzing text data (e.g., sentiment analysis)
7. **Computer Vision**: Analyzing image and video data (e.g., object recognition)

## Data Science in Industry

Data Science is applied across numerous industries:

- **Healthcare**: Disease prediction, medical image analysis, drug discovery
- **Finance**: Risk assessment, fraud detection, algorithmic trading
- **Retail**: Customer analytics, inventory management, price optimization
- **Technology**: Recommendation systems, search algorithms, user behavior analysis
- **Transportation**: Route optimization, demand prediction, autonomous vehicles
- **Marketing**: Customer segmentation, campaign optimization, sentiment analysis
- **Manufacturing**: Predictive maintenance, quality control, supply chain optimization

## Next Steps

In the following modules, we'll explore each component of the data science process in depth and work on practical projects to apply these concepts.
"""

MACHINE_LEARNING_CONTENT = """
# Introduction to Machine Learning

Machine Learning (ML) is a subset of artificial intelligence that focuses on building systems that learn from data. Instead of explicitly programming rules, ML algorithms identify patterns in data and make predictions or decisions based on these patterns.

## Types of Machine Learning

### 1. Supervised Learning

In supervised learning, algorithms learn from labeled training data and make predictions on new, unseen data.

**Key Algorithms**:
- Linear Regression
- Logistic Regression
- Decision Trees
- Random Forests
- Support Vector Machines (SVM)
- Neural Networks

**Example (Python using scikit-learn)**:
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Assume X (features) and y (labels) are already defined
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Create and train the model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
```

### 2. Unsupervised Learning

Unsupervised learning algorithms find patterns in unlabeled data.

**Key Algorithms**:
- K-means Clustering
- Hierarchical Clustering
- Principal Component Analysis (PCA)
- Autoencoders
- Generative Adversarial Networks (GANs)

**Example (Python using scikit-learn)**:
```python
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Assume X (features) is already defined
kmeans = KMeans(n_clusters=3)
clusters = kmeans.fit_predict(X)

# Visualize clusters (assuming X has 2 dimensions)
plt.figure(figsize=(10, 6))
plt.scatter(X[:, 0], X[:, 1], c=clusters)
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], 
            marker='x', color='red', s=100)
plt.title('K-means Clustering')
plt.show()
```

### 3. Reinforcement Learning

Reinforcement learning involves an agent that learns to make decisions by taking actions in an environment to maximize rewards.

**Key Concepts**:
- Agent
- Environment
- State
- Action
- Reward

**Key Algorithms**:
- Q-Learning
- Deep Q Networks (DQN)
- Policy Gradient Methods
- Proximal Policy Optimization (PPO)

## The Machine Learning Workflow

1. **Problem Definition**: Define the problem and determine the appropriate ML approach
2. **Data Collection**: Gather relevant data from various sources
3. **Data Preprocessing**:
   - Handle missing values
   - Encode categorical variables
   - Scale numerical features
   - Split data into training and testing sets
4. **Model Selection**: Choose an appropriate algorithm based on the problem
5. **Model Training**: Train the model on the training data
6. **Model Evaluation**: Assess model performance using evaluation metrics
7. **Model Tuning**: Optimize hyperparameters to improve performance
8. **Deployment**: Implement the model in a production environment
9. **Monitoring**: Continuously monitor model performance in production

## Evaluation Metrics

### Classification Metrics
- Accuracy
- Precision
- Recall
- F1 Score
- ROC Curve and AUC
- Confusion Matrix

### Regression Metrics
- Mean Absolute Error (MAE)
- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)
- R-squared

## Challenges in Machine Learning

- **Overfitting**: Model performs well on training data but poorly on new data
- **Underfitting**: Model fails to capture the underlying pattern in the data
- **Data Quality**: Missing values, outliers, and noisy data
- **Feature Selection**: Identifying the most relevant features
- **Imbalanced Data**: Classes with significantly different numbers of samples
- **Interpretability**: Understanding and explaining model decisions
- **Ethical Considerations**: Bias, fairness, and privacy concerns

## Applications of Machine Learning

- **Healthcare**: Disease diagnosis, treatment recommendation, medical image analysis
- **Finance**: Fraud detection, credit scoring, algorithmic trading
- **Retail**: Product recommendations, customer segmentation, demand forecasting
- **Transportation**: Autonomous vehicles, route optimization, traffic prediction
- **Manufacturing**: Predictive maintenance, quality control, process optimization
- **Natural Language Processing**: Language translation, sentiment analysis, chatbots
- **Computer Vision**: Object detection, facial recognition, image classification

## Next Steps

In the following modules, we'll explore these concepts in detail and implement various machine learning algorithms in practical projects.
"""

# Course data with rich content
COURSES = [
    {
        "title": "Python Programming for Beginners",
        "description": "A comprehensive introduction to Python programming language, covering syntax, data types, control structures, functions, and more.",
        "content": PYTHON_INTRO_CONTENT,
        "modules": [
            {
                "title": "Python Fundamentals",
                "description": "Introduction to Python syntax, data types, and basic operations.",
                "content": """
# Python Fundamentals

## Variables and Data Types

In Python, you can assign values to variables using the `=` operator. Variable names can contain letters, numbers, and underscores, but cannot start with a number.

```python
# Assigning values to variables
x = 10
name = "Alice"
is_student = True
```

Python has several built-in data types:

- **Integers**: Whole numbers, positive or negative (e.g., `42`, `-7`)
- **Floats**: Decimal numbers (e.g., `3.14`, `-2.5`)
- **Strings**: Text enclosed in quotes (e.g., `"Hello"`, `'World'`)
- **Booleans**: Truth values (`True` or `False`)
- **Lists**: Ordered, mutable collections of items (e.g., `[1, 2, 3]`)
- **Tuples**: Ordered, immutable collections of items (e.g., `(1, 2, 3)`)
- **Dictionaries**: Key-value pairs (e.g., `{"name": "Alice", "age": 25}`)
- **Sets**: Unordered collections of unique items (e.g., `{1, 2, 3}`)

## Basic Operations

Python supports various arithmetic operations:

```python
# Addition
result = 5 + 3  # result = 8

# Subtraction
result = 10 - 4  # result = 6

# Multiplication
result = 6 * 3  # result = 18

# Division
result = 15 / 5  # result = 3.0 (always returns a float)

# Integer Division
result = 17 // 5  # result = 3 (returns the quotient without remainder)

# Modulo (Remainder)
result = 17 % 5  # result = 2

# Exponentiation
result = 2 ** 3  # result = 8 (2 raised to the power of 3)
```

String operations are also common:

```python
# String concatenation
greeting = "Hello" + " " + "World"  # "Hello World"

# String repetition
repeated = "Python " * 3  # "Python Python Python "

# String indexing (accessing individual characters)
first_char = "Python"[0]  # "P"

# String slicing (extracting substrings)
substring = "Python"[1:4]  # "yth"
```
""",
                "quizzes": [
                    {
                        "title": "Python Basics Quiz",
                        "description": "Test your understanding of Python fundamentals.",
                        "time_limit_minutes": 15,
                        "passing_score": 70,
                        "questions": [
                            {
                                "type": "multiple_choice",
                                "text": "Which of the following is a valid Python variable name?",
                                "explanation": "Variable names can contain letters, numbers, and underscores, but cannot start with a number.",
                                "points": 10,
                                "choices": [
                                    {"text": "1variable", "is_correct": False, "feedback": "Variable names cannot start with a number."},
                                    {"text": "_variable", "is_correct": True, "feedback": "Correct! Variable names can start with an underscore."},
                                    {"text": "variable-1", "is_correct": False, "feedback": "Hyphens are not allowed in variable names."},
                                    {"text": "variable@1", "is_correct": False, "feedback": "Special characters like @ are not allowed in variable names."}
                                ]
                            },
                            {
                                "type": "multiple_choice",
                                "text": "What is the output of the following code: `print(10 / 3)`?",
                                "explanation": "The / operator in Python performs floating-point division.",
                                "points": 10,
                                "choices": [
                                    {"text": "3", "is_correct": False, "feedback": "The / operator returns a float, not an integer."},
                                    {"text": "3.0", "is_correct": False, "feedback": "Close, but the actual result has more decimal places."},
                                    {"text": "3.33", "is_correct": False, "feedback": "Close, but the actual result has more decimal places."},
                                    {"text": "3.3333333333333335", "is_correct": True, "feedback": "Correct! The / operator returns a float with this value."}
                                ]
                            },
                            {
                                "type": "true_false",
                                "text": "In Python, strings can be enclosed in either single quotes (') or double quotes (\").",
                                "explanation": "Python allows strings to be defined using either single or double quotes.",
                                "points": 5,
                                "is_correct": True
                            },
                            {
                                "type": "true_false",
                                "text": "The expression `5 + '5'` is valid in Python.",
                                "explanation": "Python doesn't support automatic type conversion between numbers and strings.",
                                "points": 5,
                                "is_correct": False
                            },
                            {
                                "type": "essay",
                                "text": "Explain the difference between lists and tuples in Python, and provide an example of when you would use each.",
                                "explanation": "This question tests understanding of mutable vs. immutable collections and their appropriate use cases.",
                                "points": 20,
                                "answer_guidelines": "A good answer should mention that lists are mutable (can be changed) while tuples are immutable (cannot be changed after creation). Examples should include using lists for collections that need to be modified and tuples for data that shouldn't change, like coordinates or RGB values."
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Control Flow",
                "description": "Learn about conditional statements, loops, and control structures in Python.",
                "content": """
# Control Flow in Python

Control flow in programming refers to the order in which statements are executed. Python provides several control flow statements to control the execution of your code.

## Conditional Statements

Conditional statements allow you to execute different code blocks based on specified conditions.

### if-elif-else Statements

```python
# Basic if statement
age = 20

if age >= 18:
    print("You are an adult.")

# if-else statement
temperature = 15

if temperature > 25:
    print("It's warm outside.")
else:
    print("It's cool outside.")

# if-elif-else statement
score = 85

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"Your grade is {grade}.")
```

## Loops

Loops allow you to repeat a block of code multiple times.

### for Loops

The `for` loop in Python iterates over a sequence (such as a list, tuple, string, or range).

```python
# Iterating over a range of numbers
for i in range(5):  # 0, 1, 2, 3, 4
    print(i)

# Iterating over a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Iterating over a string
for char in "Python":
    print(char)

# Using enumerate to get both index and value
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
```

### while Loops

The `while` loop repeats a block of code as long as a specified condition is true.

```python
# Basic while loop
count = 0
while count < 5:
    print(count)
    count += 1

# while loop with break
number = 0
while True:
    print(number)
    number += 1
    if number >= 5:
        break  # Exit the loop when number reaches 5

# while loop with continue
i = 0
while i < 10:
    i += 1
    if i % 2 == 0:  # If i is even
        continue  # Skip the rest of the loop body
    print(i)  # Print only odd numbers
```

## Loop Control Statements

Python provides statements to control the flow of loops:

- `break`: Exits the loop entirely
- `continue`: Skips the current iteration and continues with the next
- `pass`: Does nothing; used as a placeholder

```python
# Example with break
for i in range(10):
    if i == 7:
        break  # Exit the loop when i is 7
    print(i)

# Example with continue
for i in range(10):
    if i % 2 == 0:
        continue  # Skip even numbers
    print(i)

# Example with pass
for i in range(5):
    if i == 2:
        pass  # Do nothing special when i is 2
    print(i)
```
""",
                "quizzes": [
                    {
                        "title": "Control Flow Quiz",
                        "description": "Test your understanding of Python control flow structures.",
                        "time_limit_minutes": 20,
                        "passing_score": 70,
                        "questions": [
                            {
                                "type": "multiple_choice",
                                "text": "What will be the output of the following code?\n\n```python\nx = 5\nif x > 10:\n    print('A')\nelif x > 5:\n    print('B')\nelif x == 5:\n    print('C')\nelse:\n    print('D')\n```",
                                "explanation": "This code checks multiple conditions using if-elif-else statements.",
                                "points": 10,
                                "choices": [
                                    {"text": "A", "is_correct": False, "feedback": "This would print if x > 10, but x is 5."},
                                    {"text": "B", "is_correct": False, "feedback": "This would print if x > 5, but x is exactly 5."},
                                    {"text": "C", "is_correct": True, "feedback": "Correct! Since x equals 5, the third condition (x == 5) is True."},
                                    {"text": "D", "is_correct": False, "feedback": "This would print if none of the conditions were True, but the third condition (x == 5) is True."}
                                ]
                            },
                            {
                                "type": "multiple_choice",
                                "text": "What will be the output of the following code?\n\n```python\nfor i in range(1, 6):\n    if i % 2 == 0:\n        continue\n    print(i)\n```",
                                "explanation": "This code uses a for loop with a continue statement to skip even numbers.",
                                "points": 10,
                                "choices": [
                                    {"text": "1 2 3 4 5", "is_correct": False, "feedback": "The continue statement skips even numbers."},
                                    {"text": "2 4", "is_correct": False, "feedback": "The continue statement skips even numbers, not odd ones."},
                                    {"text": "1 3 5", "is_correct": True, "feedback": "Correct! The loop prints only odd numbers because the continue statement skips the even ones."},
                                    {"text": "No output", "is_correct": False, "feedback": "The loop does produce output for odd numbers."}
                                ]
                            },
                            {
                                "type": "true_false",
                                "text": "The `break` statement exits only the innermost loop when used in nested loops.",
                                "explanation": "The break statement only affects the loop in which it is directly contained.",
                                "points": 5,
                                "is_correct": True
                            },
                            {
                                "type": "true_false",
                                "text": "In Python, indentation is optional in control flow statements.",
                                "explanation": "Python uses indentation to define code blocks in control flow statements.",
                                "points": 5,
                                "is_correct": False
                            },
                            {
                                "type": "essay",
                                "text": "Write a Python program that prints the first 10 Fibonacci numbers using a loop. Explain your approach.",
                                "explanation": "This tests understanding of loops and algorithm implementation.",
                                "points": 20,
                                "answer_guidelines": "A good answer should include a working loop (for or while) that calculates and prints the first 10 Fibonacci numbers (0, 1, 1, 2, 3, 5, 8, 13, 21, 34). The explanation should discuss how the algorithm initializes the first two numbers and then iteratively computes subsequent numbers in the sequence."
                            }
                        ]
                    }
                ]
            },
            {
                "title": "Functions and Modules",
                "description": "Learn how to create and use functions, as well as organize code into modules.",
                "quizzes": []
            }
        ]
    },
    {
        "title": "Web Development Fundamentals",
        "description": "Learn the basics of web development, including HTML, CSS, and JavaScript, to build modern, responsive websites.",
        "content": WEB_DEV_CONTENT,
        "modules": [
            {
                "title": "HTML Fundamentals",
                "description": "Introduction to HTML structure, elements, and semantic markup.",
                "content": """
# HTML Fundamentals

HTML (HyperText Markup Language) is the standard markup language for creating web pages. It describes the structure of a webpage using a series of elements that tell the browser how to display the content.

## HTML Document Structure

A basic HTML document has the following structure:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- Content goes here -->
    <h1>Hello, World!</h1>
    <p>This is a paragraph.</p>
</body>
</html>
```

- `<!DOCTYPE html>`: Declaration that tells the browser this is an HTML5 document.
- `<html>`: The root element of an HTML page.
- `<head>`: Contains meta-information about the document (not displayed).
- `<meta>`: Provides metadata about the HTML document.
- `<title>`: Specifies the title of the document (shown in the browser tab).
- `<link>`: Links to external resources like CSS files.
- `<body>`: Contains the visible content of the page.
- `<!-- ... -->`: Comments that are not displayed in the browser.

## HTML Elements

HTML elements are represented by tags:

```html
<tagname>Content goes here...</tagname>
```

Some common HTML elements include:

### Headings

HTML has six levels of headings, from `<h1>` (most important) to `<h6>` (least important).

```html
<h1>This is a level 1 heading</h1>
<h2>This is a level 2 heading</h2>
<h3>This is a level 3 heading</h3>
<h4>This is a level 4 heading</h4>
<h5>This is a level 5 heading</h5>
<h6>This is a level 6 heading</h6>
```

### Paragraphs and Text Formatting

```html
<p>This is a paragraph.</p>

<p>This paragraph contains <strong>bold text</strong> and <em>italicized text</em>.</p>

<p>This text includes a <a href="https://www.example.com">link to Example.com</a>.</p>
```

### Lists

HTML supports ordered lists, unordered lists, and description lists.

```html
<!-- Unordered List -->
<ul>
    <li>Item 1</li>
    <li>Item 2</li>
    <li>Item 3</li>
</ul>

<!-- Ordered List -->
<ol>
    <li>First item</li>
    <li>Second item</li>
    <li>Third item</li>
</ol>

<!-- Description List -->
<dl>
    <dt>Term 1</dt>
    <dd>Definition 1</dd>
    <dt>Term 2</dt>
    <dd>Definition 2</dd>
</dl>
```

### Images

```html
<img src="image.jpg" alt="Description of the image" width="500" height="300">
```

### Tables

```html
<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Country</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>John Doe</td>
            <td>28</td>
            <td>USA</td>
        </tr>
        <tr>
            <td>Jane Smith</td>
            <td>32</td>
            <td>Canada</td>
        </tr>
    </tbody>
</table>
```

### Forms

Forms are used to collect user input.

```html
<form action="/submit" method="post">
    <label for="name">Name:</label>
    <input type="text" id="name" name="name" required>
    
    <label for="email">Email:</label>
    <input type="email" id="email" name="email" required>
    
    <label for="message">Message:</label>
    <textarea id="message" name="message" rows="4" required></textarea>
    
    <button type="submit">Submit</button>
</form>
```

## Semantic HTML

Semantic HTML uses tags that convey meaning about the structure of the content, rather than just its appearance.

```html
<header>
    <h1>Website Title</h1>
    <nav>
        <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>
</header>

<main>
    <section id="home">
        <h2>Home</h2>
        <p>Welcome to our website!</p>
    </section>
    
    <section id="about">
        <h2>About Us</h2>
        <p>We are a company that...</p>
    </section>
    
    <article>
        <h2>Latest News</h2>
        <p>Published on <time datetime="2023-07-10">July 10, 2023</time></p>
        <p>Content of the news article...</p>
    </article>
</main>

<aside>
    <h3>Related Links</h3>
    <ul>
        <li><a href="#">Link 1</a></li>
        <li><a href="#">Link 2</a></li>
    </ul>
</aside>

<footer>
    <p>&copy; 2023 My Website. All rights reserved.</p>
</footer>
```

Semantic tags include:
- `<header>`: Represents introductory content or a set of navigational links.
- `<nav>`: Defines a section of navigation links.
- `<main>`: Specifies the main content of a document.
- `<section>`: Defines a section in a document.
- `<article>`: Represents a self-contained composition in a document.
- `<aside>`: Defines content aside from the main content.
- `<footer>`: Defines a footer for a document or section.
- `<figure>` and `<figcaption>`: Used to encapsulate media content and its caption.
- `<time>`: Represents a specific time or datetime.
""",
                "quizzes": [
                    {
                        "title": "HTML Basics Quiz",
                        "description": "Test your knowledge of HTML fundamentals.",
                        "time_limit_minutes": 15,
                        "passing_score": 70,
                        "questions": [
                            {
                                "type": "multiple_choice",
                                "text": "Which HTML tag is used to define the main content of an HTML document?",
                                "explanation": "Semantic HTML tags help define the structure and meaning of content.",
                                "points": 10,
                                "choices": [
                                    {"text": "<content>", "is_correct": False, "feedback": "There is no <content> tag in HTML."},
                                    {"text": "<section>", "is_correct": False, "feedback": "<section> defines a section in a document, not the main content."},
                                    {"text": "<body>", "is_correct": False, "feedback": "<body> contains all the content, but doesn't specifically define the main content area."},
                                    {"text": "<main>", "is_correct": True, "feedback": "Correct! The <main> tag specifies the main content of a document."}
                                ]
                            },
                            {
                                "type": "multiple_choice",
                                "text": "Which of the following is the correct way to create a hyperlink in HTML?",
                                "explanation": "Hyperlinks are created using the anchor tag in HTML.",
                                "points": 10,
                                "choices": [
                                    {"text": "<link href='https://example.com'>Example</link>", "is_correct": False, "feedback": "The <link> tag is used to link to external resources, not to create hyperlinks."},
                                    {"text": "<a>https://example.com</a>", "is_correct": False, "feedback": "The href attribute is missing."},
                                    {"text": "<a href='https://example.com'>Example</a>", "is_correct": True, "feedback": "Correct! This is the proper way to create a hyperlink using the anchor tag."},
                                    {"text": "<href>https://example.com</href>", "is_correct": False, "feedback": "There is no <href> tag in HTML."}
                                ]
                            },
                            {
                                "type": "true_false",
                                "text": "In HTML, the <img> tag requires a closing tag like </img>.",
                                "explanation": "Some HTML elements are self-closing and don't need a closing tag.",
                                "points": 5,
                                "is_correct": False
                            },
                            {
                                "type": "true_false",
                                "text": "The <!DOCTYPE html> declaration is required at the beginning of HTML5 documents.",
                                "explanation": "The DOCTYPE declaration tells the browser which version of HTML the page is using.",
                                "points": 5,
                                "is_correct": True
                            },
                            {
                                "type": "essay",
                                "text": "Explain the importance of semantic HTML elements. Provide at least three examples of semantic elements and how they improve web development.",
                                "explanation": "This question tests understanding of the purpose and benefits of semantic HTML.",
                                "points": 20,
                                "answer_guidelines": "A good answer should explain that semantic HTML elements give meaning to the structure of web content rather than just defining its appearance. It should mention benefits like improved accessibility, SEO, and code readability. Examples should include elements like <header>, <nav>, <main>, <section>, <article>, <aside>, <footer>, etc., with explanations of their specific purposes."
                            }
                        ]
                    }
                ]
            },
            {
                "title": "CSS Styling",
                "description": "Learn how to style web pages using Cascading Style Sheets (CSS).",
                "quizzes": []
            },
            {
                "title": "JavaScript Basics",
                "description": "Introduction to JavaScript programming for interactive web pages.",
                "quizzes": []
            }
        ]
    },
    {
        "title": "Data Science with Python",
        "description": "Explore data science concepts and techniques using Python libraries like NumPy, Pandas, and Matplotlib.",
        "content": DATA_SCIENCE_CONTENT,
        "modules": [
            {
                "title": "Introduction to NumPy",
                "description": "Learn the basics of NumPy for numerical computing.",
                "quizzes": []
            },
            {
                "title": "Data Analysis with Pandas",
                "description": "Explore data manipulation and analysis with Pandas.",
                "quizzes": []
            },
            {
                "title": "Data Visualization with Matplotlib",
                "description": "Learn to create informative and appealing data visualizations.",
                "quizzes": []
            }
        ]
    },
    {
        "title": "Machine Learning Fundamentals",
        "description": "Learn the core concepts of machine learning, including supervised and unsupervised learning techniques.",
        "content": MACHINE_LEARNING_CONTENT,
        "modules": [
            {
                "title": "Supervised Learning",
                "description": "Learn about classification and regression techniques.",
                "quizzes": []
            },
            {
                "title": "Unsupervised Learning",
                "description": "Explore clustering and dimensionality reduction methods.",
                "quizzes": []
            },
            {
                "title": "Model Evaluation",
                "description": "Learn how to evaluate and validate machine learning models.",
                "quizzes": []
            }
        ]
    }
]

def create_demo_rag_content():
    """Create comprehensive demo content for RAG integration."""
    # Get or create test users
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print(f"Created admin user: {admin_user.username}")
    
    # Get or create instructor users
    instructors = []
    instructor_data = [
        {'username': 'professor', 'email': 'professor@example.com', 'first': 'Jane', 'last': 'Smith'},
        {'username': 'teacher', 'email': 'teacher@example.com', 'first': 'Robert', 'last': 'Johnson'}
    ]
    
    for data in instructor_data:
        try:
            instructor = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            instructor = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password='password123',
                first_name=data['first'],
                last_name=data['last']
            )
            # Create or get profile
            if not hasattr(instructor, 'profile'):
                profile = UserProfile.objects.create(user=instructor)
            else:
                profile = instructor.profile
            profile.is_instructor = True
            profile.save()
            print(f"Created instructor: {instructor.username}")
        instructors.append(instructor)
    
    # Get or create student users
    students = []
    student_data = [
        {'username': 'student1', 'email': 'student1@example.com', 'first': 'Alice', 'last': 'Brown'},
        {'username': 'student2', 'email': 'student2@example.com', 'first': 'Bob', 'last': 'Davis'},
        {'username': 'student3', 'email': 'student3@example.com', 'first': 'Charlie', 'last': 'Wilson'}
    ]
    
    for data in student_data:
        try:
            student = User.objects.get(username=data['username'])
        except User.DoesNotExist:
            student = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password='password123',
                first_name=data['first'],
                last_name=data['last']
            )
            print(f"Created student: {student.username}")
        students.append(student)
    
    created_courses = 0
    created_modules = 0
    created_quizzes = 0
    created_questions = 0
    created_enrollments = 0
    
    with transaction.atomic():
        # Process each course
        for course_data in COURSES:
            # Assign instructor (alternate between available instructors)
            instructor = instructors[created_courses % len(instructors)]
            
            # Check if course already exists
            existing_course = Course.objects.filter(title=course_data['title']).first()
            if existing_course:
                print(f"Course already exists: {existing_course.title}")
                course = existing_course
            else:
                # Create course
                course = Course.objects.create(
                    title=course_data['title'],
                    description=course_data['description'],
                    instructor=instructor,
                    start_date=timezone.now() - timedelta(days=30),
                    end_date=timezone.now() + timedelta(days=180),
                    enrollment_type='open',
                    course_type='standard',
                    analytics_enabled=True
                )
                created_courses += 1
                print(f"Created course: {course.title}")
            
            # Process modules
            for i, module_data in enumerate(course_data.get('modules', [])):
                # Check if module already exists
                existing_module = Module.objects.filter(course=course, title=module_data['title']).first()
                if existing_module:
                    print(f"Module already exists: {existing_module.title}")
                    module = existing_module
                else:
                    # Create module
                    module = Module.objects.create(
                        course=course,
                        title=module_data['title'],
                        description=module_data['description'],
                        order=i + 1,
                        content=module_data.get('content', '')
                    )
                    created_modules += 1
                    print(f"Created module: {module.title}")
                
                # Process quizzes
                for quiz_data in module_data.get('quizzes', []):
                    # Check if quiz already exists
                    existing_quiz = Quiz.objects.filter(module=module, title=quiz_data['title']).first()
                    if existing_quiz:
                        print(f"Quiz already exists: {existing_quiz.title}")
                        # Clear existing questions if needed
                        existing_quiz.questions.all().delete()
                        quiz = existing_quiz
                    else:
                        # Create quiz
                        quiz = Quiz.objects.create(
                            module=module,
                            title=quiz_data['title'],
                            description=quiz_data['description'],
                            time_limit_minutes=quiz_data.get('time_limit_minutes', 30),
                            passing_score=quiz_data.get('passing_score', 70),
                            allow_multiple_attempts=True,
                            max_attempts=3,
                            randomize_questions=True
                        )
                        created_quizzes += 1
                        print(f"Created quiz: {quiz.title}")
                    
                    # Create questions
                    for question_data in quiz_data.get('questions', []):
                        if question_data['type'] == 'multiple_choice':
                            # Create multiple choice question
                            question = MultipleChoiceQuestion.objects.create(
                                quiz=quiz,
                                text=question_data['text'],
                                explanation=question_data.get('explanation', ''),
                                points=question_data.get('points', 10),
                                allow_multiple=False
                            )
                            # Create choices
                            for j, choice_data in enumerate(question_data['choices']):
                                Choice.objects.create(
                                    question=question,
                                    text=choice_data['text'],
                                    is_correct=choice_data['is_correct'],
                                    feedback=choice_data.get('feedback', ''),
                                    order=j + 1
                                )
                                
                        elif question_data['type'] == 'true_false':
                            # Create true/false question
                            TrueFalseQuestion.objects.create(
                                quiz=quiz,
                                text=question_data['text'],
                                explanation=question_data.get('explanation', ''),
                                points=question_data.get('points', 5),
                                correct_answer=question_data['is_correct']
                            )
                            
                        elif question_data['type'] == 'essay':
                            # Create essay question
                            essay = EssayQuestion.objects.create(
                                quiz=quiz,
                                text=question_data['text'],
                                explanation=question_data.get('explanation', ''),
                                points=question_data.get('points', 20),
                                rubric=question_data.get('answer_guidelines', ''),
                                min_word_count=50,  # Set a reasonable minimum word count
                                max_word_count=500  # Set a reasonable maximum word count
                            )
                        
                        created_questions += 1
                    
                    print(f"Created {len(quiz_data.get('questions', []))} questions for quiz: {quiz.title}")
            
            # Enroll students in the course
            for student in students:
                # Check if enrollment already exists
                if not Enrollment.objects.filter(user=student, course=course).exists():
                    enrollment = Enrollment.objects.create(
                        user=student,
                        course=course,
                        status='active',
                        progress=random.randint(0, 100)
                    )
                    created_enrollments += 1
                    print(f"Enrolled {student.username} in {course.title}")
    
    # Print summary
    print("\n=== Demo Content Creation Summary ===")
    print(f"Created {created_courses} new courses")
    print(f"Created {created_modules} new modules")
    print(f"Created {created_quizzes} new quizzes")
    print(f"Created {created_questions} new questions")
    print(f"Created {created_enrollments} new enrollments")
    print(f"\nTotal courses: {Course.objects.count()}")
    print(f"Total modules: {Module.objects.count()}")
    print(f"Total quizzes: {Quiz.objects.count()}")
    print(f"Total questions: {Question.objects.count()}")
    print(f"Total enrollments: {Enrollment.objects.count()}")
    print("\nDemo content creation complete!")

if __name__ == "__main__":
    create_demo_rag_content()