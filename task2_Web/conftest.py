"""
Pytest conftest for Playwright browser configuration.
This file is automatically discovered by pytest-playwright
and allows custom browser launch options.
"""
import pytest


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """
    Customize browser launch arguments.
    - slow_mo: adds a small delay between actions for stability and visibility.
    """
    return {
        **browser_type_launch_args,
        "slow_mo": 100,  # ms delay between each Playwright action
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """
    Customize browser context arguments.
    - viewport: sets a standard desktop viewport size.
    - ignore_https_errors: prevents failures on HTTPS certificate issues.
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }
