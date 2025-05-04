# Automated Job Application Bot

This project is an AI-powered automated job application system that uses the Gemini API to help you apply for jobs without manual intervention. The system parses your resume, searches for relevant job postings, evaluates job matches against your qualifications, and automatically fills out application forms.

## Features

- **Resume Parsing**: Extracts key information from your PDF resume using Gemini AI
- **Job Search**: Scrapes job listings from popular job boards like LinkedIn and Indeed
- **Job Matching**: Uses AI to evaluate how well your qualifications match job requirements
- **Automated Application**: Fills out application forms automatically using your resume data
- **Command-line Interface**: Easy to use with customizable parameters

## Requirements

- Python 3.8+
- Google Gemini API key
- Chrome browser (for Selenium WebDriver)
- PDF resume file

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Download and install ChromeDriver for your version of Chrome browser

## Configuration

Edit the `config.py` file to set your default configuration:

```python
GEMINI_API_KEY = "your-gemini-api-key"
RESUME_PATH = "path/to/your/resume.pdf"
JOB_KEYWORDS = ["Job Title 1", "Job Title 2"]
LOCATION = "City, State"
```

## Usage

Run the application with default settings:

```bash
python main.py
```

Or customize the parameters:

```bash
python main.py --resume "path/to/resume.pdf" --keywords "Data Analyst" "Data Scientist" --location "Seattle, WA" --max 5
```

### Command-line Arguments

- `--resume`: Path to your resume PDF file
- `--keywords`: Job keywords to search for (can specify multiple)
- `--location`: Job location to search in
- `--max`: Maximum number of applications to submit
- `--api-key`: Gemini API key (if not set in config.py)

## How It Works

1. **Resume Parsing**: The system extracts structured data from your PDF resume using the Gemini API
2. **Job Search**: It searches for jobs matching your keywords and location on LinkedIn and Indeed
3. **Job Matching**: Each job description is analyzed against your resume to determine match quality
4. **Application**: For matching jobs, the system automatically fills out application forms

## Components

- `resume_parser.py`: Extracts structured data from your PDF resume
- `job_search.py`: Searches job boards and evaluates job matches
- `auto_apply.py`: Automates the application form filling process
- `app.py`: Main application class that coordinates the process
- `main.py`: Command-line interface

## Limitations

- Some job application systems may have anti-bot measures that prevent automation
- Complex application forms with custom fields may not be fully supported
- The system works best with standard application forms

## Disclaimer

This tool is for educational purposes only. Use responsibly and in accordance with the terms of service of job boards and application systems.