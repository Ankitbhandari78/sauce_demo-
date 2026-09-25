const { test, expect } = require('../fixtures/test');

test.describe('Authentication', () => {
  test('allows a configured user to log in @smoke', async ({ loginPage }) => {
    await loginPage.goto();
    await loginPage.loginAsConfiguredUser();

    await expect(loginPage.dashboardHeading).toBeVisible();
  });
});
