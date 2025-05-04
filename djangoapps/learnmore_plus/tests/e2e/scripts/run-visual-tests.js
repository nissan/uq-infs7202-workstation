#!/usr/bin/env node

/**
 * Script to run visual regression tests
 * Usage: node run-visual-tests.js
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Define key pages to capture screenshots
const pagesToTest = [
  '/', // Home page
  '/login/', // Login page
  '/courses/catalog/', // Course catalog
  '/register/', // Registration page
];

// Define viewport sizes
const viewports = [
  { width: 1920, height: 1080, name: 'desktop' },
  { width: 768, height: 1024, name: 'tablet' },
  { width: 375, height: 667, name: 'mobile' },
];

// Create screenshots directory if it doesn't exist
const screenshotsDir = path.join(__dirname, '..', 'screenshots');
if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

// Get the reference directory
const referenceDir = path.join(screenshotsDir, 'reference');
if (!fs.existsSync(referenceDir)) {
  fs.mkdirSync(referenceDir, { recursive: true });
}

// Get the current directory for new screenshots
const currentDir = path.join(screenshotsDir, `current-${new Date().toISOString().replace(/:/g, '-')}`);
fs.mkdirSync(currentDir, { recursive: true });

// Get the diff directory
const diffDir = path.join(screenshotsDir, 'diff');
if (!fs.existsSync(diffDir)) {
  fs.mkdirSync(diffDir, { recursive: true });
}

// Function to take screenshots
async function takeScreenshots() {
  // Generate Playwright script to take screenshots
  const scriptPath = path.join(__dirname, 'temp-screenshot.js');
  
  let script = `
    const { chromium } = require('@playwright/test');
    
    (async () => {
      const browser = await chromium.launch();
      
      try {
        for (const viewport of ${JSON.stringify(viewports)}) {
          const context = await browser.newContext({
            viewport: {
              width: viewport.width,
              height: viewport.height,
            },
          });
          
          const page = await context.newPage();
          
          for (const pageUrl of ${JSON.stringify(pagesToTest)}) {
            console.log(\`Taking screenshot of \${pageUrl} at \${viewport.name}\`);
            
            try {
              await page.goto('http://localhost:8000' + pageUrl);
              
              // Wait for page to be fully loaded
              await page.waitForLoadState('networkidle');
              
              // Generate filename
              const pageName = pageUrl === '/' ? 'home' : pageUrl.replace(/\\//g, '-').replace(/^-/, '');
              const filename = \`\${pageName}--\${viewport.name}.png\`;
              
              // Save screenshot to current directory
              await page.screenshot({
                path: '${currentDir}/' + filename,
                fullPage: true,
              });
            } catch (err) {
              console.error(\`Error capturing \${pageUrl}: \${err.message}\`);
            }
          }
          
          await context.close();
        }
      } finally {
        await browser.close();
      }
    })();
  `;
  
  fs.writeFileSync(scriptPath, script);
  
  try {
    // Run the script
    execSync(`node ${scriptPath}`, { stdio: 'inherit' });
  } finally {
    // Clean up
    fs.unlinkSync(scriptPath);
  }
}

// Function to compare screenshots
function compareScreenshots() {
  if (!fs.existsSync(referenceDir) || fs.readdirSync(referenceDir).length === 0) {
    console.log('No reference screenshots found. Copying current screenshots as reference.');
    
    // Copy current screenshots to reference directory
    fs.readdirSync(currentDir).forEach(file => {
      fs.copyFileSync(
        path.join(currentDir, file),
        path.join(referenceDir, file)
      );
    });
    
    return true;
  }
  
  const results = {
    passed: [],
    failed: [],
    missing: [],
  };
  
  // Generate comparison script
  const scriptPath = path.join(__dirname, 'temp-compare.js');
  
  let script = `
    const fs = require('fs');
    const path = require('path');
    const { PNG } = require('pngjs');
    const pixelmatch = require('pixelmatch');
    
    const referenceDir = '${referenceDir}';
    const currentDir = '${currentDir}';
    const diffDir = '${diffDir}';
    
    const results = {
      passed: [],
      failed: [],
      missing: [],
    };
    
    // Get all reference screenshots
    const referenceFiles = fs.readdirSync(referenceDir);
    
    for (const refFile of referenceFiles) {
      const currentFile = path.join(currentDir, refFile);
      
      // Skip if the current screenshot doesn't exist
      if (!fs.existsSync(currentFile)) {
        console.log(\`Missing current screenshot for: \${refFile}\`);
        results.missing.push(refFile);
        continue;
      }
      
      // Load images
      const img1 = PNG.sync.read(fs.readFileSync(path.join(referenceDir, refFile)));
      const img2 = PNG.sync.read(fs.readFileSync(currentFile));
      
      // Check dimensions
      if (img1.width !== img2.width || img1.height !== img2.height) {
        console.log(\`Size mismatch for \${refFile}: \${img1.width}x\${img1.height} vs \${img2.width}x\${img2.height}\`);
        results.failed.push(refFile);
        continue;
      }
      
      // Create output image
      const diff = new PNG({ width: img1.width, height: img1.height });
      
      // Compare images
      const numDiffPixels = pixelmatch(
        img1.data,
        img2.data,
        diff.data,
        img1.width,
        img1.height,
        { threshold: 0.1 }
      );
      
      // Calculate percentage difference
      const totalPixels = img1.width * img1.height;
      const percentDiff = (numDiffPixels / totalPixels) * 100;
      
      // Save diff image
      fs.writeFileSync(path.join(diffDir, refFile), PNG.sync.write(diff));
      
      // Add to results
      if (percentDiff < 0.5) {
        console.log(\`PASS: \${refFile} - \${percentDiff.toFixed(2)}% different\`);
        results.passed.push(refFile);
      } else {
        console.log(\`FAIL: \${refFile} - \${percentDiff.toFixed(2)}% different\`);
        results.failed.push(refFile);
      }
    }
    
    console.log(\`\\nResults: \${results.passed.length} passed, \${results.failed.length} failed, \${results.missing.length} missing\`);
    
    const result = {
      passed: results.passed.length,
      failed: results.failed.length,
      missing: results.missing.length,
      details: results,
    };
    
    fs.writeFileSync(
      path.join('${screenshotsDir}', 'results.json'),
      JSON.stringify(result, null, 2)
    );
    
    process.exit(results.failed.length > 0 ? 1 : 0);
  `;
  
  fs.writeFileSync(scriptPath, script);
  
  try {
    console.log('\nComparing screenshots...');
    console.log('------------------------');
    
    // Install dependencies if needed
    if (!fs.existsSync(path.join(__dirname, '..', 'node_modules', 'pixelmatch'))) {
      console.log('Installing dependencies for image comparison...');
      execSync('npm install pixelmatch pngjs', { cwd: path.join(__dirname, '..'), stdio: 'inherit' });
    }
    
    try {
      execSync(`node ${scriptPath}`, { stdio: 'inherit' });
      return true;
    } catch (error) {
      console.error('Visual tests failed. See diff images for details.');
      return false;
    }
  } finally {
    // Clean up
    fs.unlinkSync(scriptPath);
  }
}

// Main function
async function main() {
  console.log('Taking screenshots...');
  await takeScreenshots();
  
  const result = compareScreenshots();
  
  if (result) {
    console.log('\nVisual tests completed successfully!');
    console.log(`Reference screenshots: ${referenceDir}`);
    console.log(`Current screenshots: ${currentDir}`);
    console.log(`Diff images: ${diffDir}`);
  }
}

main().catch(console.error);