
from Bank import RetailerStrategyGPMultiplier, RetailerSustainabilityIntercept
from app_globals import gpApp

def validate_retailer_name(name: str):
    
    return gpApp.validateRetailerName(name=name)


def validate_retailer_strategy(name: str, strategy: str):
    return bool(strategy in RetailerStrategyGPMultiplier.__members__.keys())


def validate_retailer_sustainability(name: str, sustainability: str):
    return bool(sustainability in RetailerSustainabilityIntercept.__members__.keys())