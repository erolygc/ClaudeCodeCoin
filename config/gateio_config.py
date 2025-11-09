"""
Gate.io API Configuration
"""

# Gate.io API Credentials
GATEIO_API_KEY = "5a36b056a39a5b1e6320f0b00be654ca"
GATEIO_API_SECRET = "9225a79f6049bfa96cf25a4ca942f2594808d468ce2ce6d512ab857caf9bde1d"

# Gate.io API Endpoints
GATEIO_REST_API_URL = "https://api.gateio.ws/api/v4"
GATEIO_WS_URL = "wss://api.gateio.ws/ws/v4/"

# WebSocket Settings
WS_PING_INTERVAL = 30  # seconds
WS_RECONNECT_DELAY = 10  # seconds
MAX_RECONNECT_ATTEMPTS = 999999  # Unlimited retries
