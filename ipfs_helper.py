import requests
import json
from cryptography.fernet import Fernet
import os

IPFS_API = "http://127.0.0.1:5001/api/v0"

def generate_key():
    return Fernet.generate_key()

def encrypt_file(data, key):
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_file(data, key):
    f = Fernet(key)
    return f.decrypt(data)

def upload_to_ipfs(data):
    try:
        r = requests.post(
            f"{IPFS_API}/add",
            files={"file": ("record.enc", data)}
        )
        result = r.json()
        return result["Hash"]
    except Exception as e:
        return None

def retrieve_from_ipfs(cid):
    try:
        r = requests.post(f"{IPFS_API}/cat?arg={cid}")
        return r.content
    except Exception as e:
        return None