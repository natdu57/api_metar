from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

@app.route("/metar/<icao>", methods=["GET"])
def get_metar(icao):
    try:
        # Validate ICAO code (basic check for 4-letter code)
        if not isinstance(icao, str) or len(icao) != 4 or not icao.isalpha():
            return jsonify({"error": "Invalid ICAO code. Must be a 4-letter code."}), 400

        # Construct URL for the given ICAO code
        url = f"http://cunimb.net/decodemet.php?station={icao.upper()}"

        # Make request with User-Agent header to mimic browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)

        # Check if request was successful
        if response.status_code != 200:
            return jsonify({"error": f"Failed to fetch page: HTTP {response.status_code}"}), response.status_code

        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the table cell containing the raw METAR
        metar_cell = soup.find("th")
        if not metar_cell:
            return jsonify({"error": "Raw METAR data not found on the page. Check if the website structure has changed."}), 404

        # Extract the raw METAR text
        raw_metar = metar_cell.text.strip()

        # Verify that the METAR starts with the ICAO code
        if not raw_metar.startswith(icao.upper()):
            return jsonify({"error": "METAR data does not match the provided ICAO code."}), 404

        return jsonify({"icao": icao.upper(), "metar": raw_metar}), 200

    except requests.Timeout:
        return jsonify({"error": "Request timed out while fetching the page."}), 504
    except requests.ConnectionError:
        return jsonify({"error": "Failed to connect to the website."}), 503
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
