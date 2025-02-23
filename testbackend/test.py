#!/usr/bin/env python

import asyncio
import websockets
import os
from process import answer

async def process(websocket):  # Removed 'path' parameter as it's no longer needed in newer websockets versions
    try:
        async for message in websocket:
            response = answer(message)
            await websocket.send(response)
            await websocket.send("[END]")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

async def main():
    print("WebSocket server starting", flush=True)
    port = int(os.environ.get('PORT', 8090))
    # Create the server with CORS headers
    async with websockets.serve(
        process,
        "0.0.0.0",
        port
    ) as server:
        print(f"WebSocket server running on port {port}", flush=True)
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
