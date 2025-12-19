import unittest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path
import tempfile
import shutil
import threading
import time
import json

import requests

from awesome_cli.config import CryptoSettings
from awesome_cli.core.crypto.fetcher import CryptoDataFetcher
from awesome_cli.core.crypto.cache import CacheManager
from awesome_cli.core.crypto.repository import CryptoAssetRepository
from awesome_cli.core.crypto.scheduler import CryptoDataScheduler

class TestCryptoDataFetcher(unittest.TestCase):
    def setUp(self):
        self.settings = CryptoSettings()

    @patch("awesome_cli.core.crypto.fetcher.requests.Session")
    def test_fetch_top_coins_success(self, mock_session_cls):
        # Prepare the mock session
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        # Initialize fetcher
        fetcher = CryptoDataFetcher(self.settings)

        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                "name": "Bitcoin",
                "current_price": 50000.0,
                "total_volume": 1000000000.0
            },
            {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum",
                "current_price": 4000.0,
                "total_volume": 500000000.0
            }
        ]
        mock_session.get.return_value = mock_response

        # Call method
        data = fetcher.fetch_top_coins(limit=2)

        # Assertions
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["symbol"], "BTC")
        self.assertEqual(data[0]["current_price"], 50000.0)
        self.assertEqual(data[1]["symbol"], "ETH")

        # Verify URL construction
        args, kwargs = mock_session.get.call_args
        self.assertIn("coins/markets", args[0])
        self.assertEqual(kwargs['params']['per_page'], 2)

    @patch("awesome_cli.core.crypto.fetcher.requests.Session")
    def test_fetch_top_coins_normalization(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        fetcher = CryptoDataFetcher(self.settings)

        # Mock response with mixed types and missing fields
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "bitcoin",
                "symbol": "btc",
                # missing name
                "current_price": "50000", # string instead of float
                "total_volume": None
            }
        ]
        mock_session.get.return_value = mock_response

        data = fetcher.fetch_top_coins(limit=1)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["current_price"], 50000.0)
        self.assertIsNone(data[0]["total_volume"])

    @patch("awesome_cli.core.crypto.fetcher.requests.Session")
    def test_fetch_top_coins_http_error_429(self, mock_session_cls):
        """Test handling of 429 rate limit error with response object"""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        fetcher = CryptoDataFetcher(self.settings)

        # Create a mock response with 429 status
        mock_response = Mock()
        mock_response.status_code = 429
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response
        mock_session.get.side_effect = http_error

        with self.assertRaises(requests.exceptions.HTTPError):
            fetcher.fetch_top_coins(limit=10)

    @patch("awesome_cli.core.crypto.fetcher.requests.Session")
    def test_fetch_top_coins_http_error_no_response(self, mock_session_cls):
        """Test handling of HTTPError with no response object"""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        fetcher = CryptoDataFetcher(self.settings)

        # Create an HTTPError with no response attribute
        http_error = requests.exceptions.HTTPError()
        http_error.response = None
        mock_session.get.side_effect = http_error

        with self.assertRaises(requests.exceptions.HTTPError):
            fetcher.fetch_top_coins(limit=10)

    @patch("awesome_cli.core.crypto.fetcher.requests.Session")
    def test_fetch_top_coins_request_exception(self, mock_session_cls):
        """Test handling of general request exceptions"""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        fetcher = CryptoDataFetcher(self.settings)

        mock_session.get.side_effect = requests.exceptions.ConnectionError()

        with self.assertRaises(requests.exceptions.RequestException):
            fetcher.fetch_top_coins(limit=10)

    @patch("awesome_cli.core.crypto.fetcher.requests.Session")
    def test_fetch_top_coins_json_parse_error(self, mock_session_cls):
        """Test handling of JSON parsing errors"""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        fetcher = CryptoDataFetcher(self.settings)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_session.get.return_value = mock_response

        with self.assertRaises(ValueError):
            fetcher.fetch_top_coins(limit=10)


