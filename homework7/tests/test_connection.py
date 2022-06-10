from unittest import mock as m

import pytest

from app.connections import ConnectionManager


class TestConnectionManager:
    @pytest.mark.asyncio
    async def test_connect(self, ws: m.AsyncMock):
        mgr = ConnectionManager()

        await mgr.connect(ws)
        assert mgr.active_connections[0] == ws
        assert ws.accept.await_count == 1

    @pytest.mark.asyncio
    async def test_broadcast(self, ws: m.AsyncMock):
        mgr = ConnectionManager()
        await mgr.broadcast('User123 says: Hello')
        assert ws.send_json.call_count == 0
