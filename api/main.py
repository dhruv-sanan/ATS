import os
import time
import csv
from crewai import Crew
from langchain_groq import ChatGroq
from agents import EmailPersonalizationAgents
from tasks import PersonalizeEmailTask
import PyPDF2 as pdf

# 0. Setup environment
from dotenv import load_dotenv
load_dotenv()


def input_pdf_text(uploaded_file):
    if uploaded_file is not None:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in range(len(reader.pages)):
            page = reader.pages[page]
            text += str(page.extract_text())
        return text
    else:
        print("Please upload pdf")


email_template = """
Dear [Candidate Name],

We are pleased to inform you that you have successfully progressed to the next round of interviews for the [Job Title] position at [Company Name].
We were impressed with your performance and qualifications during the first round, and we are eager to learn more about you.
The next round will consist of an in-person interview with the team. We will be in touch shortly to schedule a convenient time for you.
In the meantime, feel free to review the job description again and prepare any questions you may have for us.
We look forward to meeting with you again soon!

Regards,
Dhruv Sanan
"""

# 1. Create agents
agents = EmailPersonalizationAgents()

email_personalizer = agents.personalize_email_agent()
ghostwriter = agents.ghostwriter_agent()

# 2. Create tasks
tasks = PersonalizeEmailTask()

personalize_email_tasks = []
ghostwrite_email_tasks = []

# Path to the CSV file containing client information
uploaded_file = 'resume.pdf'
pdf_content = input_pdf_text(uploaded_file)

first_name = "Dhruv"
last_name = "Sanan"
email = "dhruvsanan01@gmail.com"
jd = """Roles:
We are looking for ML Engineers for an AI based product development for one of our clients in the banking industry. As a Machine Learning Engineer, you will collaborate with colleagues to bring AI-driven solutions to life, assisting in the productionization of machine learning models and ensuring their effective deployment in a production environment.
 
Responsibilities:
Understand the requirements and needs of business stakeholders, building strong relationships, and identifying how AI and machine learning solutions can support our business strategy.
Support the productionization of machine learning models, including pipeline design, development, testing, and deployment, ensuring the original intent is preserved in the production environment.
Contribute to frameworks for robust monitoring of machine learning models within a production environment, ensuring they deliver quality and performance.
We'll rely on your experience in constructing, testing, maintaining, and deploying machine learning models into a production setting. This involves utilizing contemporary CI/CD tools such as Git, AWS, AWS Sagemaker, Docker, Terraform, Cloud Formation, Kubernetes, PyTorch, TensorFlow, Jax, Numpy, Scikit-learn, and other related technologies.
 
Qualifications:
Minimum 5+ years of relevant experience as a Machine Learning Engineer.
Proficiency in machine learning approaches and algorithms, including time-series forecasting, classification, regression, large language models, and generative AI.
Strong programming and scripting skills, particularly in Python, are essential.
Basic knowledge of the financial services industry and the ability to identify wider business impact and risk opportunities is preferred.
"""

# Access each field in the row
recipient = {
    'first_name': first_name,
    'last_name': last_name,
    'email': email,
    'resume': pdf_content,
    'job': jd
}

# Create a personalize_email task for each recipient
personalize_email_task = tasks.personalize_email(
    agent=email_personalizer,
    recipient=recipient,
    email_template=email_template
)

# Create a ghostwrite_email task for each recipient
ghostwrite_email_task = tasks.ghostwrite_email(
    agent=ghostwriter,
    draft_email=personalize_email_task,
    recipient=recipient
)

# Add the task to the crew
personalize_email_tasks.append(personalize_email_task)
ghostwrite_email_tasks.append(ghostwrite_email_task)

# Setup Crew
crew = Crew(
    agents=[
        email_personalizer,
        ghostwriter
    ],
    tasks=[
        *personalize_email_tasks,
        *ghostwrite_email_tasks
    ],
    max_rpm=29
)

# Kick off the crew
start_time = time.time()

results = crew.kickoff()

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Crew kickoff took {elapsed_time} seconds.")
print("Crew usage", crew.usage_metrics)
