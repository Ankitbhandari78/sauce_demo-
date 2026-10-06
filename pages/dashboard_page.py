"""Page Object Model for the SauceDemo inventory (dashboard) page."""

from playwright.sync_api import Locator, Page, expect


class DashboardPage:
    """Encapsulates the locators and actions for the SauceDemo dashboard.

    Relies on ``conftest.py`` mapping ``data-test`` to Playwright's test id
    attribute, so ``get_by_test_id()`` resolves SauceDemo's stable hooks.
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        self.page_title: Locator = page.get_by_test_id("title")
        self.sort_dropdown: Locator = page.get_by_role("combobox", name="Sort products")
        self.inventory_items: Locator = page.get_by_test_id("inventory-item")
        self.product_names: Locator = page.get_by_test_id("inventory-item-name")
        self.product_prices: Locator = page.get_by_test_id("inventory-item-price")
        self.cart_link: Locator = page.get_by_test_id("shopping-cart-link")
        self.cart_badge: Locator = page.get_by_test_id("shopping-cart-badge")

    def goto(self) -> None:
        """Navigate to the dashboard (resolved against the configured base URL)."""
        self.page.goto("/inventory.html")

    def is_dashboard_loaded(self) -> bool:
        """Return True once the "Products" title is visible."""
        try:
            expect(self.page_title).to_be_visible()
            expect(self.page_title).to_have_text("Products")
        except AssertionError:
            return False
        return True

    def get_product_names(self) -> list[str]:
        """Return the name of every product currently rendered."""
        return self.product_names.all_text_contents()

    def get_product_prices(self) -> list[float]:
        """Return every product price as a float, e.g. "$29.99" -> 29.99."""
        return [
            float(raw.strip().replace("$", "").replace(",", ""))
            for raw in self.product_prices.all_text_contents()
        ]

    def get_cart_badge_count(self) -> int:
        """Return the number on the cart badge, or 0 while it is hidden."""
        if not self.cart_badge.is_visible():
            return 0
        return int(self.cart_badge.text_content() or 0)

    def sort_by(self, option: str) -> None:
        """Select a sort option by value: az, za, lohi or hilo."""
        self.sort_dropdown.select_option(option)
        expect(self.sort_dropdown).to_have_value(option)

    def add_product_to_cart(self, name: str) -> None:
        """Click Add to cart on the product row matching ``name``."""
        item = self.inventory_items.filter(has_text=name)
        item.get_by_role("button", name="Add to cart").click()

    def go_to_cart(self) -> None:
        """Click the cart link to open the cart page."""
        self.cart_link.click()