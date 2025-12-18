from app.intent_schema import IntentLabel

INTENT_PRIORITY = {
    IntentLabel.REFUND: 4,
    IntentLabel.ORDER_STATUS: 3,
    IntentLabel.POLICY: 2,
    IntentLabel.OTHER: 1,
}

