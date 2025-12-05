import streamlit as st
import pandas as pd

# ------------------------------------------------
# 1. SETUP AND DYNAMIC DATA LOADING (Phase 4)
# ------------------------------------------------

st.title("Interactive Sales Data Analyzer")
st.sidebar.header("Upload & Filters")

# File Uploader: This replaces the static pd.read_csv('sales_data.csv')
uploaded_file = st.sidebar.file_uploader(
    "Upload Your CSV File", 
    type=["csv"]
)

# Initialize df as an empty DataFrame
df = pd.DataFrame() 

if uploaded_file is not None:
    # Read the uploaded file object directly
    try:
        # NOTE: We skip index_col here as user-uploaded files might not have a clean index column.
        df = pd.read_csv(uploaded_file) 
        st.success("File uploaded and read successfully!")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.markdown("Please ensure the file is a clean CSV with standard comma delimiters.")
    
    
# ------------------------------------------------
# 2. FILTERING LOGIC (Phase 2)
# The rest of the app only runs if the DataFrame is not empty
# ------------------------------------------------

if not df.empty:
    
    # --- Data Preview ---
    st.subheader("Raw Data Preview")
    st.dataframe(df)

    # --- CATEGORICAL FILTER (Dropdown/Multi-Select) ---
    # Assuming the user's data still has a 'Category' column for this demo
    if 'Category' in df.columns:
        categories = df['Category'].unique()
        selected_categories = st.sidebar.multiselect(
            'Select Product Category',
            options=categories,
            default=categories # Default selection is all
        )
        # Filter 1: Apply the categorical filter
        df_filtered_category = df[df['Category'].isin(selected_categories)]
    else:
        st.sidebar.warning("No 'Category' column found for filtering.")
        df_filtered_category = df # Use the full DataFrame if category is missing

    # --- NUMERIC FILTER (Slider) ---
    # Assuming the user's data still has a 'Units_Sold' column
    if 'Units_Sold' in df.columns:
        min_units = int(df['Units_Sold'].min())
        max_units = int(df['Units_Sold'].max())

        unit_range = st.sidebar.slider(
            'Minimum Units Sold',
            min_value=min_units,
            max_value=max_units,
            value=min_units
        )
        # Filter 2: Apply the numeric filter (AND condition with the first filter)
        df_final = df_filtered_category[df_filtered_category['Units_Sold'] >= unit_range]
    else:
        st.sidebar.warning("No 'Units_Sold' column found for slider filter.")
        df_final = df_filtered_category # Use the category-filtered data
        
        
    # ------------------------------------------------
    # 3. DISPLAY RESULTS & METRICS (Phase 3)
    # ------------------------------------------------

    st.subheader("Filtered Results")
    st.dataframe(df_final)
    
    # Only show visualization/metrics if the columns exist in the final filtered data
    if 'Category' in df_final.columns and 'Units_Sold' in df_final.columns and 'Price' in df_final.columns:
        st.subheader("Visual Summary of Filtered Data")

        # Bar Chart
        st.bar_chart(
            df_final, 
            x='Category', 
            y='Units_Sold',
            use_container_width=True
        )

        st.markdown("---")
        
        # Metrics
        total_units = df_final['Units_Sold'].sum()
        total_sales = (df_final['Price'] * df_final['Units_Sold']).sum()

        st.metric(label="Total Units in Filter", value=f"{total_units:,.0f}")
        st.metric(label="Estimated Total Sales Value", value=f"${total_sales:,.2f}")

# --- Instructions when no file is loaded ---
else:
    st.info("👈 Please use the uploader in the sidebar to begin analysis.")