import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Database connection details
DB_USER = 'postgres'
DB_PASSWORD = 'Iphone14pro'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'nanum'

# Function to create a connection to the database
def get_db_connection():
    engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
    return engine

# Function to fetch data for a specific table
def fetch_data(table_name):
    engine = get_db_connection()
    query = f'SELECT * FROM "{table_name}"'
    try:
        df = pd.read_sql(query, engine)
        if df.empty:
            st.warning(f"No data available in table {table_name}.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        df = pd.DataFrame()  
    finally:
        engine.dispose()
    return df

# Function to calculate State of Health (SoH)
def calculate_soh(discharged_capacity, nominal_capacity):
    return (discharged_capacity / nominal_capacity) * 100

# Main function to build the Streamlit app
def main():
    st.title("Li-ion Cell Dashboard")

    # Sidebar for selecting pages
    page = st.sidebar.selectbox("Select Page", ["Overview", "Cell 5308", "Cell 5329"])

    if page == "Overview":
        st.header("Overview")

        # Calculating State of Health
        discharge_capacity_5308 = 2992.02
        nominal_capacity_5308 = 3000
        discharge_capacity_5329 = 2822.56
        nominal_capacity_5329 = 3000

        soh_5308 = calculate_soh(discharge_capacity_5308, nominal_capacity_5308)
        soh_5329 = calculate_soh(discharge_capacity_5329, nominal_capacity_5329)

        # Pie chart for State of Health
        fig = px.pie(names=["5308", "5329"], values=[soh_5308, soh_5329],
                     title="State of Health (%)")
        st.plotly_chart(fig)

    elif page.startswith("Cell"):
        cell_id = page.split()[1]
        st.header(f"Cell ID: {cell_id}")

        data = fetch_data(cell_id)

        # Check and print column names
        if not data.empty:
            st.write("Columns in the DataFrame:", data.columns)

            # Define columns for each chart
            chart_columns = {
                'Cur(mA)': ('Sheet no: 4, Column No: 6', 'Current vs Time'),
                'Voltage(V)': ('Sheet no: 4, Column No: 7', 'Voltage vs Time'),
                'CapaCity(mAh)': ('Sheet no: 4, Column No: 8', 'Capacity vs Time'),
                'Auxiliary channel TU1 T(°C)': ('Sheet no: 4, Column No: 12', 'Temperature vs Time'),
                'Absolute Time': ('Sheet no: 4, Column No: 11', 'Time Data')
            }

            for col_name, (info, chart_title) in chart_columns.items():
                if col_name in data.columns:
                    st.subheader(chart_title)
                    st.line_chart(data[col_name])
                else:
                    st.warning(f"Column '{col_name}' not found in data.")
        else:
            st.error("No data available for the selected cell.")

if __name__ == "__main__":
    main()
