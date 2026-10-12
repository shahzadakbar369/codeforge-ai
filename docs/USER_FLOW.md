# CodeForge AI — User Flow

## Purpose
This document describes how a user will move through the CodeForge AI application. The current frontend is a UI prototype, and backend integration is pending.

## Main User Flow

1. **Open Dashboard**
   - The user opens the CodeForge AI workspace.

2. **Upload PHP File**
   - The user selects a PHP file.
   - The application displays the selected file and its code.

3. **Convert PHP to Python**
   - The user starts the migration process.
   - The planned backend sends the PHP code for AI-assisted conversion.
   - The generated Python code is displayed to the user.

4. **Run Equivalence Checks**
   - The application runs the original PHP and migrated Python code against the same inputs.
   - The results are compared to check whether the functions behave equivalently.

5. **Security Scan**
   - The planned security workflow checks the code for security issues.
   - The application displays the scan report when the security backend is available.

6. **Review Results**
   - The user reviews the generated Python code, comparison results, and security report.

## Current Status

- Frontend UI prototype: implemented.
- PHP file selection and display: implemented.
- Real AI conversion: pending backend integration.
- Equivalence testing: pending integration.
- Real security scanning: pending integration.

**Note:** The conversion and security buttons currently demonstrate the UI workflow; they do not perform real backend migration or security analysis.