# main.py
import argparse
import sys
from app import JobApplicationBot
from config import GEMINI_API_KEY, RESUME_PATH, JOB_KEYWORDS, LOCATION

def main():
    parser = argparse.ArgumentParser(description='Automated Job Application Bot')
    parser.add_argument('--resume', type=str, default=RESUME_PATH,
                        help='Path to your resume PDF file')
    parser.add_argument('--keywords', type=str, nargs='+', default=JOB_KEYWORDS,
                        help='Job keywords to search for')
    parser.add_argument('--location', type=str, default=LOCATION,
                        help='Job location to search in')
    parser.add_argument('--max', type=int, default=10,
                        help='Maximum number of applications to submit')
    parser.add_argument('--api-key', type=str, default=GEMINI_API_KEY,
                        help='Gemini API key')
    
    args = parser.parse_args()
    
    print("=== Automated Job Application Bot ===")
    print(f"Resume: {args.resume}")
    print(f"Keywords: {args.keywords}")
    print(f"Location: {args.location}")
    print(f"Max Applications: {args.max}")
    print("====================================")
    
    try:
        bot = JobApplicationBot(args.api_key, args.resume)
        bot.run(args.keywords, args.location, max_applications=args.max)
        print("\nJob application process completed successfully!")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()