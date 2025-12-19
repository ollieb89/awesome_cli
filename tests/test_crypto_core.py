import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import shutil

from awesome_cli.config import CryptoSettings
from awesome_cli.core.crypto.fetcher import CryptoDataFetcher
from awesome_cli.core.crypto.cache import CacheManager
from awesome_cli.core.crypto.repository import CryptoAssetRepository
from awesome_cli.core.crypto.scheduler import CryptoDataScheduler

class TestCryptoDataFetcher(unittest.TestCase):
    def setUp(self):
        self.settings = CryptoSettings()
        # Ensure base URL is patched or handled in tests if real requests are made
        # But we will mock the session so it shouldn't matter as much,
        # except for url construction verification.

    @patch("awesome_cli.core.crypto.fetcher.requests.Session")
    def test_fetch_top_coins_success(self, mock_session_cls):
        # Create fetcher inside test so the patch applies if it were patching the import
        # (but here we patch requests.Session used in __init__)

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

    def test_scheduler_lifecycle(self):
        settings = CryptoSettings(scheduler_interval_minutes=1)
        mock_fetcher = MagicMock()
        mock_repo = MagicMock()

        scheduler = CryptoDataScheduler(settings, mock_fetcher, mock_repo)

        # Test start
        scheduler.start()
        self.assertTrue(scheduler._thread.is_alive())

        # Test stop
        scheduler.stop()
        self.assertFalse(scheduler._thread.is_alive())

    def test_scheduler_error_handling(self):
        settings = CryptoSettings()
        mock_fetcher = MagicMock()
        mock_repo = MagicMock()

        # Simulate error in fetcher
        mock_fetcher.fetch_top_coins.side_effect = Exception("API Error")

        scheduler = CryptoDataScheduler(settings, mock_fetcher, mock_repo)

        # Should not raise exception
        try:
            scheduler.refresh_now()
        except Exception:
            self.fail("scheduler.refresh_now() raised Exception unexpectedly!")

if __name__ == "__main__":
    unittest.main()
