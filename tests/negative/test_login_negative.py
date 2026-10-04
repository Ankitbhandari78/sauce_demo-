"""Negative authentication scenarios."""

from playwright.sync_api import Page, expect


def test_shows_an_error_for_invalid_credentials(page: Page) -> None:
    page.goto("/")
    page.get_by_role("textbox", name="Username").fill("invalid_user")
    page.get_by_role("textbox", name="Password").fill("invalid_password")
    page.get_by_role("button", name="Login").click()

    expect(page.locator('[data-test="error"]')).to_contain_text(
        "Username and password do not match"
    )
