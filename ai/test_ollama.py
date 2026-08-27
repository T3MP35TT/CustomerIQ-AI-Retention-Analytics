import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3:4b"

payload = {
    "model": MODEL,
    "prompt": "Explain customer churn in one sentence.",
    "stream": False
}

response = requests.post(
    OLLAMA_URL,
    json=payload,
    timeout=120
)

response.raise_for_status()

result = response.json()

print("\nOllama response:")
print(result["response"])