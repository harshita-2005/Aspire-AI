# Pathly-AI Career Guidance Platform

## Introduction
This project is an AI-powered career guidance platform that helps users explore career paths, get personalized roadmaps, and receive AI-driven career advice. The platform is designed to assist various user types including students, freelancers, professionals, and career shifters in making informed decisions about their career paths.

## Features
- User profiling and data collection
- Industry-specific career exploration
- AI-powered chatbot for career guidance
- Personalized career roadmaps
- Job role recommendations
- Interactive career path visualization

## Tech Stack
- **Backend Framework**: Flask 3.0.0
- **AI/ML Components**:
  - LangChain for AI model integration
  - Ollama for local LLM deployment
  - Transformers for advanced NLP tasks
- **Database**: MySQL
- **Vector Database**: Pinecone for semantic search
- **Frontend**: HTML, CSS, JavaScript
- **Additional Libraries**:
  - NumPy for numerical operations
  - PyTorch for deep learning capabilities
  - Python-dotenv for environment management

## Project Structure
```
src/
├── app.py              # Main application file
├── aspire_ai/         # Core AI components
├── RAG/               # Retrieval Augmented Generation system
└── Data/              # Data storage and management
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/harshita-2005/Pathly.git
cd Pathly
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Important:**
After activating your virtual environment, always make sure you are using the correct pip and python. Run:
```bash
which python
which pip
```
Both should point to your `env` (or `venv`) directory, e.g.:
```
/path/to/your/project/env/bin/python
/path/to/your/project/env/bin/pip
```
If not, use:
```bash
/path/to/your/project/env/bin/pip install <package>
```
This ensures all packages (like crewai) are installed in the virtual environment, not globally.

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

---

## Install CrewAI CLI and Python Package (separately, in terminal)

After installing the main requirements, install CrewAI CLI and its dependencies using the following commands in your terminal:

1. Install UV (Universal Virtualenv/Package Manager):
   - On macOS/Linux:
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   - On Windows (PowerShell):
     ```powershell
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```

2. Install CrewAI CLI:
   ```bash
   uv tool install crewai
   ```

3. (If you see a Command 'uv' not found):
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   uv tool install crewai
   ```
     pip install crewai
4. Verify CrewAI CLI installation:
   ```bash
   uv tool list
   ```
   You should see `crewai` in the list.

6. Install CrewAI as a Python package (for import in code):
   ```bash
   pip install crewai
   ```


---

**Install Ollama:**
Before pulling a model, you must install Ollama from [https://ollama.com/download](https://ollama.com/download) and ensure the `ollama` command is available in your terminal.

**Pull the required Ollama model:**
After installing Ollama, download the required model (e.g., llama3.1) with:
```bash
ollama pull llama3.1
```
4. Run the application:
```bash
cd src
python3 app.py
```

## Usage Flow
1. Users start at the landing page where they can select their user type
2. Fill out a detailed profile form with education, experience, and career goals
3. Explore different industries and job roles
4. Get personalized career roadmaps
5. Interact with the AI chatbot for career guidance
6. View and download career path recommendations

## Key Components
- **User Profiling**: Collects comprehensive user data to provide personalized recommendations
- **Career Exploration**: Interactive interface to explore different industries and roles
- **AI Chatbot**: Powered by LangChain and Ollama for intelligent career guidance
- **Roadmap Generation**: Creates detailed career paths based on user profiles and goals
- **Database Integration**: Secure storage of user data and career information

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
