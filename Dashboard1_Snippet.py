import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
import os

# Function to initialize and cache the database connection
@st.cache_resource
def init_db_connection():
    # Path to the configuration file containing DB credentials
    config_path = os.path.join(".streamlit", "Dashboard1.toml")

    if os.path.exists(config_path):
        config = {}
        with open(config_path, 'r') as f:
            # Parse simple key=value lines from the config
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip().strip('"')
        # Extract connection string or build from parameters
        connection_url = config.get('url', 
            f"mssql+pyodbc://{config.get('db_server', 'localhost')}/"
            f"{config.get('db_database', 'eoc')}?driver=ODBC+Driver+17+for+SQL+Server&"
            "trusted_connection=yes&TrustServerCertificate=yes")
    else:
        # Inform user if config file missing
        st.error("Dashboard1.toml file not found in .streamlit folder")
        return None

    # Create and return SQLAlchemy engine
    return create_engine(connection_url)

# Function to load cold wave data from the database with caching to enhance performance
@st.cache_data(ttl=600)
def load_data():
    query = "SELECT * FROM dbo.ColdWaveDetails"  # Simplified main data query

    engine = init_db_connection()
    if not engine:
        # Return empty DataFrame if DB connection unavailable
        return pd.DataFrame()

    # Load data directly into a pandas DataFrame
    df = pd.read_sql(query, engine)

    # Convert 'RecordDate' column to datetime for easier handling in app
    df['date'] = pd.to_datetime(df['RecordDate'], errors='coerce')

    # Return cleaned and ready dataframe
    return df

# Main Streamlit app function which hosts the dashboard UI logic
def run():
    df = load_data()

    if df.empty:
        st.error("Could not load cold wave data, please check connection.")
        return

    # Title/header of the dashboard
    st.title("ColdWave Disaster Management Dashboard")

    # Display last updated timestamp dynamically
    st.write(f"Last updated: {datetime.now():%Y-%m-%d %H:%M:%S}")

    # Aggregate some key KPIs from data for display
    affected_population = df['AffectedPeople'].sum()
    death_count = df['DeadPeople'].sum()

    # Show KPIs as metrics on the dashboard
    st.metric("Total Affected Population", affected_population)
    st.metric("Total Deaths Reported", death_count)

    # Additional dashboard UI components & visualizations would go here...

# Run the app when script executed
if __name__ == "__main__":
    run()
