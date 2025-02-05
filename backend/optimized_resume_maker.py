# optimized_resume_maker.py

import ollama
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import datetime
# Register fonts
pdfmetrics.registerFont(TTFont('Helvetica', '/Users/saikundansuddapalli/Documents/Automation/jobAssistant/backend/resume_maker/helvetica-255/Helvetica.ttf'))
pdfmetrics.registerFont(TTFont('Helvetica-Bold', '/Users/saikundansuddapalli/Documents/Automation/jobAssistant/backend/resume_maker/helvetica-255/Helvetica-Bold.ttf'))

styles = getSampleStyleSheet()
story = []

# Custom styles
styles.add(ParagraphStyle(name='Center', fontName='Helvetica', fontSize=10, leading=12, alignment=1, spaceAfter=6))
styles.add(ParagraphStyle(name='SectionTitle', fontName='Helvetica-Bold', fontSize=12, leading=14, spaceAfter=6, underline=True))
styles.add(ParagraphStyle(name='Body', fontName='Helvetica', fontSize=10, leading=12, spaceAfter=6))
styles.add(ParagraphStyle(name='Company', fontName='Helvetica-Bold', fontSize=10, leading=12))
styles.add(ParagraphStyle(name='Date', fontName='Helvetica', fontSize=10, alignment=2))

# Create document
doc = SimpleDocTemplate("resume.pdf", pagesize=letter, leftMargin=0.6*inch, rightMargin=0.6*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)

# Header with center alignment
header = [
    Paragraph("<font size=18><b>SAI KUNDAN SUDDAPALLI</b></font>", styles['Center']),
    Paragraph("706-300-2779 • <a href='mailto:kundan16@hotmail.com' color='blue'>kundan16@hotmail.com</a> • " +
              "<a href='https://linkedin.com/in/saikundan' color='blue'>linkedin.com/in/saikundan</a> • " +
              "<a href='https://github.com/Ironman20121' color='blue'>github.com/Ironman20121</a>", styles['Center']),
    Paragraph("<b>Authorized to work in the U.S. on F1 OPT (STEM extension eligible)</b>", styles['Center']),
    Spacer(1, 0.2*inch)
]

story.extend(header)

# Section function
def add_section(title, content):
    story.append(Paragraph(f"<b>{title}</b>", styles['SectionTitle']))
    story.append(Spacer(1, 0.1*inch))
    story.extend(content)
    story.append(Spacer(1, 0.2*inch))

# Function to add experience or project sections
def add_experience_section(title, company, date, location, sentences):
    experience = [
        Table([
            [Paragraph(title, styles['Company']), Paragraph(date, styles['Date'])],
            [Paragraph(company, styles['Body']), Paragraph(location, styles['Body'])],
        ], colWidths=[doc.width*0.7, doc.width*0.3])
    ]
    for sentence in sentences:
        experience.append(Paragraph(f"• {sentence}", styles['Body']))
    experience.append(Spacer(1, 0.2*inch))
    return experience

# Function to add project sections
def add_project_section(title, description, github_link, sentences):
    project = [
        Table([
            [Paragraph(title, styles['Company']), Paragraph(description, styles['Body'])],
            [Paragraph(f"<a href='{github_link}' color='blue'>GitHub</a>", styles['Body']), ""]
        ], colWidths=[doc.width*0.7, doc.width*0.3])
    ]
    for sentence in sentences:
        project.append(Paragraph(f"• {sentence}", styles['Body']))
    project.append(Spacer(1, 0.2*inch))
    return project

# Function to add technical skills section
def add_skills_section(skills_dict):
    skills = []
    for category, items in skills_dict.items():
        skills.append(Paragraph(f"<b>{category}</b>: {', '.join(items)}", styles['Body']))
    skills.append(Spacer(1, 0.2*inch))
    return skills

# # Ollama-based AI function
def askai(prompt):
    try:
        response = ollama.generate(model='mistral', prompt=prompt)
        return response['response']
    except Exception as e:
        print(f"Error in Ollama API call: {e}")
        return prompt  # Fallback to original prompt if Ollama fails

# def askai(prompt):
#     try:
#         # Use "phi3" instead of mistral
#         response = ollama.generate(model='gemma:2b', prompt=prompt)
#         return response['response']
#     except Exception as e:
#         print(f"Error in Ollama API call: {e}")
#         return prompt  # Fallback to original prompt

