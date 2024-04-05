# -*- coding: utf-8 -*-
"""Module 2 Past Prices, Trading Volume.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LxqvBxYM5a-_EV-merwyPbvghekSZkzc

# How much of the variation in the current stock price is caused by past prices and trading volume?
"""

! pip install pmdarima

pip install pykalman

# imports

import yfinance as yf
import pandas as pd
import numpy as np
from tqdm import tqdm

from statsmodels.api import OLS
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
from sklearn.metrics import make_scorer, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import TimeSeriesSplit

from statsmodels.tsa.arima.model import ARIMA
from pmdarima import auto_arima
from pykalman import KalmanFilter
import xgboost as xgb

import plotly.graph_objs as go

"""# OLS Linear Regression"""

def past_price_volume_ols(ticker_symbol):

  # download price and volume data from Yahoo! Finance
  start_date = '2004-01-01'
  end_date = '2023-12-31'
  data = yf.download(ticker_symbol, start=start_date, end=end_date)

  data['Past_Return'] = data['Adj Close'].pct_change()

  data['Volume_Lagged'] = data['Volume'].shift(1)

  data.dropna(inplace=True)

  X = data[['Past_Return', 'Volume_Lagged']]
  y = data['Adj Close']
  X = sm.add_constant(X)

  tscv = TimeSeriesSplit(n_splits=4)

  coefficients = []
  rsquareds = []
  rsquareds_adj = []
  fstats = []
  pvalues = []
  aics = []
  mses = []

  # Perform OLS regression with TimeSeriesSplit cross-validation
  for train_index, test_index in tscv.split(X):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    model = sm.OLS(y_train, X_train).fit()

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    mses.append(mse)

    coefficients.append(model.params)
    rsquareds.append(model.rsquared)
    rsquareds_adj.append(model.rsquared_adj)
    fstats.append(model.fvalue)
    pvalues.append(model.pvalues)
    aics.append(model.aic)

  average_mse = np.mean(mses)

  average_coefficients = pd.concat(coefficients, axis=1).mean(axis=1)

  average_rsquared = round(np.mean(rsquareds),3)
  average_rsquared_adj = np.mean(rsquareds_adj)

  average_fstat = np.mean(fstats)

  average_pvalues = pd.concat(pvalues, axis=1).mean(axis=1)

  average_aic = np.mean(aics)

  # Create DataFrame for average model summary
  coeff_summary = pd.DataFrame({f'{ticker_symbol} Coefficients': average_coefficients,
                                        f'{ticker_symbol} p-value': average_pvalues})

  average_model_summary = pd.DataFrame({'Ticker':ticker_symbol,
                              'R-squared': [average_rsquared],
                              'Adjusted R-squared': [average_rsquared_adj],
                              'F-Stat': [average_fstat],
                              'AIC': [average_aic],
                              'MSE on Test Data': [average_mse]})


  return coeff_summary, average_model_summary

past_price_volume_ols('MSFT')

"""The OLS model indicates both past prices and trading volume are statistically significant predictors for the current stock price of MSFT. The model shows that a one percent increase in the adjusted closing price from the previous trading day is associated with an increase of approximately 21.39 in the current price, holding other variables constant. Similarly, a 1 million unit increase in trading volume decreases the share price by approximately $0.1467. The AIC for this model is 18093 and the Mean Squared Error on Test Data is 12897."""

# List of tickers
tickers = ['^GSPC', 'MSFT', 'AAPL', 'EL', 'KR', 'RL', 'HAS', 'APA', 'CZR', 'MKTX', 'BR', 'BIIB', 'REGN']

# Initialize an empty list to store dataframes
summary_dfs = []


for ticker in tickers:
    average_model_summary = past_price_volume_ols(ticker)[1]
    summary_df = pd.concat([average_model_summary], axis=1)
    summary_df.index = [ticker]  # Set index to ticker symbol
    summary_dfs.append(summary_df)

main_df = pd.concat(summary_dfs)

main_df

