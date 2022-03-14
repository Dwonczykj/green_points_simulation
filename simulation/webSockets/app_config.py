import os

flaskHttpAppConfig = {}
flaskHttpAppConfig['USE_HTTPS'] = False
flaskHttpAppConfig['GEMBER_HTTPS_KEYFILE'] = '/private/etc/ssl/localhost/localhost.key'
flaskHttpAppConfig['GEMBER_HTTPS_CERTFILE'] = '/private/etc/ssl/localhost/localhost.crt'
flaskHttpAppConfig['GEMBER_BIND_HOST'] = '127.0.0.1'
flaskHttpAppConfig['GEMBER_PORT'] = 8443
flaskHttpAppConfig['GEMBER_WS_PORT'] = 5001
flaskHttpAppConfig['SECRET_KEY'] = os.urandom(24)
flaskHttpAppConfig["ALLOW_THREADING"] = True
flaskHttpAppConfig['DEBUG_APP'] = True

class SimulationIterationConfig:
    def __init__(self):
        self.BASKET_FULL_SIZE = 3
        self.NUM_SHOP_TRIPS_PER_ITERATION = 2
        self.NUM_CUSTOMERS = 4
        
    @classmethod
    def createFromDict(cls,data:dict[str,str|int|None]):
        '''create SimulationConfig params from the passed dict
            if any updates occur, return True else False'''
        instance = cls()
        
        instance.BASKET_FULL_SIZE = data['BASKET_FULL_SIZE'] if 'BASKET_FULL_SIZE' in data else instance.BASKET_FULL_SIZE
        instance.NUM_SHOP_TRIPS_PER_ITERATION = data['NUM_SHOP_TRIPS_PER_ITERATION'] if 'NUM_SHOP_TRIPS_PER_ITERATION' in data else instance.NUM_SHOP_TRIPS_PER_ITERATION
        instance.NUM_CUSTOMERS = data['NUM_CUSTOMERS'] if 'NUM_CUSTOMERS' in data else instance.NUM_CUSTOMERS
        
        return instance
    
    def toJson(self):
        return {
            'BASKET_FULL_SIZE': self.BASKET_FULL_SIZE,
            'NUM_SHOP_TRIPS_PER_ITERATION': self.NUM_SHOP_TRIPS_PER_ITERATION,
            'NUM_CUSTOMERS': self.NUM_CUSTOMERS,
        }
    
class SimulationConfig(SimulationIterationConfig):
    '''class containing simulation config parameters that can be changed.'''
    def __init__(self):
        super().__init__()
        self.maxN = 5
        self.convergenceTH = 1.0
    
    
    def toJson(self):
        return {
            'BASKET_FULL_SIZE': self.BASKET_FULL_SIZE,
            'NUM_SHOP_TRIPS_PER_ITERATION': self.NUM_SHOP_TRIPS_PER_ITERATION,
            'NUM_CUSTOMERS': self.NUM_CUSTOMERS,
            'maxN': self.maxN,
            'convergenceTH': self.convergenceTH,
        }
        
    def _updateParam(self,staticFieldName:str,data:dict[str,str|int|None]):
        existingData:dict[str,int] = self.toJson()
        assert staticFieldName in existingData.keys(), 'Can not update global param for variable name that is not a global parameter.'
        if staticFieldName in data.keys():
            paramVal = data[staticFieldName]
            if paramVal is None:
                return False
            elif isinstance(paramVal,str):
                try:
                    paramVal = int(paramVal)
                except:
                    return False
            
            if paramVal != existingData[staticFieldName]:
                self._setParamValue(staticFieldName, paramVal)
                return True
            else:
                return False
        else:
            return False
                    
    
    def _setParamValue(self,staticFieldName:str,val:int):
        if staticFieldName == 'BASKET_FULL_SIZE':
            self.BASKET_FULL_SIZE = val
        elif staticFieldName == 'NUM_SHOP_TRIPS_PER_ITERATION':
            self.NUM_SHOP_TRIPS_PER_ITERATION = val
        elif staticFieldName == 'NUM_CUSTOMERS':
            self.NUM_CUSTOMERS = val
        elif staticFieldName == 'maxN':
            self.maxN = val
        elif staticFieldName == 'convergenceTH':
            self.convergenceTH = val
        else:
            raise TypeError('Can not update global param for variable name that is not a global parameter.')
        
    
    def updateFromDict(self,data:dict[str,str|int|None]):
        '''update SimulationConfig params from the passed dict
            if any updates occur, return True else False'''
        updatesOccured = False
        updatesOccured = bool(updatesOccured or self._updateParam('BASKET_FULL_SIZE', data))
        updatesOccured = bool(updatesOccured or self._updateParam('NUM_SHOP_TRIPS_PER_ITERATION', data))
        updatesOccured = bool(
            updatesOccured or self._updateParam('NUM_CUSTOMERS', data))
        updatesOccured = bool(updatesOccured or self._updateParam('maxN', data))
        updatesOccured = bool(
            updatesOccured or self._updateParam('convergenceTH', data))
        return updatesOccured
    
    @classmethod
    def createFromDict(cls,data:dict[str,str|int|None]):
        '''create SimulationConfig params from the passed dict
            if any updates occur, return True else False'''
        instance = cls()
        
        instance.BASKET_FULL_SIZE = data['BASKET_FULL_SIZE'] if 'BASKET_FULL_SIZE' in data else instance.BASKET_FULL_SIZE
        instance.NUM_SHOP_TRIPS_PER_ITERATION = data['NUM_SHOP_TRIPS_PER_ITERATION'] if 'NUM_SHOP_TRIPS_PER_ITERATION' in data else instance.NUM_SHOP_TRIPS_PER_ITERATION
        instance.NUM_CUSTOMERS = data['NUM_CUSTOMERS'] if 'NUM_CUSTOMERS' in data else instance.NUM_CUSTOMERS
        instance.maxN = data['maxN'] if 'maxN' in data else instance.maxN
        instance.convergenceTH = data['convergenceTH'] if 'convergenceTH' in data else instance.convergenceTH
        
        return instance



ssl_args = {}
if flaskHttpAppConfig.get('USE_HTTPS') and flaskHttpAppConfig.get('GEMBER_HTTPS_KEYFILE') and flaskHttpAppConfig.get('GEMBER_HTTPS_CERTFILE'):
    ssl_args = {
        'keyfile': flaskHttpAppConfig.get('GEMBER_HTTPS_KEYFILE'),
        'certfile': flaskHttpAppConfig.get('GEMBER_HTTPS_CERTFILE')
    }
