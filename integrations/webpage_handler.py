import webbrowser

import requests
from bs4 import BeautifulSoup
import requests


class WebpageHandler:
    def __init__(self):
        # Set a browser-like user-agent to help avoid 403 errors from sites blocking non-browser requests.
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def get_content(self, url):
        """Fetches and returns the text content and links (with hyperlink names) of a webpage given its URL."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text(separator=' ', strip=True)
            links = [{'name': a.get_text(strip=True), 'url': a.get('href')} for a in soup.find_all('a', href=True)]
            return str({'text': text_content, 'links': links})
        except requests.RequestException as e:
            return str(e)

    def open_link(self, url):
        """Opens a link in the default web browser."""
        webbrowser.open(url, new=2)  # new=2: open in a new tab, if possible
