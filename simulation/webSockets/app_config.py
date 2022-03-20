import os

from enums import RetailerStrategyGPMultiplier, RetailerSustainabilityIntercept

flaskHttpAppConfig = {}
flaskHttpAppConfig['USE_HTTPS'] = False
flaskHttpAppConfig['APP_LAZY_LOAD'] = False
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
        self.strategy = RetailerStrategyGPMultiplier.COMPETITIVE
        self.sustainabilityBaseline = RetailerSustainabilityIntercept.AVERAGE
        self.controlRetailerName:str|None = None
        
    @staticmethod
    def createFromDict(data:dict[str,str|int|float|None]):
        '''create SimulationConfig params from the passed dict
            if any updates occur, return True else False
            Expects keys:
            - BASKET_FULL_SIZE
            - NUM_SHOP_TRIPS_PER_ITERATION
            - NUM_CUSTOMERS
            - strategy
            - sustainabilityBaseline
            - controlRetailerName
            '''
        instance = SimulationIterationConfig()
        instance.loadFromDict(data)
        return instance
    
    def parseIntValueFromDict(self, key:str, data:dict[str,str|int|float|None]):
        if key in data and data[key] is not None:
            x = data[key]
            assert x is not None
            return int(x)
        else:
            return getattr(self,key)
    
    def parsefloatValueFromDict(self, key:str, data:dict[str,str|int|float|None]):
        if key in data and data[key] is not None:
            x = data[key]
            assert x is not None
            return float(x)
        else:
            return getattr(self,key)
        
    def loadFromDict(self,data:dict[str,str|int|float|None]):
        instance = self
        
        instance.BASKET_FULL_SIZE = self.parseIntValueFromDict('BASKET_FULL_SIZE',data)
        instance.NUM_SHOP_TRIPS_PER_ITERATION = self.parseIntValueFromDict('NUM_SHOP_TRIPS_PER_ITERATION',data)
        instance.NUM_CUSTOMERS = self.parseIntValueFromDict(
            'NUM_CUSTOMERS', data)
        instance.strategy = RetailerStrategyGPMultiplier(self.parsefloatValueFromDict(
            'strategy', data))
        instance.sustainabilityBaseline = RetailerSustainabilityIntercept(self.parsefloatValueFromDict(
            'sustainability', data))
        instance.controlRetailerName = getattr(data,'controlRetailerName',None)
        return None
    
    def toJson(self):
        return {
            'BASKET_FULL_SIZE': self.BASKET_FULL_SIZE,
            'NUM_SHOP_TRIPS_PER_ITERATION': self.NUM_SHOP_TRIPS_PER_ITERATION,
            'NUM_CUSTOMERS': self.NUM_CUSTOMERS,
            'strategy': self.strategy.value,
            'sustainability': self.sustainabilityBaseline.value,
            'controlRetailerName': self.controlRetailerName,
        }
    
class SimulationConfig(SimulationIterationConfig):
    '''class containing simulation config parameters that can be changed.'''
    def __init__(self):
        super().__init__()
        self.maxN = 5
        self.convergenceTH = 1.0
    
    
    def toJson(self) -> dict[str,float|int]:
        return {
            ** super().toJson(),
            'maxN': self.maxN,
            'convergenceTH': self.convergenceTH,
        }
        
    def _updateParam(self,staticFieldName:str,data:dict[str,str|int|None]):
        existingData = self.toJson()
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
                    
    
    def _setParamValue(self,staticFieldName:str,val:int|float|str):
        if staticFieldName == 'controlRetailerName':
            assert val is None or isinstance(val,str)
            self.controlRetailerName = val
        elif isinstance(val,int) or isinstance(val,float):
            if staticFieldName == 'BASKET_FULL_SIZE':
                self.BASKET_FULL_SIZE = int(val)
            elif staticFieldName == 'NUM_SHOP_TRIPS_PER_ITERATION':
                self.NUM_SHOP_TRIPS_PER_ITERATION = int(val)
            elif staticFieldName == 'NUM_CUSTOMERS':
                self.NUM_CUSTOMERS = int(val)
            elif staticFieldName == 'maxN':
                self.maxN = int(val)        
            elif staticFieldName == 'convergenceTH':
                self.convergenceTH = float(val)
            elif staticFieldName == 'strategy':
                self.strategy = float(val)
            elif staticFieldName == 'sustainability':
                self.sustainability = float(val)
        else:
            raise TypeError('Can not update global param for variable name that is not a global parameter.')
        
    
    def updateFromDict(self,data:dict[str,str|int|None]):
        '''update SimulationConfig params from the passed dict
            if any updates occur, return True else False'''
        updatesOccured = False
        updatesOccured = bool(updatesOccured or self._updateParam('BASKET_FULL_SIZE', data))
        updatesOccured = bool(updatesOccured or self._updateParam('strategy', data))
        updatesOccured = bool(updatesOccured or self._updateParam('sustainability', data))
        updatesOccured = bool(updatesOccured or self._updateParam('controlRetailerName', data))
        updatesOccured = bool(updatesOccured or self._updateParam('NUM_SHOP_TRIPS_PER_ITERATION', data))
        updatesOccured = bool(
            updatesOccured or self._updateParam('NUM_CUSTOMERS', data))
        updatesOccured = bool(updatesOccured or self._updateParam('maxN', data))
        updatesOccured = bool(
            updatesOccured or self._updateParam('convergenceTH', data))
        return updatesOccured
    
    @staticmethod
    def createFromDict(data:dict[str,str|int|float|None]):
        '''create SimulationConfig params from the passed dict
            if any updates occur, return True else False
            Expects keys:
            - BASKET_FULL_SIZE
            - NUM_SHOP_TRIPS_PER_ITERATION
            - NUM_CUSTOMERS
            - maxN
            - convergenceTH
            - strategy
            - sustainabilityBaseline
            - controlRetailerName
            '''
        instance = SimulationConfig()
        SimulationIterationConfig.loadFromDict(instance, data)
        instance.loadFromDict(data)
        return instance
    
    def loadFromDict(self,data:dict[str,str|int|float|None]):
        instance = self
        super().loadFromDict(data)
        # instance.BASKET_FULL_SIZE = data['BASKET_FULL_SIZE'] if 'BASKET_FULL_SIZE' in data else instance.BASKET_FULL_SIZE
        # instance.NUM_SHOP_TRIPS_PER_ITERATION = data['NUM_SHOP_TRIPS_PER_ITERATION'] if 'NUM_SHOP_TRIPS_PER_ITERATION' in data else instance.NUM_SHOP_TRIPS_PER_ITERATION
        # instance.NUM_CUSTOMERS = data['NUM_CUSTOMERS'] if 'NUM_CUSTOMERS' in data else instance.NUM_CUSTOMERS
        instance.maxN = self.parseIntValueFromDict('maxN',data)
        instance.convergenceTH = self.parseIntValueFromDict('convergenceTH',data)
         
        return None



ssl_args = {}
if flaskHttpAppConfig.get('USE_HTTPS') and flaskHttpAppConfig.get('GEMBER_HTTPS_KEYFILE') and flaskHttpAppConfig.get('GEMBER_HTTPS_CERTFILE'):
    ssl_args = {
        'keyfile': flaskHttpAppConfig.get('GEMBER_HTTPS_KEYFILE'),
        'certfile': flaskHttpAppConfig.get('GEMBER_HTTPS_CERTFILE')
    }
