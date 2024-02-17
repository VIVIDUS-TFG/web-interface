from fastapi import WebSocket


websocket_connections: dict[str, WebSocket] = {}
