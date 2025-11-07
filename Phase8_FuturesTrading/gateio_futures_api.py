"""
Gate.io Futures API Wrapper
Handles all API interactions with Gate.io Futures Trading
"""

import time
import hashlib
import hmac
import json
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from decimal import Decimal
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GateIOFuturesAPI:
    """Gate.io Futures Trading API Wrapper"""

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize Gate.io Futures API

        Args:
            api_key: Gate.io API key
            api_secret: Gate.io API secret
            testnet: Use testnet environment (default: False)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet

        # API endpoints
        if testnet:
            self.base_url = "https://fx-api-testnet.gateio.ws"
        else:
            self.base_url = "https://api.gateio.ws"

        self.api_prefix = "/api/v4"

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests

    def _generate_signature(self, method: str, url: str, query_string: str = "",
                           body_string: str = "") -> Dict[str, str]:
        """Generate Gate.io API signature"""
        timestamp = str(int(time.time()))

        # Create payload for hashing
        hashed_payload = hashlib.sha512((body_string or "").encode('utf-8')).hexdigest()

        # Create signature string
        sign_string = f"{method}\n{url}\n{query_string}\n{hashed_payload}\n{timestamp}"

        # Generate signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            sign_string.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        # Return headers
        headers = {
            'KEY': self.api_key,
            'Timestamp': timestamp,
            'SIGN': signature,
            'Content-Type': 'application/json'
        }

        return headers

    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None,
                data: Optional[Dict] = None) -> Dict:
        """
        Make API request with authentication

        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data

        Returns:
            API response as dictionary
        """
        self._rate_limit()

        url = f"{self.api_prefix}{endpoint}"
        full_url = f"{self.base_url}{url}"

        # Build query string
        query_string = ""
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])

        # Build body string
        body_string = ""
        if data:
            body_string = json.dumps(data)

        # Generate signature
        headers = self._generate_signature(method, url, query_string, body_string)

        # Make request
        try:
            if method == "GET":
                response = requests.get(full_url, params=params, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(full_url, params=params, json=data,
                                       headers=headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(full_url, params=params, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise

    # ============================================================================
    # ACCOUNT ENDPOINTS
    # ============================================================================

    def get_account_balance(self, settle: str = "usdt") -> Dict:
        """
        Get futures account balance

        Args:
            settle: Settlement currency (usdt or btc)

        Returns:
            Account balance information
        """
        endpoint = f"/futures/{settle}/accounts"
        return self._request("GET", endpoint)

    def get_account_book(self, settle: str = "usdt", limit: int = 100) -> List[Dict]:
        """
        Get account balance change history

        Args:
            settle: Settlement currency
            limit: Number of records

        Returns:
            List of balance changes
        """
        endpoint = f"/futures/{settle}/account_book"
        params = {"limit": limit}
        return self._request("GET", endpoint, params=params)

    # ============================================================================
    # POSITION ENDPOINTS
    # ============================================================================

    def get_positions(self, settle: str = "usdt", contract: Optional[str] = None) -> List[Dict]:
        """
        Get all futures positions

        Args:
            settle: Settlement currency
            contract: Specific contract (optional, e.g., BTC_USDT)

        Returns:
            List of positions
        """
        endpoint = f"/futures/{settle}/positions"
        params = {}
        if contract:
            params['contract'] = contract

        return self._request("GET", endpoint, params=params)

    def get_position(self, settle: str, contract: str) -> Dict:
        """
        Get single position

        Args:
            settle: Settlement currency
            contract: Contract name (e.g., BTC_USDT)

        Returns:
            Position information
        """
        endpoint = f"/futures/{settle}/positions/{contract}"
        return self._request("GET", endpoint)

    def update_position_margin(self, settle: str, contract: str, change: str) -> Dict:
        """
        Update position margin

        Args:
            settle: Settlement currency
            contract: Contract name
            change: Margin change amount (positive to add, negative to reduce)

        Returns:
            Updated position
        """
        endpoint = f"/futures/{settle}/positions/{contract}/margin"
        data = {"change": change}
        return self._request("POST", endpoint, data=data)

    def update_position_leverage(self, settle: str, contract: str, leverage: str) -> Dict:
        """
        Update position leverage

        Args:
            settle: Settlement currency
            contract: Contract name
            leverage: New leverage (e.g., "3" for 3x)

        Returns:
            Updated position
        """
        endpoint = f"/futures/{settle}/positions/{contract}/leverage"
        data = {"leverage": leverage}
        return self._request("POST", endpoint, data=data)

    def update_position_risk_limit(self, settle: str, contract: str, risk_limit: str) -> Dict:
        """
        Update position risk limit

        Args:
            settle: Settlement currency
            contract: Contract name
            risk_limit: New risk limit

        Returns:
            Updated position
        """
        endpoint = f"/futures/{settle}/positions/{contract}/risk_limit"
        data = {"risk_limit": risk_limit}
        return self._request("POST", endpoint, data=data)

    # ============================================================================
    # ORDER ENDPOINTS
    # ============================================================================

    def place_order(self, settle: str, contract: str, size: int, price: Optional[str] = None,
                   tif: str = "gtc", reduce_only: bool = False,
                   close: bool = False, auto_size: Optional[str] = None) -> Dict:
        """
        Place futures order

        Args:
            settle: Settlement currency (usdt)
            contract: Contract name (e.g., BTC_USDT)
            size: Order size (positive for long, negative for short)
            price: Order price (None for market order)
            tif: Time in force (gtc, ioc, poc)
            reduce_only: Reduce-only order
            close: Close position order
            auto_size: Auto-calculate size (close_long, close_short)

        Returns:
            Order information
        """
        endpoint = f"/futures/{settle}/orders"

        data = {
            "contract": contract,
            "size": size,
            "tif": tif,
            "reduce_only": reduce_only,
            "close": close
        }

        if price:
            data["price"] = price

        if auto_size:
            data["auto_size"] = auto_size

        return self._request("POST", endpoint, data=data)

    def get_orders(self, settle: str, status: str = "open",
                  contract: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Get orders list

        Args:
            settle: Settlement currency
            status: Order status (open, finished)
            contract: Filter by contract
            limit: Number of records

        Returns:
            List of orders
        """
        endpoint = f"/futures/{settle}/orders"
        params = {
            "status": status,
            "limit": limit
        }
        if contract:
            params["contract"] = contract

        return self._request("GET", endpoint, params=params)

    def get_order(self, settle: str, order_id: str) -> Dict:
        """
        Get single order

        Args:
            settle: Settlement currency
            order_id: Order ID

        Returns:
            Order information
        """
        endpoint = f"/futures/{settle}/orders/{order_id}"
        return self._request("GET", endpoint)

    def cancel_order(self, settle: str, order_id: str) -> Dict:
        """
        Cancel futures order

        Args:
            settle: Settlement currency
            order_id: Order ID to cancel

        Returns:
            Cancelled order information
        """
        endpoint = f"/futures/{settle}/orders/{order_id}"
        return self._request("DELETE", endpoint)

    def cancel_all_orders(self, settle: str, contract: str, side: Optional[str] = None) -> List[Dict]:
        """
        Cancel all orders for a contract

        Args:
            settle: Settlement currency
            contract: Contract name
            side: Order side (ask for short, bid for long)

        Returns:
            List of cancelled orders
        """
        endpoint = f"/futures/{settle}/orders"
        params = {"contract": contract}
        if side:
            params["side"] = side

        return self._request("DELETE", endpoint, params=params)

    # ============================================================================
    # MARKET DATA ENDPOINTS
    # ============================================================================

    def get_contract(self, settle: str, contract: str) -> Dict:
        """
        Get contract details

        Args:
            settle: Settlement currency
            contract: Contract name

        Returns:
            Contract information
        """
        endpoint = f"/futures/{settle}/contracts/{contract}"
        return self._request("GET", endpoint)

    def get_orderbook(self, settle: str, contract: str, limit: int = 10) -> Dict:
        """
        Get order book

        Args:
            settle: Settlement currency
            contract: Contract name
            limit: Depth limit

        Returns:
            Order book data
        """
        endpoint = f"/futures/{settle}/order_book"
        params = {"contract": contract, "limit": limit}
        return self._request("GET", endpoint, params=params)

    def get_tickers(self, settle: str, contract: Optional[str] = None) -> List[Dict]:
        """
        Get tickers

        Args:
            settle: Settlement currency
            contract: Specific contract (optional)

        Returns:
            List of tickers
        """
        endpoint = f"/futures/{settle}/tickers"
        params = {}
        if contract:
            params["contract"] = contract

        return self._request("GET", endpoint, params=params)

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def close_position(self, settle: str, contract: str, position_size: int) -> Dict:
        """
        Close position using market order

        Args:
            settle: Settlement currency
            contract: Contract name
            position_size: Current position size (negative to close)

        Returns:
            Close order information
        """
        # To close, size should be opposite of position
        close_size = -position_size

        return self.place_order(
            settle=settle,
            contract=contract,
            size=close_size,
            price=None,  # Market order
            tif="ioc",
            reduce_only=True,
            close=True
        )

    def set_leverage_for_contract(self, settle: str, contract: str, leverage: int) -> Dict:
        """
        Set leverage for a contract

        Args:
            settle: Settlement currency
            contract: Contract name
            leverage: Leverage multiplier (1-100)

        Returns:
            Updated position info
        """
        return self.update_position_leverage(settle, contract, str(leverage))

    def calculate_liquidation_price(self, entry_price: float, leverage: int,
                                   side: str = "long") -> float:
        """
        Calculate liquidation price

        Args:
            entry_price: Entry price
            leverage: Leverage multiplier
            side: Position side (long or short)

        Returns:
            Liquidation price
        """
        # Simplified liquidation calculation
        # Actual formula is more complex and includes fees
        maintenance_margin_rate = 0.005  # 0.5% for most contracts

        if side.lower() == "long":
            liq_price = entry_price * (1 - (1/leverage) + maintenance_margin_rate)
        else:  # short
            liq_price = entry_price * (1 + (1/leverage) - maintenance_margin_rate)

        return liq_price


def test_api_connection(api_key: str, api_secret: str, testnet: bool = True):
    """Test API connection and credentials"""
    try:
        api = GateIOFuturesAPI(api_key, api_secret, testnet=testnet)

        logger.info("Testing API connection...")
        balance = api.get_account_balance()
        logger.info(f"Connection successful! Balance: {balance}")

        positions = api.get_positions()
        logger.info(f"Open positions: {len(positions)}")

        return True

    except Exception as e:
        logger.error(f"API connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test with dummy credentials
    print("Gate.io Futures API Wrapper")
    print("=" * 80)
    print("\nTo use this API wrapper:")
    print("1. Create API keys at https://www.gate.io/myaccount/apiv4keys")
    print("2. Set API_KEY and API_SECRET in .env file")
    print("3. Test on testnet first: https://fx-test.gateio.pro/")
    print("\nExample usage:")
    print("""
    from gateio_futures_api import GateIOFuturesAPI

    api = GateIOFuturesAPI(api_key, api_secret, testnet=True)

    # Get balance
    balance = api.get_account_balance()

    # Place order
    order = api.place_order(
        settle="usdt",
        contract="BTC_USDT",
        size=10,  # 10 contracts long
        price="50000"
    )

    # Get positions
    positions = api.get_positions(settle="usdt")
    """)
