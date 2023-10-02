from core import LinkedinScaper
from core import PDFGenerator
import json
import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

app = Flask(__name__, template_folder='.')
CORS(app)
# todo: move scraper init above function to avoid multiple browser instances & improve speed
@app.route("/scrape/<linkedin_handle>", methods=["GET"])
def scrape_person_data(linkedin_handle: str):
    # init scraper
    liscraper = LinkedinScaper()
    # read userdata from json
    with open("userdata.json", "r") as userdata:
        userdata = json.load(userdata)
    # login
    liscraper.login(userdata[3]["email"], userdata[3]["password"])
    person_data = liscraper.scrape_person(linkedin_handle)
    if person_data:
        return jsonify(person_data)  # Return the JSON-serializable dictionary
    else:
        return jsonify([])

@app.route("/generate/<linkedin_handle>", methods=["POST"])  # Change the method to POST
def generate_pdf(linkedin_handle: str):
    try:
        person_data = request.get_json()  # Get JSON data from the request body
        if person_data:
            pdf_generator = PDFGenerator()
            filename = f"{linkedin_handle}.pdf"
            pdf_generator.generate_pdf(person_data, filename)

            # Serve the file
            response = send_file(filename, as_attachment=True)

            # Cleanup: Delete the file after sending
            os.remove(filename)

            return response
        else:
            return "Invalid JSON data in the request body", 400
    except Exception as e:
        return str(e), 500  # Handle any exceptions that may occur during PDF generation

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
