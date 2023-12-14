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
    letter_links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and (href.endswith('.pdf') or href.endswith('.html')):
            letter_links.append(href)
    return letter_links


def download_letters(letter_links, letters_dir):
    """Download each letter from the list of letter links and log possible errors."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    for letter_link in letter_links:
        letter_url = 'https://www.berkshirehathaway.com/letters/' + letter_link
        try:
            letter_response = requests.get(letter_url, headers=headers)
            letter_response.raise_for_status()  # Raises HTTPError for bad HTTP responses

            letter_path = os.path.join(letters_dir, os.path.basename(letter_link))
            mode = 'wb' if letter_link.endswith('.pdf') else 'w'
            content = letter_response.content if letter_link.endswith('.pdf') else letter_response.text

            with open(letter_path, mode) as file:
                file.write(content)
            logging.info(f"Downloaded and saved {letter_link}")
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred while downloading {letter_link}: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.error(f"Connection error occurred while downloading {letter_link}: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logging.error(f"Timeout error occurred while downloading {letter_link}: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Request error occurred while downloading {letter_link}: {req_err}")
        except IOError as io_err:
            logging.error(f"IO error occurred while writing {letter_link}: {io_err}")
        except Exception as e:
            logging.error(f"An unexpected error occurred while downloading or writing {letter_link}: {e}")


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
    logging.debug(f"Extracted letter links: {letter_links}")

    download_letters(letter_links, letters_dir)
    logging.debug("Downloaded all letters.")

    create_zip_file(letters_dir, zip_path)
    logging.info("All letters have been downloaded and zipped in %s", zip_path)


if __name__ == "__main__":
    main()