"""Examining the output from this model, AAPL has a higher Adjusted R-Squared. AAPL and MSFT have higher F-Stat values than the other tickers, suggesting a stronger relationship between the stock price and past prices and trading volume. Converseley, RL and MKTX have the lowest F-Stat scores. It is possible that small cap stocks like RL do not display the same characteristics such as large cap stocks like AAPL and MSFT, hence factors like past prices and trading volume do not play as significant a role in their current price compared to other factors not included in this analysis. Furthermore, a beta-neutral stock like MKTX has minimal sensitivity to market movements and may therefore not be affected by the factors in this analysis."""

# Iterate over tickers
for ticker in tickers:
  coefficient_summary = past_price_volume_ols(ticker)[0]
  print(coefficient_summary)

"""Examining the coefficients at the 95% significance level, almost all the tickers, except for EL appear to pass the significance threshold for trading volume. The large cap stocks display significant negative relationships with trading volume while the high beta stocks display positive relationships. Furthermore for some pairs, such as the low beta BIIB and REGN and the beta neutral MKTX and BR, it is interesting to note that one is positively related while the other is negatively related. Regarding past returns, only MSFT exhibits significance for the coefficient at the 95% significance level.

# ARIMA
"""

# with Kalman filter

ticker_symbol = 'MSFT'
start_date = '2004-01-01'
end_date = '2023-12-31'
msft_data = yf.download(ticker_symbol, start=start_date, end=end_date)
msft_data['Returns'] = msft_data['Adj Close'].pct_change() * 100  # Calculate daily returns
msft_data['Volume_Lagged'] = msft_data['Volume'].shift(1)  # Lag volume by one day


msft_data.dropna(inplace=True)

# Make the series stationary by differencing
msft_data['Adj Close_Diff'] = msft_data['Adj Close'].diff()
msft_data['Volume_Lagged_Diff'] = msft_data['Volume_Lagged'].diff()

tscv = TimeSeriesSplit(n_splits=4)

transition_matrix = [[1, 1], [0, 1]]

# Define the observation matrix
observation_matrix = [[1, 0]]

# Initialize Kalman filter
kf = KalmanFilter(transition_matrices=transition_matrix,
                  observation_matrices=observation_matrix)

r_squared_values = []
adjusted_r_squared_values = []
mean_squared_errors = []

# Calculate R-squared
def calculate_r_squared(y_true, y_pred):
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    return r_squared

for train_index, test_index in tscv.split(msft_data):
  train_data = msft_data.iloc[train_index]
  train_data.dropna(inplace=True)
  test_data = msft_data.iloc[test_index]

  train_states = kf.em(train_data['Adj Close'].values, n_iter=5).smooth(train_data['Adj Close'].values)[0]

  # Extract filtered estimates of stock prices from Kalman filter
  train_filtered_prices = train_states[:, 0]

  auto_model = auto_arima(train_filtered_prices, exogenous=train_data[['Volume_Lagged_Diff']],
                          trace=True, error_action='ignore', suppress_warnings=True)

  model = ARIMA(endog=train_filtered_prices, exog=train_data[['Volume_Lagged_Diff']],
                order=auto_model.order)
  result = model.fit()

  print(result.summary())

  # Forecast future differences
  forecast_steps = len(test_data)
  forecast_diff = result.forecast(steps=forecast_steps, exog=test_data[['Volume_Lagged_Diff']])

  forecast_states = kf.filter(test_data['Adj Close'].values)[0]
  forecast_filtered_prices = forecast_states[:, 0]
  forecast = forecast_diff.cumsum() + forecast_filtered_prices[-1]

  y_pred_train_arima = result.predict()
  r_squared_train = calculate_r_squared(train_filtered_prices, y_pred_train_arima)
  r_squared_values.append(r_squared_train)

  n = len(test_data)
  p = len(result.params)
  adjusted_r_squared = 1 - ((1 - r_squared_train) * (n - 1) / (n - p - 1))
  adjusted_r_squared_values.append(adjusted_r_squared)

  # Calculate Mean Squared Error
  mse = mean_squared_error(test_data['Adj Close'], forecast)
  mean_squared_errors.append(mse)

