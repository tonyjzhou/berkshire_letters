#!/usr/bin/env python3

import argparse
import logging
import os
import zipfile
import requests
from bs4 import BeautifulSoup

# Constants
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
BASE_URL = "https://www.berkshirehathaway.com"
LETTERS_PAGE = BASE_URL + "/letters/letters.html"
LETTERS_DIR = 'Berkshire_Hathaway_Letters'
ZIP_PATH = 'Berkshire_Hathaway_Letters.zip'
SMALL_FILE_SIZE = 3 * 1024  # 3KB


def setup_logging(debug_mode):
    """Set up logging configuration."""
    level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')


def get_soup(url):
    """Fetch and parse HTML content from the given URL."""
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None


def extract_letter_links(soup):
    """Extract and return letter links from the soup object."""
    letter_links = [link.get('href') for link in soup.find_all('a') if
                    link.get('href') and (link.get('href').endswith('.pdf') or link.get('href').endswith('.html'))]
    return letter_links


def is_small_html_file(response):
    """Check if the response is a small HTML file that likely contains indirect links."""
    return response.url.endswith('.html') and len(response.content) < SMALL_FILE_SIZE


def download_file(url, headers):
    """Download a file from the URL and return the response object."""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        logging.error(f"Error occurred while downloading {url}: {e}")
        return None


def save_file(response, letters_dir):
    """Save the content of the response to a file."""
    if response:
        file_url = response.url
        letter_path = os.path.join(letters_dir, os.path.basename(file_url))
        mode = 'wb' if file_url.endswith('.pdf') else 'w'
        content = response.content if mode == 'wb' else response.text

        with open(letter_path, mode) as file:
            file.write(content)
        logging.info(f"Downloaded and saved {file_url} to {letter_path}")


def download_letters(letter_links, letters_dir):
    """Download each letter from the list of letter links and log possible errors."""
    headers = {'User-Agent': USER_AGENT}

    for letter_link in letter_links:
        letter_url = BASE_URL + "/letters/" + letter_link if not letter_link.startswith('http') else letter_link
        if letter_link.startswith('/'):
            letter_url = BASE_URL + letter_link

        letter_response = download_file(letter_url, headers)
        if is_small_html_file(letter_response):
            logging.debug(f"Looking for actual links for {letter_url}")
            actual_links = extract_letter_links(BeautifulSoup(letter_response.text, 'html.parser'))
            for actual_link in actual_links:
                actual_url = BASE_URL + "/letters/" + actual_link if not actual_link.startswith(
                    'http') else actual_link
                if BASE_URL in actual_url:
                    save_file(download_file(actual_url, headers), letters_dir)
        else:
            save_file(letter_response, letters_dir)


def create_zip_file(source_dir, zip_path):
    """Create a zip file from all files in the source directory."""
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), file)
            logging.info(f"Created zip file at {zip_path}")
    except Exception as e:
        logging.error(f"Failed to create zip file: {e}")


def main():
    parser = argparse.ArgumentParser(description='Download Berkshire Hathaway letters and zip them.')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with verbose output.')
    args = parser.parse_args()

    setup_logging(args.debug)

    logging.info("Starting script...")

    os.makedirs(LETTERS_DIR, exist_ok=True)
    logging.debug("Created directory for letters.")

    soup = get_soup(LETTERS_PAGE)
    if soup is None:
        logging.error("Failed to fetch the webpage. Exiting.")
        return

    letter_links = extract_letter_links(soup)
    logging.debug(f"Extracted letter links: {letter_links}")

    download_letters(letter_links, LETTERS_DIR)
    logging.debug("Downloaded all letters.")

    create_zip_file(LETTERS_DIR, ZIP_PATH)
    logging.info("All letters have been downloaded and zipped in %s", ZIP_PATH)


if __name__ == "__main__":
    main()
