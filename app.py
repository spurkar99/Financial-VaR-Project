import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, skew, kurtosis, t

# 1. Page Setup
st.set_page_config(page_title="Portfolio VaR Analysis", layout="wide")
st.title("Value-at-Risk (VaR) Analysis of a Multi-Asset Portfolio")
st.write("**Author:** Shreyas Sanjay Purkar | **Institute:** IIT Gandhinagar")
st.markdown("---")

# 2. Load the Data
@st.cache_data
def load_data():
    # Read the excel file
    df = pd.read_excel("Data.xlsx")
    # Clean up column names (remove spaces, make uppercase)
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.upper()
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE'], dayfirst=True)
    return df

df = load_data()

# 3. Process Data and Calculate VaR
if df is not None:
    returns_cols = [
        'REL_RETURN', 'TCS_RETURN', 'HDFC_RETURN', 'ARTL_RETURN',
        'INFY_RETURN', 'ITC_RETURN', 'SUN_RETURN', 'ONGC_RETURN',
        'TATA_RETURN', 'DMART_RETURN'
    ]
    
    available_cols = [col for col in returns_cols if col in df.columns]
    df_returns = df[available_cols].dropna()
    
    st.sidebar.header("VaR Parameters")
    portfolio_value = st.sidebar.number_input("Portfolio Value (₹)", value=1000000, step=100000)
    confidence_level = st.sidebar.slider("Confidence Level", min_value=0.90, max_value=0.99, value=0.95, step=0.01)
    
    # Equal Weighting
    N = len(available_cols)
    weights = np.ones(N) / N
    port_returns = df_returns @ weights
    
    port_mean = port_returns.mean()
    port_std = port_returns.std()
    z = norm.ppf(1 - confidence_level)
    
    # --- Models ---
    # Historical VaR
    hist_var = np.percentile(port_returns, (1 - confidence_level) * 100)
    
    # Normal VaR
    param_var = port_mean + z * port_std
    
    # Modified VaR (Cornish-Fisher)
    S = skew(port_returns)
    K = kurtosis(port_returns)
    z_cf = (z + (1/6)*(z**2 - 1)*S + (1/24)*(z**3 - 3*z)*K - (1/36)*(2*z**3 - 5*z)*(S**2))
    mod_var = port_mean + z_cf * port_std
    
    # EWMA VaR
    lambda_ = 0.94
    ewma_var = 0
    for r in port_returns:
        ewma_var = lambda_ * ewma_var + (1 - lambda_) * (r**2)
    ewma_vol = np.sqrt(ewma_var)
    ewma_var_pct = z * ewma_vol
    
    # Student-t VaR
    df_t = 5
    t_score = t.ppf(1 - confidence_level, df=df_t)
    t_var = port_mean + t_score * port_std
    
    # 4. Display Results
    st.subheader(f"1. Base Portfolio VaR Comparison ({confidence_level:.0%} Confidence)")
    st.write(f"Based on {len(df_returns)} trading days of historical data.")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Historical VaR", f"{abs(hist_var):.4%}", f"₹{abs(hist_var * portfolio_value):,.0f}", delta_color="inverse")
    col2.metric("Normal VaR", f"{abs(param_var):.4%}", f"₹{abs(param_var * portfolio_value):,.0f}", delta_color="inverse")
    col3.metric("Modified VaR", f"{abs(mod_var):.4%}", f"₹{abs(mod_var * portfolio_value):,.0f}", delta_color="inverse")
    col4.metric("EWMA VaR", f"{abs(ewma_var_pct):.4%}", f"₹{abs(ewma_var_pct * portfolio_value):,.0f}", delta_color="inverse")
    col5.metric("Student-t VaR", f"{abs(t_var):.4%}", f"₹{abs(t_var * portfolio_value):,.0f}", delta_color="inverse")
    
    # Plotting the VaR Bar Chart
    st.markdown("<br>", unsafe_allow_html=True)
    labels = ['Historical', 'Normal', 'Modified', 'EWMA', 'Student-t']
    values = [abs(hist_var)*100, abs(param_var)*100, abs(mod_var)*100, abs(ewma_var_pct)*100, abs(t_var)*100]
    
    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.bar(labels, values, color=['#1565C0', '#2E7D32', '#E65100', '#6A1B9A', '#C62828'])
    ax.set_ylabel("VaR (%)")
    ax.set_title("VaR Model Comparison")
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05, f"{yval:.2f}%", ha='center', va='bottom', fontweight='bold')
    st.pyplot(fig)

    st.markdown("---")
    
    # 5. Monte Carlo Simulation
    st.subheader("2. Monte Carlo Simulation (Portfolio Optimization)")
    st.write("Click the button below to run 10,000 simulations and find the portfolio weights that minimize Value-at-Risk.")
    
    if st.button("Run Monte Carlo Optimization"):
        num_portfolios = 10000
        var_list = []
        weights_record = []
        
        progress_text = "Running simulations. Please wait..."
        my_bar = st.progress(0, text=progress_text)
        
        for i in range(num_portfolios):
            w = np.random.random(N)
            w /= np.sum(w)
            
            # Use historical percentile for optimization as per notebook
            temp_returns = df_returns.values @ w
            temp_var = abs(np.percentile(temp_returns, (1 - confidence_level) * 100))
            
            var_list.append(temp_var)
            weights_record.append(w)
            
            # Update progress bar every 1000 iterations
            if (i + 1) % 1000 == 0:
                my_bar.progress((i + 1) / num_portfolios, text=progress_text)
                
        my_bar.empty()
        
        # Find minimum VaR
        min_var_idx = np.argmin(var_list)
        min_var = var_list[min_var_idx]
        best_weights = weights_record[min_var_idx]
        
        st.success(f"**Optimal (Minimum) VaR Found:** {min_var:.4%}")
        
        col_w1, col_w2 = st.columns([1, 2])
        with col_w1:
            st.write("**Optimal Weights:**")
            weight_df = pd.DataFrame({"Asset": available_cols, "Weight": best_weights})
            weight_df["Weight"] = weight_df["Weight"].apply(lambda x: f"{x:.2%}")
            st.dataframe(weight_df.set_index("Asset"), use_container_width=True)
            
        with col_w2:
            fig_mc, ax_mc = plt.subplots(figsize=(8, 5))
            ax_mc.hist(np.array(var_list)*100, bins=50, color='#2E7D32', alpha=0.7, edgecolor='white')
            ax_mc.axvline(min_var*100, color='red', linestyle='--', linewidth=2, label=f'Min VaR: {min_var*100:.2f}%')
            ax_mc.set_title('Monte Carlo VaR Distribution (10,000 Portfolios)')
            ax_mc.set_xlabel('VaR (%)')
            ax_mc.set_ylabel('Frequency')
            ax_mc.legend()
            st.pyplot(fig_mc)