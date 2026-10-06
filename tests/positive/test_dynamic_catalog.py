"""Positive Dynamic Catalog scenarios: lazy load, spinner and slider."""

import os
import re

import pytest
from playwright.sync_api import Page, expect

LAZY_LOAD_URL = re.compile(r"/dynamic-catalog-lazy-load\.html$")
SPINNER_URL = re.compile(r"/dynamic-catalog-spinner\.html$")
SLIDER_URL = re.compile(r"/dynamic-catalog-slider\.html$")


def _login_and_open_dynamic_catalog(page: Page, submenu_item: str) -> None:
    """Log in, open the side menu and expand Dynamic Catalog -> submenu_item."""
    page.goto("/")
    page.get_by_role("textbox", name="Username").fill(os.environ["SAUCEDEMO_USERNAME"])
    page.get_by_role("textbox", name="Password").fill(os.environ["SAUCEDEMO_PASSWORD"])
    page.get_by_role("button", name="Login").click()
    page.get_by_role("button", name="Open Menu").click()
    page.get_by_role("button", name="Dynamic Catalog").click()
    page.get_by_role("button", name=submenu_item).click()


@pytest.mark.smoke
def test_lazy_load_renders_products_as_the_page_scrolls(page: Page) -> None:
    _login_and_open_dynamic_catalog(page, "Lazy Load")

    expect(page).to_have_url(LAZY_LOAD_URL)
    expect(page.get_by_test_id("title")).to_have_text("Dynamic Catalog - Lazy Load")

    # Items below the fold stay deferred: 8 rendered, 4 still placeholders.
    # Several placeholders match, so assert the count (to_have_count accepts
    # many elements; to_be_visible() would raise a strict-mode violation).
    loading = page.get_by_text("Loading…")
    expect(loading).to_have_count(4)

    # No single test-id covers the whole collection, so a stable data-test
    # attribute suffix is used as the last-resort locator (priority 8).
    names = page.locator('[data-test$="-name"]')
    expect(names).to_have_count(8)

    # Scrolling to the bottom fetches the next batch -> the count must grow.
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    expect(names).not_to_have_count(8)


@pytest.mark.smoke
def test_spinner_shows_while_the_catalog_loads(page: Page) -> None:
    _login_and_open_dynamic_catalog(page, "Spinner")

    # Assert the spinner first, while it is still on screen.
    spinner = page.get_by_test_id("dynamic-catalog-spinner")
    expect(spinner).to_be_visible()

    # It is a real animation, not a static box.
    animation_name = spinner.evaluate("el => getComputedStyle(el).animationName")
    assert animation_name != "none", "spinner is not animating"

    expect(page).to_have_url(SPINNER_URL)
    expect(page.get_by_test_id("title")).to_have_text("Dynamic Catalog - Spinner")

    # The spinner completes and the loaded grid replaces it.
    expect(spinner).to_be_hidden()
    expect(page.get_by_test_id("dynamic-catalog-spinner-grid")).to_be_visible()
    expect(page.get_by_text("Sauce Labs Bike Light")).to_be_visible()


@pytest.mark.smoke
def test_slider_dots_change_the_active_product(page: Page) -> None:
    _login_and_open_dynamic_catalog(page, "Slider")

    expect(page).to_have_url(SLIDER_URL)
    expect(page.get_by_test_id("title")).to_have_text("Dynamic Catalog - Slider")
    expect(page.get_by_test_id("dynamic-catalog-slider-dots")).to_be_visible()
    expect(page.get_by_role("button", name="Show Sauce Labs Bike Light")).to_be_visible()

    # NOTE: the carousel auto-advances every ~2s; each click is asserted at
    # once so the assertion lands inside the current slide's window.
    active = page.get_by_test_id("dynamic-catalog-slider-item-name")

    page.get_by_role("button", name="Show Sauce Labs Fleece Jacket").click()
    expect(active).to_have_text("Sauce Labs Fleece Jacket")

    page.get_by_role("button", name="Show Sauce Labs Onesie").click()
    expect(active).to_have_text("Sauce Labs Onesie")