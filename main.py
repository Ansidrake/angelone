from angel import Rest
import creds

angelone = Rest(local_ip = creds.local_ip,public_ip = creds.public_ip,mac_address = creds.mac_address,api_key = creds.api_key)

def login(angelone = angelone,creds = creds):
    angelone.login(client_code = creds.client_code,client_pin = creds.client_pin,totp = creds.totp)

# you can add any function now 