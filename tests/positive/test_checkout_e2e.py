"""Exercise a four-item Sauce Demo purchase through order confirmation."""

import random
import re

import pytest
from playwright.sync_api import Page, expect


def parse_price(text: str) -> float:
    """Convert a displayed currency string to a numeric price."""
    numeric_text = re.sub(r"[$,\s]", "", text)
    match = re.search(r"-?\d+(?:\.\d+)?", numeric_text)
    if match is None:
        raise ValueError(f"No price found in {text!r}")
    return round(float(match.group()), 2)


@pytest.mark.smoke
def test_checkout_e2e(page: Page) -> None:
    def wait_for_step() -> None:
        page.wait_for_timeout(1_000)

    page.goto("https://www.saucedemo.com")
    wait_for_step()
    page.get_by_placeholder("Username").fill("standard_user")
    wait_for_step()
    page.get_by_placeholder("Password").fill("secret_sauce")
    wait_for_step()
    page.get_by_role("button", name="Login").click()
    wait_for_step()

    products_heading = page.get_by_text("Products", exact=True)
    expect(
        products_heading,
        f"Expected Products page text to be visible; actual matching elements: {products_heading.count()}",
    ).to_be_visible()
    wait_for_step()

    cart_badge = page.get_by_test_id("shopping-cart-badge")
    add_to_cart_test_ids = [
        "add-to-cart-sauce-labs-backpack",
        "add-to-cart-sauce-labs-bike-light",
        "add-to-cart-sauce-labs-bolt-t-shirt",
        "add-to-cart-sauce-labs-fleece-jacket",
    ]
    for expected_count, test_id in enumerate(add_to_cart_test_ids, start=1):
        page.get_by_test_id(test_id).click()
        wait_for_step()
        expect(
            cart_badge,
            f"Expected cart badge {expected_count}; actual badge text: {cart_badge.inner_text()!r}",
        ).to_have_text(str(expected_count))
        wait_for_step()

    page.get_by_test_id("shopping-cart-link").click()
    wait_for_step()
    cart_items = page.get_by_test_id("inventory-item-name")
    expect(
        cart_items,
        f"Expected 4 items in cart; actual item count: {cart_items.count()}",
    ).to_have_count(4)
    wait_for_step()
    page.get_by_role("button", name="Checkout").click()
    wait_for_step()

    information_heading = page.get_by_text("Checkout: Your Information", exact=True)
    expect(
        information_heading,
        "Expected 'Checkout: Your Information' to be visible; "
        f"actual matching elements: {information_heading.count()}",
    ).to_be_visible()
    wait_for_step()
    page.get_by_test_id("firstName").fill(
        random.choice(["Aadmi", "bander", "Johnny", "sins", "sunny"])
    )
    wait_for_step()
    page.get_by_test_id("lastName").fill(
        random.choice(["johnny_s", "leonee", "Gunda", "takla", "tickola"])
    )
    wait_for_step()
    page.get_by_test_id("postalCode").fill(str(random.randint(42090, 92087)))
    wait_for_step()
    page.get_by_test_id("continue").click()
    wait_for_step()

    overview_heading = page.get_by_text("Checkout: Overview", exact=True)
    expect(
        overview_heading,
        "Expected 'Checkout: Overview' to be visible; "
        f"actual matching elements: {overview_heading.count()}",
    ).to_be_visible()
    wait_for_step()

    item_price_texts = page.get_by_test_id("inventory-item-price").all_text_contents()
    item_prices = [parse_price(text) for text in item_price_texts]
    assert len(item_prices) == 4, (
        f"Expected 4 item prices; actual count: {len(item_prices)} "
        f"(prices: {item_prices!r})"
    )
    wait_for_step()

    item_total_locator = page.get_by_test_id("subtotal-label")
    tax_locator = page.get_by_test_id("tax-label")
    grand_total_locator = page.get_by_test_id("total-label")
    item_total_page = parse_price(item_total_locator.inner_text())
    tax_page = parse_price(tax_locator.inner_text())
    grand_total_page = parse_price(grand_total_locator.inner_text())

    expected_item_total = round(sum(item_prices), 2)
    assert item_total_page == expected_item_total, (
        f"Expected item total {expected_item_total}; actual: {item_total_page}"
    )
    wait_for_step()
    expected_grand_total = round(item_total_page + tax_page, 2)
    assert grand_total_page == expected_grand_total, (
        f"Expected grand total {expected_grand_total}; actual: {grand_total_page}"
    )
    wait_for_step()

    page.get_by_role("button", name="Finish").click()
    wait_for_step()
    complete_heading = page.get_by_text("Checkout: Complete!", exact=True)
    expect(
        complete_heading,
        "Expected 'Checkout: Complete!' to be visible; "
        f"actual matching elements: {complete_heading.count()}",
    ).to_be_visible()
    wait_for_step()
    confirmation_text = page.get_by_text(
        "Your order has been dispatched, and will arrive just as fast as the pony can get there!",
        exact=True,
    )
    expect(
        confirmation_text,
        "Expected the exact order-dispatched confirmation text to be visible; "
        f"actual text: {confirmation_text.all_text_contents()!r}",
    ).to_be_visible()
    wait_for_step()
