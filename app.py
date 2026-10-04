
"""Flask web app and JSON API for the URL Metadata Extractor."""

import requests
from flask import Flask, jsonify, render_template, request

from utils.metadata import extract_metadata, is_valid_url, normalize_url

app = Flask(__name__)


def get_metadata_or_error(url_input):
    """Validate a URL and extract its metadata.

    Returns:
        (metadata, error_message, http_status)
    """
    if not url_input:
        return None, "Please enter a URL.", 400

    # Prevent unnecessarily large input.
    if len(url_input) > 2048:
        return None, "URL is too long.", 400

    url = normalize_url(url_input)

    if not is_valid_url(url):
        return (
            None,
            "Please enter a valid URL, for example https://example.com",
            400,
        )

    try:
        metadata = extract_metadata(url)
        return metadata, None, 200

    except requests.exceptions.Timeout:
        return None, "The website took too long to respond.", 504

    except requests.exceptions.ConnectionError:
        return None, "Could not connect to the website.", 502

    except requests.exceptions.HTTPError as error:
        if error.response is not None:
            status_code = error.response.status_code
            return (
                None,
                f"The website returned an error ({status_code}).",
                502,
            )

        return None, "The website returned an error.", 502

    except requests.exceptions.RequestException:
        return (
            None,
            "There was a problem while fetching the website.",
            502,
        )

    except ValueError as error:
        return None, str(error), 400

    except Exception:
        # Keep technical details in the Flask logs instead of
        # exposing them to users.
        app.logger.exception("Unexpected error while extracting metadata")

        return (
            None,
            "Something went wrong on our side. Please try again.",
            500,
        )


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the main webpage and handle URL submissions."""
    metadata = None
    error = None
    url_input = ""

    if request.method == "POST":
        url_input = request.form.get("url", "").strip()

        metadata, error, _ = get_metadata_or_error(url_input)

    return render_template(
        "index.html",
        metadata=metadata,
        error=error,
        url_input=url_input,
    )


@app.route("/api/metadata", methods=["GET"])
def api_metadata():
    """Return metadata as JSON.

    Example:
        /api/metadata?url=https://example.com
    """
    url_input = request.args.get("url", "").strip()

    metadata, error, status = get_metadata_or_error(url_input)

    if error:
        return jsonify({"error": error}), status

    return jsonify(metadata)


@app.route("/health", methods=["GET"])
def health():
    """Simple endpoint to check if the server is running."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Local development only.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
