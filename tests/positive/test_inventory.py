"""Positive dashboard scenario: branding, product sorting and logging out."""

import os
import re

import pytest
from playwright.sync_api import Page, expect

# Product list in each supported sort order (verified against the live demo).
NAMES_A_TO_Z = [
    "Sauce Labs Backpack",
    "Sauce Labs Bike Light",
    "Sauce Labs Bolt T-Shirt",
    "Sauce Labs Fleece Jacket",
    "Sauce Labs Onesie",
    "Test.allTheThings() T-Shirt (Red)",
]
NAMES_Z_TO_A = list(reversed(NAMES_A_TO_Z))
PRICE_LOW_TO_HIGH = [
    "Sauce Labs Onesie",
    "Sauce Labs Bike Light",
    "Sauce Labs Bolt T-Shirt",
    "Test.allTheThings() T-Shirt (Red)",
    "Sauce Labs Backpack",
    "Sauce Labs Fleece Jacket",
]
# NOTE: not an exact reverse of PRICE_LOW_TO_HIGH - the two $15.99 items tie,
# so they keep their alphabetical order in this view.
PRICE_HIGH_TO_LOW = [
    "Sauce Labs Fleece Jacket",
    "Sauce Labs Backpack",
    "Sauce Labs Bolt T-Shirt",
    "Test.allTheThings() T-Shirt (Red)",
    "Sauce Labs Bike Light",
    "Sauce Labs Onesie",
]


@pytest.mark.smoke
def test_dashboard_sorting_and_logout(page: Page, base_url: str) -> None:
    # Log in with the configured credentials.
    page.goto("/")
    page.get_by_role("textbox", name="Username").fill(os.environ["SAUCEDEMO_USERNAME"])
    page.get_by_role("textbox", name="Password").fill(os.environ["SAUCEDEMO_PASSWORD"])
    page.get_by_role("button", name="Login").click()

    # Dashboard assertion: the brand logo is shown on the products page.
    expect(page.locator(".app_logo")).to_have_text("Swag Labs")
    expect(page.get_by_test_id("title")).to_have_text("Products")
    expect(page.get_by_test_id("inventory-item-name")).to_have_count(6)

    sort = page.get_by_test_id("product-sort-container")
    names = page.get_by_test_id("inventory-item-name")

    # Default order is Name (A to Z).
    expect(sort).to_have_value("az")
    expect(names).to_have_text(NAMES_A_TO_Z)

    # Sort by Name (Z to A).
    sort.select_option("za")
    expect(sort).to_have_value("za")
    expect(names).to_have_text(NAMES_Z_TO_A)

    # Sort by Price (low to high).
    sort.select_option("lohi")
    expect(sort).to_have_value("lohi")
    expect(names).to_have_text(PRICE_LOW_TO_HIGH)

    # Sort by Price (high to low).
    sort.select_option("hilo")
    expect(sort).to_have_value("hilo")
    expect(names).to_have_text(PRICE_HIGH_TO_LOW)

    # Open the side menu and log out.
    page.get_by_role("button", name="Open Menu").click()
    expect(page.get_by_test_id("logout-sidebar-link")).to_be_visible()
    page.get_by_test_id("logout-sidebar-link").click()

    # Assertion: the user is returned to the login page.
    expect(page).to_have_url(re.compile(re.escape(base_url) + r"/?$"))
    expect(page.get_by_role("button", name="Login")).to_be_visible()
    expect(page.get_by_role("textbox", name="Username")).to_be_visible()