class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.cache = CacheManager(ttl_minutes=1)

    def test_set_and_get(self):
        self.cache.set("key1", {"data": 123})
        val = self.cache.get("key1")
        self.assertEqual(val, {"data": 123})

    def test_expiry(self):
        self.cache.set("key2", "value", ttl_minutes=-1) # Expired immediately
        val = self.cache.get("key2")
        self.assertIsNone(val)

    def test_invalidate(self):
        """Test cache invalidation"""
        self.cache.set("key3", "value")
        self.assertEqual(self.cache.get("key3"), "value")
        self.cache.invalidate("key3")
        self.assertIsNone(self.cache.get("key3"))

    def test_clear(self):
        """Test clearing all cache entries"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.clear()
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))

    def test_thread_safety(self):
        """Test concurrent access to cache"""
        results = []
        errors = []

        def writer(key_prefix):
            try:
                for i in range(100):
                    self.cache.set(f"{key_prefix}_{i}", i)
            except Exception as e:
                errors.append(e)

        def reader(key_prefix):
            try:
                for i in range(100):
                    val = self.cache.get(f"{key_prefix}_{i}")
                    results.append(val)
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(5):
            t1 = threading.Thread(target=writer, args=(f"key{i}",))
            t2 = threading.Thread(target=reader, args=(f"key{i}",))
            threads.extend([t1, t2])

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Check no errors occurred
        self.assertEqual(len(errors), 0)


class TestCryptoAssetRepository(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.storage_path = Path(self.test_dir) / "test_assets.json"
        self.settings = CryptoSettings(storage_path=str(self.storage_path))
        self.repo = CryptoAssetRepository(self.settings)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_upsert_and_get(self):
        assets = [
            {"symbol": "BTC", "name": "Bitcoin", "total_volume": 100},
            {"symbol": "ETH", "name": "Ethereum", "total_volume": 50}
        ]
        self.repo.upsert(assets)

        self.assertEqual(len(self.repo.get_all()), 2)
        self.assertEqual(self.repo.get_by_symbol("BTC")["name"], "Bitcoin")

        # Verify persistence
        new_repo = CryptoAssetRepository(self.settings)
        self.assertEqual(len(new_repo.get_all()), 2)

    def test_get_top_by_volume(self):
        assets = [
            {"symbol": "A", "total_volume": 10},
            {"symbol": "B", "total_volume": 100},
            {"symbol": "C", "total_volume": 50}
        ]
        self.repo.upsert(assets)

        top = self.repo.get_top_by_volume(limit=2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0]["symbol"], "B")
        self.assertEqual(top[1]["symbol"], "C")

    def test_load_corrupted_json_missing_symbol(self):
        """Test loading JSON with items missing the symbol key"""
        # Create a JSON file with corrupted data
        corrupted_data = [
            {"symbol": "BTC", "name": "Bitcoin"},
            {"name": "Ethereum"},  # Missing symbol
            {"symbol": "ADA", "name": "Cardano"},
            "not_a_dict",  # Not a dict
        ]
        with self.storage_path.open("w", encoding="utf-8") as f:
            json.dump(corrupted_data, f)

        # Load the repository - should skip malformed items
        repo = CryptoAssetRepository(self.settings)
        self.assertEqual(len(repo.get_all()), 2)  # Only BTC and ADA
        self.assertIsNotNone(repo.get_by_symbol("BTC"))
        self.assertIsNotNone(repo.get_by_symbol("ADA"))
        self.assertIsNone(repo.get_by_symbol("ETH"))

    def test_load_unexpected_data_format(self):
        """Test loading JSON with unexpected data format"""
        # Write a non-list, non-dict value
        with self.storage_path.open("w", encoding="utf-8") as f:
            json.dump("invalid_data", f)

        # Should handle gracefully
        repo = CryptoAssetRepository(self.settings)
        self.assertEqual(len(repo.get_all()), 0)


class TestCryptoDataScheduler(unittest.TestCase):
    def test_refresh_now(self):
        settings = CryptoSettings()
        mock_fetcher = MagicMock()
        mock_repo = MagicMock()

        mock_fetcher.fetch_top_coins.return_value = [{"symbol": "BTC"}]

        scheduler = CryptoDataScheduler(settings, mock_fetcher, mock_repo)
        scheduler.refresh_now()

        mock_fetcher.fetch_top_coins.assert_called_once()
        mock_repo.upsert.assert_called_once_with([{"symbol": "BTC"}])

    def test_refresh_now_with_error(self):
        """Test that errors in refresh_now are handled gracefully"""
        settings = CryptoSettings()
        mock_fetcher = MagicMock()
        mock_repo = MagicMock()

        mock_fetcher.fetch_top_coins.side_effect = Exception("API Error")

        scheduler = CryptoDataScheduler(settings, mock_fetcher, mock_repo)
        # Should not raise, just log the error
        scheduler.refresh_now()

        mock_repo.upsert.assert_not_called()

    def test_start_and_stop(self):
        """Test scheduler start and stop functionality"""
        settings = CryptoSettings(scheduler_interval_minutes=0.01)  # Very short interval
        mock_fetcher = MagicMock()
        mock_repo = MagicMock()
        mock_fetcher.fetch_top_coins.return_value = [{"symbol": "BTC"}]

        scheduler = CryptoDataScheduler(settings, mock_fetcher, mock_repo)
        
        # Start scheduler
        scheduler.start()
        self.assertIsNotNone(scheduler._thread)
        self.assertTrue(scheduler._thread.is_alive())

        # Let it run for a bit
        time.sleep(0.1)

        # Stop scheduler
        scheduler.stop()
        self.assertFalse(scheduler._thread.is_alive())

    def test_start_already_running(self):
        """Test that starting an already running scheduler is handled"""
        settings = CryptoSettings(scheduler_interval_minutes=1)
        mock_fetcher = MagicMock()
        mock_repo = MagicMock()
        mock_fetcher.fetch_top_coins.return_value = [{"symbol": "BTC"}]

        scheduler = CryptoDataScheduler(settings, mock_fetcher, mock_repo)
        
        scheduler.start()
        first_thread = scheduler._thread
        
        # Try to start again
        scheduler.start()
        
        # Should be the same thread
        self.assertEqual(scheduler._thread, first_thread)
        
        scheduler.stop()

if __name__ == "__main__":
    unittest.main()
