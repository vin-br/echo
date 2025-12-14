# ARC

AI Radiology Copilot (ARC) 

Web-based app to detect brain tumors from MRI images using a Convolutional Neural Network (CNN) model. 

## Overview

### Demo

Check out this [video](path/to/demo.mp4) for a demonstration on how to start and use the app.

### Visuals

<img src="path/to/screenshot_1.png" style="width: 100%; height: auto;">

<img src="path/to/screenshot_3.png" style="width: 100%; height: auto;">

## Installation

### Option A - Using Docker (recommended)

1. Make sure you have [Docker](https://www.docker.com/get-started/) installed on your machine.
2. Clone this repository.
3. Navigate to the project root directory.
4. Run the following command to build the containers: ```docker compose build --no-cache```
5. Start the containers using: ```docker compose up -d```
6. Access the app at: ```http://localhost:8000```
7. To stop the containers, run: ```docker compose down```
8. To view logs, use: ```docker compose logs -f```
   
### Option B - Local Dev setup

**Installation steps to set up the project locally using Poetry:**
1. Make sure you have Python 3.14+ and pip installed on your machine.
2. Clone this repository.
3. Navigate to the project root directory.
4. Install poetry with curl -sSL https://install.python-poetry.org | python3 -
5. Set up a virtual environment: ```poetry config virtualenvs.in-project true```
6. Install the dependencies: ```poetry install```
7. Activate the virtual environment with poetry: ```poetry env activate``` or alternatively: ```source .venv/bin/activate``` (Linux/Mac) or ```.venv\Scripts\activate``` (Windows)

**Run FastAPI app:**
- Use FastAPI's uvicorn command to start the project from root: ```uvicorn backend.app.main:app --reload```.

## Unit testing

- Run the following command to automatically test the app: ```./manage.py test --pattern="tests_*.py" ```

## Resources

### Datasets

A combination of these datasets:
- [dataset 1](https://www.kaggle.com/datasets/sartajbhuvaji/brain-tumor-classification-mri)
- [dataset 2](https://www.kaggle.com/datasets/thomasdubail/brain-tumors-256x256/data)
- [dataset 3](https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset?rvi=1)

Steps taken to clean the dataset:
1. Duplicates were removed. 
2. Files automatically renamed. 
3. Images were shuffled.
4. Images were split between training and testing (0.80/0.20).

## Disclamer

This project is built for training and learning purposes, do not use it for real use cases.