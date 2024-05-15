import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


a=os.environ.get("HOST_")
print(a)