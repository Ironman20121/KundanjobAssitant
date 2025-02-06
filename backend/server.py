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
import csv  


from datetime import datetime, timezone  # Add timezone

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
BASE_RESUME_PATH = "resume.txt"  
OUTPUT_DIR = "generated_pdfs"  

os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        if not os.path.exists(STORAGE_FILE):
            return jsonify({'total_jobs': 0, 'jobs_today': 0})

        # Read CSV with explicit column names
        columns = ['date', 'job_link', 'job_description', 'company_name']
        df = pd.read_csv(STORAGE_FILE, names=columns, header=0)
        
        # Debug: Log the first few rows of the CSV
        logger.debug(f"CSV Data:\n{df.head()}")
        
        # Convert dates to datetime objects for accurate comparison
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])  # Remove invalid dates
        
        # Get today's date in UTC
        today = datetime.now(timezone.utc).date()
        jobs_today = len(df[df['date'].dt.date == today])
        
        # Debug: Log today's date and jobs_today count
        logger.debug(f"Today's date (UTC): {today}")
        logger.debug(f"Jobs today: {jobs_today}")
        
        return jsonify({
            'total_jobs': len(df),
            'jobs_today': jobs_today
        })
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
def ispresent(link: str) -> bool:
    """Check if job link exists in storage"""
    if not os.path.exists(STORAGE_FILE):
        return False
    
    try:
        # Read CSV with proper quoting and headers
        df = pd.read_csv(STORAGE_FILE, quoting=csv.QUOTE_ALL, header=0)
        if 'job_link' not in df.columns:
            return False
        return df['job_link'].str.strip().eq(link.strip()).any()
    except pd.errors.EmptyDataError:
        return False
    except Exception as e:
        logger.error(f"Duplicate check error: {str(e)}")
        return False


@app.route('/save', methods=['POST'])
def save_job():
    try:
        data = request.json
        logger.info("Received job data for saving")
        
        # Check for duplicate before saving
        if ispresent(data['jobLink']):
            return jsonify({
                'status': 'error',
                'message': 'This job link already exists in our system'
            }), 409
            
        # Create dataframe with consistent columns
        new_entry = pd.DataFrame([{
            'date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),  # Standardized date
            'job_link': data['jobLink'].strip(),
            'job_description': data['jobDescription'],
            'company_name': data['companyName']
        }])

        # Save with CSV quoting and header management
        header = not os.path.exists(STORAGE_FILE)
        new_entry.to_csv(
            STORAGE_FILE,
            mode='a',
            header=header,
            index=False,
            quoting=csv.QUOTE_ALL,
            escapechar='\\'
        )
        
        logger.info("Job data saved successfully")
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error saving job data: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
       
        logger.info(f"{data}")
    
        logger.info("Received job data for saving")
        logger.info("Sent data to main-flow resume generator")
        main_flow(data['jobDescription'],data['companyName'])
        logger.info("Done successfully")
        return jsonify({'status': 'success'})
    
    except Exception as e:
        logger.error(f"Error saving job data: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)