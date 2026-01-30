# Quantum Resource Scheduler

This project implements a Research Resource Optimizer for the Quantum Computing workflow, designed for the IBM AI Demystified Challenge.

## Components

1.  **Python Logic (`app.py`)**: A Flask application that wraps Cloudant database calls. It implements a robust "Two-Step Filtering" logic to check for booking overlaps.
2.  **OpenAPI Specification (`openapi.yaml`)**: Defines the interface for Watsonx Orchestrate to interact with the Python tool.
3.  **Database Setup (`cloudant_setup.py`)**: Helper script to initialize the Cloudant database, create the necessary Mango Index, and seed a sample resource.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    Copy `.env.example` to `.env` and fill in your Cloudant credentials.
    ```bash
    cp .env.example .env
    ```
    *   `CLOUDANT_API_KEY`: Your IBM Cloudant Service API Key.
    *   `CLOUDANT_URL`: Your IBM Cloudant Service URL.

3.  **Initialize Database**:
    Run the setup script to create the `reservations` database and the required index.
    ```bash
    python cloudant_setup.py
    ```

4.  **Run Locally**:
    ```bash
    python app.py
    ```
    The server will start on `http://0.0.0.0:8080`.

## Deployment

1.  **Deploy to IBM Code Engine**:
    *   Push this code to a git repository or use the local source code.
    *   Create a generic web application in IBM Code Engine.
    *   Set the environment variables `CLOUDANT_API_KEY` and `CLOUDANT_URL` in the Code Engine configuration.

2.  **Connect to Watsonx Orchestrate**:
    *   Upload `openapi.yaml` to Watsonx Orchestrate as a custom skill/extension.
    *   Update the `servers.url` in `openapi.yaml` to your deployed Code Engine application URL before importing.

## API Endpoints

*   **GET /check-availability**: Check if a resource is available for a given time range.
    *   Query Params: `resource_id`, `start_time` (ISO 8601), `end_time` (ISO 8601)
*   **POST /book-slot**: Create a new booking.
    *   Body: JSON with `resource_id`, `user_id`, `start_time`, `end_time`, `project_priority`.
