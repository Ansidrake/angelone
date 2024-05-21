import http.client
import mimetypes

class broker :
    def __init__(self,local_ip,public_ip,mac_address,api_key):
        self.content_type,self.accept = 'application/json','application/json'
        self.userType,self.sourceID = 'USER','WEB'
        self.clientLocalIp,self.clientPublicIp,self.clientMacAddress,self.privateKey = local_ip, public_ip, mac_address, api_key
        self.login = False 

        # connection
        self.conn = http.client.HTTPSConnection("apiconnect.angelbroking.com")
        # given in documentation
        self.routes = {
            "api.login":"/rest/auth/angelbroking/user/v1/loginByPassword",
            "api.logout":"/rest/secure/angelbroking/user/v1/logout",
            "api.token": "/rest/auth/angelbroking/jwt/v1/generateTokens",
            "api.refresh": "/rest/auth/angelbroking/jwt/v1/generateTokens",
            "api.user.profile": "/rest/secure/angelbroking/user/v1/getProfile",
            "api.order.place": "/rest/secure/angelbroking/order/v1/placeOrder",
            "api.order.placefullresponse": "/rest/secure/angelbroking/order/v1/placeOrder",
            "api.order.modify": "/rest/secure/angelbroking/order/v1/modifyOrder",
            "api.order.cancel": "/rest/secure/angelbroking/order/v1/cancelOrder",
            "api.order.book":"/rest/secure/angelbroking/order/v1/getOrderBook",
            "api.ltp.data": "/rest/secure/angelbroking/order/v1/getLtpData",
            "api.trade.book": "/rest/secure/angelbroking/order/v1/getTradeBook",
            "api.rms.limit": "/rest/secure/angelbroking/user/v1/getRMS",
            "api.holding": "/rest/secure/angelbroking/portfolio/v1/getHolding",
            "api.position": "/rest/secure/angelbroking/order/v1/getPosition",
            "api.convert.position": "/rest/secure/angelbroking/order/v1/convertPosition",
            "api.gtt.create":"/gtt-service/rest/secure/angelbroking/gtt/v1/createRule",
            "api.gtt.modify":"/gtt-service/rest/secure/angelbroking/gtt/v1/modifyRule",
            "api.gtt.cancel":"/gtt-service/rest/secure/angelbroking/gtt/v1/cancelRule",
            "api.gtt.details":"/rest/secure/angelbroking/gtt/v1/ruleDetails",
            "api.gtt.list":"/rest/secure/angelbroking/gtt/v1/ruleList",
            "api.candle.data":"/rest/secure/angelbroking/historical/v1/getCandleData",
            "api.market.data":"/rest/secure/angelbroking/market/v1/quote",
            "api.search.scrip": "/rest/secure/angelbroking/order/v1/searchScrip",
            "api.allholding": "/rest/secure/angelbroking/portfolio/v1/getAllHolding",
            "api.individual.order.details": "/rest/secure/angelbroking/order/v1/details/",
            "api.margin.api" : 'rest/secure/angelbroking/margin/v1/batch',
            "api.estimateCharges" : 'rest/secure/angelbroking/brokerage/v1/estimateCharges',
            "api.verifyDis" : 'rest/secure/angelbroking/edis/v1/verifyDis',
            "api.generateTPIN" : 'rest/secure/angelbroking/edis/v1/generateTPIN',
            "api.getTranStatus" : 'rest/secure/angelbroking/edis/v1/getTranStatus',
            "api.optionGreek" : 'rest/secure/angelbroking/marketData/v1/optionGreek',
            "api.gainersLosers" : 'rest/secure/angelbroking/marketData/v1/gainersLosers',
            "api.putCallRatio" : 'rest/secure/angelbroking/marketData/v1/putCallRatio',
            "api.oIBuildup" : 'rest/secure/angelbroking/marketData/v1/OIBuildup',
            }

    def requestheader(self):
        if self.login:
            return{
                "Content-type":self.accept,
                "X-ClientLocalIP": self.clientLocalIp,
                "X-ClientPublicIP": self.clientPublicIp,
                "X-MACAddress": self.clientMacAddress,
                "Accept": self.accept,
                "X-PrivateKey": self.privateKey,
                "X-UserType": self.userType,
                "X-SourceID": self.sourceID,
                "Authorization": 'Bearer '+self.jwt_token
            }
        else:
            return{
                "Content-type":self.accept,
                "X-ClientLocalIP": self.clientLocalIp,
                "X-ClientPublicIP": self.clientPublicIp,
                "X-MACAddress": self.clientMacAddress,
                "Accept": self.accept,
                "X-PrivateKey": self.privateKey,
                "X-UserType": self.userType,
                "X-SourceID": self.sourceID
            }

    def send_request(self,method,route,parameters):
        if method == 'POST':
            self.conn.request("POST",self.routes[route],str(parameters),self.requestheader())
        elif method == 'GET':
            self.conn.request("GET",self.routes[route],str(parameters),self.requestheader())
        else:
            print('invalid method')
        try:
            res = self.conn.getresponse()
            data = res.read()
            data = data.decode("utf-8")
            if data['message'] == 'SUCCESS':
                return data
            elif data['message'] == 'FAIL':
                return data['errorcode']
        except Exception as e:
            print(e)
        
    def login(self,client_code,client_pin,totp):
        self.userid = client_code
        payload = {
            "clientcode":client_code,
            "password":client_pin,
            "totp":totp
            }
        
        response = self.send_request('POST',"api.login",payload)
        if response['status']==True:
            self.jwt_token = response['data']['jwtToken']
            self.refresh_token = response['data']['refreshToken']
            self.feed_token = response['data']['feedToken']
            self.login = True
            self.getprofile()
        else:
            print(response)
        
    def getprofile(self):
       
        payload = ''
        response = self.send_request('GET',"api.user.profile",payload)
        return response
        

    def renew_token(self):
        # regenerate token using refreshtoken
        
        payload = {
            "refreshToken":self.refresh_token
            }
        response = self.send_request('POST',"api.token",payload)
        self.jwt_token = response['data']['jwtToken']
        return response['message']
        
    
    def logout(self):
       
        payload = {
            "clientcode": self.userid
            }
        response = self.send_request('POST',"api.logout",payload)
        return response['message']
        
    
    def getrms(self):
        # returns marging limit for te account
        payload = ''
        response = self.send_request('GET',"api.rms.limit",payload)
        return response
        
    
    def verify_constraints(variety = None, transactiontype = None, ordertype = None, producttype = None, Duration = None, exchange = None):
        constraints = {
            variety : ['NORMAL','STOPLOSS','AMO','ROBO'],
            transactiontype : ['BUY','SELL'],
            ordertype : ['MARKET','LIMIT','STOPLOSS_LIMIT','STOPLOSS_MARKET'],
            producttype : ['DELIVERY','CARRYFORWARD','MARGIN','INTRADAY','BO'],
            Duration : ['DAY','IOC'],
            exchange : ['BSE','NSE','NFO','MCX','BFO','CDS']
            }
        flag = True
        for key in constraints:
            if key is not None:
                if key not in constraints[key]:
                    flag = False
                    break
        return flag

    
    def place_order(self,variety,tradingsymbol,symboltoken,transactiontype,exchange,ordertype,producttype,duration,quantity,price = 0, stoploss = 0, squareoff = 0):
        verify = self.verify_constraints(variety = variety, transactiontype = transactiontype, ordertype = ordertype, producttype = producttype, Duration = duration, exchange = exchange)
        if verify:
            payload = {
                "variety":variety,
                "tradingsymbol":tradingsymbol,
                "symboltoken":symboltoken,
                "transactiontype":transactiontype,
                "exchange":exchange,
                "ordertype":ordertype,
                "producttype":producttype,
                "duration":duration,
                "price":price,
                "squareoff":squareoff,
                "stoploss":stoploss,
                "quantity":quantity
                }
            response = self.send_request('POST',"api.order.place",payload)
            if response != 'FAIL':
                self.orderid = []
                self.orderid.append(response['data']['orderid'])
            return response
        else:
            return('wrong value given')
    
    def modify_order(self,variety,tradingsymbol,symboltoken,transactiontype,exchange,ordertype,producttype,duration,quantity,price,orderid):
        verify = self.verify_constraints(variety = variety, transactiontype = transactiontype, ordertype = ordertype, producttype = producttype, Duration = duration, exchange = exchange)
        if verify:
            payload = {
                "variety":variety,
                "tradingsymbol":tradingsymbol,
                "symboltoken":symboltoken,
                "orderid":orderid,
                "exchange":exchange,
                "ordertype":ordertype,
                "producttype":producttype,
                "duration":duration,
                "price":price,
                "quantity":quantity
                }
            response = self.send_request('POST',"api.order.modify",payload)
            return response
        else:
            return('wrong value given')
    
    def cancel_order(self,variety,orderid):
        payload = {
            "variety":variety,
            "orderid":orderid,
            }
        response = self.send_request('POST',"api.order.modify",payload)
        return response
    def order_book(self):
        payload = ''
        response = self.send_request('GET',"api.order.book",payload)
        return response
    def trade_book(self):
        payload = ''
        response = self.send_request('GET',"api.trade.book",payload)
        return response
    def ltp_data(self,exchange,tradingsymbol,symboltoken):
        payload = {
            "exchange":exchange,
            "tradingsymbol":tradingsymbol,
            "symboltoken":symboltoken
            }
        response = self.send_request('POST',"api.ltp.data",payload)
        return response        

    def get_candle_data(self,exchange,symboltoken,interval,fromdate,todate):
        payload = {
            "exchange": exchange,
            "symboltoken": symboltoken,
            "interval": interval,
            "fromdate": fromdate,
            "todate": todate
            }
        response = self.send_request('POST',"api.candle.data",payload)
        return response        

    def get_postion(self):
        payload = ''
        response = self.send_request('GET',"api.position",payload)
        return response    

    
    

#headers = {
#          'Authorization': 'Bearer 042ec073-5a36-49e7-aaac-65b60d0e5e27',
#          'Content-Type': 'application/json',
#          'Accept': 'application/json',
#          'X-UserType': 'USER',
#          'X-SourceID': 'WEB',
#          'X-ClientLocalIP': '192.168.168.168',
#          'X-ClientPublicIP': '106.193.147.98',
#          'X-MACAddress': '3C:91:80:37:A7:2F',
#          'X-PrivateKey': 'qMSmE1YE'
#        }    
#