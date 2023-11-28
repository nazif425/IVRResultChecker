from flask import Flask
from database.models import setup_db
from database.serializers import setup_serializers
from urls.api import api_urls
from urls.ivr import ivr_urls



# Global data
ses_data = {
    "validated" : False,
    "session_id" : "",
    "student_number" : "",
    "first_name" : "",
    "last_name" : "",
    "data": {},
}

# def create_app(test_config=None):
#Setup FLASK App
app = Flask(__name__)
app.secret_key = '6ad471762c7ff5d00015269cf9cca9c7'
setup_db(app)
setup_serializers(app)
api_urls(app, ses_data)
ivr_urls(app, ses_data)


"""
# OPENMRS
OPENMRS_BASE_URL = 'http://127.0.0.1:8081/openmrs'
OPENMRS_FHIR_VERSION = 'R4'
OPENMRS_FHIR_API = f'{OPENMRS_BASE_URL}/ws/fhir2/{OPENMRS_FHIR_VERSION}/'
bearer_token = 'Basic YWRtaW46QWRtaW4xMjM='
"""
if __name__ == '__main__':
    app.run(debug=True)
