from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import pandas as pd
import os
import logging
from time import sleep
from mistralai import Mistral
import json
import traceback
import csv  
from io import BytesIO
import zipfile
from datetime import datetime, timezone  

from optimized_resume_maker import main_flow

#not required as I am using ollama instead of mistral API
# from dotenv import load_dotenv
# load_dotenv()

# Set up logging tcs ka batcha
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

STORAGE_FILE = 'job_data.csv'
BASE_RESUME_PATH = "resume.txt"  
# OUTPUT_DIR = "generated_pdfs"  

# os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        if not os.path.exists(STORAGE_FILE):
            return jsonify({'total_jobs': 0, 'jobs_today': 0})

        # Read CSV with explicit column names
        columns = ['date', 'job_link', 'job_description', 'company_name']
        df = pd.read_csv(STORAGE_FILE, names=columns, header=0)
        
        # logger.debug(f"CSV Data:\n{df.head()}")
        
        # Converting dates for accurate comparison
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])  # Remove invalid dates
        
        # today's date UTC
        today = datetime.now(timezone.utc).date()
        jobs_today = len(df[df['date'].dt.date == today])
        
        # # Debug: Log today's date and jobs_today count
        # logger.debug(f"Today's date (UTC): {today}")
        # logger.debug(f"Jobs today: {jobs_today}")
        
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
        
        #  duplicate check broOò
        if ispresent(data['jobLink']):
            return jsonify({
                'status': 'error',
                'message': 'This job link already exists in our system'
            }), 409
            
        # Create dataframe with consistent columns  where colums consistancy is key 
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
        logger.info(f"Received generation request: {data}")
        
        # Generate PDFs in memory
        resume_buffer, cover_buffer = main_flow(data['jobDescription'], data['companyName'])
        
        # Create ZIP file in memory
        zip_buffer = BytesIO()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"{data['companyName']}_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add resume to ZIP
            resume_buffer.seek(0)
            zip_file.writestr(f"resume_{timestamp}.pdf", resume_buffer.getvalue())
            
            # Add cover letter to ZIP
            cover_buffer.seek(0)
            zip_file.writestr(f"cover_letter_{timestamp}.pdf", cover_buffer.getvalue())
        
        zip_buffer.seek(0)
        
        logger.info(f"Successfully generated ZIP package: {zip_name}")
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_name
        )
    
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)