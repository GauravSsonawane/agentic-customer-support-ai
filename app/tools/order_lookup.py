# Mock order database
ORDERS = {
    "ORD123": "Shipped - expected delivery in 2 days",
    "ORD456": "Delivered",
    "ORD789": "Cancelled",
}


def lookup_order(order_id: str) -> str:
    return ORDERS.get(order_id, "Order not found")
