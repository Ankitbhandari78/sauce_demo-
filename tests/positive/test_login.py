"""Positive authentication scenarios."""

import os
import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
def test_login_page_displays_required_elements(page: Page) -> None:
    page.goto("/")
    expect(page.get_by_role("textbox", name="Username")).to_be_visible()
    expect(page.get_by_role("textbox", name="Password")).to_be_visible()
    expect(page.get_by_role("button", name="Login")).to_be_visible()


@pytest.mark.smoke
def test_allows_a_configured_user_to_log_in(page: Page) -> None:
    page.goto("/")
    page.get_by_role("textbox", name="Username").fill(os.environ["SAUCEDEMO_USERNAME"])
    page.get_by_role("textbox", name="Password").fill(os.environ["SAUCEDEMO_PASSWORD"])
    page.get_by_role("button", name="Login").click()

    expect(page.locator('[data-test="title"]')).to_have_text("Products")


@pytest.mark.smoke
def test_successful_login_redirects_to_inventory(page: Page) -> None:
    page.goto("/")
    page.get_by_role("textbox", name="Username").fill(os.environ["SAUCEDEMO_USERNAME"])
    page.get_by_role("textbox", name="Password").fill(os.environ["SAUCEDEMO_PASSWORD"])
    page.get_by_role("button", name="Login").click()

    expect(page).to_have_url(re.compile(r"/inventory\.html$"))
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
