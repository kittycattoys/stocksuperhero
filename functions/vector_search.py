import psycopg2
from pgvector.psycopg2 import register_vector
import pandas as pd
import streamlit as st

conn_params = {
    'database': st.secrets["supabaseparams"]["database"],
    'user': st.secrets["supabaseparams"]["user"],
    'password': st.secrets["supabaseparams"]["password"],
    'host': st.secrets["supabaseparams"]["host"],
    'port': st.secrets["supabaseparams"]["port"],
    'sslmode': st.secrets["supabaseparams"]["sslmode"],
}

# Establish a connection to the database using provided parameters
def get_supabase_dataframe(search_valuation_vector, search_trend_vector):
    """
    Executes a semantic search query on Supabase using vector search and returns the result as a DataFrame.

    Parameters:
    - conn_params: dict containing connection parameters for the database.
    - search_valuation_vector: The valuation vector to search by.
    - search_trend_vector: The trend vector to search by.

    Returns:
    - DataFrame with the query results.
    """
    # Connect to the database
    connection_supabase = psycopg2.connect(**conn_params)
    cursor_supabase = connection_supabase.cursor()
    
    # Register pgvector for vector-based operations
    register_vector(connection_supabase)

    # SQL query for the semantic search
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
    cursor_supabase.execute(SEMANTIC_SQL, (search_valuation_vector, search_valuation_vector, search_trend_vector, search_trend_vector))
    
    # Fetch the result and load it into a DataFrame
    result = cursor_supabase.fetchall()
    columns = [desc[0] for desc in cursor_supabase.description]
    df = pd.DataFrame(result, columns=columns)

    # Close the connection
    cursor_supabase.close()
    connection_supabase.close()

    return df
