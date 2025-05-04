#!/usr/bin/env python
# demo.py - Example script to demonstrate the job application bot

from app import JobApplicationBot
from config import GEMINI_API_KEY, RESUME_PATH

def run_demo():
    print("=== Automated Job Application Bot Demo ===")
    print("This script demonstrates how to use the JobApplicationBot programmatically")
    
    # Initialize the bot with your API key and resume
    bot = JobApplicationBot(GEMINI_API_KEY, RESUME_PATH)
    
    # Example 1: Search for Data Analyst positions in Seattle
    print("\nExample 1: Searching for Data Analyst positions in Seattle")
    bot.run(
        job_keywords=["Data Analyst"], 
        location="Seattle, WA",
        max_applications=2  # Limit to 2 applications for demo
    )
    
    # Example 2: Search for multiple job titles in a different location
    print("\nExample 2: Searching for Data Analyst Intern positions in Seattle")
    bot.run(
        job_keywords=["Data Analyst Intern"], 
        location="Seattle, WA",
        max_applications=1  # Limit to 1 application for demo
    )

if __name__ == "__main__":
    run_demo()