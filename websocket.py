import websocket
from angel import Rest
import creds

class WebSocket:
    def __init__(self):
        rest = Rest(local_ip = creds.local_ip,public_ip = creds.public_ip,mac_address = creds.mac_address,api_key = creds.api_key)
        if rest.login:
            self.auth_token = rest.jwt_token
            self.client_code = rest.userid
            self.feed_token = rest.feed_token
        else:
            print('login first')
        self.api_key = creds.api_key
        
    def request_headers(self):
        headers = {
            "Authorization": self.auth_token,
            "x-api-key": self.api_key,
            "x-client-code": self.client_code,
            "x-feed-token": self.feed_token
            }
    
        
    def connect(self):
        self.wsapp = websocket.WebSocketApp("wss://smartapisocket.angelone.in/smart-stream",
                                            header= self.request_headers(),
                                            on_open=self.on_open(),
                                            on_error=self._on_error,
                                            on_close=self._on_close,
                                            on_data=self._on_data,
                                            on_ping=self._on_ping,
                                            on_pong=self._on_pong
                                            )
    
