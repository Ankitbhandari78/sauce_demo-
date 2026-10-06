"""Negative checkout scenario: omitting the postal code blocks progress."""

import os
import re

from playwright.sync_api import Page, expect

# data-test id for the Sauce Labs Fleece Jacket add-to-cart button.
FLEECE_JACKET_ADD = "add-to-cart-sauce-labs-fleece-jacket"


def test_checkout_without_postal_code_shows_error_and_blocks_progress(
    page: Page,
) -> None:
    # Log in with the configured SauceDemo user.
    page.goto("/")
    page.get_by_role("textbox", name="Username").fill(os.environ["SAUCEDEMO_USERNAME"])
    page.get_by_role("textbox", name="Password").fill(os.environ["SAUCEDEMO_PASSWORD"])
    page.get_by_role("button", name="Login").click()

    # Add the Sauce Labs Fleece Jacket, then open the cart.
    page.get_by_test_id(FLEECE_JACKET_ADD).click()
    page.get_by_role("button", name="Cart, 1 items").click()
    expect(page).to_have_url(re.compile(r"/cart\.html$"))

    # Proceed to checkout; the information form is shown.
    page.get_by_role("button", name="Checkout").click()
    expect(page).to_have_url(re.compile(r"/checkout-step-one\.html$"))

    # Fill first and last name only -- leave Zip/Postal Code empty.
    page.get_by_role("textbox", name="First Name").fill("John")
    page.get_by_role("textbox", name="Last Name").fill("Doe")
    page.get_by_role("button", name="Continue").click()

    # The user cannot continue: checkout stays on step one ...
    expect(page).to_have_url(re.compile(r"/checkout-step-one\.html$"))

    # ... and the postal-code error appears in the styled error container.
    expect(page.locator("div.error-message-container.error")).to_be_visible()
    expect(page.get_by_test_id("error")).to_contain_text(
        "Error: Postal Code is required"
    )

    # The error container exposes a dismiss error button.
    expect(page.get_by_test_id("error-button")).to_be_visible()

    # The cart still holds the jacket -- shopping cannot move forward.
    expect(page.get_by_role("button", name="Cart, 1 items")).to_be_visible()
