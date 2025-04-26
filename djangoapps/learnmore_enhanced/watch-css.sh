#!/bin/bash

# Watch and rebuild Tailwind CSS
echo "Watching for CSS changes..."

# Watch the input.css file and rebuild when changes are detected
npx tailwindcss -i ./learnmoreapp/static/learnmoreapp/css/tailwind/input.css -o ./learnmoreapp/static/learnmoreapp/css/tailwind/output.css --watch 