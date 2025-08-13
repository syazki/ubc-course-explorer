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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
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
            
            department_courses = []

            for header in course_headers:
                try:
                    course_info = self.parse_course_from_header(header, department)
                    if course_info:
                        department_courses.append(course_info)
                        print(f"  ✅ Extracted: {course_info['code']} - {course_info['title']}")
                    
                except Exception as e:
                    print(f"  ❌ Error processing course header: {e}")
                    continue
            
            print(f"Successfully extracted {len(department_courses)} courses from {department}")
            return department_courses
        
        except requests.RequestException as e:
            print(f"❌ Error fetching {department} page: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
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

            credits_match = re.search(r'\((\d+)\)', header_text)
            credits = credits_match.group(1) if credits_match else "3"
            
            strong_tag = header.find('strong')
            course_title = strong_tag.get_text().strip() if strong_tag else "No title available"
            
            description_p = header.find_next_sibling('p')
            if not description_p:
                parent = header.parent
                if parent:
                    description_p = parent.find_next('p')
            
            description = "No description available"
            prerequisites = "None listed"

            if description_p:
                desc_text = description_p.get_text().strip()

                prereq_indicators = [
                    "Prerequisite",
                    "Corequisite", 
                    "Not for students",
                    "Restricted to",
                    "Permission required"
                ]

                prereq_start = -1
                for indicator in prereq_indicators:
                    pos = desc_text.find(indicator)
                    if pos != -1:
                        if prereq_start == -1 or pos < prereq_start:
                            prereq_start = pos
                
                if prereq_start != -1:
                    description = desc_text[:prereq_start].strip()
                    prerequisites = desc_text[prereq_start:].strip()
                else:
                    description = desc_text
                
                description = re.sub(r'\[\d+-\d+-\d+\]\s*$', '', description).strip()
                
                if not description or len(description) < 20:
                    sentences = desc_text.split('.')
                    description = sentences[0] + '.' if sentences else desc_text[:100]
            
            return {
                'code': course_code,
                'title': course_title,
                'department': department,
                'url': f"{self.base_url}/course-descriptions/subject/{department.lower()}v",
                'description': description,
                'credits': credits,
                'prerequisites': prerequisites
            }
            
        except Exception as e:
            print(f"Error parsing course header: {e}")
            return None
    

    def scrape_all_courses(self, departments=None, limit_per_dept=None):
        """
        Main method to scrape courses from specified departments
        """
        if departments is None:
            departments = ['CPSC', 'MATH', 'ENGL']
        
        print(f"🚀 Starting to scrape {len(departments)} departments...")
        
        for i, dept in enumerate(departments):
            print(f"\n📚 Progress: {i+1}/{len(departments)} - Processing {dept}")
            
            dept_courses = self.scrape_department_courses(dept)
            
            if limit_per_dept and len(dept_courses) > limit_per_dept:
                dept_courses = dept_courses[:limit_per_dept]
                print(f"   Limited to {limit_per_dept} courses")
            
            self.courses_data.extend(dept_courses)

            time.sleep(2)
        
        print(f"✅ Scraping complete! Found {len(self.courses_data)} total courses.")
        return self.courses_data

    def save_to_file(self, filename='../data/courses.json'):
        """
        Save scraped course data to JSON file
        """
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.courses_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Data saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving data: {e}")

    def load_from_file(self, filename='../data/courses.json'):
        """
        Load previously scraped data from JSON file
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.courses_data = json.load(f)
            print(f"✅ Loaded {len(self.courses_data)} courses from {filename}")
            return self.courses_data
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return []

# Test the scraper
if __name__ == "__main__":
    print("🎓 UBC Course Scraper - Fixed Version")
    print("=" * 50)
    
    scraper = UBCCourseScraper()
    
    print("Testing with CPSC...")
    courses = scraper.scrape_all_courses(departments=['CPSC'], limit_per_dept=5)
    
    if courses:
        print(f"\n🎉 SUCCESS! Found {len(courses)} courses")
        
        # Save the data
        scraper.save_to_file()
        
        # Display results
        print(f"\n📚 COURSE DETAILS:")
        for course in courses:
            print(f"\n{'='*60}")
            print(f"📖 {course['code']}: {course['title']}")
            print(f"💳 Credits: {course['credits']}")
            print(f"📝 Description: {course['description']}")
            print(f"📋 Prerequisites: {course['prerequisites']}")
    else:
        print("❌ No courses found - check the parsing logic")
    
    print(f"\n Done!")

