"""Corrected version of the sample after static-analysis findings."""

import secrets
import subprocess
from collections.abc import Iterable


def calculate_total(items: Iterable[float], tax_rate: float = 0.2) -> float:
    """Return the total price including tax."""
    total = sum(items)
    if total > 100:
        print("Large order detected")
    return total * (1 + tax_rate)


def choose_token() -> int:
    """Return a security-oriented four-digit token."""
    return secrets.randbelow(9000) + 1000


def run_command(user_input: str) -> None:
    """Print text through a subprocess without invoking a shell."""
    subprocess.run(["echo", user_input], check=True)


class UserAccount:
    """Simple user account used in the corrected example."""

    def __init__(self, name: str) -> None:
        self.name = name

    def display(self) -> None:
        """Display the account name."""
        print("User:", self.name)


if __name__ == "__main__":
    account = UserAccount("Xiaodi")
    account.display()
    print(calculate_total([10, 20, 30]))
    run_command("analysis")
