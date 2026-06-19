import os

from dotenv import load_dotenv
from mem0 import MemoryClient

load_dotenv()

client = MemoryClient(
    api_key=os.getenv("MEM0_API_KEY")
)
