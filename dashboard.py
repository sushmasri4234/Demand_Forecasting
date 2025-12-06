import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from forecast_model import DemandForecaster, generate_sample_data

def create_dashboard():
    st.title("Retail Demand Forecasting Dashboard")
    
    # Load data
    if 'data' not in st.session_state:
        st.session_state.data = generate_sample_data()
        st.session_state.forecaster = DemandForecaster()
        st.session_state.forecaster.fit(st.session_state.data)
    
    data = st.session_state.data
    forecaster = st.session_state.forecaster
    
    # Sidebar controls
    st.sidebar.header("Forecast Settings")
    forecast_periods = st.sidebar.slider("Forecast Periods (weeks)", 1, 12, 4)
    
    # Generate predictions
    predictions = forecaster.predict(data, periods=forecast_periods)
    
    # Main forecast chart
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['demand'],
        mode='lines+markers',
        name='Historical Demand',
        line=dict(color='blue')
    ))
    
    # Forecast
    future_dates = pd.date_range(
        start=data['date'].max() + pd.Timedelta(weeks=1),
        periods=forecast_periods,
        freq='W'
    )
    
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=predictions,
        mode='lines+markers',
        name='Forecast',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title="Weekly Demand Forecast",
        xaxis_title="Date",
        yaxis_title="Demand",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Avg Weekly Demand", f"{data['demand'].mean():.1f}")
    
    with col2:
        st.metric("Next Week Forecast", f"{predictions[0]:.1f}")
    
    with col3:
        change = ((predictions[0] - data['demand'].iloc[-1]) / data['demand'].iloc[-1]) * 100
        st.metric("Week-over-Week Change", f"{change:.1f}%")
    
    # Forecast table
    st.subheader("Forecast Details")
    forecast_df = pd.DataFrame({
        'Week': range(1, forecast_periods + 1),
        'Date': future_dates,
        'Predicted Demand': [f"{p:.1f}" for p in predictions]
    })
    st.dataframe(forecast_df, use_container_width=True)

if __name__ == "__main__":
    create_dashboard()