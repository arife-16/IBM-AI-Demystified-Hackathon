import os
import uuid
from flask import Flask, request, jsonify
from ibmcloudant.cloudant_v1 import CloudantV1, Document
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION (Load from Environment) ---
# You set these in the Code Engine Dashboard, NOT in the code.
API_KEY = os.getenv("CLOUDANT_API_KEY")
URL = os.getenv("CLOUDANT_URL")

# --- INITIALIZATION ---
if API_KEY and URL:
    authenticator = IAMAuthenticator(API_KEY)
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url(URL)
else:
    print("WARNING: Cloudant credentials not found in environment.")
    service = None

DB_NAME = 'reservations'

# --- ROUTES ---

@app.route('/check-availability', methods=['GET'])
def check_availability():
    resource_id = request.args.get('resource_id')
    req_end = request.args.get('end_time') # Expecting ISO format
    req_start = request.args.get('start_time')

    if not all([resource_id, req_end, req_start]):
        return jsonify({"error": "Missing parameters"}), 400
        
    if not service:
        return jsonify({"error": "Database not configured"}), 500

    try:
        # STEP 1: Cloudant Selector (Filter future bookings)
        selector = {
            "resource_id": resource_id,
            "type": "booking",
            "status": "active",
            "start_time": { "$lt": req_end }
        }
        
        response = service.post_find(
            db=DB_NAME, # Ensure this DB exists!
            selector=selector,
            fields=["user_id", "start_time", "end_time", "project_priority"]
        ).get_result()

        # STEP 2: Precision Filter (Python Logic)
        conflicts = []
        for booking in response['docs']:
            if booking['end_time'] > req_start:
                conflicts.append(booking)

        if not conflicts:
            return jsonify({"status": "available", "message": "Slot is open."})
        
        return jsonify({
            "status": "conflict",
            "blocking_booking": {
                "user": conflicts[0].get('user_id'),
                "priority": conflicts[0].get('project_priority'),
                "end_time": conflicts[0].get('end_time')
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/book-slot', methods=['POST'])
def book_slot():
    data = request.json
    required_fields = ['resource_id', 'user_id', 'start_time', 'end_time', 'project_priority']
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
        
    if not service:
        return jsonify({"error": "Database not configured"}), 500

    # Create booking
    booking_doc = Document(
        id=f"booking:{uuid.uuid4().hex[:8]}",
        type="booking",
        resource_id=data['resource_id'],
        user_id=data['user_id'],
        project_priority=data['project_priority'],
        start_time=data['start_time'],
        end_time=data['end_time'],
        status="active"
    )

    try:
        response = service.post_document(
            db=DB_NAME,
            document=booking_doc
        ).get_result()
        return jsonify(response), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
