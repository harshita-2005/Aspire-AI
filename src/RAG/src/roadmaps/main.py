import os
import sys
import json
import warnings
from datetime import datetime
from crew import Day5  # type: ignore
from tools.rag_tool import JobSearchTool

warnings.simplefilter("ignore", DeprecationWarning)
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run(job_role: str):
    """
    Run the crew with provided job role for generating roadmap.
    
    Args:
        job_role (str): The job role to generate roadmap for
    """
    
    if not job_role:
        print("Error: Job role cannot be empty")
        return
    
    print(f"\nFetching information for: {job_role}")
    
    try:  
        # Create query using database information
        inputs = {'query': f"Create a career roadmap for {job_role}"}
        
        try:
            print("Initializing Day5 crew...")
            crew = Day5()
            crew.crew().kickoff(inputs=inputs)
        except Exception as e:
            print(f"\nError in crew execution: {str(e)}")
            raise
    except Exception as e:
        print(f"\nError in database operation: {str(e)}")
        raise

# ... existing code ...
if __name__ == "__main__":
    try:
        print("\n=== Environment Information ===")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Python path: {sys.path}")
        
        # Get job role from environment variable
        job_role = os.environ.get("SELECTED_JOB_ROLE")
        if not job_role:
            # Prompt user for input if not set
            job_role = input("Enter the job role to generate roadmap for: ").strip()
        print(f"Retrieved job role: {job_role}")
        
        if not job_role:
            print("\nError: Job role not provided")
            sys.exit(1)
        
        run(job_role)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nDone.")
# ... existing code ...
