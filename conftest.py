"""Shared pytest configuration, fixtures and hooks for the Playwright framework."""

import os
import re
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, Playwright, expect

# --- Environment -----------------------------------------------------------
# Load credentials/config from the project root .env file.
_HERE = Path(__file__).resolve().parent
load_dotenv(_HERE / ".env")

DEFAULT_BASE_URL = "https://www.saucedemo.com"

# Default timeouts in milliseconds.
EXPECT_TIMEOUT_MS = 5_000
ACTION_TIMEOUT_MS = 10_000
NAVIGATION_TIMEOUT_MS = 30_000
expect.set_options(timeout=EXPECT_TIMEOUT_MS)

SCREENSHOTS_DIR = _HERE / "screenshots"


# --- Fixtures --------------------------------------------------------------
@pytest.fixture(scope="session")
def base_url() -> str:
    """Override the pytest-base-url fixture with the env-driven base URL."""
    return os.getenv("BASE_URL", DEFAULT_BASE_URL)


@pytest.fixture(scope="session", autouse=True)
def _sauce_demo_test_id_attribute(playwright: Playwright) -> None:
    """Treat the site's `data-test` attribute as the test id for get_by_test_id()."""
    playwright.selectors.set_test_id_attribute("data-test")


@pytest.fixture(autouse=True)
def _playwright_timeouts(page: Page) -> None:
    """Apply the default action and navigation timeouts to every page."""
    page.set_default_timeout(ACTION_TIMEOUT_MS)
    page.set_default_navigation_timeout(NAVIGATION_TIMEOUT_MS)


# --- Automatic post-test screenshot ----------------------------------------
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """Expose the call-phase report on the item so fixtures can read the status."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def screenshot_after_test(request, page: Page) -> None:
    """Capture a full-page screenshot after every test, named by node id + status."""
    yield

    report = getattr(request.node, "rep_call", None)
    status = report.outcome if report is not None else "unknown"

    raw_name = request.node.nodeid.replace("::", "-").replace("/", "-")
    safe_name = re.sub(r"[^a-zA-Z0-9-_]+", "-", raw_name).lower()
    screenshot_path = SCREENSHOTS_DIR / f"{safe_name}-{status}.png"

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        if not page.is_closed():
            page.screenshot(path=str(screenshot_path), full_page=True)
    except Exception:  # pragma: no cover - never let a screenshot mask the result
        pass
