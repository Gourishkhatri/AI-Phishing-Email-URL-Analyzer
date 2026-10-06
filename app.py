import os
import sys
import pandas as pd
import joblib
from flask import Flask, render_template, request, jsonify

# Ensure 'src' is in python path for importing url_feature_extractor
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


from url_feature_extractor import extract_features, FEATURE_NAMES

app = Flask(__name__, template_folder="templates", static_folder="static")

# Load trained Random Forest model
MODEL_PATH = os.path.join(BASE_DIR, "model", "url_only_random_forest.joblib")
model = None


def get_model():
    global model
    if model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
        model = joblib.load(MODEL_PATH)
    return model


def build_security_indicators(features: dict) -> list:
    """
    Construct user-facing security indicators from extracted features.
    """
    indicators = []

    # 1. HTTPS Enabled
    is_https = bool(features.get("IsHTTPS", 0))
    indicators.append({
        "id": "https",
        "name": "HTTPS Enabled",
        "value": "Enabled" if is_https else "Disabled (HTTP)",
        "status": "safe" if is_https else "warning",
        "description": "Secure SSL/TLS encryption detected on URL connection." if is_https else "Unencrypted HTTP protocol detected, potentially insecure."
    })

    # 2. IP Address Domain
    is_ip = bool(features.get("IsDomainIP", 0))
    indicators.append({
        "id": "ip_domain",
        "name": "IP Address Domain",
        "value": "IP Address Used" if is_ip else "Domain Name Used",
        "status": "danger" if is_ip else "safe",
        "description": "URL uses a raw IP address instead of a domain name." if is_ip else "URL uses a standard registered domain name."
    })

    # 3. URL Length
    url_len = features.get("URLLength", 0)
    if url_len > 75:
        len_status = "danger"
        len_desc = f"Excessively long URL ({url_len} chars), often used to conceal target destination."
    elif url_len > 54:
        len_status = "warning"
        len_desc = f"Moderately long URL ({url_len} chars)."
    else:
        len_status = "safe"
        len_desc = f"Standard concise URL length ({url_len} chars)."

    indicators.append({
        "id": "url_length",
        "name": "URL Length",
        "value": f"{url_len} Characters",
        "status": len_status,
        "description": len_desc
    })

    # 4. Subdomains
    sub_count = features.get("NoOfSubDomain", 0)
    if sub_count >= 3:
        sub_status = "danger"
        sub_desc = f"High subdomain count ({sub_count}), frequently used in deceptive domain spoofing."
    elif sub_count == 2:
        sub_status = "warning"
        sub_desc = f"Multiple subdomains ({sub_count}) present."
    else:
        sub_status = "safe"
        sub_desc = f"Normal subdomain count ({sub_count})."

    indicators.append({
        "id": "subdomains",
        "name": "Subdomain Count",
        "value": f"{sub_count} Subdomain(s)",
        "status": sub_status,
        "description": sub_desc
    })

    # 5. URL Obfuscation
    has_obf = bool(features.get("HasObfuscation", 0))
    obf_count = features.get("NoOfObfuscatedChar", 0)
    indicators.append({
        "id": "obfuscation",
        "name": "URL Obfuscation",
        "value": f"Detected ({obf_count} encoded chars)" if has_obf else "None Detected",
        "status": "danger" if has_obf else "safe",
        "description": f"URL contains percent-encoded hex sequences to hide suspicious strings." if has_obf else "No hex percent-encoding obfuscation detected."
    })

    # 6. Password Keyword
    has_pwd = bool(features.get("HasPasswordField", 0))
    indicators.append({
        "id": "password_keyword",
        "name": "Password-Related Keyword",
        "value": "Detected in URL" if has_pwd else "Not Present",
        "status": "warning" if has_pwd else "safe",
        "description": "URL contains credential harvesting keywords (e.g. 'password', 'passwd', 'pwd')." if has_pwd else "No password harvesting keywords found in URL path."
    })

    # 7. Bank Keyword
    has_bank = bool(features.get("Bank", 0))
    indicators.append({
        "id": "bank_keyword",
        "name": "Bank-Related Keyword",
        "value": "Detected in URL" if has_bank else "Not Present",
        "status": "warning" if has_bank else "safe",
        "description": "URL contains financial or banking keywords (e.g. 'bank', 'netbanking', 'account')." if has_bank else "No banking keywords found in URL."
    })

    # 8. Payment Keyword
    has_pay = bool(features.get("Pay", 0))
    indicators.append({
        "id": "payment_keyword",
        "name": "Payment-Related Keyword",
        "value": "Detected in URL" if has_pay else "Not Present",
        "status": "warning" if has_pay else "safe",
        "description": "URL contains payment terms (e.g. 'pay', 'checkout', 'billing')." if has_pay else "No payment processing keywords found in URL."
    })

    # 9. Crypto Keyword
    has_crypto = bool(features.get("Crypto", 0))
    indicators.append({
        "id": "crypto_keyword",
        "name": "Crypto-Related Keyword",
        "value": "Detected in URL" if has_crypto else "Not Present",
        "status": "warning" if has_crypto else "safe",
        "description": "URL contains cryptocurrency terms (e.g. 'bitcoin', 'crypto', 'wallet')." if has_crypto else "No cryptocurrency terms found in URL."
    })

    return indicators


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze_url_endpoint():
    try:
        data = request.get_json(silent=True) or {}
        url = data.get("url", "").strip()

        if not url:
            # Fallback for form-data if sent via standard web form
            url = request.form.get("url", "").strip()

        if not url:
            return jsonify({
                "error": "URL parameter is required."
            }), 400

        # Load ML model
        clf = get_model()

        # Extract features using existing feature extractor
        features = extract_features(url)

        # Prepare DataFrame input with exact feature ordering expected by model
        X = pd.DataFrame(
            [[features[name] for name in FEATURE_NAMES]],
            columns=FEATURE_NAMES
        )

        # Generate ML model predictions
        pred_class = clf.predict(X)[0]
        probabilities = clf.predict_proba(X)[0]

        class_probabilities = dict(zip(clf.classes_, probabilities))

        # Model mapping: 0 = PHISHING, 1 = LEGITIMATE
        phishing_prob = float(class_probabilities.get(0, 0.0))
        legitimate_prob = float(class_probabilities.get(1, 0.0))

        if pred_class == 0:
            prediction = "PHISHING"
            confidence = phishing_prob * 100.0
        else:
            prediction = "LEGITIMATE"
            confidence = legitimate_prob * 100.0

        # Determine Risk Level based on phishing probability
        if phishing_prob >= 0.75:
            risk = "HIGH"
        elif phishing_prob >= 0.40:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        # Build security indicators
        indicators = build_security_indicators(features)

        response_payload = {
            "prediction": prediction,
            "confidence": round(confidence, 2),
            "phishing_probability": round(phishing_prob * 100.0, 2),
            "legitimate_probability": round(legitimate_prob * 100.0, 2),
            "risk": risk,
            "indicators": indicators
        }

        return jsonify(response_payload), 200

    except Exception as e:
        app.logger.error(f"Error analyzing URL: {e}", exc_info=True)
        return jsonify({
            "error": f"An error occurred while processing the URL: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
