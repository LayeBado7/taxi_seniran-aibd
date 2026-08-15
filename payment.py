import os

class PaymentProvider:
    """Unified payment boundary for Wave/Orange Money/card integrations."""
    def create_payment(self, method: str, amount: float, reference: str) -> dict:
        mode = os.getenv("PAYMENT_MODE", "sandbox")
        return {
            "mode": mode,
            "provider": method,
            "amount": amount,
            "reference": reference,
            "status": "pending"
        }

    def verify_webhook(self, headers, body) -> bool:
        # Production: verify the provider's cryptographic signature.
        return os.getenv("PAYMENT_WEBHOOK_VERIFY", "false").lower() == "true"
