import re
from urllib.parse import urlparse


FEATURE_NAMES = [
    "URLLength",
    "DomainLength",
    "IsDomainIP",
    "TLDLength",
    "NoOfSubDomain",
    "HasObfuscation",
    "NoOfObfuscatedChar",
    "ObfuscationRatio",
    "NoOfLettersInURL",
    "LetterRatioInURL",
    "NoOfDegitsInURL",
    "DegitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL",
    "IsHTTPS",
    "HasPasswordField",
    "Bank",
    "Pay",
    "Crypto",
]


def extract_url_features(url: str):

    if not url:
        raise ValueError("URL cannot be empty")

    url = url.strip()

    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "https://" + url

    parsed = urlparse(url)
    hostname = parsed.hostname or ""

    # -------------------------
    # Basic features
    # -------------------------

    url_length = len(url)
    domain_length = len(hostname)

    is_domain_ip = int(
        bool(
            re.fullmatch(
                r"(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})"
                r"(\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})){3}",
                hostname,
            )
        )
    )

    domain_parts = hostname.split(".") if hostname else []

    no_of_subdomain = max(
        len(domain_parts) - 2,
        0
    )

    tld = (
        domain_parts[-1]
        if len(domain_parts) >= 2
        else ""
    )

    tld_length = len(tld)

    # -------------------------
    # Character features
    # -------------------------

    no_of_letters = len(
        re.findall(r"[A-Za-z]", url)
    )

    no_of_digits = len(
        re.findall(r"\d", url)
    )

    letter_ratio = (
        no_of_letters / url_length
        if url_length
        else 0
    )

    digit_ratio = (
        no_of_digits / url_length
        if url_length
        else 0
    )

    # -------------------------
    # URL structure
    # -------------------------

    no_of_equals = url.count("=")
    no_of_qmark = url.count("?")
    no_of_ampersand = url.count("&")

    # -------------------------
    # Obfuscation
    # -------------------------

    encoded_chars = re.findall(
        r"%[0-9A-Fa-f]{2}",
        url
    )

    has_obfuscation = int(
        len(encoded_chars) > 0
    )

    no_of_obfuscated_char = len(
        encoded_chars
    )

    obfuscation_ratio = (
        no_of_obfuscated_char / url_length
        if url_length
        else 0
    )

    # -------------------------
    # Other special characters
    # -------------------------

    structural_chars = set(
        ":/?&=._#%-"
    )

    no_of_other_special_chars = sum(
        1
        for char in url
        if (
            not char.isalnum()
            and char not in structural_chars
        )
    )

    # IMPORTANT:
    # Keep this feature for compatibility
    # with the already-trained model.
    #
    # This is only a temporary calculation.
    # We will validate the exact dataset
    # formula before final model training.

    special_ratio = (
        no_of_other_special_chars / url_length
        if url_length
        else 0
    )

    # -------------------------
    # HTTPS
    # -------------------------

    is_https = int(
        parsed.scheme.lower() == "https"
    )

    lower_url = url.lower()

    # -------------------------
    # Password
    # -------------------------

    has_password_field = int(
        any(
            word in lower_url
            for word in [
                "password",
                "passwd",
                "pwd",
            ]
        )
    )

    # -------------------------
    # Bank
    # -------------------------

    bank = int(
        any(
            word in lower_url
            for word in [
                "bank",
                "banking",
                "netbanking",
                "account",
            ]
        )
    )

    # -------------------------
    # Payment
    # -------------------------

    pay = int(
        any(
            word in lower_url
            for word in [
                "pay",
                "payment",
                "checkout",
                "billing",
            ]
        )
    )

    # -------------------------
    # Crypto
    # -------------------------

    crypto = int(
        any(
            word in lower_url
            for word in [
                "bitcoin",
                "crypto",
                "wallet",
                "ethereum",
            ]
        )
    )

    # -------------------------
    # Final features
    # -------------------------

    features = {
        "URLLength": url_length,
        "DomainLength": domain_length,
        "IsDomainIP": is_domain_ip,
        "TLDLength": tld_length,
        "NoOfSubDomain": no_of_subdomain,
        "HasObfuscation": has_obfuscation,
        "NoOfObfuscatedChar": no_of_obfuscated_char,
        "ObfuscationRatio": obfuscation_ratio,
        "NoOfLettersInURL": no_of_letters,
        "LetterRatioInURL": letter_ratio,
        "NoOfDegitsInURL": no_of_digits,
        "DegitRatioInURL": digit_ratio,
        "NoOfEqualsInURL": no_of_equals,
        "NoOfQMarkInURL": no_of_qmark,
        "NoOfAmpersandInURL": no_of_ampersand,
        "NoOfOtherSpecialCharsInURL": no_of_other_special_chars,
        "SpacialCharRatioInURL": special_ratio,
        "IsHTTPS": is_https,
        "HasPasswordField": has_password_field,
        "Bank": bank,
        "Pay": pay,
        "Crypto": crypto,
    }

    return features


def extract_features(url: str):
    return extract_url_features(url)