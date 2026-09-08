import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import norm, skew, kurtosis, t

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="Portfolio VaR Analysis", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# Custom CSS to mimic the deep dashboard look
st.markdown("""
    <style>
    .stMetric { background-color: #1E1E2E; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .stDataFrame { border-radius: 8px; overflow: hidden; }
    h1, h2, h3 { color: #E0E0FF; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATA LOADING & PREPARATION
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Data.xlsx")
        df.columns = df.columns.str.strip().str.replace(" ", "_").str.upper()
        if 'DATE' in df.columns:
            df['DATE'] = pd.to_datetime(df['DATE'], dayfirst=True)
            df.set_index('DATE', inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data()

if df is not None:
    # Map raw columns to clean display names
    col_mapping = {
        'REL_RETURN': 'Reliance', 'TCS_RETURN': 'TCS', 'HDFC_RETURN': 'HDFC Bank', 
        'ARTL_RETURN': 'Bharti Airtel', 'INFY_RETURN': 'Infosys', 'ITC_RETURN': 'ITC', 
        'SUN_RETURN': 'Sun Pharma', 'ONGC_RETURN': 'ONGC', 'TATA_RETURN': 'Tata Motors', 
        'DMART_RETURN': 'DMart'
    }
    available_cols = [c for c in col_mapping.keys() if c in df.columns]
    df_returns = df[available_cols].dropna()
    df_returns.rename(columns=col_mapping, inplace=True)
    clean_cols = list(df_returns.columns)
    N = len(clean_cols)

    # ==========================================
    # 3. SIDEBAR CONTROLS
    # ==========================================
    st.sidebar.markdown("### ⚙️ Dashboard Controls")
    portfolio_value = st.sidebar.number_input("💰 Portfolio Value (₹)", value=1000000, step=100000)
    confidence_level = st.sidebar.slider("🎯 Confidence Level", min_value=0.90, max_value=0.99, value=0.95, step=0.01)
    
    st.sidebar.markdown("### 🔧 Model Parameters")
    lambda_ = st.sidebar.slider("EWMA λ (decay factor)", min_value=0.90, max_value=0.99, value=0.94, step=0.01)
    df_t = st.sidebar.slider("Student-t degrees of freedom", min_value=3, max_value=30, value=5, step=1)
    num_portfolios = st.sidebar.slider("Monte Carlo simulations", min_value=1000, max_value=50000, value=10000, step=1000)

    st.sidebar.markdown("---")
    st.sidebar.info(f"📅 Data: {df_returns.index.min().strftime('%b %Y')} → {df_returns.index.max().strftime('%b %Y')}")
    st.sidebar.info(f"📈 {N} Stocks · {len(df_returns)} Trading Days")

    # ==========================================
    # 4. CORE CALCULATIONS (EQUAL WEIGHTS)
    # ==========================================
    weights = np.ones(N) / N
    port_returns = df_returns.values @ weights
    port_mean = port_returns.mean()
    port_std = port_returns.std()
    
    # Metrics
    S = skew(port_returns)
    K = kurtosis(port_returns)
    z = norm.ppf(1 - confidence_level)
    
    # 5 VaR Models
    hist_var = abs(np.percentile(port_returns, (1 - confidence_level) * 100))
    param_var = abs(port_mean + z * port_std)
    z_cf = (z + (1/6)*(z**2 - 1)*S + (1/24)*(z**3 - 3*z)*K - (1/36)*(2*z**3 - 5*z)*(S**2))
    mod_var = abs(port_mean + z_cf * port_std)
    
    ewma_var_sq = 0
    for r in port_returns:
        ewma_var_sq = lambda_ * ewma_var_sq + (1 - lambda_) * (r**2)
    ewma_vol = np.sqrt(ewma_var_sq)
    ewma_var_pct = abs(z * ewma_vol)
    
    t_score = t.ppf(1 - confidence_level, df=df_t)
    t_var = abs(port_mean + t_score * port_std)

    # ==========================================
    # 5. MAIN DASHBOARD UI
    # ==========================================
    st.markdown("### 🟪 Portfolio VaR Analysis Dashboard")
    st.caption(f"Multi-Asset Indian Equity Portfolio — Value-at-Risk Analysis | Equal-Weighted · {N} Stocks · {confidence_level:.0%} Confidence")

    # Top Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("PORTFOLIO VALUE", f"₹{portfolio_value:,.0f}")
    m2.metric("MEAN DAILY RETURN", f"{port_mean*100:.4f}%")
    m3.metric("DAILY VOLATILITY (σ)", f"{port_std*100:.4f}%")
    m4.metric("SKEWNESS", f"{S:.4f}")
    m5.metric("EXCESS KURTOSIS", f"{K:.4f}")

    st.markdown("---")
    
    # ==========================================
    # SECTION 1: VaR MODEL COMPARISON
    # ==========================================
    st.markdown("#### 📊 VaR Model Comparison")
    colA, colB = st.columns([1.5, 1])
    
    # Bar Chart
    model_names = ['Historical', 'Normal', 'Modified (CF)', 'EWMA', 'Student-t']
    var_values = [hist_var, param_var, mod_var, ewma_var_pct, t_var]
    colors = ['#7B61FF', '#21C488', '#FF6384', '#FFCA28', '#42A5F5']
    
    fig1 = go.Figure(data=[go.Bar(
        x=model_names, y=[v * 100 for v in var_values],
        marker_color=colors, text=[f"{v*100:.4f}%" for v in var_values], textposition='auto'
    )])
    fig1.update_layout(title=f"VaR Comparison ({confidence_level:.0%} Confidence)", template="plotly_dark",
                       yaxis_title="VaR (%)", margin=dict(l=0, r=0, t=40, b=0), height=350)
    colA.plotly_chart(fig1, use_container_width=True)
    
    # Table & Descriptions
    df_compare = pd.DataFrame({
        "MODEL": model_names,
        "VaR %": [f"{v*100:.4f}%" for v in var_values],
        "₹ VALUE": [f"₹{v * portfolio_value:,.2f}" for v in var_values]
    })
    colB.dataframe(df_compare, hide_index=True, use_container_width=True)
    colB.markdown("""
    **Model Descriptions**
    * **Historical** — Empirical percentile of returns
    * **Normal** — Gaussian assumption (μ + zσ)
    * **Modified (CF)** — Adjusts for skew & kurtosis
    * **EWMA** — Exponentially Weighted Volatility
    * **Student-t** — Captures extreme fat tails
    """)

    st.markdown("---")

    # ==========================================
    # SECTION 2: RETURN DISTRIBUTION
    # ==========================================
    st.markdown("#### 📈 Portfolio Return Distribution")
    fig2 = go.Figure()
    # Histogram
    fig2.add_trace(go.Histogram(x=port_returns*100, histnorm='probability density', name='Daily Returns', marker_color='#5C5CFF', opacity=0.7, nbinsx=100))
    # Normal Curve Fit
    x_range = np.linspace(port_returns.min(), port_returns.max(), 500)
    y_norm = norm.pdf(x_range, port_mean, port_std)
    fig2.add_trace(go.Scatter(x=x_range*100, y=y_norm/100, mode='lines', name='Normal Fit', line=dict(color='white', dash='dash')))
    
    # Threshold Lines
    for name, val, col in zip(model_names, var_values, colors):
        fig2.add_vline(x=-val*100, line_dash="dash", line_color=col, annotation_text=f"{name}: {val*100:.2f}%", annotation_position="top left")
    
    fig2.update_layout(template="plotly_dark", xaxis_title="Daily Return (%)", yaxis_title="Density", height=450, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ==========================================
    # SECTION 3: CRISIS PERIOD ANALYSIS
    # ==========================================
    st.markdown("#### 🔥 Crisis Period Analysis")
    crisis_periods = {
        "2018 Market Stress": ('2018-01-01', '2018-12-31'),
        "COVID-19 Crash": ('2020-03-01', '2020-12-31'),
        "2022 Inflation": ('2022-01-01', '2022-12-31')
    }
    
    crisis_data = []
    for period, (start, end) in crisis_periods.items():
        mask = (df_returns.index >= start) & (df_returns.index <= end)
        sub_ret = df_returns[mask].values @ weights
        if len(sub_ret) > 20:
            h_var = abs(np.percentile(sub_ret, (1 - confidence_level) * 100))
            p_var = abs(sub_ret.mean() + z * sub_ret.std())
            crisis_data.append([period, len(sub_ret), h_var, p_var])
            
    df_crisis = pd.DataFrame(crisis_data, columns=["PERIOD", "DAYS", "HIST VAR", "PARAM VAR"])
    
    colC, colD = st.columns([1.5, 1])
    
    fig3 = go.Figure(data=[
        go.Bar(name='Historical VaR', x=df_crisis['PERIOD'], y=df_crisis['HIST VAR']*100, marker_color='#636EFA', text=[f"{v*100:.3f}%" for v in df_crisis['HIST VAR']], textposition='auto'),
        go.Bar(name='Parametric VaR', x=df_crisis['PERIOD'], y=df_crisis['PARAM VAR']*100, marker_color='#EF553B', text=[f"{v*100:.3f}%" for v in df_crisis['PARAM VAR']], textposition='auto')
    ])
    fig3.update_layout(barmode='group', template="plotly_dark", yaxis_title="VaR (%)", height=350, margin=dict(l=0, r=0, t=30, b=0))
    colC.plotly_chart(fig3, use_container_width=True)
    
    colD.markdown("**Crisis Period Details**")
    df_crisis_display = df_crisis.copy()
    df_crisis_display['HIST VAR'] = df_crisis_display['HIST VAR'].apply(lambda x: f"{x*100:.4f}%")
    df_crisis_display['PARAM VAR'] = df_crisis_display['PARAM VAR'].apply(lambda x: f"{x*100:.4f}%")
    colD.dataframe(df_crisis_display, hide_index=True, use_container_width=True)
    if not df_crisis.empty:
        max_crisis = df_crisis.loc[df_crisis['HIST VAR'].idxmax()]
        colD.info(f"📌 **{max_crisis['PERIOD']}** had the highest Historical VaR at {max_crisis['HIST VAR']*100:.4f}%, showing significantly elevated risk.")

    st.markdown("---")

    # ==========================================
    # SECTION 4: MONTE CARLO SIMULATION
    # ==========================================
    st.markdown("#### 🎲 Monte Carlo Simulation")
    # Pre-calculate a small batch so the user sees something immediately, but allow full run on demand
    with st.spinner("Running Monte Carlo Optimization..."):
        np.random.seed(42) # For consistent look
        rand_weights = np.random.dirichlet(np.ones(N), num_portfolios)
        mc_returns = df_returns.values @ rand_weights.T
        mc_vars = abs(np.percentile(mc_returns, (1 - confidence_level) * 100, axis=0))
        
        min_idx = np.argmin(mc_vars)
        min_var = mc_vars[min_idx]
        best_weights = rand_weights[min_idx]
        mean_var = mc_vars.mean()

    colE, colF = st.columns([1.5, 1])
    
    fig4 = go.Figure()
    fig4.add_trace(go.Histogram(x=mc_vars*100, nbinsx=60, marker_color='#2BAE66', opacity=0.8, name='Simulated Portfolios'))
    fig4.add_vline(x=min_var*100, line_dash="dash", line_color="red", annotation_text=f"Min VaR: {min_var*100:.4f}%")
    fig4.add_vline(x=mean_var*100, line_dash="dash", line_color="orange", annotation_text=f"Mean: {mean_var*100:.4f}%")
    fig4.add_vline(x=hist_var*100, line_dash="dash", line_color="blue", annotation_text=f"Equal-Wt: {hist_var*100:.4f}%")
    fig4.update_layout(template="plotly_dark", xaxis_title="VaR (%)", yaxis_title="Frequency", height=400, margin=dict(l=0, r=0, t=30, b=0))
    colE.plotly_chart(fig4, use_container_width=True)

    colF.markdown("🏆 **Minimum VaR Portfolio**")
    colF.metric("MIN VAR", f"{min_var*100:.4f}%")
    colF.metric("MEAN VAR (ALL SIMS)", f"{mean_var*100:.4f}%")
    
    fig_pie = go.Figure(data=[go.Pie(labels=clean_cols, values=best_weights, hole=.5, textinfo='label+percent')])
    fig_pie.update_layout(template="plotly_dark", showlegend=False, height=250, margin=dict(l=0, r=0, t=10, b=10))
    colF.markdown("**Optimal Weights**")
    colF.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # ==========================================
    # SECTION 5: DATA EXPLORER & CORRELATIONS
    # ==========================================
    st.markdown("#### 🔗 Stock Return Correlations")
    corr = df_returns.corr()
    fig_corr = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="Purples")
    fig_corr.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("#### 📄 Individual Stock VaR")
    ind_data = []
    for col in clean_cols:
        r = df_returns[col]
        m = r.mean()
        s = r.std()
        h = abs(np.percentile(r, (1 - confidence_level) * 100))
        p = abs(m + z * s)
        ind_data.append([col, f"{m*100:.4f}%", f"{s*100:.4f}%", f"{h*100:.4f}%", f"{p*100:.4f}%"])
        
    df_ind = pd.DataFrame(ind_data, columns=["STOCK", "MEAN RETURN", "VOLATILITY", "HISTORICAL VAR", "PARAMETRIC VAR"])
    st.dataframe(df_ind, hide_index=True, use_container_width=True)

    with st.expander("📂 View Raw Return Data"):
        st.dataframe(df_returns.style.format("{:.4%}"), use_container_width=True)