"""Send a text question to xiaozhi-esp32-server over WebSocket, as the board would
after wake-word detection, and print the server's text events with timings.

Usage: ws_text_test.py "What's the weather?" [ws://host:8000/xiaozhi/v1/]
"""
import asyncio, json, sys, time
import websockets

async def main(question, url):
    t0 = time.time()
    headers = {"device-id": "00:11:22:33:44:55", "client-id": "ws-text-test", "protocol-version": "1"}
    async with websockets.connect(url, additional_headers=headers) as ws:
        await ws.send(json.dumps({"type": "hello", "version": 1, "transport": "websocket",
                                  "audio_params": {"format": "opus", "sample_rate": 16000, "channels": 1, "frame_duration": 60}}))
        await ws.send(json.dumps({"type": "listen", "state": "detect", "text": question}))
        audio = 0
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=30)
            except asyncio.TimeoutError:
                print("timeout"); break
            dt = time.time() - t0
            if isinstance(msg, bytes):
                audio += 1
                continue
            m = json.loads(msg)
            if m.get("type") in ("stt", "llm", "tts"):
                print(f"{dt:6.2f}s {m['type']:>4} {m.get('state','')} {m.get('text','')}")
            if m.get("type") == "tts" and m.get("state") == "stop":
                break
        print(f"{time.time()-t0:6.2f}s done, {audio} audio frames")

asyncio.run(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "ws://10.10.10.31:8000/xiaozhi/v1/"))
