import os

class SmsProvider:
    """Production adapter boundary. Replace send() with the contracted SMS provider."""
    name = "demo"

    def send(self, phone: str, message: str) -> dict:
        if os.getenv("SMS_PROVIDER", "demo") == "demo":
            return {"sent": False, "mode": "demo", "phone": phone}
        raise NotImplementedError("Configure the contracted SMS provider.")
