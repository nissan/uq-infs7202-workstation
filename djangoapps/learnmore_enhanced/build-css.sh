#!/bin/bash

# Build Tailwind CSS once
echo "Building Tailwind CSS..."

# Build the CSS file
npx tailwindcss -i ./learnmoreapp/static/learnmoreapp/css/tailwind/input.css -o ./learnmoreapp/static/learnmoreapp/css/tailwind/output.css 