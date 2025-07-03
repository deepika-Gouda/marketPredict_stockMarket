import streamlit as st
from datetime import datetime, date
import yfinance as yf
from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go
import pandas as pd
import time

# Custom styles
st.markdown("""
    <style>
    .main-title {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        color: #4CAF50;
    }
    .sidebar-title {
        font-size: 24px;
        font-weight: bold;
        color: #2196F3;
    }
    .expander-header {
        font-weight: bold;
        font-size: 20px;
        color: #FF5722;
    }
    .footer {
        font-size: 14px;
        text-align: center;
        margin-top: 50px;
        color: #757575;
    }
    </style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<p class="main-title">📊 Welcome to Stock World</p>', unsafe_allow_html=True)

# Sidebar title
st.sidebar.markdown('<p class="sidebar-title">🔧 Check Your Forecast</p>', unsafe_allow_html=True)

# Sidebar inputs
stocks = [
    "ADANIENT.NS", "WIPRO.NS", "HEROMOTOCO.NS", "SUZLON.NS", "TVSMOTOR.NS", "TATAMOTORS.NS", "OLAELEC.NS",
    "HYUNDAI.NS", "INFY.NS", "IRCON.NS", "RVNL.NS", "GENSOL.NS", "HINDCOPPER.NS", "OLECTRA.NS",
    "KPITTECH.NS", "BSOFT.NS", "RELIANCE.NS", "HINDPETRO.NS", "BPCL.NS", "CASTROLIND.NS", "MARUTI.NS",
    "M&M.NS", "AMBUJACEM.NS"
]
selected_stock = st.sidebar.selectbox("📌 Select Stock", stocks)

START = st.sidebar.date_input("📅 Start Date", value=date(2023, 1, 1))
END = st.sidebar.date_input("📅 End Date", value=date.today())
if START >= END:
    st.sidebar.error("⚠ End date must be after start date.")
    st.stop()
n_years = st.sidebar.slider("⏳ Prediction Period (Years):", 1, 5)
period = n_years * 365

# Function to load intraday stock data with fallback
@st.cache_data
def load_data(ticker, start, end, interval="1m"):
    try:
        data = yf.download(ticker, start=start, end=end, interval=interval)
        if data.empty:
            return None
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return None
    
# Function to fetch today's price for the selected stock
@st.cache_data
def get_today_price(ticker):
    try:
        time.sleep(2)  # Introduce a 2-second delay
        # Download the last day's data (1 day interval)
        data = yf.download(ticker, period="1d", interval="1m")
        if data.empty:
            st.error("⚠ No data available for the selected stock.")
            st.stop()
        # Get the latest close price
        latest_price = data['Close'].iloc[-1]
        return latest_price
    except Exception as e:
        st.error(f"❌ Error fetching today's price: {e}")
        st.stop()

# Function to refresh data
def refresh_data():
    data = load_data(selected_stock, START, END, interval="1m")  # Try 1m interval first
    if data is None:
        st.warning("⚠ Failed to load 1-minute data. Trying hourly data...")
        data = load_data(selected_stock, START, END, interval="1h")  # Fallback to 1-hour interval
        if data is None:
            st.error(f"⚠ No data available for {selected_stock}.")
    st.write(data) 
    return data

# Real-time updates functionality
st.subheader("📈 Real-time Stock Price Updates")
st.text("Refreshing stock data every minute...")

# Display today's price
today_price = get_today_price(selected_stock)
st.write(f"📉 {selected_stock} Price is : ₹{today_price:.2f}")

# Refresh data initially
data = refresh_data()

# Display updated data if data is available
if data is not None:
    with st.expander("📋 Price Movements"):
        st.markdown('<p class="expander-header">Stock Data</p>', unsafe_allow_html=True)
        st.write(data)
    
    # Candlestick chart plotting function for real data
    def plot_candlestick(data):
        fig = go.Figure(
            data=[go.Candlestick(
                x=data['Datetime'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Candlestick Chart"
            )]
        )
        fig.update_layout(
            title=f"Candlestick Chart for {selected_stock}",
            xaxis_title="Datetime",
            yaxis_title="Price (₹)",
            width=2000,  # Increased width
            height=700,  # Adjusted height
            xaxis_rangeslider_visible=True  # Added range slider
        )
        st.plotly_chart(fig)

    # Candlestick chart display for real data
    st.subheader("📉 Stock Analysis")
    plot_candlestick(data)

    # Forecasting function
    def forecast_stock(data, period):
        if 'Datetime' in data.columns:
            data = data.rename(columns={"Datetime": "Date"})
        data['Date'] = pd.to_datetime(data['Date']).dt.tz_localize(None)  # Remove timezone

        # Prepare data for Prophet
        df_train = data[['Date', 'Close']].rename(columns={"Date": "ds", "Close": "y"})

        # Initialize and train Prophet model
        model = Prophet()
        model.fit(df_train)

        # Create future dates and remove timezone
        future_dates = model.make_future_dataframe(periods=period)
        future_dates['ds'] = future_dates['ds'].dt.tz_localize(None)  # Ensure timezone-naive

        # Generate forecast
        forecast = model.predict(future_dates)

        return model, forecast

    # Generate forecast
    st.subheader("📈 Stock Forecast")
    model, forecast = forecast_stock(data, period)

    # Ensure current date filtering
    today = date.today()  # Correct usage of date.today()
    forecast['ds'] = pd.to_datetime(forecast['ds']).dt.date  # Convert to date format
    future_forecast = forecast[forecast['ds'] >= today]  # Filter only future dates

    # Display the future forecast
    if not future_forecast.empty:
        st.write(f"🔮 Future forecast data starting from today:")
        st.write(future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']])
    else:
        st.error("⚠ No forecast data available starting from tomorrow.")

    # Forecast explanation
    st.caption("""
- ds: Date of the forecasted data.
- yhat: Predicted stock price.
- yhat_lower: Lower bound of the predicted price (confidence interval).
- yhat_upper: Upper bound of the predicted price (confidence interval).
""")

    # Forecast Candlestick plot using predicted data
    st.subheader("📊 Forecasted Stock Data")

    # Preparing forecasted data as open, high, low, close for candlestick
    forecast_candlestick_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()

    # Rename columns to match the candlestick chart format
    forecast_candlestick_data.columns = ['Date', 'Close', 'Low', 'High']

    # Create the Candlestick chart for the forecasted data
    fig = go.Figure(
        data=[go.Candlestick(
            x=forecast_candlestick_data['Date'],
            open=forecast_candlestick_data['Close'],  # You can use Close for 'open' here
            high=forecast_candlestick_data['High'],
            low=forecast_candlestick_data['Low'],
            close=forecast_candlestick_data['Close'],
            name="Forecasted Chart"
        )]
    )

    fig.update_layout(
        title=f"Forecasted Candlestick Chart for {selected_stock}",
        xaxis_title="Date",
        yaxis_title="Price (₹)",
        width=2000,  # Set the width of the chart
        height=700,  # Set the height of the chart
        autosize=True,  # Automatically adjust chart size
        xaxis=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=7, label="1 Week", step="day", stepmode="todate"),
                    dict(count=1, label="1 Month", step="month", stepmode="todate"),
                    dict(count=3, label="3 Months", step="month", stepmode="todate"),
                    dict(count=1, label="1 Year", step="year", stepmode="todate"),
                    dict(step="all", label="All")  # Option to show all data
                ],
                visible=True,  # Make the range selector visible
                x=0.5,  # Center the range selector
                xanchor="center"  # Align it to the center
            ),
            rangeslider=dict(
                visible=True,  # Keep the range slider visible
                thickness=0.1  # Adjust the thickness of the range slider
            ),
            type="date"  # Set x-axis to interpret data as dates
        ),
        showlegend=False  # Optionally hide the legend if not needed
    )

    # Display the plot
    st.plotly_chart(fig)

    # Download options
    st.sidebar.download_button(
        label="📥 Download Raw Data",
        data=data.to_csv(index=False),
        file_name=f"{selected_stock}_raw_data.csv",
        mime="text/csv"
    )
    st.sidebar.download_button(
        label="📥 Download Forecast Data",
        data=future_forecast.to_csv(index=False),
        file_name=f"{selected_stock}_forecast_data.csv",
        mime="text/csv"
    )
else:
    st.error(f"⚠ Unable to fetch data for {selected_stock} in the given date range.")