avg_r_squared = np.mean(r_squared_values)
avg_adjusted_r_squared = np.mean(adjusted_r_squared_values)
avg_mse = np.mean(mean_squared_errors)

print("Average R-Squared:", avg_r_squared)
print("Average Adjusted R-Squared:", avg_adjusted_r_squared)
print("Average Mean Squared Error:", avg_mse)

print("Average R-Squared:", avg_r_squared)
print("Average Adjusted R-Squared:", avg_adjusted_r_squared)
print("Average Mean Squared Error:", avg_mse)

"""Just like with the OLS Regression model, the ARIMA model includes 4 fold cross-validation. A Kalman filter was incorporated into the model to address noisy data and estimate the time-varying coefficients that capture the evolving relationships between past prices, trading volume and current prices. Including the Kalman filter reduced the AIC from 9217 to 5098 on the last fold, suggesting that the filter provides a better fit to the data compared to the model without the data. Nonetheless the AIC parameter suggests that there is further room for improvement in the model. The R-Squared and Adjusted R-Squared values show that the model caputres 97.6% of the variation in the dependent variable, however the elevated Mean Squared Error value shows that the model does not have good predictive power. Taken together, these output parameter indicate that this model fits the data well in terms of explaining the variation in the current stock price but has poor predictive ability. Overfitting is also a potential issue in this model. Subsequent modules will include additional variables to capture further causes of the variation in the dependent variable."""

# create a function to perform this analysis on the simple cross-section of tickers
def arima_model(ticker_symbol):
  start_date = '2004-01-01'
  end_date = '2023-12-31'
  data = yf.download(ticker_symbol, start=start_date, end=end_date)
  data['Returns'] = data['Adj Close'].pct_change() * 100  # Calculate daily returns
  data['Volume_Lagged'] = data['Volume'].shift(1)  # Lag volume by one day

  data.dropna(inplace=True)

  data['Adj Close_Diff'] = data['Adj Close'].diff()
  data['Volume_Lagged_Diff'] = data['Volume_Lagged'].diff()

  # Initialize TimeSeriesSplit with 4 splits
  tscv = TimeSeriesSplit(n_splits=4)

  # Define the state transition matrix
  transition_matrix = [[1, 1], [0, 1]]

  # Define the observation matrix
  observation_matrix = [[1, 0]]

  # Initialize Kalman filter
  kf = KalmanFilter(transition_matrices=transition_matrix,
                    observation_matrices=observation_matrix)

  # Initialize lists to store evaluation metrics
  r_squared_values = []
  adjusted_r_squared_values = []
  mean_squared_errors = []

  # Calculate R-squared
  def calculate_r_squared(y_true, y_pred):
      ss_res = np.sum((y_true - y_pred) ** 2)
      ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
      r_squared = 1 - (ss_res / ss_tot)
      return r_squared

  # Iterate over each split
  for train_index, test_index in tscv.split(data):
    # Split data into train and test sets
    train_data = data.iloc[train_index]
    train_data.dropna(inplace=True)
    test_data = data.iloc[test_index]

    # Fit Kalman filter to training data
    train_states = kf.em(train_data['Adj Close'].values, n_iter=5).smooth(train_data['Adj Close'].values)[0]

    # Extract filtered estimates of stock prices from Kalman filter
    train_filtered_prices = train_states[:, 0]

    # Use filtered estimates of stock prices as input for ARIMA model
    auto_model = auto_arima(train_filtered_prices, exogenous=train_data[['Volume_Lagged_Diff']],
                            trace=True, error_action='ignore', suppress_warnings=True)

    # Fit ARIMA model with optimal order
    model = ARIMA(endog=train_filtered_prices, exog=train_data[['Volume_Lagged_Diff']],
                  order=auto_model.order)
    result = model.fit()

    # Print model summary
    # print(result.summary())

    # Forecast future differences
    forecast_steps = len(test_data)  # Forecast for the length of the test set
    forecast_diff = result.forecast(steps=forecast_steps, exog=test_data[['Volume_Lagged_Diff']])

    # Convert differenced forecasts back to original scale using Kalman filter estimates
    forecast_states = kf.filter(test_data['Adj Close'].values)[0]
    forecast_filtered_prices = forecast_states[:, 0]
    forecast = forecast_diff.cumsum() + forecast_filtered_prices[-1]  # Add last observed value

    # Calculate R-Squared
    y_pred_train_arima = result.predict()
    r_squared_train = calculate_r_squared(train_filtered_prices, y_pred_train_arima)
    r_squared_values.append(r_squared_train)

    # Calculate Adjusted R-squared
    n = len(test_data)
    p = len(result.params)
    adjusted_r_squared = 1 - ((1 - r_squared_train) * (n - 1) / (n - p - 1))
    adjusted_r_squared_values.append(adjusted_r_squared)

    # Calculate Mean Squared Error
    mse = mean_squared_error(test_data['Adj Close'], forecast)
    mean_squared_errors.append(mse)

  # Calculate average metrics
  avg_r_squared = np.mean(r_squared_values)
  avg_adjusted_r_squared = np.mean(adjusted_r_squared_values)
  avg_mse = np.mean(mean_squared_errors)

  result_dict = {'Ticker': ticker_symbol,
                'AIC': round(result.aic,3),
               "Average R-Squared": round(avg_r_squared,3),
               "Average Adjusted R-Squared": round(avg_adjusted_r_squared,3),
               "Average Mean Squared Error": round(avg_mse,3)}
  result_df = pd.DataFrame.from_dict(result_dict, orient='index', columns=['Values'])
  result_df = result_df.transpose()

  return result_df, result.summary()

