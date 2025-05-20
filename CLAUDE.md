# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains Django-based Learning Management System (LMS) projects, with two main versions:

1. **LearnMore Reborn** (`djangoapps/learnmore-reborn/`):
   - Django 4.x with REST Framework integration
   - JWT authentication
   - Basic apps: courses, progress, users, ai_tutor, analytics
   - Current Development Focus: Migrating and rebuilding the LMS
     - Referencing tutorials and labs in `labs/` folder
     - Using `djangoapps/learnmore_plus` as a reference for front-ends and models
     - Scope defined in `docs/design-document.md`
     - UI mockups available in `docs/mockups`
     - Phased migration plan outlined in `djangoapps/learnmore_reborn/MIGRATION-PLAN.md`

2. **LearnMore Plus** (`djangoapps/learnmore_plus/`):
   - More feature-rich version with additional functionality
   - Advanced modular architecture with separate apps for each feature
   - Includes AI Tutor with LangChain and Ollama integration
   - Uses Tailwind CSS for UI components

3. **ResumeBuilder** (`labs/resumebuilder/`):
   - Simple Django app for CRUD operations
   - Part of class labs

(Rest of the file remains unchanged from the previous content)