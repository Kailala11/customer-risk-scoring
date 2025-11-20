"""
Customer Risk Scoring - Interactive Dashboard
Built with Streamlit for interactive data exploration

To run: streamlit run streamlit_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Customer Risk Scoring Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 20px;
    }
    .risk-low {
        color: #2ecc71;
        font-weight: bold;
    }
    .risk-medium {
        color: #f39c12;
        font-weight: bold;
    }
    .risk-high {
        color: #e74c3c;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================

@st.cache_data
def generate_customer_data(n_customers=1000, seed=42):
    """Generate synthetic customer data"""
    np.random.seed(seed)
    
    data = {
        'customer_id': [f'CUST{str(i).zfill(5)}' for i in range(1, n_customers + 1)],
        'age': np.random.randint(21, 65, n_customers),
        'income': np.random.choice(
            [3000000, 5000000, 7500000, 10000000, 15000000, 20000000], 
            n_customers, 
            p=[0.20, 0.25, 0.20, 0.15, 0.12, 0.08]
        ),
        'employment_status': np.random.choice(
            ['Employed', 'Self-employed', 'Unemployed'], 
            n_customers, 
            p=[0.70, 0.25, 0.05]
        ),
        'dependents': np.random.randint(0, 5, n_customers),
        'credit_limit': np.random.choice(
            [5000000, 10000000, 15000000, 25000000, 50000000], 
            n_customers,
            p=[0.30, 0.30, 0.20, 0.15, 0.05]
        ),
        'credit_utilization': np.random.beta(2, 5, n_customers) * 100,
        'late_payment_count': np.random.poisson(0.5, n_customers),
        'account_age_months': np.random.randint(6, 120, n_customers),
        'payment_status': np.random.choice(
            ['Current', 'Late', 'Delinquent'], 
            n_customers, 
            p=[0.75, 0.20, 0.05]
        ),
        'missed_payment_6m': np.random.poisson(0.3, n_customers),
        'full_payment_ratio': np.random.beta(5, 2, n_customers) * 100
    }
    
    df = pd.DataFrame(data)
    df['avg_monthly_spending'] = (df['credit_limit'] * df['credit_utilization'] / 100).astype(int)
    df['credit_utilization'] = df['credit_utilization'].clip(upper=100)
    df['debt_to_income'] = (df['avg_monthly_spending'] / df['income'] * 100).round(2)
    
    return df

def calculate_risk_score(row):
    """Calculate risk score using weighted methodology"""
    score = 0
    
    # Credit Utilization (25%)
    if row['credit_utilization'] < 30:
        score += 5
    elif row['credit_utilization'] < 60:
        score += 15
    else:
        score += 25
    
    # Late Payment Count (30%)
    if row['late_payment_count'] == 0:
        score += 5
    elif row['late_payment_count'] <= 2:
        score += 20
    else:
        score += 30
    
    # Income Level (15%)
    if row['income'] >= 10000000:
        score += 3
    elif row['income'] >= 5000000:
        score += 10
    else:
        score += 15
    
    # Payment Status (20%)
    if row['payment_status'] == 'Current':
        score += 5
    elif row['payment_status'] == 'Late':
        score += 15
    else:
        score += 20
    
    # Missed Payments (10%)
    if row['missed_payment_6m'] == 0:
        score += 2
    elif row['missed_payment_6m'] <= 2:
        score += 7
    else:
        score += 10
    
    return min(score, 100)

def categorize_risk(score):
    """Categorize risk based on score"""
    if score <= 33:
        return 'Low Risk'
    elif score <= 66:
        return 'Medium Risk'
    else:
        return 'High Risk'

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Header
    st.title("📊 Customer Risk Scoring Dashboard")
    st.markdown("### Interactive Credit Card Risk Assessment System")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("---")
        
        # Data generation parameters
        st.subheader("Data Parameters")
        n_customers = st.slider(
            "Number of Customers", 
            min_value=100, 
            max_value=5000, 
            value=1000, 
            step=100
        )
        
        seed = st.number_input("Random Seed", min_value=1, max_value=100, value=42)
        
        # Risk threshold customization
        st.subheader("Risk Thresholds")
        low_threshold = st.slider("Low Risk Max Score", 0, 50, 33)
        high_threshold = st.slider("High Risk Min Score", 51, 100, 67)
        
        # Generate data button
        if st.button("🔄 Generate New Data", type="primary"):
            st.cache_data.clear()
        
        st.markdown("---")
        st.subheader("📋 About")
        st.info("""
        This dashboard provides interactive exploration of customer risk scores using:
        - Rule-based scoring methodology
        - Multiple risk factors analysis
        - Real-time visualization
        - Segment comparison tools
        """)
    
    # Generate and process data
    with st.spinner("Generating customer data..."):
        df = generate_customer_data(n_customers, seed)
        df['risk_score'] = df.apply(calculate_risk_score, axis=1)
        df['risk_category'] = df['risk_score'].apply(categorize_risk)
    
    # ========================================================================
    # KPI METRICS
    # ========================================================================
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Customers",
            value=f"{len(df):,}",
            delta=None
        )
    
    with col2:
        avg_risk = df['risk_score'].mean()
        st.metric(
            label="Avg Risk Score",
            value=f"{avg_risk:.1f}",
            delta=None
        )
    
    with col3:
        low_risk_pct = (df['risk_category'] == 'Low Risk').sum() / len(df) * 100
        st.metric(
            label="Low Risk %",
            value=f"{low_risk_pct:.1f}%",
            delta="Good" if low_risk_pct > 60 else "Monitor"
        )
    
    with col4:
        high_risk_pct = (df['risk_category'] == 'High Risk').sum() / len(df) * 100
        st.metric(
            label="High Risk %",
            value=f"{high_risk_pct:.1f}%",
            delta="Alert" if high_risk_pct > 15 else "Normal"
        )
    
    with col5:
        avg_utilization = df['credit_utilization'].mean()
        st.metric(
            label="Avg Utilization",
            value=f"{avg_utilization:.1f}%",
            delta=None
        )
    
    st.markdown("---")
    
    # ========================================================================
    # VISUALIZATION TABS
    # ========================================================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", 
        "🎯 Risk Analysis", 
        "💰 Financial Metrics",
        "👥 Customer Segments",
        "🔍 Individual Lookup"
    ])
    
    # TAB 1: OVERVIEW
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk Score Distribution
            fig1 = go.Figure()
            fig1.add_trace(go.Histogram(
                x=df['risk_score'],
                nbinsx=30,
                name='Risk Score',
                marker_color='steelblue',
                opacity=0.7
            ))
            fig1.add_vline(
                x=df['risk_score'].mean(),
                line_dash="dash",
                line_color="red",
                annotation_text=f"Mean: {df['risk_score'].mean():.1f}"
            )
            fig1.update_layout(
                title="Risk Score Distribution",
                xaxis_title="Risk Score",
                yaxis_title="Frequency",
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Risk Category Pie Chart
            risk_counts = df['risk_category'].value_counts()
            fig2 = go.Figure(data=[go.Pie(
                labels=risk_counts.index,
                values=risk_counts.values,
                marker=dict(colors=['#2ecc71', '#f39c12', '#e74c3c']),
                hole=0.4
            )])
            fig2.update_layout(
                title="Risk Category Distribution",
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Summary Statistics Table
        st.subheader("📋 Summary Statistics by Risk Category")
        summary_stats = df.groupby('risk_category').agg({
            'age': 'mean',
            'income': 'mean',
            'credit_utilization': 'mean',
            'late_payment_count': 'mean',
            'risk_score': 'mean'
        }).round(2)
        
        summary_stats.columns = ['Avg Age', 'Avg Income', 'Avg Utilization %', 'Avg Late Payments', 'Avg Risk Score']
        st.dataframe(summary_stats, use_container_width=True)
    
    # TAB 2: RISK ANALYSIS
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Credit Utilization vs Risk Score
            fig3 = px.scatter(
                df,
                x='credit_utilization',
                y='risk_score',
                color='risk_category',
                color_discrete_map={'Low Risk': '#2ecc71', 'Medium Risk': '#f39c12', 'High Risk': '#e74c3c'},
                title='Credit Utilization vs Risk Score',
                labels={'credit_utilization': 'Credit Utilization (%)', 'risk_score': 'Risk Score'}
            )
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Late Payments Box Plot
            fig4 = px.box(
                df,
                x='risk_category',
                y='late_payment_count',
                color='risk_category',
                color_discrete_map={'Low Risk': '#2ecc71', 'Medium Risk': '#f39c12', 'High Risk': '#e74c3c'},
                title='Late Payments by Risk Category'
            )
            fig4.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig4, use_container_width=True)
        
        # Correlation Heatmap
        st.subheader("🔥 Feature Correlation Heatmap")
        corr_features = ['age', 'income', 'credit_utilization', 'late_payment_count', 'risk_score']
        corr_matrix = df[corr_features].corr()
        
        fig5 = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_features,
            y=corr_features,
            colorscale='RdBu_r',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10}
        ))
        fig5.update_layout(height=500, title="Correlation Matrix")
        st.plotly_chart(fig5, use_container_width=True)
    
    # TAB 3: FINANCIAL METRICS
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Income Distribution
            fig6 = px.histogram(
                df,
                x='income',
                color='risk_category',
                color_discrete_map={'Low Risk': '#2ecc71', 'Medium Risk': '#f39c12', 'High Risk': '#e74c3c'},
                title='Income Distribution by Risk Category',
                labels={'income': 'Income (IDR)'},
                barmode='overlay',
                opacity=0.7
            )
            fig6.update_layout(height=400)
            st.plotly_chart(fig6, use_container_width=True)
        
        with col2:
            # Debt to Income Ratio
            fig7 = px.box(
                df,
                x='risk_category',
                y='debt_to_income',
                color='risk_category',
                color_discrete_map={'Low Risk': '#2ecc71', 'Medium Risk': '#f39c12', 'High Risk': '#e74c3c'},
                title='Debt-to-Income Ratio by Risk'
            )
            fig7.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig7, use_container_width=True)
        
        # Payment Status Analysis
        st.subheader("💳 Payment Status Analysis")
        payment_risk = pd.crosstab(df['payment_status'], df['risk_category'])
        
        fig8 = go.Figure()
        for category in ['Low Risk', 'Medium Risk', 'High Risk']:
            fig8.add_trace(go.Bar(
                name=category,
                x=payment_risk.index,
                y=payment_risk[category],
                marker_color={'Low Risk': '#2ecc71', 'Medium Risk': '#f39c12', 'High Risk': '#e74c3c'}[category]
            ))
        
        fig8.update_layout(
            barmode='stack',
            title='Payment Status vs Risk Category',
            xaxis_title='Payment Status',
            yaxis_title='Number of Customers',
            height=400
        )
        st.plotly_chart(fig8, use_container_width=True)
    
    # TAB 4: CUSTOMER SEGMENTS
    with tab4:
        st.subheader("🎯 Segment Deep Dive")
        
        # Segment selector
        selected_segment = st.selectbox(
            "Select Risk Segment to Analyze:",
            options=['All', 'Low Risk', 'Medium Risk', 'High Risk']
        )
        
        # Filter data
        if selected_segment != 'All':
            segment_df = df[df['risk_category'] == selected_segment]
        else:
            segment_df = df
        
        # Segment metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Customers", f"{len(segment_df):,}")
        with col2:
            st.metric("Avg Score", f"{segment_df['risk_score'].mean():.1f}")
        with col3:
            st.metric("Avg Utilization", f"{segment_df['credit_utilization'].mean():.1f}%")
        with col4:
            st.metric("Avg Late Payments", f"{segment_df['late_payment_count'].mean():.2f}")
        
        # Segment characteristics
        col1, col2 = st.columns(2)
        
        with col1:
            # Age distribution
            fig9 = px.histogram(
                segment_df,
                x='age',
                nbins=20,
                title=f'Age Distribution - {selected_segment}',
                color_discrete_sequence=['steelblue']
            )
            fig9.update_layout(height=350)
            st.plotly_chart(fig9, use_container_width=True)
        
        with col2:
            # Employment status
            employment_counts = segment_df['employment_status'].value_counts()
            fig10 = px.pie(
                values=employment_counts.values,
                names=employment_counts.index,
                title=f'Employment Status - {selected_segment}'
            )
            fig10.update_layout(height=350)
            st.plotly_chart(fig10, use_container_width=True)
        
        # Top risky customers in segment
        st.subheader(f"⚠️ Top 10 Highest Risk Customers in {selected_segment}")
        top_risk = segment_df.nlargest(10, 'risk_score')[
            ['customer_id', 'risk_score', 'credit_utilization', 'late_payment_count', 'payment_status']
        ]
        st.dataframe(top_risk, use_container_width=True)
    
    # TAB 5: INDIVIDUAL LOOKUP
    with tab5:
        st.subheader("🔍 Individual Customer Lookup")
        
        # Customer ID input
        customer_id = st.selectbox(
            "Select Customer ID:",
            options=df['customer_id'].tolist()
        )
        
        # Get customer data
        customer = df[df['customer_id'] == customer_id].iloc[0]
        
        # Display customer card
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown("### 👤 Customer Profile")
            st.write(f"**Customer ID:** {customer['customer_id']}")
            st.write(f"**Age:** {customer['age']} years")
            st.write(f"**Income:** Rp {customer['income']:,.0f}")
            st.write(f"**Employment:** {customer['employment_status']}")
            st.write(f"**Dependents:** {customer['dependents']}")
        
        with col2:
            st.markdown("### 💳 Credit Profile")
            st.write(f"**Credit Limit:** Rp {customer['credit_limit']:,.0f}")
            st.write(f"**Utilization:** {customer['credit_utilization']:.1f}%")
            st.write(f"**Monthly Spending:** Rp {customer['avg_monthly_spending']:,.0f}")
            st.write(f"**Account Age:** {customer['account_age_months']} months")
        
        with col3:
            st.markdown("### 📊 Risk Assessment")
            
            # Risk score with color
            risk_color = {'Low Risk': 'green', 'Medium Risk': 'orange', 'High Risk': 'red'}[customer['risk_category']]
            st.markdown(f"**Risk Score:** <span style='font-size:24px; color:{risk_color}; font-weight:bold;'>{customer['risk_score']:.0f}</span>", unsafe_allow_html=True)
            st.markdown(f"**Category:** <span style='color:{risk_color}; font-weight:bold;'>{customer['risk_category']}</span>", unsafe_allow_html=True)
            st.write(f"**Payment Status:** {customer['payment_status']}")
            st.write(f"**Late Payments:** {customer['late_payment_count']}")
            st.write(f"**Missed Payments (6m):** {customer['missed_payment_6m']}")
        
        # Risk gauge chart
        st.markdown("### 🎯 Risk Score Gauge")
        
        fig11 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=customer['risk_score'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Risk Score", 'font': {'size': 24}},
            delta={'reference': df['risk_score'].mean(), 'increasing': {'color': "red"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': risk_color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 33], 'color': '#d4edda'},
                    {'range': [33, 66], 'color': '#fff3cd'},
                    {'range': [66, 100], 'color': '#f8d7da'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 66
                }
            }
        ))
        
        fig11.update_layout(height=300)
        st.plotly_chart(fig11, use_container_width=True)
        
        # Recommendations
        st.markdown("### 💡 Recommendations")
        
        if customer['risk_category'] == 'Low Risk':
            st.success("""
            ✅ **Low Risk Customer - Maintain Good Standing**
            - Continue monitoring regular payment behavior
            - Consider for credit limit increase
            - Eligible for premium product offerings
            - Reward loyalty with benefits program
            """)
        elif customer['risk_category'] == 'Medium Risk':
            st.warning("""
            ⚠️ **Medium Risk Customer - Enhanced Monitoring**
            - Send payment reminders before due dates
            - Monitor credit utilization closely
            - Offer financial literacy resources
            - Consider payment plan options if needed
            """)
        else:
            st.error("""
            🚨 **High Risk Customer - Intensive Review**
            - Immediate collections team review required
            - Freeze or reduce credit limit
            - Require collateral for new transactions
            - Implement strict payment monitoring
            - Consider account suspension if delinquent
            """)
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Customer Risk Scoring Dashboard v1.0 | Built with Streamlit & Plotly</p>
        <p>© 2024 | For Portfolio Demonstration</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
```

---

## 📝 CARA COPY & SAVE (CODE 2):

### **Step 1: Copy Code**
1. **Select semua** code di atas (Ctrl+A di dalam code box)
2. **Copy** (Ctrl+C)

### **Step 2: Paste ke Notepad**
1. Buka **Notepad** baru
2. **Paste** (Ctrl+V)

### **Step 3: Save as .py File**
1. **File** → **Save As**
2. **File name:** `streamlit_dashboard.py`
3. **Save as type:** **All Files (*.*)**
4. **Save di:** `Desktop/upload-github/src/`
5. Klik **Save**

---

## ✅ Sekarang Anda Punya 2 Files Python:

Di folder `src/`, seharusnya ada:
- ✅ `risk_scoring_model.py` (file pertama)
- ✅ `streamlit_dashboard.py` (file kedua)

---

## 📦 RECAP: Semua Files yang Harus Ada

Di folder `Desktop/upload-github/`:
```
upload-github/
├── outputs/
│   └── risk_scoring_dashboard.png       ← Dari Colab
│
├── data/
│   └── customer_risk_scores.csv         ← Dari Colab
│
├── notebooks/
│   └── Customer_Risk_Scoring_Model.ipynb ← Dari Colab
│
└── src/
    ├── risk_scoring_model.py            ← CODE 1 (yang tadi)
    └── streamlit_dashboard.py           ← CODE 2 (yang ini)