import aiohttp
import asyncio
import json


async def consume_sse(url: str, payload: str):
    """
    Connects to an SSE endpoint and prints out parsed JSON lines.
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            async for chunk, _ in response.content.iter_chunks():
                # Decode chunk into text
                text_chunk = chunk.decode("utf-8")

                # The server might send multiple lines in one chunk,
                # so we split by newlines to handle them individually
                for line in text_chunk.splitlines():
                    line = line.strip()
                    if not line:
                        # Skip empty lines
                        continue

                    if line.startswith("event: partial"):
                        # This is the SSE event descriptor line; skip it
                        continue

                    # If we reach here, line should be JSON (e.g. {"data": "some content"})
                    try:
                        json_data = json.loads(line)
                        # The server code yields {"data": "..."} so you can extract that:
                        content = json_data.get("data")
                        print("Received SSE data:", content)
                    except json.JSONDecodeError:
                        print("Could not parse JSON:", line)


async def main():

    while True:
        # Get user query
        query = input(f"\nAsk GPT: ")
        if query.lower() == "exit":
            exit(0)

        # Point this to your actual SSE endpoint
        url = "http://localhost:7071/shadow-sk"

        # Construct request payload
        payload = {"query": query}
        await consume_sse(url, payload)


if __name__ == "__main__":
    asyncio.run(main())
