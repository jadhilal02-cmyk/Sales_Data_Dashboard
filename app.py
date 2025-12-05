import streamlit as st
import pandas as pd
import io 

# ------------------------------------------------
# 0. SAMPLE DATA DEFINITION
# ------------------------------------------------

# Dataset 1: Sales Data (Original)
SALES_DATA_CSV = """
Product_ID,Product_Name,Category,Price,Units_Sold,Region
1,Laptop,Electronics,1200.00,50,North
2,Headphones,Accessories,99.99,150,South
3,Monitor,Electronics,350.50,75,North
4,Keyboard,Accessories,75.00,200,West
5,Webcam,Electronics,45.99,120,East
6,Desk Lamp,Home,25.00,300,South
7,Mouse,Accessories,15.99,500,West
8,Coffee Maker,Home,150.00,60,North
9,Speaker,Electronics,400.00,90,East
10,Book Stand,Home,12.50,450,South
"""

# Dataset 2: Team Data (New)
TEAM_DATA_CSV = """
Employee_ID,Full_Name,Department,Years_of_Service,Performance_Score,Review_Rating
T101,Smith, Alex,Engineering,5,92,Excellent
T203,Chen, Li,Product,2,85,Good
T305,Garcia, Maria,Design,8,98,Excellent
T401,Johnson, Ben,Engineering,1,79,Average
T504,Williams, Sam,Engineering,12,88,Good
T607,Patel, Kiran,Product,4,74,Average
T702,Davis, Nicole,Design,7,95,Excellent
T806,Brown, Tom,Engineering,3,82,Good
"""


# ------------------------------------------------
# 1. SETUP AND DYNAMIC DATA LOADING
# ------------------------------------------------

st.set_page_config(layout="wide") 
st.title("Interactive Data Analysis Dashboard")
st.sidebar.header("Data Source Selection")

# User Choice: Sample vs. Upload
source_choice = st.sidebar.radio(
    "Choose Data Source:",
    ('Upload Your Own CSV', 'Use Sample Data')
)

df = pd.DataFrame()

if source_choice == 'Use Sample Data':
    st.sidebar.markdown("---")
    st.sidebar.subheader("Sample Selection")
    sample_name = st.sidebar.selectbox(
        "Select a Sample File:",
        options=['Sales Data (Products)', 'Team Data (Employees)']
    )
    
    data_to_load = SALES_DATA_CSV if sample_name == 'Sales Data (Products)' else TEAM_DATA_CSV
    
    df = pd.read_csv(io.StringIO(data_to_load))
    st.info(f"Loaded Sample Data: **{sample_name}**")
    
else:
    # File Uploader Logic
    st.sidebar.markdown("---")
    st.sidebar.subheader("Upload Options")
    uploaded_file = st.sidebar.file_uploader(
        "Upload Your CSV File", 
        type=["csv"]
    )
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file) 
            st.success("File uploaded and read successfully!")
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.markdown("Please ensure the file is a clean CSV with standard comma delimiters.")


# ------------------------------------------------
# 2. DYNAMIC FILTERING LOGIC
# ------------------------------------------------

