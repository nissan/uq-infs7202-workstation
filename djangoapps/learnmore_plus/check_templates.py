#!/usr/bin/env python
"""
Script to check for template syntax issues in Django templates.
This script doesn't require Django to be installed since it directly reads the files.
"""
import os
import re
import sys

def check_templates_for_issues(templates_dir):
    """Check all templates for common syntax issues."""
    print(f"Checking templates in: {templates_dir}")
    issues = []
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, templates_dir)
                
                with open(file_path, 'r') as f:
                    try:
                        content = f.read()
                        file_issues = []
                        
                        # Check for mismatched with/endwith tags
                        with_tags = re.findall(r'{%\s*with', content)
                        endwith_tags = re.findall(r'{%\s*endwith', content)
                        
                        if len(with_tags) != len(endwith_tags):
                            file_issues.append(f"Mismatched with and endwith tags ({len(with_tags)} vs {len(endwith_tags)})")
                            
                        # Detect problematic inline conditional pattern
                        inline_if_with = re.findall(r'{%\s*if not \w+\s*%}{%\s*with', content)
                        if inline_if_with:
                            proper_format = re.findall(r'{%\s*if not \w+\s*%}\s+{%\s*with', content)
                            if len(inline_if_with) != len(proper_format):
                                file_issues.append(f"Contains inline if-with pattern which may cause issues")
                                
                        # Check for mismatched if/endif tags
                        if_tags = re.findall(r'{%\s*if', content)
                        endif_tags = re.findall(r'{%\s*endif', content)
                        
                        if len(if_tags) != len(endif_tags):
                            file_issues.append(f"Mismatched if and endif tags ({len(if_tags)} vs {len(endif_tags)})")
                        
                        # Check nested logic errors
                        # Find all blocks that open with one tag and close with another
                        lines = content.splitlines()
                        stack = []
                        for i, line in enumerate(lines):
                            # Check for opening tags
                            if re.search(r'{%\s*if', line) and not re.search(r'{%\s*endif', line):
                                stack.append(('if', i+1))
                            elif re.search(r'{%\s*with', line) and not re.search(r'{%\s*endwith', line):
                                stack.append(('with', i+1))
                            
                            # Check for closing tags
                            if re.search(r'{%\s*endif', line) and stack and stack[-1][0] != 'if':
                                file_issues.append(f"Line {i+1}: Found endif but expected end{stack[-1][0]} (opened on line {stack[-1][1]})")
                            elif re.search(r'{%\s*endwith', line) and stack and stack[-1][0] != 'with':
                                file_issues.append(f"Line {i+1}: Found endwith but expected end{stack[-1][0]} (opened on line {stack[-1][1]})")
                        
                        if file_issues:
                            issues.append(f"{relative_path}:\n  - " + "\n  - ".join(file_issues))
                    
                    except Exception as e:
                        issues.append(f"{relative_path}: Error reading file: {str(e)}")
    
    return issues

def main():
    """Main entry point."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(current_dir, 'templates')
    
    if not os.path.exists(templates_dir):
        print(f"Templates directory not found: {templates_dir}")
        return 1
    
    issues = check_templates_for_issues(templates_dir)
    
    if issues:
        print("Found template syntax issues:")
        for issue in issues:
            print(f"  - {issue}")
        print(f"\nTotal issues found: {len(issues)}")
        return 1
    else:
        print("No template syntax issues found! All templates are properly formatted.")
        return 0

if __name__ == "__main__":
    sys.exit(main())