import os
from ibmcloudant.cloudant_v1 import CloudantV1, Document
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv

load_dotenv()

# Initialize Cloudant Service
API_KEY = os.getenv('CLOUDANT_API_KEY')
URL = os.getenv('CLOUDANT_URL')

if not API_KEY or not URL:
    print("Please set CLOUDANT_API_KEY and CLOUDANT_URL in .env file")
    exit(1)

authenticator = IAMAuthenticator(API_KEY)
service = CloudantV1(authenticator=authenticator)
service.set_service_url(URL)

DB_NAME = 'reservations'

def setup_database():
    # 1. Create Database
    try:
        service.put_database(db=DB_NAME).get_result()
        print(f"Database '{DB_NAME}' created.")
    except Exception as e:
        print(f"Database might already exist: {e}")

    # 2. Create Index
    try:
        service.post_index(
            db=DB_NAME,
            name="resource-status-start-index",
            type="json",
            index={
                "fields": ["resource_id", "status", "start_time"]
            }
        ).get_result()
        print("Index created successfully.")
    except Exception as e:
        print(f"Error creating index: {e}")

    # 3. Create Sample Resource Document
    resource_doc = {
      "_id": "resource:quantum_eagle_01",
      "type": "resource",
      "name": "IBM Eagle Processor (127-qubit)",
      "status": "online",
      "access_tier": "premium",
      "capabilities": ["quantum", "high-coherence"]
    }
    
    try:
        service.post_document(db=DB_NAME, document=resource_doc).get_result()
        print("Sample resource created.")
    except Exception as e:
        print(f"Error creating sample resource (might exist): {e}")

if __name__ == "__main__":
    setup_database()
