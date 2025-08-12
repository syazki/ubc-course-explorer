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
