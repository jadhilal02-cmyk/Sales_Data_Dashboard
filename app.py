import streamlit as st
import pandas as pd

# ------------------------------------------------
# 1. SETUP AND DYNAMIC DATA LOADING (Phase 4)
# ------------------------------------------------

st.title("Interactive Data Analysis Dashboard")
st.sidebar.header("Upload & Filters")

# File Uploader: Allows users to upload any CSV file
uploaded_file = st.sidebar.file_uploader(
    "Upload Your CSV File", 
    type=["csv"]
)

# Initialize df as an empty DataFrame
df = pd.DataFrame() 

if uploaded_file is not None:
    # Read the uploaded file object directly
    try:
        # NOTE: Using a robust read without assuming index columns.
        df = pd.read_csv(uploaded_file) 
        st.success("File uploaded and read successfully!")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.markdown("Please ensure the file is a clean CSV with standard comma delimiters.")
    
    
# ------------------------------------------------
# 2. DYNAMIC FILTERING LOGIC (Phase 5)
# ------------------------------------------------

# The rest of the app only runs if the DataFrame is not empty
if not df.empty:
    
    # --- Data Preview ---
    st.subheader("Raw Data Preview")
    st.dataframe(df)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Dynamic Filters")

    # --- CATEGORICAL FILTER (Text Columns) ---
    df_filtered_category = df.copy() # Start with a copy of the original data
    
    # Find all columns that contain text data (object or string type)
    categorical_cols = df.select_dtypes(include=['object', 'bool']).columns.tolist()

    if categorical_cols:
        # Let the user choose which categorical column to filter on
        cat_to_filter = st.sidebar.selectbox(
            'Select Categorical Column',
            options=categorical_cols
        )

        # Get the unique values from the chosen column for the multiselect options
        unique_values = df[cat_to_filter].unique()
        selected_values = st.sidebar.multiselect(
            f'Filter by {cat_to_filter}',
            options=unique_values,
            default=unique_values
        )
        # Apply the categorical filter (OR condition)
        df_filtered_category = df[df[cat_to_filter].isin(selected_values)]
    
    
    # --- NUMERIC FILTER (Number Columns) ---
    df_final = df_filtered_category.copy() # Start with the category-filtered data
    
    # Find all columns that contain numeric data (int or float type)
    numeric_cols = df_final.select_dtypes(include=['number']).columns.tolist()

    if numeric_cols:
        # Let the user choose which numeric column to filter on
        num_to_filter = st.sidebar.selectbox(
            'Select Numeric Column',
            options=numeric_cols
        )

        min_val = df_final[num_to_filter].min()
        max_val = df_final[num_to_filter].max()

        # Create a slider based on the min/max of the chosen column
        min_range = st.sidebar.slider(
            f'Minimum {num_to_filter}',
            min_value=min_val,
            max_value=max_val,
            value=min_val 
        )
        # Filter 2: Apply the numeric filter (AND condition)
        df_final = df_filtered_category[df_filtered_category[num_to_filter] >= min_range]
    
    
    # ------------------------------------------------
    # 3. DISPLAY RESULTS & METRICS (Phase 3)
    # ------------------------------------------------

    st.subheader("Filtered Results")
    st.markdown(f"**Total Rows Found:** {len(df_final)}")
    st.dataframe(df_final)
    
    
    # --- Visualization and Metrics ---
    st.markdown("---")
    
    # Check if necessary columns exist for visualization before plotting
    # This prevents the app from crashing if the user uploads data without specific columns
    required_cols_for_vis = [col for col in ['Category', 'Units_Sold', 'Price'] if col in df_final.columns]

    if len(required_cols_for_vis) >= 2 and 'Units_Sold' in required_cols_for_vis:
        st.subheader("Visual Summary")
        
        # We rely on the user selecting meaningful columns for charting
        chart_x = st.selectbox("Select column for X-axis (Chart Grouping)", options=df_final.columns.tolist())
        chart_y = st.selectbox("Select column for Y-axis (Chart Value)", options=numeric_cols)
        
        st.bar_chart(
            df_final, 
            x=chart_x, 
            y=chart_y,
            use_container_width=True
        )

    # --- Metrics (Aggregation) ---
    if all(col in df_final.columns for col in ['Price', 'Units_Sold']):
        total_units = df_final['Units_Sold'].sum()
        total_sales = (df_final['Price'] * df_final['Units_Sold']).sum()

        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total Units in Filter", value=f"{total_units:,.0f}")
        with col2:
            st.metric(label="Estimated Total Sales Value", value=f"${total_sales:,.2f}")
    
    st.markdown("---")


# --- Instructions when no file is loaded ---
else:
    st.info("👈 Please use the uploader in the sidebar to begin analysis. This tool works with any standard CSV file.")
