from enum import Enum


class Intent(str, Enum):
    POLICY = "policy"
    ORDER_STATUS = "order_status"
    REFUND = "refund"
    OTHER = "other"