# Batch processing for sentences
def askaiList(sentences, JD):
    rewritten_sentences = []
    for sentence in sentences:
        prompt_exp = f"""
You are a professional resume writer. Your task is to rewrite the following sentence from my resume to be more effective and targeted towards the provided job description. Maintain a similar length and structure for the rewritten sentence. Do not add any extra characters like # or `. Focus on using strong action verbs and quantifiable achievements whenever possible.

Job Description: {JD}

Original Sentence: {sentence}

Rewritten Sentence:
avoid spcial characters like '*' ,'#' ,'`','"'
"""
        rewritten_sentences.append(askai(prompt_exp))
    return rewritten_sentences

# Example input data
summary = "As a highly motivated M.S. in Computer Science, I possess a strong passion for building secure and resilient systems. With a focused foundation in Python and C++, along with extensive experience in machine learning frameworks such as TensorFlow and PyTorch, I am eager to contribute my skills to innovative security solutions. My experience includes developing interpretable AI models and optimizing large-scale deployments."

graduate_experience = [
    "Contributed to the development of an advanced version of the CrystaLLM library for large language models, focusing on interpretability and explainability, to aid in the discovery of novel therapeutic compounds for Alzheimer’s disease. Led research in training deep models (e.g., GPT-based architecture) to predict chemical properties, accelerating drug discovery processes.",
    "Utilized LoRA to fine-tune existing open-source LLM models (e.g., LLaMA, GEEMA) for specific chemical tasks.",
    "Utilized high-performance computing resources (HPC) on Bridges to expedite training and inference.",
    "Developed and led tutorials on Quantum Computing using IBM Quantum Experience and Qiskit."
]

cpp_experience = [
    "Developed and customized a trading platform for a client in the BFSI sector, specifically the Multi Commodity Exchange (MCX), utilizing extensive experience in C/C++ and Python, with a strong focus on UNIX platforms and proficiency in analyzing and debugging in C, C++, and Python.",
    "Demonstrated expertise in C++ development, enhancing the trading platform by mastering critical components such as the Order Book Interface, Market Data Distribution, Info Feed, and integrating seamlessly with Kafka, resulting in enhanced analytical prowess through meticulous C++ craftsmanship.",
    "Achieved a significant 1 million user increase by optimizing the Enhanced Order Book Interface, significantly growing user engagement and market footprint, showcasing ability to drive business growth through technical expertise.",
    "Engineered a low-latency Info Feed for alpha clients, surpassing expectations and elevating satisfaction levels, highlighting ability to deliver high-quality solutions under tight deadlines.",
    "Implemented a seamless Git flow, enhancing collaboration efficiency by 30% and achieving error-free code deployments with improved version control, demonstrating expertise in DevOps and version control systems.",
    "Developed a robust CI/CD pipeline using Bash, Python, and Ansible, reducing deployment time by 40% and improving deployment reliability by 25%, showcasing ability to automate and streamline development processes.",
    "Led a Python-powered deployment process that cut deployment time by 50% across 100 servers, enhancing efficiency and time utilization, highlighting ability to lead and manage large-scale deployments.",
    "Ensured a flawless environment handover well before live trading, resulting in a seamless transition with zero disruptions, demonstrating ability to manage and deliver high-stakes projects.",
    "Automated Python scripts for monthly SLA report extraction, reducing report generation time by 30%, showcasing ability to automate and optimize business processes.",
    "Automated system checks, reducing manual effort by 20% and fostering a proactive and reliable system, highlighting ability to identify and implement process improvements."
]

full_stack_experience = [
    "Specialized in developing cutting-edge ML-based analytics for wearable devices.",
    "Contributed to the development of a medical chatbot assistant by creating algorithms to process data from band watches, focusing on heart rate time series analysis.",
    "Improved model accuracy by 10% through rigorous data preprocessing and feature engineering.",
    "Integrated ML models into complex systems and contributed to frontend development using ReactJS to visualize key metrics."
]

drdo_experience = [
    "Developed a machine learning model for predicting missile failures to enhance system reliability.",
    "Worked on data collection, preprocessing, and storage using SQLite.",
    "Explored deep learning techniques using TensorFlow and Keras, achieving significant improvements in prediction accuracy.",
    "Identified critical failure factors and provided actionable insights for system enhancement."
]