arima_model('AAPL')

arima_model('^GSPC')

arima_model('EL')

arima_model('KR')

# Initialize an empty DataFrame to store result_df for all tickers
result_df_concat = pd.DataFrame()

# Initialize an empty dictionary to store model summaries for all tickers
model_summaries = {}

# Loop through each ticker symbol
for ticker in tqdm(tickers, desc="Processing tickers"):
    # Apply the arima_model function to get result_df and model summary for the current ticker
    result_df, summary = arima_model(ticker)

    # Concatenate result_df for the current ticker to the result_df_concat DataFrame
    result_df_concat = pd.concat([result_df_concat, result_df])

    # Store the model summary in the dictionary with ticker symbol as the key
    model_summaries[ticker] = summary

# Show the concatenated result_df
# result_df_conca = result_df_concat.set_index('Ticker', inplace=True)
result_df_concat = result_df_concat.sort_values(by='Average Mean Squared Error')
result_df_concat

"""Looking at the results of this model, the mid-cap (KR) and both the large-cap (AAPL and MSFT) have the lowest AIC values, while both the low beta (BIIB and REGN) as well as the market itself (^GSPC) have the highest AIC values. Adjusted R-Squared values are more disparate with a large-cal (AAPL), a small-cap (RL) and a high-beta (CZR) exhibiting the highest adjusted R-Squared and a large-cap (MSFT), mid-cap and beta-neutral (BR) exhibiting the lowest values. The range of adjusted R-Squared values, however, is very narrow throughout all the tickers, ranging from 0.976 to 1.0. Average MSE is extremely high for all tickers, with a beta neutral (MKTX) having the highest and a high beta (CZR) having the lowest MSE.Overall, while the ARIMA models appear to explain a significant portion of the variance in stock prices for different tickers, they might not perform well in terms of predictive accuracy, as indicated by the high MSE values. Additionally, the relatively consistent adjusted R-squared values across tickers suggest that the explanatory power of the models is similar across different stocks but this may be due to overfitting or model misspecification, which needs to be addressed through additional model calibration.

"""

model_summaries['AAPL']

"""Examining the coefficients of AAPL, it appears that the trading volume is not a statistically significant variable. The summary also indicates the presence of heteroskedasticity in the model, suggesting that further modiciation to this model is needed."""

model_summaries

"""Examining the model summaries of all tickers, it appears only ^GSPC and KR show that trading volume is statistically significant."""

from scipy.stats import chi2

# Define the significance level
alpha = 0.05

# Define the degrees of freedom
df = 4025

# Find the critical value
critical_value = chi2.ppf(1 - alpha, df)

print("Critical Value:", critical_value)