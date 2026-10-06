"""Positive logout scenario: a signed-in user returns to the login page."""

import os
import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_user_can_log_out_and_return_to_login(page: Page, base_url: str) -> None:
    # Log in with the configured credentials.
    page.goto("/")
    page.get_by_role("textbox", name="Username").fill(os.environ["SAUCEDEMO_USERNAME"])
    page.get_by_role("textbox", name="Password").fill(os.environ["SAUCEDEMO_PASSWORD"])
    page.get_by_role("button", name="Login").click()

    # Dashboard assertion: signing in lands on the products page.
    expect(page).to_have_url(re.compile(r"/inventory\.html$"))
    expect(page.get_by_test_id("title")).to_have_text("Products")
    expect(page.get_by_test_id("inventory-item-name")).to_have_count(6)

    # Open the side menu and click Logout.
    page.get_by_role("button", name="Open Menu").click()
    logout_link = page.get_by_test_id("logout-sidebar-link")
    expect(logout_link).to_be_visible()
    logout_link.click()

    # Assertion: the user is returned to the login page.
    expect(page).to_have_url(re.compile(re.escape(base_url) + r"/?$"))
    expect(page.get_by_role("button", name="Login")).to_be_visible()
    expect(page.get_by_role("textbox", name="Username")).to_be_visible()
    expect(page.get_by_role("textbox", name="Password")).to_be_visible()

    # The dashboard is gone, so the session really did end.
    expect(page.get_by_test_id("inventory-item")).to_have_count(0)