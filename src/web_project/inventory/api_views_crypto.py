from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from awesome_cli.config import load_settings
from awesome_cli.core.crypto.repository import CryptoAssetRepository

# We should avoid module level instantiation here if possible,
# but for ViewSet it's tricky without a DI framework.
# A common pattern is to initialize it lazily or use Django's settings to hold the singleton.
# For this task, let's keep it simple but allow the settings to be loaded fresh.

# However, to share the SAME repository instance (and thus the same in-memory data)
# across requests and potentially the background scheduler (if running in the same process),
# we need a true singleton or app-level registry.

# In Django, apps.py is a good place to hold app-global state.
from django.apps import apps

def get_repository():
    # Attempt to retrieve from AppConfig
    try:
        app_config = apps.get_app_config('inventory')
        if hasattr(app_config, 'crypto_repository'):
            return app_config.crypto_repository
    except Exception:
        pass

    # Fallback for tests or if not initialized (though it should be)
    settings = load_settings()
    return CryptoAssetRepository(settings.crypto)


class AssetViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing crypto assets.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        List top assets.
        Supports query params:
        - limit: number of assets to return (default 50)
        - sort: sort field (default 'volume') - currently only supports volume desc
        """
        try:
            limit = int(request.query_params.get("limit", 50))
        except ValueError:
            limit = 50

        repository = get_repository()
        assets = repository.get_top_by_volume(limit=limit)

        return Response({
            "data": assets,
            "meta": {
                "count": len(assets),
                "limit": limit
            }
        })

    def retrieve(self, request, pk=None):
        """Retrieve a specific asset by symbol."""
        repository = get_repository()
        asset = repository.get_by_symbol(pk)
        if asset:
            return Response({"data": asset})
        return Response(
            {"errors": [{"detail": "Asset not found"}]},
            status=status.HTTP_404_NOT_FOUND
        )
