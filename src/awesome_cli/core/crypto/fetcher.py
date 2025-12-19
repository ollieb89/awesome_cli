"""
Crypto Data Fetcher
===================

This module implements the fetching logic for cryptocurrency data.
It primarily uses CoinGecko API to retrieve market data for the top 50 cryptocurrencies.

Rationale for using CoinGecko:
------------------------------
1.  **Cost-Effectiveness**: CoinGecko offers a generous free tier (~50 requests/minute) which is sufficient for our use case (fetching top 50 coins every 5-10 minutes).
    Other providers like CoinMarketCap require paid plans for similar access or have stricter limits.
2.  **Data Comprehensiveness**: It provides essential market data (price, volume, market cap, changes) and metadata (logos, descriptions, categories) in a single ecosystem.
3.  **Ease of Use**: The API is RESTful, well-documented, and stable. No API key is strictly required for basic endpoints.
4.  **Community Standard**: It is a widely used and trusted source in the crypto community.

"""

import logging
import time
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from awesome_cli.config import CryptoSettings

logger = logging.getLogger(__name__)


class CryptoDataFetcher:
    """
    Fetcher for cryptocurrency data using CoinGecko API.
    Handles rate limiting, retries, and response parsing.
    """

    def __init__(self, settings: CryptoSettings):
        self.base_url = settings.coingecko_api_base_url
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        self.timeout = settings.coingecko_request_timeout
        self.rate_limit_delay = 60.0 / settings.coingecko_rate_limit_requests  # Simple spacing
        self.session = self._create_session()
        self._last_request_time = 0.0

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _wait_for_rate_limit(self):
        """Ensure we respect the rate limit by sleeping if necessary."""
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def fetch_top_coins(self, limit: int = 50, currency: str = "usd") -> List[Dict[str, Any]]:
        """
        Fetch top coins by trading volume.

        Args:
            limit: Number of coins to fetch (default 50).
            currency: Target currency (default 'usd').

        Returns:
            List of dictionaries containing coin data.
        """
        endpoint = "coins/markets"
        url = urljoin(self.base_url, endpoint)

        # Note: CoinGecko API allows 'per_page' up to 250.
        params = {
            "vs_currency": currency,
            "order": "volume_desc",  # Sort by volume as per requirements
            "per_page": limit,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h,7d"
        }

        self._wait_for_rate_limit()

        try:
            logger.info(f"Fetching top {limit} coins from {url}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            return self._normalize_response(data)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning("Rate limit exceeded (429).")
            logger.error(f"HTTP error occurred: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise

    def _normalize_response(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and normalize the API response.
        Ensures required fields are present and types are correct.
        """
        normalized_data = []
        for item in data:
            try:
                # Basic validation
                if not item.get("id") or not item.get("symbol"):
                    continue

                # Extract and normalize fields
                coin = {
                    "id": item.get("id"),
                    "symbol": item.get("symbol", "").upper(),
                    "name": item.get("name"),
                    "image": item.get("image"),
                    "current_price": self._to_float(item.get("current_price")),
                    "market_cap": self._to_float(item.get("market_cap")),
                    "market_cap_rank": item.get("market_cap_rank"),
                    "total_volume": self._to_float(item.get("total_volume")),
                    "high_24h": self._to_float(item.get("high_24h")),
                    "low_24h": self._to_float(item.get("low_24h")),
                    "price_change_percentage_24h": self._to_float(item.get("price_change_percentage_24h")),
                    "price_change_percentage_7d_in_currency": self._to_float(item.get("price_change_percentage_7d_in_currency")),
                    "ath": self._to_float(item.get("ath")),
                    "atl": self._to_float(item.get("atl")),
                    "last_updated": item.get("last_updated"),
                }
                normalized_data.append(coin)
            except Exception as e:
                logger.warning(f"Skipping malformed item {item.get('id', 'unknown')}: {e}")
                continue

        return normalized_data

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        """Safely convert value to float."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
