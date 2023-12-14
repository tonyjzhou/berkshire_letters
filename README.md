
# Berkshire Hathaway Letters Downloader

## Overview
This Python script is designed to automatically download the annual shareholder letters from the Berkshire Hathaway website, save them locally, and then compress them into a zip file. It's a convenient tool for investors, analysts, and enthusiasts who follow Warren Buffett's insights and the performance of Berkshire Hathaway.

## Features
- Downloads all available shareholder letters in PDF and HTML formats.
- Handles indirect links to letters that are not direct downloads.
- Saves letters in a specified directory and compresses them into a single zip file for easy access.
- Offers a debug mode for detailed logging.

## Requirements
- Python 3
- `requests` library
- `beautifulsoup4` library

To install the required libraries, run:
```bash
pip install requests beautifulsoup4
```

## Usage
1. Clone or download this repository.
2. Navigate to the directory containing the script.
3. Run the script using Python 3. For example:
   ```bash
   python berkshire_hathaway_letters_downloader.py
   ```
4. Optionally, enable debug mode for verbose output:
   ```bash
   python berkshire_hathaway_letters_downloader.py --debug
   ```

## How It Works
The script performs the following steps:
1. Sets up logging based on the chosen mode (default or debug).
2. Creates a directory for downloading the letters.
3. Fetches the list of letter links from the Berkshire Hathaway letters webpage.
4. Downloads each letter. If a letter is an HTML file smaller than 3KB (likely an indirect link), it parses that HTML to find the actual letter link and then downloads it.
5. Saves the downloaded letters in the specified directory.
6. Compresses all downloaded letters into a zip file.

## Customization
You can modify the constants at the beginning of the script to change the base URL, directory for letters, or the threshold for small file sizes.

## License
This project is open-source and available under the MIT License.
