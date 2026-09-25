# OrangeHRM Playwright Framework

JavaScript Playwright test framework with page objects, custom fixtures, environment configuration, and HTML reporting.

## Setup

```bash
npm install
npx playwright install
cp .env.example .env
```

Update `.env` with the credentials for the OrangeHRM environment under test.

## Run tests

```bash
npm test                 # Headless tests
npm run test:headed      # Run with a visible browser
npm run test:debug       # Open Playwright Inspector
npm run test:smoke       # Run tests tagged @smoke
npm run report           # Open the latest HTML report
```

Override the target environment without changing files:

```bash
BASE_URL=https://your-orangehrm-host.example npm test
```

## Structure

```text
pages/       Page Object Model classes
fixtures/    Reusable Playwright fixtures
tests/       Test specifications
playwright.config.js
```
