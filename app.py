# import libraries
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


def streamlit_dvd():
    # page config
    st.set_page_config(
        page_title="DVD Rental Business",
        layout="wide",
        initial_sidebar_state="expanded"
    )  
        
    #load datast
    df = pd.read_csv("full_data_dvdrental_cleaned.csv")
    
    # header
    st.title("📀 DVD Rental Business")
    st.caption("A stragetic overview of film rentals and revenue")
    st.markdown("---")
    
     # Sidebar Title
    st.sidebar.markdown("## 🧭 Dashboard Filters")
    st.sidebar.markdown("Fine-tune the dashboard using the filters below.")
    
     # date filter
    date_filter = st.sidebar.multiselect(
        "Date",
        options=df["date"].unique(),
        default=df["date"].unique()
    )
    
    # category filter
    category_filter = st.sidebar.multiselect(
        "Category",
        options=df["category"].unique(),
        default=df["category"].unique()
    )
    
     # store filter
    store_filter = st.sidebar.multiselect(
        "Store Id",
        options=df["store_id"].unique(),
        default=df["store_id"].unique()
    )
    
     # country filter
    country_filter = st.sidebar.multiselect(
        "Country",
        options=df["country"].unique(),
        default=df["country"].unique()
    )
    
     # apply filter
    filtered_df = df[
        (df["date"].isin(date_filter)) &
        (df["category"].isin(category_filter)) &
        (df["store_id"].isin(store_filter)) &
        (df["country"].isin(country_filter))
    ]
    
    # kpi summary
    if not filtered_df.empty:
        total_revenue = filtered_df["revenue"].sum()
        total_rental = filtered_df["rental_id"].count()
        active_customers = filtered_df["customer_id"].nunique()
        monthly_revenue = (filtered_df.groupby("year_month")["revenue"].sum().sort_index())
        if len(monthly_revenue) < 2:
            current_month_sales = monthly_revenue.iloc[-1]
            previous_month_sales = 0
            monthly_growth = 0
        else:
            current_month_sales = monthly_revenue.iloc[-1]
            previous_month_sales = monthly_revenue.iloc[-2]
            if previous_month_sales == 0:
                monthly_growth = 0
            else:
                monthly_growth = ((current_month_sales - previous_month_sales)/ previous_month_sales) * 100
    else:
        total_revenue = 0
        total_rental = 0
        active_customers = 0
        monthly_growth = 0
        
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.0f}")

    with col2:
        st.metric("Total Rental", total_rental)

    with col3:
        st.metric("Active Customers", active_customers)

    with col4:
        st.metric("Monthly Revenue Growth", f"{monthly_growth:.2f}%")
        
    st.markdown("---")
    
    
    # row 1 - monthly revenue growth and rental distribution
    left, right = st.columns(2)
    with left:
        monthly_revenue = (
            filtered_df.groupby("date")
            .agg(revenue=("revenue", "sum"))
            .sort_index()
            .reset_index()
        )
        st.subheader("Monthly Revenue Trend")
        fig_monthly_revenue = px.line(
            monthly_revenue,
            x="date",
            y="revenue",
            title="Line chart of Monthly Revenue"
        )
        fig_monthly_revenue.update_layout(showlegend=False)
        st.plotly_chart(fig_monthly_revenue, use_container_width=True)
        
        
    with right:
        customer_rental_distribution = (
            filtered_df.groupby("full_name")
            .agg(count=("rental_id", "count"))
            .sort_index()
            .reset_index()
         )
        st.subheader("Customer Rental Distribution")   
        fig_ren_dis = px.histogram(
            customer_rental_distribution,
            x="count",
            title="Histogram of Customer rentals",
            labels={
            "count": "Rentals per Customer"
            },
            nbins=30
        )
        fig_ren_dis.update_layout(showlegend=False)
        st.plotly_chart(fig_ren_dis, use_container_width=True)
        
    st.markdown("---") 
    
    
    # row 2 - top revenue film and category total revenue share
    left, right = st.columns(2)
    with left:
        top_10 = (
            filtered_df.groupby("film_title", as_index=False)
                .agg(value=("revenue", "sum"))
                .sort_values("value", ascending=False)
                .head(10)
        )
        st.subheader("Top 10 Films by Total revenue Revenue")
        fig_bar = px.bar(
            top_10,
            x="film_title",
            y="value",
            title="Bar of top 10 films by total revenue",
            labels={"film_title": "Film title", "value": "Total revenue ($)"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with right:
        revenue_by_category = (
            df.groupby("category", as_index=False)
                .agg(total_revenue=("revenue", "sum"))
        )
        st.subheader("Category Revenue Share")   
        fig_pie = px.pie(
        revenue_by_category,
        names="category",
        values="total_revenue",
        title="Pie chart of Revenue Share by Category",
        hole=0.4  # makes it a donut chart (optional but classy)
        )
        fig_pie.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---") 
    
    
    # row 3 - store comparism and  
    left, right = st.columns(2)
    with left:
        store_metrics = (
            df.groupby("store_id", as_index=False)
                .agg(
                total_revenue=("revenue", "sum"),
                total_rentals=("rental_id", "count")
                )
        )
        st.subheader("Store Rentals and Revenue Comparism")
        fig_store = px.bar(
            store_metrics,
            x="store_id",
            y=["total_revenue", "total_rentals"],
            barmode="group",
            title="Bar chart of Store Revenue and Rentals",
            labels={
                "value": "Metric Value",
                "store_id": "Store",
                "variable": "Metric"
            }
        )
        st.plotly_chart(fig_store, use_container_width=True)
        
    with right:
        top_5_country = (
            df.groupby("country", as_index=False)
                .agg(total_revenue=("revenue", "sum"))
                .sort_values("total_revenue", ascending=False)
                .head(5)
        )
        st.subheader("Top 5 Country by revenue")   
        fig_top_5 = px.bar(
            top_5_country,
            x="country",
            y="total_revenue",
            title="Bar chart of the Top 5 Countries",
            labels={
                "country": "Country",
                "total_revenue": "Total Revenue ($)"
            }
        )
        st.plotly_chart(fig_top_5, use_container_width=True) 
        st.markdown("---")
    
    
    # data overview
    st.subheader("Data Preview")
    st.dataframe(filtered_df.head(10))  
  
streamlit_dvd()