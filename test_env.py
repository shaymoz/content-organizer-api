import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if the key is loaded
api_key = os.getenv("NVIDIA_API_KEY")
if api_key:
    print("API Key loaded successfully: {}".format(api_key[:20]))
else:
    print("API Key not found!")

# Test that it matches our expected value
expected_key = "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"
if api_key == expected_key:
    print("API Key matches expected value")
else:
    print("API Key does not match expected value")
    print("Expected: {}".format(expected_key))
    print("Got: {}".format(api_key))