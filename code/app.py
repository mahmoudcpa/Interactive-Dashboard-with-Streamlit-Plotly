import pandas as pd
import streamlit as st
import datetime

import plotly.express as px
import plotly.graph_objects as go

from PIL import Image

# Read data
df = pd.read_csv("kayan.csv", encoding="latin-1")

# Set the streamlit page
st.set_page_config(layout='wide')
# Use style to add some padding
st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)

# Use the logo
image = Image.open("Kayan_1.jpg")

img_col, title_col = st.columns([0.1, 0.9])

with img_col:
    st.image(image, width=130)

html_title = """
    <style>
        .title-test {
        font-weight:bold;
        padding:5px;
        border-radius:6px;
        }
    </style>
    <center>
        <h1 class="title-test"Kayan Sales Dashboard></h1>
    </center>""" 
with title_col:
    st.markdown(html_title, unsafe_allow_html=True)


date_col, retailer_bar_col, month_linechart_col = st.columns([0.1, 0.45, 0.45])

with date_col:
    box_date = str(datetime.datetime.now().strftime("%d %B %Y"))
    st.write(f"Last updated on:  \n {box_date}")

# Display bar chart for sales comparison by retailers
with retailer_bar_col:
    fig = px.bar(
        df, x="Retailer", y="TotalSales", labels={"TotalSales": "Total Sales (US$)"},
        title = "Total Sales by Retailer", hover_data=["TotalSales"],
    )
    st.plotly_chart(fig, use_container_width=True)

# Convert the "TotalSales" column to numeric
df['TotalSales'] = pd.to_numeric(df['TotalSales'].str.strip().str.replace('$', '').str.replace(',', ''))

# Display tables
_, retailer_table, month_table = st.columns([0.1, 0.45, 0.45])

# Display a table for sales by retailer
with retailer_table:
    expander = st.expander("Sales by Retailer")
    data = df[["Retailer", "TotalSales"]].groupby(["Retailer"])["TotalSales"].sum()
    expander.write(data)

# Display a table for sales by month

# First convert the "InvoiceDate" column to date
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], format="mixed")
# Then add a month column to the dataframe
df["month_year"] = df["InvoiceDate"].dt.strftime("%B-%Y")
month_df = df.groupby("month_year")["TotalSales"].sum().reset_index()

with month_table:
    expander = st.expander("Sales by Month")
    expander.write(month_df)
    
with month_linechart_col:
    fig = px.line(month_df, x="month_year", y="TotalSales", title="Total Sales by Month",
                  template="gridon")
    st.plotly_chart(fig, use_container_width=True)

# Add a line to divide the screen
st.divider()

# Scatter / Bar chart for Sales by State with Units sold on the secondary y-axis
# Convert the "TotalSales" column to numeric
df['UnitsSold'] = pd.to_numeric(df['UnitsSold'].str.strip().str.replace(',', ''))
state_df = df.groupby("State")[["TotalSales","UnitsSold"]].sum().reset_index()

fig_state = go.Figure()
fig_state.add_trace(go.Bar(x=state_df["State"], y=state_df["TotalSales"], name="Total Sales"))
fig_state.add_trace(
    go.Scatter(x=state_df["State"], y=state_df["TotalSales"]
               , mode="lines", name="Units Sold", yaxis="y2")
               )
fig_state.update_layout(
    title="Total Sales and Units Sold by State",
    xaxis=dict(title="State"),
    yaxis=dict(title="Total Sales"),
    yaxis2=dict(title="Units Sold", overlaying="y", side="right", showgrid=False),
    template="gridon",
    legend=dict(x=1, y=1.1)
)

st.divider()

_, state_chart = st.columns([0.1, 0.9])
with state_chart:
    st.plotly_chart(fig_state, use_container_width=True)

# Display the state table and a button to donwload the data
_, state_table, state_data = st.columns([0.1, 0.45, 0.45])

with state_table:
    expander = st.expander("View Data for Sales and Units Sold by State")
    expander.write(state_df)

with state_data:
    st.download_button(
        "Get Date", data=state_df.to_csv(), file_name="sales_by_state.csv", mime="text/csv"
        )
    
st.divider()

# Treemap for Sales by Region and City
_, region_treemap = st.columns([0.1, 1])

region_df = df[['Region', 'City', "TotalSales"]].groupby(['Region', 'City'])["TotalSales"].sum().reset_index()

region_fig = px.treemap(
    region_df, path=["Region","City"], values="TotalSales",
    hover_name="TotalSales",
    hover_data=["TotalSales"],
    color="City", height=600, width=700
)
region_fig.update_traces(textinfo="label+value")

with region_treemap:
    st.subheader("Total Sales by Region and City")
    st.plotly_chart(region_fig, use_container_width=True)