unisys_experience = [
    "Developed a flight delay prediction model using historical data to improve operational efficiency.",
    "Engineered key features influencing delays and optimized models using Logistic Regression and Random Forest.",
    "Integrated the model into operational workflows, reducing unexpected delays.",
    "Received commendations from senior management for impactful contributions."
]

project_1 = [
    "Engineered a POSIX thread (pthreads)-based simulation to model concurrent interactions between 50+ students and TAs, resolving race conditions with mutex locks and semaphores.",
    "Containerized the system using Docker, reducing cross-platform setup time by 70%; automated builds via CMake for seamless scalability testing.",
    "Optimized thread scheduling and CPU utilization by 25% using GDB/Valgrind for debugging; archived logs to track student wait times and TA idle states."
]

project_2 = [
    "Designed a hybrid CNN+Transformer (ViT) model using TensorFlow, achieving 98% detection accuracy on deep fakes; deployed on Azure ML Studio and AKS for real-time scalability.",
    "Streamlined data pipelines with Azure Data Factory & Cognitive Services, reducing anomalies by 15% and manual labeling effort by 50% via automated preprocessing.",
    "Optimized architecture with FastAI and Azure Batch AI, cutting training time by 20% and resource use by 25%; published findings on forgery detection in peer-reviewed venues."
]

# Example skills input
skills_dict = {
    "Languages": ["C++", "Python", "Java", "HTML/CSS", "JavaScript", "SQL", "Assembly (x86 and AArch64)", "bash"],
    "Machine Learning Frameworks": ["TensorFlow (Certified)", "PyTorch", "Qiskit", "Hugging Face Transformers"],
    "Technologies/Frameworks": ["Git", "Docker", "GDB", "CMake", "PDB", "OpenCV", "Ghidra", "Cutter"]
}




# ----------- Cover Letter Generation -----------
def generate_cover_letter(company_name,job_description):
    resume_content = ''
    with open('/Users/saikundansuddapalli/Documents/Automation/JobApplicationHelper/resume.txt')as f:
        resume_content=f.read()    
    prompt = f"""
You are a professional cover letter writer. Your sole task is to generate a concise and impactful cover letter based on the provided resume content and job description.  Adhere strictly to the following guidelines:

Resume Content:
{resume_content}

Job Description:
{job_description}

Instructions:

companyname :{company_name}

1. **Output Format:** Deliver *only* the cover letter text.  Do not include any introductory or concluding remarks, explanations, or other text outside of the cover letter itself.  Do not use any markdown formatting.

2. **Length and Structure:** The cover letter must consist of exactly 3 -4 paragraphs, suitable for a single page.  Keep the paragraphs concise and focused.

3. **Content:**
    * Highlight three key qualifications from the resume that are highly relevant to the job description.
    * Explicitly mention two specific requirements or skills mentioned in the job description, demonstrating how your qualifications meet those requirements.
    * Use professional and concise language.  **Do not use placeholder text of any kind.**  If you don't have specific information (like a company name), omit it entirely.  Do not use brackets, placeholders, or anything that needs to be filled in later.
    * The cover letter should be addressed to the Hiring Manager (if a specific name is provided in the job description, use it; otherwise, use "Hiring Manager").
    * The closing should be "Sincerely," followed by your full name: SaiKundanSuddapalli.

4. **Absolutely No Placeholders:**  Ensure there are no bracketed placeholders like "[Company Name]" or any similar constructions.  The generated cover letter should be ready to submit as-is, with no further editing required on your part (except for potentially very minor formatting adjustments if the AI introduces unexpected spacing).  Do not include sentences like "Thank you for considering me for this opportunity, and I look forward to the possibility of contributing my skills... at [Company Name]."  If you don't know the company name, simply omit it from that sentence.

"""
    try:
        response = ollama.generate(
            model='mistral',
            prompt=prompt,
            options={'temperature': 0.2}  # Keep it focused
        )
        return response['response']
    except Exception as e:
        print(f"Cover letter generation failed: {e}")
        return f"Error generating cover letter. Please refer to my resume for qualifications."

