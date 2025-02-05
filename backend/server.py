from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import pandas as pd
import os
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from time import sleep
from mistralai import Mistral
import json
import traceback

from optimized_resume_maker import main_flow

from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Constants
STORAGE_FILE = 'job_data.csv'
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")  # Replace with your actual API key
BASE_RESUME_PATH = "resume.txt"  # Make sure this matches your actual resume file name
OUTPUT_DIR = "generated_pdfs"  # Directory for generated PDFs

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/save', methods=['POST'])
def save_job():
    try:
        data = request.json
        logger.info("Received job data for saving")
        
        df = pd.DataFrame([{
            'date': data['date'],
            'job_link': data['jobLink'],
            'job_description': data['jobDescription']
        }])
        
        if os.path.exists(STORAGE_FILE):
            df.to_csv(STORAGE_FILE, mode='a', header=False, index=False)
        else:
            df.to_csv(STORAGE_FILE, index=False)
            
        logger.info("Job data saved successfully")
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error saving job data: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/generate',methods=['POST'])
def generate():
    try:
        data = request.json
        logger.info(f"checking data {data}")
        
        logger.info("Received job data for saving")
        logger.info("sent data main-flow resume generater")
        main_flow(data['jobDescription'])
        logger.info("done success")
        return jsonify({'status': 'success'})
    
    except Exception as e:
        logger.error(f"Error saving job data: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)