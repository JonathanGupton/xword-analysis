"""Module containing functions for walking and scraping the crossword site."""
import time

import requests
from bs4 import BeautifulSoup


BASE_URL = r"https://nytcrosswordanswers.org"
SITEMAP_URL = r"/sitemap_index.xml"


def request_with_exponential_backoff(url, max_retries=10, backoff_factor=1) -> requests.Response | None:
    """Make a request with exponential backoff.

    Args:
        url (str): The URL to request.
        max_retries (int): Maximum number of retries.
        backoff_factor (int): Factor by which the delay increases.

    Returns:
        Response object or None if all retries fail.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            return response
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Failed after {max_retries} attempts")
                return None
            delay = backoff_factor * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)


def get_sitemap() -> BeautifulSoup:
    """Get the sitemap from the crossword site"""
    response = request_with_exponential_backoff(BASE_URL + SITEMAP_URL)
    return BeautifulSoup(response.content, features="xml")


# for tag in soup.find_all('loc'):
#     print(tag.text)