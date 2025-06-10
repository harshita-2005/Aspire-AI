from flask import (
    Flask, request, jsonify, render_template, 
    redirect, url_for, flash, session
)
from markupsafe import Markup
from aspire_ai.variables import CONFIG
from aspire_ai.storageutils import MySQLManager
from datetime import datetime
import os
import sys
import subprocess
import time
import logging
# Add necessary directories to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'aspire_ai'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'RAG ', 'src'))


#   chain imports
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferWindowMemory

# Local imports
from aspire_ai.chatbot import get_assistant_response

# Global memory instance with k=1
memory = ConversationBufferWindowMemory(k=1, return_messages=True)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize ChatOllama for the app
class LLMWrapper:
    def __init__(self, llm):
        self.llm = llm
    
    def invoke(self, prompt):
        class Response:
            def __init__(self, content):
                self.content = content
        
        return Response(self.llm.invoke(prompt).content)

ollama_llm = LLMWrapper(ChatOllama(
    model="llama3.1",
    temperature=0.4,
    max_tokens=500,
    gpu=True
))

# Dictionary to store chat memories per session
chat_memories = {}

# Define absolute paths for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, 
           template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'aspire_ai', 'templates')),
           static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'aspire_ai', 'static')))

app.secret_key = os.urandom(24)
@app.route('/')
def root():
    # Redirect to landing page
    return redirect(url_for('landing'))  # Note: 'landing' matches the function name below

@app.route('/landing')
def landing():  # This name must match url_for('landing')
    return render_template('landing.html')

@app.route('/index')
def index():
    return render_template('index.html')
@app.route('/form/<user_type>')
def show_form(user_type):
    valid_types = ['student', 'freelancer', 'professional', 'career-shifter', 'other']
    if user_type not in valid_types:
        return redirect(url_for('index'))
    return render_template('form.html', user_type=user_type)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        user_type = request.form.get('user_type')
        email = request.form.get('email_id')  # Store the email in a variable
        # Store the email in the session
        session['user_email'] = email

        # Extract data from the form
        full_name = request.form.get('full_name')
        email_id = request.form.get('email_id')
        location = request.form.get('location')

        # Handle education level and other
        education_level = request.form.get('education_level')
        education_other = request.form.get('education_other')
        if education_level == 'other':
            education_level = education_other

        # Handle field/domain and other
        field_or_domain = request.form.get('field_or_domain')
        domain_other = request.form.get('domain_other')
        if field_or_domain == 'other':
            field_or_domain = domain_other

        year_of_passing = request.form.get('year_of_passing')

        skills = request.form.get('skills')
        technical_courses = request.form.get('technical_courses')

        # Handle industry and other
        industry = request.form.get('industry')
        industry_other = request.form.get('industry_other')
        if industry == 'other':
            industry = industry_other

        specific_role = request.form.get('specificRole')
        expected_salary_range = request.form.get('expected_salary_range')

        extracurricular_activities = request.form.get('extracurricular_activities')

        current_job_role = request.form.get('current_job_role')
        current_salary = request.form.get('current_salary')
        years_of_experience = request.form.get('years_of_experience')
        future_aspirations = request.form.get('future_aspirations')

        previous_job_roles = request.form.get('previous_job_roles')

        # Define the SQL query
        query = """
        INSERT INTO users (
            user_type,full_name, email_id, location, education_level, field_or_domain, year_of_passing,
            skills, technical_courses, industry, specific_role, expected_salary_range,
            extracurricular_activities, current_job_role, current_salary, years_of_experience,
            future_aspirations, previous_job_roles
        ) VALUES (
            %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """

        # Define the values tuple
        values = (
            user_type,full_name, email_id, location, education_level, field_or_domain, year_of_passing,
            skills, technical_courses, industry, specific_role, expected_salary_range,
            extracurricular_activities, current_job_role, current_salary, years_of_experience,
            future_aspirations, previous_job_roles
        )

        # Execute the query
        MySQLManager.execute_query(query, values, **CONFIG['database']['vjit'])

        # Flash a success message
        flash("Form submitted successfully!", "success")

    except Exception as e:
        print(f"\nERROR: {str(e)}\n")  # Print any errors that occur
        flash(f"An error occurred: {str(e)}", "danger")

    # Redirect to the success page after processing
    return redirect(url_for('success'))