def create_cover_letter_pdf(content, filename="cover_letter.pdf"):
    # Custom styles
    styles.add(ParagraphStyle(name='cv_Body', fontName='Helvetica', fontSize=11, leading=13))
    styles.add(ParagraphStyle(name='cv_Header', fontName='Helvetica-Bold', fontSize=12, alignment=1))
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    story = []
    
    # Header
    story.append(Paragraph("SAI KUNDAN SUDDAPALLI", styles['Center']))
    story.append(Paragraph("Email: kundan16@hotmail.com | Phone: (706)300-2779", styles['Center']))
    story.append(Spacer(1, 0.3*inch))
    date_now = datetime.datetime.now()
    formatted_date = date_now.strftime("%d %b %Y")
    # Date and Hiring Manager Info
    story.append(Paragraph(f"Date: {formatted_date}", styles['cv_Body']))
    story.append(Paragraph("Hiring Manager<br/>", styles['cv_Body']))
    story.append(Spacer(1, 0.3*inch))
    
    # Body Content
    lines = content.split('\n')
    for line in lines:
        if line.strip():  # Skip empty lines
            story.append(Paragraph(line.strip(), styles['cv_Body']))
            story.append(Spacer(1, 0.1*inch))
    
    doc.build(story)


def genreate_resume(JD):
    # Generate AI-enhanced content
    prompt_sum = f"Here is my {JD} please go though my summary {summary} and modify based on JD please make sure to same length as before not make sure not more 4 lines  "
    s = askai(prompt_sum)
    ai_grade_exp = askaiList(graduate_experience, JD)
    ai_tcs_exp = askaiList(cpp_experience, JD)
    ai_full_stack = askaiList(full_stack_experience,JD)
    ai_drdo = askaiList(drdo_experience,JD)
    ai_unisys = askaiList(unisys_experience,JD)
    ai_proj1 = askaiList(project_1,JD)
    ai_proj2 = askaiList(project_2,JD)
    


    # Add sections dynamically
    add_section("Summary", [Paragraph(s, styles['Body'])])
    add_section("Experience", 
        add_experience_section("Graduate Research Assistant", "University of North Georgia", "May 2024 – Dec 2024", "Dahlonega, GA, USA", ai_grade_exp) +
        add_experience_section("C++ & Python Developer", "Tata Consultancy Services", "Nov 2021 – Nov 2023", "Hyderabad, Telangana, India", ai_tcs_exp) +
        add_experience_section("Full Stack Developer", "River Bend Data Solutions", "Apr 2020 – Oct 2021", "Hyderabad, Telangana, India", ai_full_stack) +
        add_experience_section("Internship: Missile Technology Case Study", "Defence Research and Development Laboratory (DRDL) - DRDO", "Apr 2019 – Jul 2019", "Hyderabad, Telangana, India", ai_drdo) +
        add_experience_section("Machine Learning Intern", "Unisys (Remote)", "Oct 2017 – April 2018", "India", ai_unisys)
    )
    add_section("Projects", 
        add_project_section("Multi-threaded TA-Student Simulation", "Systems Programming Project | C++, Docker, CMake", "https://github.com/Ironman20121/OS-threading-", ai_proj1) +
        add_project_section("Deep Fake Video Detection", "Project (Kaggle Competition)", "https://github.com/Ironman20121/FakeVideoDetector", ai_proj2)
    )
    add_section("Technical Skills", add_skills_section(skills_dict))

    # Build PDF
    doc.build(story)

def main_flow(JD):
    
    genreate_resume(JD)
    cover_letter_text = generate_cover_letter("amazon",JD)
    create_cover_letter_pdf(cover_letter_text, f"Cover_Letter.pdf")
    print("Done Genreated ")
    


JD="""
                  Job Title – Python DeveloperLocation – Irving, TXJob Type – Full TimeExperience Required - 8+ YearsResponsibilities:Design, develop, and maintain efficient, reusable, and reliable Python code.Build robust APIs to power our applications with a focus on performance and scalability.Collaborate with frontend developers to integrate user-facing elements with server-side logic.Implement security and data protection measures.Work closely with product owners and stakeholders to gather requirements and translate them into technical solutions.Troubleshoot issues, fix bugs, and improve application performance.Stay up to date with emerging technologies and trends in the Python and FastAPI community. Requirements:Proficient in Python, with strong knowledge of its ecosystem.Experience developing APIs using FastAPI (experience with other frameworks like Flask or Django is a plus).Familiarity with asynchronous programming in Python.Solid understanding of SQL and NoSQL databases.Experience with version control systems (e.g., Git).Good understanding of front-end technologies, such as JavaScript, HTML5, and CSS3 (optional).Excellent communication and collaboration skills."

"""
main_flow(JD)