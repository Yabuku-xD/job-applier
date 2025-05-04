import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict, List
import time
import json
from google import genai
# Using the new Google GenAI SDK

class JobSearcher:
    def __init__(self, resume_data: Dict, gemini_model=None):
        self.resume_data = resume_data
        self.driver = webdriver.Chrome()
        self.model = gemini_model
        
    def search_jobs(self, keywords: List[str], location: str) -> List[Dict]:
        jobs = []
        
        # Search on LinkedIn
        linkedin_jobs = self._search_linkedin(keywords, location)
        jobs.extend(linkedin_jobs)
        
        # Search on Indeed
        indeed_jobs = self._search_indeed(keywords, location)
        jobs.extend(indeed_jobs)
        
        return jobs
    
    def _search_linkedin(self, keywords: List[str], location: str) -> List[Dict]:
        """Search for jobs on LinkedIn"""
        jobs = []
        
        for keyword in keywords:
            search_query = f"{keyword} {location}"
            encoded_query = search_query.replace(' ', '%20')
            url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}"
            
            try:
                self.driver.get(url)
                time.sleep(3)  # Wait for page to load
                
                # Scroll down to load more jobs
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                
                # Extract job listings
                job_cards = self.driver.find_elements(By.CLASS_NAME, "job-card-container")
                
                for card in job_cards:
                    try:
                        title_elem = card.find_element(By.CLASS_NAME, "job-card-list__title")
                        company_elem = card.find_element(By.CLASS_NAME, "job-card-container__company-name")
                        link_elem = card.find_element(By.CSS_SELECTOR, "a.job-card-list__title")
                        
                        job = {
                            'title': title_elem.text,
                            'company': company_elem.text,
                            'url': link_elem.get_attribute('href'),
                            'source': 'LinkedIn',
                            'description': self._get_job_description(link_elem.get_attribute('href'))
                        }
                        
                        jobs.append(job)
                    except Exception as e:
                        print(f"Error extracting LinkedIn job: {str(e)}")
            
            except Exception as e:
                print(f"Error searching LinkedIn: {str(e)}")
        
        return jobs
    
    def _search_indeed(self, keywords: List[str], location: str) -> List[Dict]:
        """Search for jobs on Indeed"""
        jobs = []
        
        for keyword in keywords:
            search_query = f"{keyword} {location}"
            encoded_query = search_query.replace(' ', '+')
            url = f"https://www.indeed.com/jobs?q={encoded_query}"
            
            try:
                self.driver.get(url)
                time.sleep(3)  # Wait for page to load
                
                # Extract job listings
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".jobsearch-ResultsList > .result")
                
                for card in job_cards:
                    try:
                        title_elem = card.find_element(By.CSS_SELECTOR, "h2.jobTitle")
                        company_elem = card.find_element(By.CSS_SELECTOR, ".companyName")
                        link_elem = title_elem.find_element(By.TAG_NAME, "a")
                        
                        job = {
                            'title': title_elem.text,
                            'company': company_elem.text,
                            'url': "https://www.indeed.com" + link_elem.get_attribute('href'),
                            'source': 'Indeed',
                            'description': self._get_job_description("https://www.indeed.com" + link_elem.get_attribute('href'))
                        }
                        
                        jobs.append(job)
                    except Exception as e:
                        print(f"Error extracting Indeed job: {str(e)}")
            
            except Exception as e:
                print(f"Error searching Indeed: {str(e)}")
        
        return jobs
    
    def _get_job_description(self, url: str) -> str:
        """Get the full job description from the job detail page"""
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for page to load
            
            # Different sites have different selectors for job descriptions
            description = ""
            
            # Try different common selectors
            selectors = [
                ".description", ".job-description", "#job-description",
                ".jobDescriptionText", ".job-desc", "#jobDescriptionText"
            ]
            
            for selector in selectors:
                try:
                    desc_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    description = desc_elem.text
                    if description:
                        break
                except:
                    continue
            
            return description
        
        except Exception as e:
            print(f"Error getting job description: {str(e)}")
            return ""
    
    def filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        # Use Gemini to filter jobs based on resume match
        filtered_jobs = []
        
        for job in jobs:
            if not job['description']:
                continue  # Skip jobs with no description
                
            prompt = f"""
            Based on this resume data: {self.resume_data}
            And this job description: {job['description']}
            
            Rate the match from 1-10 and explain why. Return your response in JSON format with the following structure:
            {{
                "score": <number between 1-10>,
                "explanation": "<your explanation>"
            }}
            """
            
            try:
                response = self.model.generate_content(prompt)
                result = json.loads(response.text)
                
                # Add score and explanation to job data
                job['match_score'] = result.get('score', 0)
                job['match_explanation'] = result.get('explanation', '')
                
                # Filter jobs with a score of 6 or higher
                if job['match_score'] >= 6:
                    filtered_jobs.append(job)
                    print(f"Found matching job: {job['title']} at {job['company']} (Score: {job['match_score']})")
            except Exception as e:
                print(f"Error analyzing job match: {str(e)}")
                # If there's an error, include the job anyway to avoid missing opportunities
                job['match_score'] = 5  # Default middle score
                job['match_explanation'] = "Error analyzing match"
                filtered_jobs.append(job)
        
        # Sort jobs by match score (highest first)
        filtered_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        return filtered_jobs