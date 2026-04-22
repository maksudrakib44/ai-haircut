import replicate
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("REPLICATE_API_TOKEN")
print(f"Token starts with: {token[:10]}... (length {len(token)})")

client = replicate.Client(api_token=token)

# Test with a simple text-to-image model to verify API connectivity
try:
    output = client.run(
        "black-forest-labs/flux-schnell",
        input={"prompt": "a cat", "num_outputs": 1}
    )
    print("API works! Output URL:", output[0])
except Exception as e:
    print("API error:", e)