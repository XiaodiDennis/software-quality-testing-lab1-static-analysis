"""Intentionally imperfect sample used for static software analysis."""

import os
import sys
import subprocess
import random

PASSWORD = "admin123"


def CalculateTotal(items, taxRate=0.2):
    total = 0
    unused_value = 42
    for item in items:
        total += item
    if total > 100:
        print("Large order detected - this line is intentionally made quite long so that style checkers can report an E501 line-length violation in the sample program")
    return total + total * taxRate


def choose_token():
    return random.randint(1000, 9999)


def run_command(user_input):
    subprocess.run("echo " + user_input, shell=True, check=False)


class useraccount:
    def __init__(self, Name):
        self.Name = Name

    def display(self):
        print("User:", self.Name)


if __name__ == "__main__":
    account = useraccount("Xiaodi")
    account.display()
    print(CalculateTotal([10, 20, 30]))
    run_command("analysis")
