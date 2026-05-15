
# Internet Archive Bulk Uploader GUI

A simple, dark-mode desktop application built in Python to bulk upload a folder of files directly to the Internet Archive (archive.org) without using the browser interface.

## Prerequisites

Make sure you have Python installed, then run the following command in your Command Prompt to install the required libraries (cmd):

`pip install internetarchive customtkinter`


## How to Run

1. Save the python script as `ia_uploader.py`.
2. Open your Command Prompt, navigate to the folder where you saved the file, and run: `python ia_uploader.py`

## Uploading

* **Unique Item Identifier:** This forms the URL of your item page (`archive.org/details/your-identifier`). 
* **Length Rule:** It must be **at least 5 characters long** (up to 100 characters). Short terms like `pidi` will be rejected by the server.
* **Uniqueness:** It must be completely unique across the entire Internet Archive. If someone else has used it, your upload will fail. Try adding your username or a date to make it unique (e.g., `alf-audio-collection-pidi`).
* **Special Characters:** The app automatically cleans this field to lowercase letters, numbers, hyphens, and periods to match Internet Archive naming rules.
