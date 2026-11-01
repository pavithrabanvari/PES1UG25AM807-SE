
"""Insurance premium calculator with safer input and file handling."""

import math
import os
import secrets
import tarfile
import urllib.request
from datetime import date, datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit

from defusedxml import ElementTree

BASE_RATES = {"health": 5000, "motor": 3000, "life": 8000}
LOG_FILE = Path("premium_quotes.log")
CLAIMS_DIRECTORY = Path("claims_docs")
quotes = {}


def calculate_premium(
    policy_type: str,
    age: int,
    sum_insured: float,
    smoker: bool,
    claims: int,
    discounts: Optional[list] = None,
) -> float:
    """Calculate a premium without sharing discount state across calls."""
    if policy_type not in BASE_RATES:
        raise ValueError("Unsupported policy type.")

    if discounts is None:
        discounts = []

    premium = BASE_RATES[policy_type] + sum_insured * 0.002

    if age > 45:
        premium *= 1.5

    if smoker:
        premium *= 1.3

    premium += claims * 1000

    for discount in discounts:
        premium -= discount

    return max(premium, 0)


def age_from_dob(dob: str) -> int:
    """Return completed years of age for a date in DD-MM-YYYY format."""
    birth_date = datetime.strptime(dob, "%d-%m-%Y").date()
    today = date.today()

    age = today.year - birth_date.year

    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    if age < 0:
        raise ValueError("Date of birth cannot be in the future.")

    return age


def policy_number() -> str:
    """Generate a hard-to-guess policy reference."""
    return f"POL-{secrets.randbelow(900000) + 100000}"


def save_quote(name: str, premium: float) -> str:
    """Save a quote in memory and append it to the quote log."""
    number = policy_number()
    quotes[number] = {"name": name, "premium": premium}

    with LOG_FILE.open("a", encoding="utf-8") as quote_file:
        quote_file.write(f"{number},{name},{premium:.2f}\n")

    return number


def import_policies(xml_text: str) -> list:
    """Parse policy records using an XML parser hardened against entities."""
    root = ElementTree.fromstring(xml_text)
    result = []

    for policy in root.findall("policy"):
        try:
            policy_type = policy.get("type")
            age = int(policy.get("age", ""))
            sum_insured = int(policy.get("sum", ""))

            if policy_type in BASE_RATES and age >= 0 and sum_insured >= 0:
                result.append((policy_type, age, sum_insured))

        except (TypeError, ValueError):
            continue

    return result


def fetch_rates(url: str) -> bytes:
    """Download rate data using HTTPS and verified TLS."""
    parsed_url = urlsplit(url)

    if parsed_url.scheme != "https" or not parsed_url.netloc:
        raise ValueError("Only valid HTTPS URLs are allowed.")

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "PremiumCalculator/1.0"},
    )

    with urllib.request.urlopen(
        request,
        timeout=10,
    ) as response:  # nosec B310
        return response.read()


def import_claim_documents(archive_path: str) -> None:
    """Extract an uploaded archive using tarfile's safe data filter."""
    CLAIMS_DIRECTORY.mkdir(parents=True, exist_ok=True)

    with tarfile.open(archive_path, "r:*") as archive:
        archive.extractall(path=CLAIMS_DIRECTORY, filter="data")


def monthly_instalment(premium: float, months: int = 12) -> float:
    """Return the rounded-down monthly instalment."""
    if months <= 0:
        raise ValueError("Months must be greater than zero.")

    return math.floor(premium / months)


def is_authorised(token: str) -> bool:
    """Compare a supplied token with one configured in the environment."""
    expected_token = os.environ.get("UNDERWRITER_TOKEN", "")

    return bool(expected_token) and secrets.compare_digest(
        token, expected_token
    )


def renewal_due(start: str, years: int = 1) -> str:
    """Calculate the renewal date, handling leap-day start dates."""
    start_date = datetime.strptime(start, "%Y-%m-%d").date()

    try:
        renewal_date = start_date.replace(year=start_date.year + years)

    except ValueError:
        renewal_date = start_date.replace(
            year=start_date.year + years,
            day=28,
        )

    return renewal_date.strftime("%Y-%m-%d")


def print_quotes() -> None:
    """Print all quotes currently held in memory."""
    print("===== Quote Book =====")

    for index, (number, quote) in enumerate(quotes.items(), start=1):
        print(
            index,
            number,
            quote["name"],
            "Rs.",
            quote["premium"],
        )


def main() -> None:
    """Run a small demonstration of the calculator."""
    premium_one = calculate_premium("health", 30, 500000, False, 0)
    premium_two = calculate_premium("health", 30, 500000, False, 0)
    motor_premium = calculate_premium("motor", 50, 800000, False, 0)

    life_premium = calculate_premium(
        "life", 25, 100000, False, 0, [3000, 3000, 3000]
    )

    print("Quote 1:", premium_one)
    print("Quote 2 (same customer details):", premium_two)
    print("Non-smoker aged 50:", motor_premium)
    print("Life with stacked discounts:", life_premium)
    print("Age from DOB 31-12-1990:", age_from_dob("31-12-1990"))
    print("Monthly instalment:", monthly_instalment(motor_premium))
    print("Renewal due:", renewal_due("2025-03-15"))

    sample_xml = (
        "<policies><policy type='health' age='40' sum='300000'/>"
        "<policy type='motor' age='abc' sum='1'/></policies>"
    )

    print("Imported:", import_policies(sample_xml))
    print("Saved as:", save_quote("Kiran", premium_one))

    token = os.environ.get("UNDERWRITER_TOKEN", "")
    print("Authorised:", is_authorised(token))

    print_quotes()


if __name__ == "__main__":
    main()
