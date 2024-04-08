# MADS Capstone Project: A Multifactorial Analysis of Microsoft Corporation’s Stock Price Dynamics

Welcome to the GitHub repository for my Capstone Project. This project aims to explore the impact of various factors on the stock price of Microsoft (MSFT).
These factors include fundamental data, like financial statements, volatility, performance metrics and financial ratios, sentiment from news, social media and earnings call, Congress trades and technical indicators. The process for this project is structured as follows:
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
The Ensemble.zip file contains the data required to run the notebook. Extract this zip file in the project directory to access the datasets. Some files are raw (downloaded using API keys from the sources specified in the Data Access section). Other files contain code which is the output of functions with longer runtimes (such as those findBERT model, backwards elimination process, etc.). Some files are also the output results of models. Use pd.read_csv() to read the appropriate files in to the notebook in the specified cells, as stated in the comments of the Ensemble file. 

## Running the Code
The code can be run with a Jupyter notebook or with Google Colab. The collapsing sections feature of Colab may make it easier to navigate the code.

Data_Processing.ipynb is the first notebook to run. This notebook get the raw datasets from CSV files (which were previously downloaded from the sources mentioned in the Data Access section using an API key) and cleans and pre-processes them. These datasets are then joined together in a Master DataFrame.

Models.ipynb is the second notebook to run. This notebook starts off with the Master DataFrame created in Data_Processing.ipynb and runs the various models on the data to obtain the top features and the price forecast.

Keep all the files from the Ensemble.zip file in the directory. Some cells (like finBERT model, Random Forest with Grid Search CV and Backwards Elimination) have long runtimes (+1hour). The output from these executions have been saved in CSV files, which are specified in the cell following the long-runtime cell with the line "<data> = pd.read_csv('<output from long-runtime cell>.csv')"

## Data Access
1. Yahoo! Finance: The datasets for stock price data, trading volume and CBOE VIX time series were downloaded from Yahoo! Finance using the yfinance package. This is publicly available and does not require an API key.
2. Nasdaq Data Link (formerly Quandl): The dataset for implied volatility was obtained from here using an API key.
3. Financial Modeling Prep: The datasets for financial statements, stock grade, analyst ratings and recommendations, earnings surprise, dividends payments and declarations, and key metrics and ratios were obtained from here using an API key.
4. AlphaVantage: The datasets for earnings call transcripts and company related news were obtained from here using an API key.
5. Quiver Quantitative: The dataset for Congress trading activity was obtained from hre using an API key.
6. Reddit: The dataset for social media sentiment was obtained from here by creating a Reddit instance with a personal Reddit account.
