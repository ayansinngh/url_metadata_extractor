"""Flask app: a web page plus a small JSON API for the metadata extractor."""

import requests
from flask import Flask, jsonify, render_template, request

from utils.metadata import extract_metadata, is_valid_url, normalize_url

app = Flask(__name__)


def get_metadata_or_error(url_input):
    """Validate the input and fetch metadata.

    Returns (metadata, error_message, http_status). On success the error
    is None; on failure metadata is None. Both routes below share this,
    so the error handling lives in one place.
    """
    if not url_input:
        return None, "Please enter a URL.", 400

    url = normalize_url(url_input)
    if not is_valid_url(url):
        return None, "Please enter a valid URL, for example https://example.com", 400

    try:
        return extract_metadata(url), None, 200

    except requests.exceptions.Timeout:
        return None, "The website took too long to respond.", 504

    except requests.exceptions.ConnectionError:
        return None, "Could not connect to the website.", 502

    except requests.exceptions.HTTPError as e:
        # A Response object is falsy for 4xx/5xx codes, so we must compare
        # with None instead of writing "if e.response:".
        if e.response is not None:
            return None, f"The website returned an error ({e.response.status_code}).", 502
        return None, "The website returned an error.", 502

    except requests.exceptions.RequestException:
        return None, "There was a problem while fetching the website.", 502

    except ValueError as e:
        return None, str(e), 400

    except Exception:
        # Log the details for you, but don't show internals to the user.
        app.logger.exception("Unexpected error while extracting metadata")
        return None, "Something went wrong on our side. Please try again.", 500


@app.route("/", methods=["GET", "POST"])
def index():
    metadata = None
    error = None
    url_input = ""

    if request.method == "POST":
        url_input = request.form.get("url", "").strip()
        metadata, error, _status = get_metadata_or_error(url_input)

    return render_template("index.html", metadata=metadata, error=error, url_input=url_input)


@app.route("/api/metadata", methods=["GET"])
def api_metadata():
    """Example: /api/metadata?url=https://example.com"""
    url_input = request.args.get("url", "").strip()
    metadata, error, status = get_metadata_or_error(url_input)

    if error:
        return jsonify({"error": error}), status
    return jsonify(metadata)


if __name__ == "__main__":
    # 127.0.0.1 keeps the app reachable only from your own computer.
    # Never combine host="0.0.0.0" with debug=True: the debugger lets anyone
    # on your network run Python code on your machine.
    app.run(host="127.0.0.1", port=5000, debug=True)