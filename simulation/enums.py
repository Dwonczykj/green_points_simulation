import enum
from typing_extensions import Self

class RetailerStrategyGPMultiplier(float, enum.Enum):
    ZERO=0.0
    MIN=0.1
    COMPETITIVE=1.0
    MAX=10.0
    

class RetailerSustainabilityIntercept(float, enum.Enum):
    LOW=-0.25
    AVERAGE=0.0
    HIGH=0.25
    
class InvalidRetailerReason(enum.Enum):
    validRetailer=-1,
    invalidName=0,
    invalidStrategy=1,
    invalidSustainability=2
    
class GemberMeasureType(enum.Enum):
    sales_count='sales_count'
    GP_Issued='green_points_issued'
    market_share='market_share'
    total_sales_revenue='total_sales_revenue'
    total_sales_revenue_less_gp='total_sales_revenue_less_gp'
    total_sales_revenue_by_item='total_sales_revenue_by_item'
    
    @classmethod
    def formatName(cls, measure:Self):
        return ' '.join(measure.name.split('_'))