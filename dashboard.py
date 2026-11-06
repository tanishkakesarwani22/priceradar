import os
import pandas as pd
import mysql.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="PriceRadar", page_icon="📡", layout="wide")
st.title("📡 PriceRadar")
st.caption("Price tracker aur deal alert system")


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def load_products():
    conn = get_connection()
    df = pd.read_sql(
        "SELECT id, name, current_price, lowest_price, target_price, last_checked "
        "FROM products",
        conn,
    )
    conn.close()
    return df


def load_history(product_id):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT checked_at, price FROM price_history "
        "WHERE product_id = %s ORDER BY checked_at",
        conn,
        params=(product_id,),
    )
    conn.close()
    return df


products = load_products()

st.subheader("Tracked products")
st.dataframe(
    products.drop(columns=["id"]),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Price history")
choice = st.selectbox("Product chuno", products["name"])
product_id = int(products.loc[products["name"] == choice, "id"].iloc[0])

history = load_history(product_id)
history["checked_at"] = pd.to_datetime(history["checked_at"])
history["price"] = history["price"].astype(float)

row = products[products["id"] == product_id].iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("Current price", f"{float(row['current_price']):.2f}")
c2.metric("Lowest price", f"{float(row['lowest_price']):.2f}")
c3.metric("Average price", f"{history['price'].mean():.2f}")

chart_df = history.set_index("checked_at")[["price"]].copy()
if pd.notna(row["target_price"]):
    chart_df["target"] = float(row["target_price"])
st.line_chart(chart_df)