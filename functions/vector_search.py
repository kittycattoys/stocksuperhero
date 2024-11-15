from supabase import create_client, Client
import pandas as pd
import streamlit as st

# Initialize Supabase client using Streamlit secrets with explicit typing
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    supabase: Client = create_client(url, key)  # Explicitly specifying the type
    return supabase

def get_supabase_dataframe(search_valuation_vector, search_trend_vector):
    """
    Executes a semantic search query on Supabase using vector search and returns the result as a DataFrame.

    Parameters:
    - search_valuation_vector: The valuation vector to search by.
    - search_trend_vector: The trend vector to search by.
    - selected_stock_symbol: Filter by specific stock symbol if provided.

    Returns:
    - DataFrame with the query results.
    """
    supabase: Client = init_supabase()  # Using explicit typing here as well

    # Define the SQL query, including symbol filtering
    SEMANTIC_SQL = """
    SELECT 
        sym, 
        valuation_string, 
        1 - (valuation_string_vector <=> %s::vector) AS cos_sim_val_supa,
        (valuation_string_vector <=> %s::vector) AS cos_dif_val_supa,
        trend_string, 
        1 - (trend_string_vector <=> %s::vector) AS cos_sim_trend_supa,
        (trend_string_vector <=> %s::vector) AS cos_dif_trend_supa
    FROM vector_table
    ORDER BY cos_sim_val_supa DESC
    LIMIT 100
    """

    # Execute the query
    response = supabase.rpc("execute_sql", {
        "sql": SEMANTIC_SQL,
        "params": [search_valuation_vector, search_valuation_vector, search_trend_vector, search_trend_vector]
    }).execute()

    # Check for errors in the response
    if response.error:
        print("Error:", response.error)
        return pd.DataFrame()

    # Convert response data to a DataFrame
    data = response.data
    df = pd.DataFrame(data)

    return df
