"""
Jupyter-friendly helpers for the delivery_service project.
Use inside a notebook like:
    import jupyter_helpers as jh
    jh.update_manager("R001", manager="Alice", email="alice@alpha.com", years=3)
    jh.plot_delivery_histogram()
    df = jh.mean_food_rating_by_restaurant(); df
"""
import re
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "delivery_service.db"
EMAIL_REGEX = re.compile(r"^[A-Za-z]+@[A-Za-z]+\.[A-Za-z]+$")

def update_manager(restaurant_id: str, manager: str=None, email: str=None, years: int=None):
    """
    Update manager/email/years for a RestaurantID.
    Email must match ccc@aaa.bbb (letters only), per coursework spec.
    """
    if not restaurant_id:
        raise ValueError("restaurant_id is required.")
    if email and not EMAIL_REGEX.match(email):
        raise ValueError("Email must match ccc@aaa.bbb (letters only).")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM Restaurants WHERE RestaurantID=?;", (restaurant_id,))
        if not cur.fetchone():
            raise ValueError(f"RestaurantID '{restaurant_id}' not found in Restaurants.")
        cur.execute("""
            UPDATE Restaurants
            SET Manager = COALESCE(?, Manager),
                Email = COALESCE(?, Email),
                Years_as_manager = COALESCE(?, Years_as_manager)
            WHERE RestaurantID = ?;
        """, (manager, email, years, restaurant_id))
        conn.commit()
        return f"Updated manager info for RestaurantID={restaurant_id}"
    finally:
        conn.close()

def plot_delivery_histogram(bins: int = 20):
    """
    Extract DeliveryTimeMins from Orders and plot a histogram inline.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT DeliveryTimeMins FROM Orders WHERE DeliveryTimeMins IS NOT NULL;", conn)
    finally:
        conn.close()
    if df.empty:
        print("No delivery time data available.")
        return
    plt.figure()
    plt.hist(df["DeliveryTimeMins"].astype(float), bins=bins)
    plt.title("Histogram of Delivery Time Taken (mins)")
    plt.xlabel("Delivery Time (mins)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()

def mean_food_rating_by_restaurant():
    """
    Returns a DataFrame of mean CustomerRatingFood per restaurant.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("""
            SELECT o.RestaurantID,
                   r.RestaurantName,
                   AVG(o.CustomerRatingFood) AS MeanCustomerRatingFood,
                   COUNT(*) AS NumOrders
            FROM Orders o
            LEFT JOIN Restaurants r ON r.RestaurantID = o.RestaurantID
            GROUP BY o.RestaurantID, r.RestaurantName
            ORDER BY MeanCustomerRatingFood DESC;
        """, conn)
    finally:
        conn.close()
    return df