@app.route('/success')
def success():
    # Fetch user data using the utility function
    user_data, error = get_user_data_by_email()
    
    if error:
        flash(error, "danger")
        return redirect(url_for('index'))

    return render_template('success.html', user_data=user_data)

@app.route('/industry/<industry_name>')
def show_industry(industry_name):
    # Decode the industry name to handle HTML entities
    decoded_industry = Markup(industry_name).unescape()
    return render_template('industry.html', industry_name=decoded_industry)

@app.route('/api/job_roles')
def get_job_roles():
    sub_industry = request.args.get('sub_industry')
    if not sub_industry:
        return jsonify({"error": "Missing sub_industry parameter"}), 400

    decoded_sub_industry = Markup(sub_industry).unescape()
    print(f"Fetching job roles for sub-industry: {decoded_sub_industry}")

    try:
        # Make sure this import works from the RAG/src/roadmaps
        from roadmaps.fetch_jobs_by_industry import search_job_roles_by_industry
        job_roles = search_job_roles_by_industry(decoded_sub_industry)
        return jsonify({"job_roles": job_roles})
    except Exception as e:
        print(f"Import Error: {str(e)}")
        return jsonify({
            "error": "Failed to import or execute function",
            "details": str(e)
        }), 500

@app.route('/roadmap/<job_role>')
def show_roadmap(job_role):
    # Decode the job role to handle HTML entities
    decoded_job_role = Markup(job_role).unescape()
    return render_template('roadmap.html', job_role=decoded_job_role)

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No data provided',
                'details': 'Request body is empty or not valid JSON'
            }), 400
            
        user_message = data.get('message', '')
        if not user_message:
            return jsonify({
                'error': 'No message provided',
                'details': 'Message field is required'
            }), 400
        
        # Get session ID (using user's email or a random ID if not available)
        session_id = session.get('user_email', 'default_session')
        print(f"\n=== Chat Session Info ===")
        print(f"Session ID: {session_id}")
        print("=======================\n")
        
        try:
            # Get user data from session or fetch if not available
            user_data = session.get('user_profile_data')
            if user_data is None:
                print("\n=== Fetching User Data ===")
                user_data, error = get_user_data_by_email()
                
                if error:
                    print(f"⚠️ Warning: Could not fetch user data: {error}")
                    print("Will proceed without personalization")
                    user_data = None
                else:
                    if user_data and len(user_data) > 0:
                        print("✅ Successfully fetched user data:")
                        print("\n=== User Profile Data ===")
                        for key, value in user_data[0].items():
                            print(f"{key}: {value}")
                        print("=======================\n")
                        # Store user data in session
                        session['user_profile_data'] = user_data
                    else:
                        print("⚠️ No user data found in database")

            
            response = get_assistant_response(
                user_message, 
                session_id, 
                ollama_llm,
                memory,
                user_data
            )
            memory.save_context(
                {"input": user_message},
                {"output": response}
            )
            
            # Log the response for debugging
            print(f"🤖 Assistant response: {response}")
            
            if not response:
                return jsonify({
                    'error': 'Empty response',
                    'details': 'The AI assistant returned an empty response'
                }), 500
            
            return jsonify({
                'response': response,
                'status': 'success'
            })
            
        except ImportError as e:
            print(f"Import error details: {str(e)}")
            return jsonify({
                'error': 'Import Error',
                'details': f"The AI assistant module could not be loaded: {str(e)}"
            }), 500
            
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'Server Error',
            'details': f"An unexpected error occurred: {str(e)}"
        }), 500

