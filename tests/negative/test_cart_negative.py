"""Negative cart scenarios: removing an item must clear it from the cart."""

import os
import re

from playwright.sync_api import Page, expect

# data-test ids for the Sauce Labs Bike Light add/remove buttons.
BIKE_LIGHT_ADD = "add-to-cart-sauce-labs-bike-light"
BIKE_LIGHT_REMOVE = "remove-sauce-labs-bike-light"


def test_removing_the_only_item_leaves_an_empty_cart(page: Page) -> None:
    # Log in with the configured credentials.
    page.goto("/")
    page.get_by_role("textbox", name="Username").fill(os.environ["SAUCEDEMO_USERNAME"])
    page.get_by_role("textbox", name="Password").fill(os.environ["SAUCEDEMO_PASSWORD"])
    page.get_by_role("button", name="Login").click()
    expect(page.locator('[data-test="title"]')).to_have_text("Products")

    # Add the Sauce Labs Bike Light, then open the cart.
    page.get_by_test_id(BIKE_LIGHT_ADD).click()
    page.get_by_role("button", name="Cart, 1 items").click()
    expect(page).to_have_url(re.compile(r"/cart\.html$"))
    expect(page.get_by_test_id(BIKE_LIGHT_REMOVE)).to_be_visible()

    # Remove the item from the cart.
    page.get_by_test_id(BIKE_LIGHT_REMOVE).click()

    # Negative checks: the line item and its Remove button are gone, cart is empty.
    expect(page.get_by_test_id(BIKE_LIGHT_REMOVE)).to_have_count(0)
    expect(page.locator('[data-test="inventory-item"]')).to_have_count(0)
    expect(page.get_by_role("button", name="Cart, empty")).to_be_visible()

    # Continue Shopping returns to the inventory with the item no longer added.
    page.get_by_role("button", name="Continue Shopping").click()
    expect(page).to_have_url(re.compile(r"/inventory\.html$"))
    expect(page.locator('[data-test="title"]')).to_have_text("Products")
    expect(page.get_by_test_id(BIKE_LIGHT_ADD)).to_be_visible()
    expect(page.get_by_test_id(BIKE_LIGHT_REMOVE)).to_have_count(0)
