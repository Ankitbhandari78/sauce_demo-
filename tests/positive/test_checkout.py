"""End-to-end purchase flow: add to cart, checkout and confirm the order."""

import os
import re

import pytest
from playwright.sync_api import Page, expect

COMPLETE_MESSAGE = (
    "Your order has been dispatched, and will arrive just as fast as the pony can get there!"
)


@pytest.mark.smoke
def test_can_complete_a_purchase_and_return_to_products(page: Page) -> None:
    # Log in with the configured SauceDemo user.
    page.goto("/")
    page.get_by_role("textbox", name="Username").fill(os.environ["SAUCEDEMO_USERNAME"])
    page.get_by_role("textbox", name="Password").fill(os.environ["SAUCEDEMO_PASSWORD"])
    page.get_by_role("button", name="Login").click()
    expect(page.locator('[data-test="title"]')).to_have_text("Products")

    # Add the first product to the cart; the header button reflects the item count.
    page.get_by_role("button", name="Add to cart").first.click()
    page.get_by_role("button", name="Cart, 1 items").click()
    expect(page).to_have_url(re.compile(r"/cart\.html$"))

    # Proceed to checkout and provide the required information.
    page.get_by_role("button", name="Checkout").click()
    page.get_by_role("textbox", name="First Name").fill("John")
    page.get_by_role("textbox", name="Last Name").fill("Doe")
    page.get_by_role("textbox", name="Zip/Postal Code").fill("12345")
    page.get_by_role("button", name="Continue").click()

    # Order overview lists the selected item before finishing.
    expect(page).to_have_url(re.compile(r"/checkout-step-two\.html$"))
    expect(page.locator('[data-test="item-quantity"]')).to_have_text("1")
    expect(page.locator('[data-test="inventory-item-name"]')).to_be_visible()

    # Finish the purchase and confirm the success message.
    page.get_by_role("button", name="Finish").click()
    expect(page).to_have_url(re.compile(r"/checkout-complete\.html$"))
    expect(page.get_by_role("heading", name="Thank you for your order!")).to_be_visible()
    expect(page.locator('[data-test="complete-text"]')).to_contain_text(COMPLETE_MESSAGE)

    # Returning home lands back on the (now empty) inventory.
    page.get_by_role("button", name="Back Home").click()
    expect(page).to_have_url(re.compile(r"/inventory\.html$"))
    expect(page.get_by_role("button", name="Cart, empty")).to_be_visible()
