from typing import Dict, List
from resume_parser import ResumeParser
from job_search import JobSearcher
from auto_apply import ApplicationAutomator
import os
import time

class JobApplicationBot:
    def __init__(self, gemini_api_key: str, resume_path: str):
        self.gemini_api_key = gemini_api_key
        self.resume_path = resume_path
        self.resume_parser = ResumeParser(gemini_api_key)
        self.resume_data = self.resume_parser.parse_resume(resume_path)
        # Add resume path to resume data for file uploads
        self.resume_data['resume_path'] = os.path.abspath(resume_path)
        self.job_searcher = JobSearcher(self.resume_data, self.resume_parser.model)
        self.app_automator = ApplicationAutomator(self.resume_data, self.resume_parser.model)
    
    def run(self, job_keywords: List[str], location: str, max_applications: int = 10):
        print(f"\nStarting job search for: {', '.join(job_keywords)} in {location}")
        
        # Search for jobs
        print("Searching for jobs...")
        jobs = self.job_searcher.search_jobs(job_keywords, location)
        print(f"Found {len(jobs)} job postings")
        
        if not jobs:
            print("No jobs found. Please try different keywords or location.")
            return
        
        # Filter jobs based on match
        print("\nAnalyzing job matches against your resume...")
        filtered_jobs = self.job_searcher.filter_jobs(jobs)
        print(f"Found {len(filtered_jobs)} matching jobs")
        
        if not filtered_jobs:
            print("No matching jobs found. Please try different keywords or location.")
            return
        
        # Display top matches
        print("\nTop job matches:")
        for i, job in enumerate(filtered_jobs[:5], 1):
            print(f"{i}. {job['title']} at {job['company']} - Match Score: {job['match_score']}/10")
            print(f"   Reason: {job['match_explanation'][:100]}...")
        
        # Apply to jobs
        print(f"\nStarting application process for up to {max_applications} jobs...")
        applied_count = 0
        for i, job in enumerate(filtered_jobs[:max_applications], 1):
            print(f"\nApplying to job {i}/{min(max_applications, len(filtered_jobs))}: {job['title']} at {job['company']}")
            try:
                success = self.app_automator.fill_application(job['url'])
                if success:
                    applied_count += 1
                    print(f"✓ Successfully applied to: {job['title']} at {job['company']}")
                else:
                    print(f"✗ Could not complete application for: {job['title']} at {job['company']}")
            except Exception as e:
                print(f"✗ Failed to apply to {job['title']}: {str(e)}")
            
            # Wait between applications to avoid being detected as a bot
            if i < min(max_applications, len(filtered_jobs)):
                print("Waiting before next application...")
                time.sleep(5)
        
        print(f"\nCompleted {applied_count} applications out of {min(max_applications, len(filtered_jobs))} attempts")
        print("Thank you for using the Automated Job Application Bot!")
        
        # Clean up
        self.job_searcher.driver.quit()
        self.app_automator.driver.quit()