@app.route('/api/roadmap/<job_role>')
def get_roadmap(job_role):
    try:
        # Get the original role name from header if available
        original_role = request.headers.get('X-Original-Role', job_role)
        
        # Decode the job role to handle HTML entities and URL encoding
        decoded_job_role = Markup(job_role).unescape()
        print(f"Generating roadmap for job role: {decoded_job_role}")
        print(f"Original job role: {original_role}")
        
        # Clean up the role name for environment variable
        clean_role = decoded_job_role.replace('/', '-').replace(',', '').strip()
        os.environ["SELECTED_JOB_ROLE"] = clean_role

        # Construct the path using os.path.join
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "RAG ", "src", "roadmaps", "main.py")
        
        print(f"Current working directory: {os.getcwd()}")
        print(f"Script path: {script_path}")
        
        # Check if script exists
        if not os.path.exists(script_path):
            print(f"Script not found at: {script_path}")
            return jsonify({"error": "Script not found", "details": f"Could not find {script_path}"}), 404

        # Set the working directory to the script's directory
        script_dir = os.path.dirname(script_path)
        original_dir = os.getcwd()
        os.chdir(script_dir)
        
        try:
            print(f"Changed working directory to: {os.getcwd()}")
            print("Starting roadmap generation...")
            
            # Run the script with output capture
            result = subprocess.run(
                ["python3", "main.py"],
                check=True,
                capture_output=True,
                text=True,
                env=os.environ.copy() 
                 # Pass current environment variables
            )
            
            if result.stdout:
                print("Script output:", result.stdout)
            if result.stderr:
                print("Script errors:", result.stderr)
                
            # Read the markdown file generated by the crew
            roadmap_path = os.path.join(script_dir, "career_info.md")
            print(f"Looking for roadmap file at: {roadmap_path}")
            
            # Wait for file to be generated with retries
            max_retries = 30
            retries = 0
            while retries < max_retries:
                if os.path.exists(roadmap_path):
                    try:
                        with open(roadmap_path, "r", encoding="utf-8") as f:
                            markdown_text = f.read()
                            if markdown_text.strip():
                                print(f"Successfully read roadmap file after {retries} retries")
                                return jsonify({"markdown": markdown_text})
                    except Exception as e:
                        print(f"Error reading file: {str(e)}")
                
                print(f"Waiting for file to be generated (attempt {retries + 1}/{max_retries})")
                time.sleep(1)
                retries += 1
            
            raise FileNotFoundError(f"Timeout waiting for roadmap file at {roadmap_path}")
            
        finally:
            # Always restore the original working directory
            os.chdir(original_dir)
            print(f"Restored working directory to: {os.getcwd()}")

    except subprocess.CalledProcessError as e:
        print(f"Script execution failed: {str(e)}")
        if hasattr(e, 'stdout'):
            print("Script output:", e.stdout)
        if hasattr(e, 'stderr'):
            print("Script errors:", e.stderr)
        return jsonify({
            "error": "Failed to generate roadmap",
            "details": str(e),
            "stdout": e.stdout if hasattr(e, 'stdout') else None,
            "stderr": e.stderr if hasattr(e, 'stderr') else None
        }), 500

    except Exception as e:
        print(f"Unexpected error in get_roadmap: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e),
            "type": type(e).__name__
        }), 500

def get_user_data_by_email():
    email = session.get('user_email')
    if not email:
        return None, "Email not found in session"

    try:
        # Query the database for the user with the given email
        query = "SELECT * FROM users WHERE email_id = %s"
        result = MySQLManager.execute_query(query, (email,), **CONFIG['database']['vjit'])
        if result:
            # Filter out fields that are None
            filtered_result = [{k: v for k, v in user.items() if v is not None} for user in result]
            return filtered_result, None
        else:
            return None, "User not found"

    except Exception as e:
        print(f"Database error: {str(e)}")  # Debugging line
        return None, str(e)

if __name__ == '__main__':
    print("Starting Flask application...")
    print("Access the application at:")
    print("- Local: http://localhost:5001")
    print("- Network: http://0.0.0.0:5001")
    app.run(debug=True, port=5001, host='0.0.0.0', use_reloader=False)
