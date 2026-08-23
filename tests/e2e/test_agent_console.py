import os
import shutil

import pytest
from playwright.sync_api import sync_playwright


pytestmark = pytest.mark.e2e


@pytest.mark.skipif(os.getenv("RUN_E2E") != "1", reason="Set RUN_E2E=1 to run browser tests")
def test_cancelled_booking_shows_full_refund_suggestion():
    system_chromium = shutil.which("chromium") or shutil.which("google-chrome")
    launch_kwargs = {"headless": True}
    if system_chromium:
        launch_kwargs["executable_path"] = system_chromium

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**launch_kwargs)
        page = browser.new_page()
        page.goto("http://127.0.0.1:8000")
        page.get_by_role("button", name="Review case").click()

        page.get_by_text('"status": "cancelled_by_property"').wait_for()
        page.get_by_text('"action": "refund_full"').wait_for()
        browser.close()