if not df.empty:
    
    # --- Data Preview ---
    st.subheader("Raw Data Preview")
    st.dataframe(df)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Dynamic Filters")

    # Initialize dataframes for filtering
    df_filtered_category = df.copy()
    
    # --- CATEGORICAL FILTER (Text Columns) ---
    categorical_cols = df.select_dtypes(include=['object', 'bool']).columns.tolist()

    if categorical_cols:
        cat_to_filter = st.sidebar.selectbox(
            'Select Categorical Column',
            options=categorical_cols
        )
        unique_values = df[cat_to_filter].unique()
        selected_values = st.sidebar.multiselect(
            f'Filter by {cat_to_filter}',
            options=unique_values,
            default=unique_values
        )
        df_filtered_category = df[df[cat_to_filter].isin(selected_values)]
    
    
    # --- NUMERIC FILTER (Number Columns) ---
    df_final = df_filtered_category.copy() 
    numeric_cols = df_final.select_dtypes(include=['number']).columns.tolist()

    if numeric_cols:
        num_to_filter = st.sidebar.selectbox(
            'Select Numeric Column',
            options=numeric_cols
        )

        min_val = df_final[num_to_filter].min()
        max_val = df_final[num_to_filter].max()

        min_range = st.sidebar.slider(
            f'Minimum {num_to_filter}',
            min_value=min_val,
            max_value=max_val,
            value=min_val 
        )
        # Apply the numeric filter (AND condition)
        df_final = df_filtered_category[df_filtered_category[num_to_filter] >= min_range]
    
    
    # ------------------------------------------------
    # 3. DISPLAY RESULTS & METRICS
    # ------------------------------------------------

    st.subheader("Filtered Results")
    st.markdown(f"**Total Rows Found:** {len(df_final)}")
    st.dataframe(df_final)
    
    
    # --- Visualization and Metrics ---
    st.markdown("---")
    
    if len(df_final) > 0 and numeric_cols:
        
        st.subheader("Visual Summary")

        # --- Chart Type Selection ---
        chart_type = st.selectbox(
            "Select Chart Type:",
            options=['Bar Chart (Grouped)', 'Line Chart (Trend)', 'Histogram (Distribution)', 'Pie Chart (Composition)']
        )
        
        # Determine best defaults for charting
        default_x = categorical_cols[0] if categorical_cols else df_final.columns.tolist()[0]
        default_y = numeric_cols[0]
        
        # --- X-Axis Selection ---
        x_options = df_final.columns.tolist()
        default_x_index = x_options.index(default_x) if default_x in x_options else 0
        
        chart_x = st.selectbox("Select column for Grouping/X-axis", 
                               options=x_options, 
                               index=default_x_index)
        
        # --- Y-Axis Selection ---
        y_options = numeric_cols
        default_y_index = y_options.index(default_y) if default_y in y_options else 0
        
        chart_y = st.selectbox("Select column for Value/Y-axis", 
                               options=y_options, 
                               index=default_y_index)

        st.markdown("---") 

        # --- Conditional Chart Rendering ---
        
        if chart_type == 'Bar Chart (Grouped)':
            st.bar_chart(
                df_final.groupby(chart_x)[chart_y].sum(),
                use_container_width=True
            )
            st.caption(f"Bar Chart showing the sum of **{chart_y}** grouped by **{chart_x}**.")

        elif chart_type == 'Line Chart (Trend)':
            st.line_chart(
                data=df_final, 
                x=chart_x, 
                y=chart_y,
                use_container_width=True
            )
            st.caption(f"Line Chart showing the raw trend of **{chart_y}** over **{chart_x}**.")

        elif chart_type == 'Histogram (Distribution)':
            # Uses value_counts to simulate a histogram on the chosen numeric column
            st.bar_chart(
                df_final[chart_y].value_counts().sort_index(),
                use_container_width=True
            )
            st.caption(f"Distribution Chart showing the frequency of values in **{chart_y}**.")

        elif chart_type == 'Pie Chart (Composition)':
            st.subheader(f"Composition by {chart_x}")
            
            composition_data = df_final.groupby(chart_x)[chart_y].sum()
            total_sum = composition_data.sum()
            
            if total_sum > 0:
                composition_data = (composition_data / total_sum) * 100
                top_groups = composition_data.sort_values(ascending=False).head(3)
                
                col_top = st.columns(3)
                for i, (label, percent) in enumerate(top_groups.items()):
                    if i < 3:
                        col_top[i].metric(
                            label=label, 
                            value=f"{percent:.1f}%"
                        )
                st.caption("Composition analysis shown via top group percentages.")
            else:
                st.warning("Cannot calculate composition. Sum of selected value is zero.")

        
        # --- Metrics (Aggregation) ---
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Units_Sold' in df_final.columns:
                total_units = df_final['Units_Sold'].sum()
                st.metric(label="Total Units Sold in Filter", value=f"{total_units:,.0f}")
            elif 'Performance_Score' in df_final.columns:
                 avg_score = df_final['Performance_Score'].mean()
                 st.metric(label="Average Performance Score", value=f"{avg_score:.1f}")

        with col2:
            if all(col in df_final.columns for col in ['Price', 'Units_Sold']):
                total_sales = (df_final['Price'] * df_final['Units_Sold']).sum()
                st.metric(label="Estimated Total Sales Value", value=f"${total_sales:,.2f}")
            elif 'Years_of_Service' in df_final.columns:
                avg_service = df_final['Years_of_Service'].mean()
                st.metric(label="Average Years of Service", value=f"{avg_service:.1f} years")

    st.markdown("---")


# --- Instructions when no file is loaded ---
else:
    st.info("👈 Please select a sample file or use the uploader to begin analysis. This tool works with any standard CSV file.")
