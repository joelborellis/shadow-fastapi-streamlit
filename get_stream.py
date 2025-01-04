import aiohttp
import asyncio
import json

async def consume_sse(url: str, payload: str):
    """
    Connects to an SSE endpoint and prints out parsed JSON lines
    character by character (to simulate typing).
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
                    # If we reach here, line should be JSON (e.g. {"data": "some content"}).
                    try:
                        # Handle extra "data:" prefix if present
                        if line.startswith("data: "):
                            line = line[len("data: ") :]

                        json_data = json.loads(line)
                        content = json_data.get("data", "")
                        if content:
                            # Print character by character
                            for char in content:
                                print(char, end="", flush=True)
                                # Adjust sleep time to control the "typing" speed
                                await asyncio.sleep(0.01)
                    except json.JSONDecodeError:
                        print("Could not parse JSON:", line)


async def main():

    while True:
        # Get user query
        query = input(f"\nAsk Shadow: ")
        if query.lower() == "exit":
            exit(0)

        # Point this to your actual SSE endpoint
        #url = "https://shadow-fastapi-sk-rgrhhk5mtlr7i-function-app.azurewebsites.net/shadow-sk"
        url = "http://localhost:7071/shadow-sk"

        # Construct request payload
        payload = {"query": query}
        await consume_sse(url, payload)


if __name__ == "__main__":
    asyncio.run(main())