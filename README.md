# Portfolio Value-at-Risk Analysis

An interactive financial risk analytics dashboard for measuring and comparing **Value-at-Risk (VaR)** across a portfolio of major Indian equities.

The project evaluates portfolio downside risk using multiple statistical approaches, examines how risk changes during stressed market periods, and uses Monte Carlo simulation to identify portfolio allocations with lower historical VaR.

## 🚀 Live Demo

**[Open the Interactive Portfolio VaR Dashboard](https://financial-var-project-nwmibm6rwsdohfee9hkvdu.streamlit.app/)**

---

## Overview

Value-at-Risk estimates the potential loss of a portfolio over a specified period at a given confidence level.

Instead of relying on a single VaR methodology, this project compares **five different risk models** to understand how assumptions about return distributions and volatility influence estimated portfolio risk.

The dashboard allows the user to dynamically change:

* Portfolio value
* Confidence level
* EWMA decay factor
* Student-t degrees of freedom
* Number of Monte Carlo simulations

All calculations and visualizations update interactively.

---

## Portfolio

The analysis uses historical return data for 10 major Indian equities:

* Reliance Industries
* TCS
* HDFC Bank
* Bharti Airtel
* Infosys
* ITC
* Sun Pharma
* ONGC
* Tata Motors
* DMart

The baseline portfolio is **equally weighted across all available assets**.

---

## VaR Models Implemented

### 1. Historical VaR

Uses the empirical distribution of historical portfolio returns and calculates the loss corresponding to the selected percentile.

This method makes no assumption about the shape of the return distribution.

### 2. Parametric VaR

Assumes portfolio returns follow a normal distribution and estimates VaR using the portfolio mean and standard deviation.

### 3. Modified VaR — Cornish-Fisher

Extends the normal VaR model by adjusting the critical value for:

* Skewness
* Excess kurtosis

This allows the estimate to better reflect non-normal characteristics observed in financial return distributions.

### 4. EWMA VaR

Uses an **Exponentially Weighted Moving Average** volatility model so that recent observations receive greater importance than older observations.

The decay factor can be changed directly from the dashboard.

### 5. Student-t VaR

Models returns using a Student-t distribution to better capture the **fat tails and extreme movements** commonly observed in financial markets.

The degrees-of-freedom parameter is user-adjustable.

---

## Dashboard Features

### VaR Model Comparison

Compares all five VaR methodologies side-by-side in both:

* Percentage terms
* Rupee loss for the selected portfolio value

This makes it possible to see how strongly the choice of risk model affects the estimated downside exposure.

### Return Distribution Analysis

Visualizes the historical portfolio return distribution together with:

* Normal distribution fit
* VaR thresholds from each model

This helps highlight deviations from normality and differences between model assumptions.

### Crisis Period Analysis

Portfolio risk is separately evaluated during major periods of market stress:

* 2018 Market Stress
* COVID-19 Crash
* 2022 Inflation Period

Historical and Parametric VaR are recalculated for each period to show how portfolio risk behaves during stressed market conditions.

### Monte Carlo Portfolio Analysis

Random portfolio weights are generated using Monte Carlo simulation.

For every simulated portfolio, Historical VaR is calculated and compared.

The dashboard identifies:

* Minimum-VaR portfolio
* Mean VaR across simulated portfolios
* Equal-weight portfolio VaR
* Asset allocation of the minimum-VaR portfolio

Users can run between **1,000 and 50,000 simulated portfolios**.

### Correlation Analysis

An interactive correlation heatmap displays the relationship between stock returns across the portfolio.

This provides insight into diversification and common market exposure.

### Individual Stock Risk

The dashboard also calculates stock-level:

* Mean daily return
* Volatility
* Historical VaR
* Parametric VaR

for every company in the dataset.

---

## Methodology

For an equal-weighted portfolio with \(N\) assets:

$$
w_i = \frac{1}{N}
$$

Portfolio return for each trading day is:

$$
R_p = \sum_{i=1}^{N} w_iR_i
$$

The resulting portfolio return distribution is then used to estimate downside risk using the five VaR methodologies.

For a confidence level \(c\), Historical VaR is obtained from the lower:

$$
(1-c)\times100
$$

percentile of portfolio returns.

Parametric VaR is estimated using:

$$
VaR = |\mu + z_{\alpha}\sigma|
$$

where:

* \(\mu\) = mean portfolio return
* \(\sigma\) = portfolio volatility
* \(z_{\alpha}\) = standard-normal critical value

The remaining models modify either the distributional assumption or volatility estimate to better capture characteristics of financial returns.

---

## Tech Stack

**Language**

* Python

**Data Analysis**

* Pandas
* NumPy

**Statistics**

* SciPy

**Visualization**

* Plotly

**Application**

* Streamlit

**Data Source**

* Historical return dataset stored in Excel

---

## Project Structure

```text
Financial-VaR-Project/
│
├── app.py              # Streamlit application and VaR calculations
├── Data.xlsx           # Historical stock return dataset
├── Report.pdf          # Detailed project report
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## Running Locally

Clone the repository:

```bash
git clone https://github.com/spurkar99/Financial-VaR-Project.git
```

Enter the project directory:

```bash
cd Financial-VaR-Project
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the dashboard:

```bash
streamlit run app.py
```

The application will open in your browser locally.

---

## Key Takeaways

The project demonstrates why VaR should not be treated as a single universal risk number.

Different methodologies respond differently to:

* Non-normal return distributions
* Fat tails
* Changing volatility
* Market crises
* Portfolio composition

By combining traditional VaR estimation with crisis analysis and Monte Carlo portfolio construction, the dashboard provides a broader view of portfolio downside risk than a single-model approach.

---

## Disclaimer

This project is intended for educational and analytical purposes only. It should not be interpreted as investment advice or as a production-grade financial risk management system.
