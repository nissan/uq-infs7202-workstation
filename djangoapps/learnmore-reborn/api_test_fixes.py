"""
This script helps update API test files to use the AuthDisabledTestCase.

Execute this script to update your test files.
"""
import os
import re
import glob

# Files to update
test_files = [
    'courses/api_tests.py', 
    'courses/module_quiz_tests.py',
    'progress/api_tests.py',
    'users/api_tests.py'
]

# Base directory
base_dir = os.getcwd()

# New import statement to add
new_import = 'from test_auth_settings import AuthDisabledTestCase'

# Pattern to find the APITestCase inheritance
api_test_pattern = r'class\s+(\w+)\s*\(\s*APITestCase\s*\)'

# Replacement pattern for inheritance
replacement = r'class \1(APITestCaseBase)'

# Add import for APITestCaseBase
api_utils_import = 'from api_test_utils import APITestCaseBase'

def update_file(file_path):
    """Update a test file to use AuthDisabledTestCase."""
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Add import for AuthDisabledTestCase if not already present
    if 'from test_auth_settings import AuthDisabledTestCase' not in content:
        # Find the imports section
        import_lines = content.split('\n')
        import_end = 0
        for i, line in enumerate(import_lines):
            if line.startswith('from') or line.startswith('import'):
                import_end = i
        
        # Insert our import after the last import
        import_lines.insert(import_end + 1, new_import)
        content = '\n'.join(import_lines)
    
    # Add import for APITestCaseBase if not already present
    if 'from api_test_utils import APITestCaseBase' not in content:
        # Find the imports section
        import_lines = content.split('\n')
        import_end = 0
        for i, line in enumerate(import_lines):
            if line.startswith('from') or line.startswith('import'):
                import_end = i
        
        # Insert our import after the last import
        import_lines.insert(import_end + 1, api_utils_import)
        content = '\n'.join(import_lines)
    
    # Replace APITestCase with AuthDisabledTestCase
    content = re.sub(api_test_pattern, replacement, content)
    
    # Also replace "TestCase" with "AuthDisabledTestCase" for regular test cases
    content = re.sub(r'class\s+(\w+)\s*\(\s*TestCase\s*\)', r'class \1(AuthDisabledTestCase)', content)
    
    # Remove APIClient imports and replace with Django's client
    content = content.replace('from rest_framework.test import APIClient', '')
    content = content.replace('self.client = APIClient()', 'self.client.handler.enforce_csrf_checks = False')
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Updated file: {file_path}")
    return True

def main():
    """Main function to run the script."""
    print("Starting API test file updates...")
    
    # Convert relative paths to absolute paths
    abs_test_files = [os.path.join(base_dir, f) for f in test_files]
    
    # Update each file
    successful = 0
    for file_path in abs_test_files:
        if update_file(file_path):
            successful += 1
    
    # Also search for other test files that might need updating
    other_test_files = glob.glob(os.path.join(base_dir, 'courses/tests/*.py'))
    for file_path in other_test_files:
        if update_file(file_path):
            successful += 1
    
    print(f"Updated {successful} test files successfully!")

if __name__ == "__main__":
    main()