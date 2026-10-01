import os
import requests
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("COPERNICUS_CLIENT_ID")
client_secret = os.getenv("COPERNICUS_CLIENT_SECRET")

token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

response = requests.post(
    token_url,
    data={
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    },
    timeout=30,
)

print("Status:", response.status_code)

response.raise_for_status()

token = response.json().get("access_token")

print("Authentication successful:", bool(token))