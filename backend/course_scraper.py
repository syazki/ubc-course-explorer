import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os

class UBCCourseScraper:
    def __init__(self):
        """
        Initialize the scraper for UBC Vancouver Calendar
        """
        self.base_url = "https://vancouver.calendar.ubc.ca"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.courses_data = []
        
    def scrape_department_courses(self, department):
        """
        Scrape all courses for a specific department from UBC Calendar
        """
        print(f"Scraping courses for {department}...")
        
        dept_lower = department.lower()
        url = f"{self.base_url}/course-descriptions/subject/{dept_lower}v"
        
        try:
            print(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            course_headers = soup.find_all('h3', class_='text-lg')
            print(f"Found {len(course_headers)} course headers")
            
            return course_headers
        
        except requests.RequestException as e:
            print(f"❌ Error fetching {department} page: {e}")
            return []

    def parse_course_from_header(self, header, department):
        """
        Parse course information from an h3 header element
        """
        try:
            header_text = header.get_text()
            code_pattern = f"{department.upper()}_V \d+[A-Z]?"
            code_match = re.search(code_pattern, header_text)
            if not code_match:
                return None
            
            raw_code = code_match.group()
            course_code = raw_code.replace('_V', '')
            
            strong_tag = header.find('strong')
            course_title = strong_tag.get_text().strip() if strong_tag else "No title available"
            
            description_p = header.find_next_sibling('p')
            description = description_p.get_text().strip() if description_p else "No description available"
            
            return {
                'code': course_code,
                'title': course_title,
                'department': department,
                'description': description
            }
        except Exception as e:
            print(f"Error parsing course header: {e}")
            return None

