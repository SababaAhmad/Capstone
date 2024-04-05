# MADS Capstone Project: A Multifactorial Analysis of Microsoft Corporation’s Stock Price Dynamics

Welcome to the GitHub repository for my Capstone Project. This project aims to explore the impact of various factors on the stock price of Microsoft (MSFT).
These factors include fundamental data, like financial statements, volatility, performance metrics and financial ratios, sentiment from news, social media and earnings call, Congress trades and technical indicators. The main Ensemble notebook is structures as follows:
1. Imports and Installs
2. Download and clean each type of data
3. Join datastes together in a master dataframe
4. Create Random Forest models to get feature importances
5. Create predictive models (baseline, Random Forest and LSTM) to get next day stock price prediction

## Getting Started
These instructions will guide you on how to set up your environment to run the project on your computer.
## Prerequisites
Before running the code, ensure you have Python installed on your system. This project is developed using Python 3.8. 

## Installation
1. Clone the repository:

  To get started, clone this repository to your computer using the following command:

  git clone https://github.com/SababaAhmad/Capstone.git

2. Set up a virtual environment
  Navigate to the project directory and create a virtual environment:
  python -m venv venv
  Activate the virtual environment:
    On Windows: .\venv\Scripts\activate
    On macOS and Linux: source venv/bin/activate

3. Install the required libraries:
   Install all the dependencies listed in requirements.txt by running:
   pip install -r requirements.txt

## Data
The Ensemble.zip file contains the raw data required to run the notebook. Extract this zip file in the project directory to access the datasets.

## Running the Code
There are two main ways to run the project:

Jupyter Notebook: if you prefer using Jupyter Notebooks, open Ensemble.ipynb:
jupyter notebook Ensemble.ipynb

Python Script: you can also run the Python script version of the project:
python ensemble.py

## Data Access
1. Yahoo! Finance: The datasets for stock price data, trading volume and CBOE VIX time series were downloaded from Yahoo! Finance using the yfinance package. This is publicly available and does not require an API key.
2. 
