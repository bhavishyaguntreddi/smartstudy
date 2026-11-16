# test_claude.py - one tiny call to check that the key and model work
from dotenv import load_dotenv
import anthropic

load_dotenv()                 # reads ANTHROPIC_API_KEY from your .env file
client = anthropic.Anthropic()  # finds the key automatically; never type it here

MODEL = "claude-haiku-5-5"    # the one place the model name lives

response = client.messages.create(
    model=MODEL,
    max_tokens=50,            # short cap keeps the cost tiny
    messages=[{"role": "user", "content": "Reply with exactly: SmartStudy test OK"}],
)

print(response.content[0].text)   # Claude's reply
print("tokens in:", response.usage.input_tokens,
      "| tokens out:", response.usage.output_tokens)