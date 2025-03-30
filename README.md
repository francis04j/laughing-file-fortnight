# README #

Job Application and CV Uploader API

## What's this repository for?

This repository is for the API that takes job application and CV from a frontend, upload it into a storage and save the details in the database

Version: 0.0

### How do i set it up?

1. Open Terminal and Navigate to Your Project Folder
cd /path/to/your/project
2. Create a Virtual Environment - so that your application dependencies dont conflict and your application build is reproducible and consistent
python3 -m venv venv
3. Activate the Virtual Environment
source venv/bin/activate
4. Install Required Packages
pip install fastapi uvicorn boto3 python-multipart
5. Generate requirements.txt - so that It provides a consistent environment and makes collaboration easier.
pip freeze > requirements.txt
6. Deactivate Environment When Done

### Alternative: use makefile
Usage
From your project root, run:

make setup       # One-stop setup
make install     # If you already have requirements.txt
make freeze      # Save current deps to requirements.txt
make clean       # Remove the venv
⚠️ The source command works in bash/zsh.
