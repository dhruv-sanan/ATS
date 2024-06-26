# Standard library imports
from datetime import datetime
import json
from threading import Thread
from uuid import uuid4

# Related third-party imports
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import PyPDF2 as pdf
# Local application/library specific imports
from crew import CompanyResearchCrew, EmailPersonalizationCrew, HRCrew
from job_manager import append_event, jobs, jobs_lock, Event
# from utils.logging import logger
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


def input_pdf_text(url):
    try:
        response = requests.get(url, allow_redirects=True)  # Fetch PDF content
        response.raise_for_status()  # Raise error for non-2xx status codes
        with open("fetched_pdf.pdf", "wb") as f:  # Write fetched content to temporary file
            f.write(response.content)
        with open("fetched_pdf.pdf", "rb") as f:
            reader = pdf.PdfReader(f)
            text = ""
            for page in range(len(reader.pages)):
                page = reader.pages[page]
                text += str(page.extract_text())
            return text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PDF: {e}")
        return "Error: Failed to retrieve PDF"
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return "Error: An error occurred while processing the PDF"
    finally:
        os.remove("fetched_pdf.pdf")  # Remove temporary file


@app.route('/api/extract-text', methods=['POST'])
def extract_text():
    data = request.get_json()
    if data is None or 'url' not in data:
        return jsonify({'error': 'Missing or invalid data'}), 400

    pdf_url = data['url']
    extracted_text = input_pdf_text(pdf_url)
    return jsonify({'text': extracted_text})


def kickoff_crew(job_id, companies: list[str], positions: list[str]):
    results = None
    try:
        company_research_crew = CompanyResearchCrew(job_id)
        company_research_crew.setup_crew(
            companies, positions)
        results = company_research_crew.kickoff()
        # logger.info(f"Crew for job {job_id} is complete", results)

    except Exception as e:
        # logger.error(f"Error in kickoff_crew for job {job_id}: {e}")
        append_event(job_id, f"An error occurred: {e}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)

    with jobs_lock:
        jobs[job_id].status = 'COMPLETE'
        jobs[job_id].result = results
        jobs[job_id].events.append(
            Event(timestamp=datetime.now(), data="Crew complete"))


def kickoff_crewpdf(job_id, pdf_content, jd):
    results = None
    try:
        Email_Personalization_Crew = EmailPersonalizationCrew(job_id)
        Email_Personalization_Crew.setup_crew(
            pdf_content, jd)
        results = Email_Personalization_Crew.kickoff()
        # logger.info(f"Crew for job {job_id} is complete", results)

    except Exception as e:
        # logger.error(f"Error in kickoff_crew for job {job_id}: {e}")
        append_event(job_id, f"An error occurred: {e}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)

    with jobs_lock:
        jobs[job_id].status = 'COMPLETE'
        jobs[job_id].result = results
        jobs[job_id].events.append(
            Event(timestamp=datetime.now(), data="Crew complete"))


def kickoff_crewHR(job_id, pdf_content, jd):
    results = None
    try:
        HRcrew = HRCrew(job_id)
        HRcrew.setup_crew(
            pdf_content, jd)
        results = HRcrew.kickoff()
        # logger.info(f"Crew for job {job_id} is complete", results)

    except Exception as e:
        # logger.error(f"Error in kickoff_crew for job {job_id}: {e}")
        append_event(job_id, f"An error occurred: {e}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)

    with jobs_lock:
        jobs[job_id].status = 'COMPLETE'
        jobs[job_id].result = results
        jobs[job_id].events.append(
            Event(timestamp=datetime.now(), data="Crew complete"))


@app.route("/api/crew", methods=["POST"])
def run_crew():
    data = request.json
    if not data or 'companies' not in data or 'positions' not in data:
        abort(400, description="Invalid input data provided.")

    job_id = str(uuid4())
    companies = data['companies']
    positions = data['positions']
    thread = Thread(target=kickoff_crew, args=(
        job_id, companies, positions))
    thread.start()
    return jsonify({"job_id": job_id}), 202


@app.route("/api/crewpdf", methods=["POST"])
def run_crewpdf():
    data = request.json

    job_id = str(uuid4())
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    pdf_content = data['pdf_content']
    jd = data['jd']
    thread = Thread(target=kickoff_crewpdf, args=(
        job_id, pdf_content, jd))
    thread.start()
    return jsonify({"job_id": job_id}), 202


@app.route("/api/crewHR", methods=["POST"])
def run_crewHR():
    data = request.json
    job_id = str(uuid4())
    pdf_content = data['pdf_content']
    jd = data['jd']
    thread = Thread(target=kickoff_crewHR, args=(
        job_id, pdf_content, jd))
    thread.start()
    return jsonify({"job_id": job_id}), 202


@app.route("/api/crew/<job_id>", methods=["GET"])
def get_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
        if job is None:
            abort(404, description="Job not found")

     # Parse the job.result string into a JSON object
    try:
        result_json = job.result
    except json.JSONDecodeError:
        # If parsing fails, set result_json to the original job.result string
        result_json = job.result

    return jsonify({
        "job_id": job_id,
        "status": job.status,
        "result": result_json,
        "events": [{"timestamp": event.timestamp.isoformat(), "data": event.data} for event in job.events]
    })

