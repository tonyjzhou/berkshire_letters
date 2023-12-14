#!/usr/bin/env python3


import argparse
import logging
import os
import zipfile

import requests
from bs4 import BeautifulSoup


def setup_logging(debug_mode):
    """Set up logging configuration."""
    if debug_mode:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def get_soup(url):
    """Fetch and parse HTML content from the given URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    if response.status_code == 403:
        logging.error("Access to the page is forbidden.")
        return None
    return BeautifulSoup(response.text, 'html.parser')


def extract_letter_links(soup):
    """Extract and return letter links from the soup object."""
    return [link.get('href') for link in soup.find_all('a') if link.get('href') and link.get('href').endswith('.pdf')]


def download_letters(letter_links, letters_dir):
    """Download each letter from the list of letter links."""
    for letter_link in letter_links:
        letter_url = 'https://www.berkshirehathaway.com/letters/' + letter_link
        letter_response = requests.get(letter_url)
        if letter_response.status_code == 200:
            letter_path = os.path.join(letters_dir, os.path.basename(letter_link))
            with open(letter_path, 'wb') as file:
                file.write(letter_response.content)


def create_zip_file(source_dir, zip_path):
    """Create a zip file from all files in the source directory."""
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                zipf.write(os.path.join(root, file), file)


def main():
    parser = argparse.ArgumentParser(description='Download Berkshire Hathaway letters and zip them.')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode with verbose output.')
    args = parser.parse_args()

    setup_logging(args.debug)

    logging.info("Starting script...")
    url = "https://www.berkshirehathaway.com/letters/letters.html"
    letters_dir = 'Berkshire_Hathaway_Letters'
    zip_path = 'Berkshire_Hathaway_Letters.zip'

    os.makedirs(letters_dir, exist_ok=True)
    logging.debug("Created directory for letters.")

    soup = get_soup(url)
    if soup is None:
        logging.error("Failed to fetch the webpage. Exiting.")
        return

    letter_links = extract_letter_links(soup)
    logging.debug("Extracted letter links.")

    download_letters(letter_links, letters_dir)
    logging.debug("Downloaded all letters.")

    create_zip_file(letters_dir, zip_path)
    logging.info("All letters have been downloaded and zipped in %s", zip_path)


if __name__ == "__main__":
    main()
