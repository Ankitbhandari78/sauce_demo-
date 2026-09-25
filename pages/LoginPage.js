class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.getByRole('textbox', { name: 'Username' });
    this.passwordInput = page.getByRole('textbox', { name: 'Password' });
    this.loginButton = page.getByRole('button', { name: 'Login' });
    this.dashboardHeading = page.getByRole('heading', { name: 'Dashboard' });
  }

  async goto() {
    await this.page.goto('/web/index.php/auth/login');
  }

  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async loginAsConfiguredUser() {
    const username = process.env.ORANGEHRM_USERNAME;
    const password = process.env.ORANGEHRM_PASSWORD;

    if (!username || !password) {
      throw new Error(
        'ORANGEHRM_USERNAME and ORANGEHRM_PASSWORD must be set in .env or the environment.',
      );
    }

    await this.login(username, password);
  }
}

module.exports = { LoginPage };
