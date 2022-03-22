from __future__ import annotations
from enum import Enum
from typing import Any, Callable, Literal, Tuple, TypeGuard
import cachetools.func # for ttl_cacheing of sim_envs
import cachetools
import eventlet
import time
from eventlet import queue
import uuid
from colorama import Fore, Back, Style
# from queue_main_global import QueueHolder
import logging
import pandas as pd
import numpy as np
from flask_socketio import SocketIO
import abc
from Multipliable import Numeric

# from Singleton import classproperty
from enums import *
from data_fetcher import get_dataset, pd_dataframe_explain_update
from Observer import Observable, Observer
from Bank import Bank, BankAccountView, ControlRetailer, Customer, Entity, RetailerStrategyGPMultiplier, Retailer, RetailerSustainabilityIntercept, SalesAggregation
from Bank import debug as APP_DEBUG
from Coin import Money
# import random
from ISerializable import TSTRUC_ALIAS, SerializableList
from event_names import WebSocketServerResponseEvent
from gpApp_entity_initializer import *
from app_config import SimulationConfig, SimulationIterationConfig



from web_socket_stack import WebSocketsStack
# import sys
# sys.path += ['./Observable/utils']


class SimulationEnvType(Enum):
    Full = 1
    Scenario = 2
    SingleIteration = 3

class GreenPointsLoyaltyApp():
    '''Singleton: Call getInstance() to get'''
    __instance: GreenPointsLoyaltyApp | None = None
    debug:bool=APP_DEBUG
    # __callback_queue = QueueHolder.global_callback_queue
    
    # @classproperty
    # def callback_queue(cls):
    #     return cls.__callback_queue
    
    # @classmethod
    # def get_callback_queue(cls):
    #     return cls.__callback_queue

    @staticmethod
    def getInstance(data:pd.DataFrame,socketio:SocketIO,debug:bool=False):
        """ Static access method. """
        if GreenPointsLoyaltyApp.__instance == None:
            GreenPointsLoyaltyApp.debug=debug
            GreenPointsLoyaltyApp(data=data,socketio=socketio)
            
        assert isinstance(GreenPointsLoyaltyApp.__instance,
                          GreenPointsLoyaltyApp)
        return GreenPointsLoyaltyApp.__instance

    def __init__(self,data:pd.DataFrame,socketio:SocketIO):
        """ Virtually private constructor. """
        if GreenPointsLoyaltyApp.__instance != None:
            raise Exception(type(self).__name__ + " class is a singleton!")
        else:
            GreenPointsLoyaltyApp.__instance = self
            df = data
            self._entityInitialiser = EntityInitialiser(df=df)
            self._envInitializer = GreenPointsLoyaltyApp.Initializer(
                gpApp=self)
            # self._simulationEnvironments:dict[str,Tuple[float,GreenPointsLoyaltyApp.SimulationEnvironment]] = {}
            self._simulationEnvironments: cachetools.TTLCache[str, Tuple[float, GreenPointsLoyaltyApp.SimulationEnvironment]] = \
                cachetools.TTLCache(maxsize=128, ttl=30 * 60)
            self._active_simulation_environment = None
            self._running = False
            # self._retailers = self._entityInitialiser.retailers
            # self._customers = []
            self._initialised = False
            self._simsRun: int = 0
            self._secondsBetweenPurchases = 2.0
            self._df_strategized: pd.DataFrame | None = None
            self._simulation_results: list[pd.DataFrame] = []
            
            self._websocket = WebSocketsStack.getInstance(self,socketio)
            # self.nonBlockingQueueChecker()
            
    # def nonBlockingQueueChecker(self):
    #     while True:
    #         try:
    #             callback = GreenPointsLoyaltyApp.get_callback_queue().get(False)  # doesn't block
    #         except queue.Empty: #raised when queue is empty
    #             break
    #         callback()
    #         eventlet.sleep(secs=2)
      
    # @property          
    # def initialEntitiesSnapshot(self):
    #     return self._envInitializer.entities
            
    @property
    def websocket(self):
        return self._websocket
    
    # def registerWebSocketStack(self):
    #     # assert ws is not None
    #     self._websocket = ws
    
    
    
    @property
    def secondsBetweenPurchases(self):
        # if self._runningIsolatedSimulation[taskId]
        return self._secondsBetweenPurchases
    
    @secondsBetweenPurchases.setter
    def secondsBetweenPurchases(self, value: float):
        self._secondsBetweenPurchases = value
        
    def validateRetailerName(self,name:str):
        return bool(name in self._envInitializer.retailerNames)
    
    def _getEntity(self, simulationEnvId:str, entityId):
        simEnv = self.getSimulationEnvironment(simulationId=simulationEnvId)
        if simEnv is not None:
            retailer = next((r for r in simEnv.retailers.values() if r.id == entityId), None)
            if retailer:
                return retailer
            customer = next((r for r in simEnv.customers if r.id == entityId), None)
            if customer:
                return customer
        

    def transactionsToEntity(self, simulationEnvId:str, entityId: str):
        simEnv = self.getSimulationEnvironment(simulationId=simulationEnvId)
        if simEnv is not None:
            entityMatch: Entity | None = next(
                (r for r in simEnv.retailers.values() if r.id == entityId), None)
            if entityMatch is not None:
                return [t.toDictUI() for t in entityMatch.allTransactionsIn]
            entityMatch = next(
                (r for r in simEnv.customers if r.id == entityId), None)
            if entityMatch is not None:
                return [t.toDictUI() for t in entityMatch.allTransactionsIn]
        return []

    def transactionsFromEntity(self, simulationEnvId:str, entityId: str):
        simEnv = self.getSimulationEnvironment(simulationId=simulationEnvId)
        if simEnv is not None:
            entityMatch: Entity | None = next(
                (r for r in simEnv.retailers.values() if r.id == entityId), None)
            if entityMatch is not None:
                return [t.toDictUI() for t in entityMatch.allTransactionsOut]
            entityMatch = next(
                (r for r in simEnv.customers if r.id == entityId), None)
            if entityMatch is not None:
                return [t.toDictUI() for t in entityMatch.allTransactionsOut]
        return []

    def salesForItem(self, simulationEnvId:str, itemName: str):
        simEnv = self.getSimulationEnvironment(simulationId=simulationEnvId, throw=True)
        assert simEnv is not None
        return SerializableList([sale.toDictUI()
                                for retailer in simEnv.retailers
                                for sale in simEnv.retailers[retailer].salesHistory
                                if sale.item.name.lower() == itemName.lower()
                                ])
    
    class BankEventObserver(Observer):
        def __init__(self,gpApp:GreenPointsLoyaltyApp,simEnv:GreenPointsLoyaltyApp.SimulationEnvironment) -> None:
            super().__init__()
            self.gpAppOuter = gpApp
            self.simEnv = simEnv
        
        def update(self, observable:Observable, **kwargs:Any):
            '''self._bank notified us that it has sent money, check if we are in the arg and then do something if we are?'''
            eventName:Bank.Event = kwargs['event_name']
            data:Any = kwargs['data']
            
            if eventName == Bank.Event.account_added:
                self.gpAppOuter._emit_event(WebSocketServerResponseEvent.bank_account_added, data=data)
                pass
            elif eventName == Bank.Event.transaction_completed:
                self.gpAppOuter._emit_event(WebSocketServerResponseEvent.bank_transaction_completed, data=data)
                try:
                    entity = self.simEnv._getEntity(data["accountFrom"]["owner"]["id"])
                    if entity is not None:
                        self.gpAppOuter._emit_event(
                            WebSocketServerResponseEvent.entity_updated, data=entity.toDictUI())
                    entity = self.simEnv._getEntity(
                        data["accountTo"]["owner"]["id"])
                    if entity is not None:
                        self.gpAppOuter._emit_event(
                            WebSocketServerResponseEvent.entity_updated, data=entity.toDictUI())
                except:
                    pass
                pass
            elif eventName == Bank.Event.transaction_created:
                self.gpAppOuter._emit_event(WebSocketServerResponseEvent.bank_transaction_created, data=data)
                pass
            elif eventName == Bank.Event.transaction_failed:
                self.gpAppOuter._emit_event(WebSocketServerResponseEvent.bank_transaction_failed, data=data)
                pass
            else:
                pass
            
    class Initializer:
        def __init__(self, gpApp:GreenPointsLoyaltyApp):
            self.gpApp = gpApp
            if not self.gpApp._entityInitialiser:
                raise Exception('GreenPointsLoyaltyApp.__init__ order of initialisation error. _entityInitialiser:EntityInitialiser must be set before constructing this GreenPointsLoyaltyApp.Initializer')
            self._df_strategized = self.gpApp._entityInitialiser.initialDataSet
            self._expectedNumIncludedInBasket = {r: (self._df_strategized[f'{r} Sells'].astype(int).to_numpy()
                   * self._df_strategized[f'Prob Customer Select']
                   ).sum() for r in self.gpApp._entityInitialiser.retailerNames}
            self._retailers = self.gpApp._entityInitialiser.retailers
            self._retailerStrategiesInitialised = False
            self._gpIssueingVolumeIsEqualisedBetweenRetailers = False
            self._gpRewardsAdjustedForRetailerSustainability = False
            self._gpRewardsScaledByRetailerStrategy = False
            self._out_df:pd.DataFrame|None=None
            
        
        @property
        def retailers(self):
            return self._retailers
        
        @property
        def retailerNames(self):
            return [name for name in self.retailers.keys()]
        
        # @property
        # def customers(self):
        #     return self.gpApp._entityInitialiser.customers
        
        
        @property
        def entities(self) -> dict[str, dict[str, TSTRUC_ALIAS]]:
            aggregatedBalance = sum(
                [r.balance for r in self._retailers.values()], start=BankAccountView.zero())
            return {
                'retailers': {rName: self._retailers[rName].toDictUI() for rName in self._retailers},
                'retailersCluster': {
                    "balance": aggregatedBalance.toDictUI(),
                    "balanceMoney": aggregatedBalance.combinedBalance.toDictUI(),
                    'salesHistory': [s.toDictUI() for r in self._retailers.values() for s in r.salesHistory],
                    'totalSales': sum((r.totalSales for r in self._retailers.values()), start=SalesAggregation.zero()).toDictUI()
                },
                # 'customers': {c.name: c.toDictUI() for c in self.customers}
            }
        
        @property
        def df_strategized(self):
            '''A copy of the initialised data set with Green Points Rewards calculated & adjusted'''
            return self._df_strategized.copy()
        
        # @property
        # def gpIssueingVolumeIsEqualisedBetweenRetailerss(self):
        #     '''Flag specifying whether the initialised data set has been updated so that all retailers start with the same expectation for the number of green points that they will issue.'''
        #     return self._gpIssueingVolumeIsEqualisedBetweenRetailers
        
        # @property
        # def output_df(self):
        #     if self._out_df is None:
        #         out_df = pd.DataFrame(
        #             columns=self.gpApp._entityInitialiser.retailerNames)
        #         out_df.loc['strategy'] = pd.Series(self.greenPointStrategies)
        #         out_df.loc['sustainabilityOfItems'] = pd.Series(
        #             self.sustainabilityUpdates)
        #         out_df.loc['expectedPoints'] = pd.Series(self.expectedPoints)
        #         out_df.loc['expectedNumIncludedInBasket'] = pd.Series(
        #             self.expectedNumIncludedInBasket)
        #         self._out_df = out_df
        #     return self._out_df
        
        # @property
        # def expectedNumIncludedInBasket(self):
        #     '''The expected number of items sold if a consumer came in and purchased one of every item in this retailers store with probability p (defined vs each item)
                
        #         This is calculated to ensure that no store is expected to sell ridiculously more than any of the others in the simulation which would skew the simulation.'''
        #     return self._expectedNumIncludedInBasket
            
            
        # def recordRetailerStrategies(self):
        #     # Declare lookups:
        #     self.greenPointStrategies = {
        #         k: self._retailers[k].strategy for k in self._retailers.keys()}
        #     self.sustainabilityUpdates = {
        #         k: self._retailers[k].sustainability for k in self._retailers.keys()}
        #     self._retailerStrategiesInitialised = True
        #     return self
        
        # def mutliplyGPRewardsByRetailerStrategy(self, retailerName: str, debugShowDiff: bool = False):
        #     assert self._retailerStrategiesInitialised, 'Retailer Strategies must be initialised before scaling the GP Rewards'
        #     _old = None
        #     if debugShowDiff:
        #         _old = self._df_strategized.copy()
        #     if self._gpRewardsAdjustedForRetailerSustainability:
        #         raise Warning('Green Point rewards have already adjusted for the relative sustainability factor' + 
        #                       ' of each retailer. This method will multiply the adjusted GP rewards and thereby make the adjustment more extreme...')
        #     # Update df for Retailer Strategy
        #     # self._df_strategized = self._df_strategized.set_index('Item')
        #     self._df_strategized[f'{retailerName} GP'] = (np.round(self.gpApp._entityInitialiser.initialDataSet[f'{retailerName} GP'].astype(float).to_numpy()
        #                                                     * self.greenPointStrategies[retailerName]
        #                                                     * 10
        #                                                     )).astype(int)
        #     self._gpRewardsScaledByRetailerStrategy = True
        #     if debugShowDiff:
        #         assert isinstance(_old, pd.DataFrame)
        #         logging.debug(pd_dataframe_explain_update(_old, self._df_strategized))
        #     return self
        
        # def equalizeGreenPointIssuingVolumeForRetailers(self, setExpectedGPIssuedTo:int, debugShowDiff:bool=False):
        #     if self._gpRewardsScaledByRetailerStrategy:
        #         raise Warning('Green Point rewards have already been scaled for strategy in the initializer. This method will undo this work by equalising the GPs issued by each retailer...')
        #     _old = None
        #     if debugShowDiff:
        #         _old = self._df_strategized.copy()
        #     # Get Expected Number Points per Retailer
        #     nItems = self._df_strategized.shape[0]
        #     self.expectedPoints = {r: (self._df_strategized[f'{r} GP'].astype(float).to_numpy()
        #                             * self._df_strategized['Prob Customer Select']
        #                             * (AppConfig.BASKET_FULL_SIZE/float(nItems))
        #                             * AppConfig.NUM_SHOP_TRIPS_PER_ITERATION
        #                             ).sum() for r in self.retailerNames}

        #     # Equalise Expected Number Points to 500
        #     _EXPECTED_POINTS = setExpectedGPIssuedTo # 500.0
        #     for r in self.retailerNames:
        #         if self.expectedPoints[r] > 0:
        #             self._df_strategized[f'{r} GP'] = self._df_strategized[f'{r} GP'] * \
        #                 (_EXPECTED_POINTS/self.expectedPoints[r])
        #     self._gpIssueingVolumeIsEqualisedBetweenRetailers = True
            
        #     # Record the effects of the normalisation transformation.
        #     self.expectedPointsUniformed = {r: (self._df_strategized[f'{r} GP'].astype(float).to_numpy()
        #                                         * self._df_strategized['Prob Customer Select']
        #                                         * (AppConfig.BASKET_FULL_SIZE/float(nItems))
        #                                         * AppConfig.NUM_SHOP_TRIPS_PER_ITERATION).sum() for r in self.retailerNames}
        #     if debugShowDiff:
        #         assert isinstance(_old,pd.DataFrame)
        #         logging.debug(pd_dataframe_explain_update(_old, self._df_strategized))
        #     return self
        
        # def adjustGPRewardsByRetailerSustainabilityBaseline(self, debugShowDiff: bool = False):
        #     '''Add a positive bump to the number of GPs that a retailer with a good ESG rating (level of responsible actions towards society) is allowed to issue and the converse for poorly ESG rated retailers'''
        #     _old = None
        #     if debugShowDiff:
        #         _old = self._df_strategized.copy()
        #     nItems = self._df_strategized.shape[0]
        #     # Adjust GPs for Sustainability of Retailer
        #     for r in self.retailerNames:
        #         def _func(x: float):
        #             return x + self._retailers[r].sustainability
        #         self._df_strategized[f"{r} Relative Sustainability of Item Multiplier"] = \
        #             (self._df_strategized[f"{r} Relative Sustainability of Item Multiplier"].astype(float)
        #             # FIX Type of lambda function for type inference of result
        #             .transform([_func])
        #             .transform([lambda x: min(max(x, -1), 1)])
        #             )
        #         self._df_strategized[f'{r} GP'] = \
        #             pd.Series(self._df_strategized[f'{r} GP']
        #                     * self._df_strategized[f"{r} Relative Sustainability of Item Multiplier"].astype(float).to_numpy()
        #                     )\
        #             .transform([lambda x: round(x, ndigits=0)])
        #     self._gpRewardsAdjustedForRetailerSustainability = True
            
        #     self.expectedPoints = {r: (self._df_strategized[f'{r} GP'].astype(float).to_numpy()
        #                                * self._df_strategized['Prob Customer Select']
        #                                * (AppConfig.BASKET_FULL_SIZE/float(nItems))
        #                                * AppConfig.NUM_SHOP_TRIPS_PER_ITERATION
        #                                ).sum() 
        #                            for r in self.retailerNames}
        #     if debugShowDiff:
        #         assert isinstance(_old, pd.DataFrame)
        #         logging.debug(pd_dataframe_explain_update(_old, self._df_strategized))
        #     return self
        
        def createSimulationFullEnvironment(self, simConfigParams:SimulationConfig, equalizeGPIssueingVol:bool=False):
            '''Initialises and calibrates the initial dataset of retailers, items etc adjusted for the parameters specified in retailerStrategy and retailerSustainability'''
            
            EXPECTED_POINTS = 500
            simEnv = GreenPointsLoyaltyApp.SimulationFullEnvironment(initializer=self, simConfig=simConfigParams)
            if equalizeGPIssueingVol:
                simEnv.equalizeGreenPointIssuingVolumeForRetailers(setExpectedGPIssuedTo=EXPECTED_POINTS)
            return simEnv
        
        def createSimulationSingleIterationEnvironment(self, simConfigParams:SimulationIterationConfig, equalizeGPIssueingVol:bool=False):
            '''Initialises and calibrates the initial dataset of retailers, items etc adjusted for the parameters specified in retailerStrategy and retailerSustainability'''
            
            EXPECTED_POINTS = 500
            simEnv = GreenPointsLoyaltyApp.SimulationSingleIterationEnvironment(initializer=self, simConfig=simConfigParams)
            if equalizeGPIssueingVol:
                simEnv.equalizeGreenPointIssuingVolumeForRetailers(setExpectedGPIssuedTo=EXPECTED_POINTS)
            return simEnv
        
        def createSimulationScenarioRunEnvironment(self, simConfigParams:SimulationIterationConfig, equalizeGPIssueingVol:bool=False):
            '''Initialises and calibrates the initial dataset of retailers, items etc adjusted for the parameters specified in retailerStrategy and retailerSustainability'''
            
            EXPECTED_POINTS = 500
            simEnv = GreenPointsLoyaltyApp.SimulationScenarioEnvironment(initializer=self, simConfig=simConfigParams)
            if equalizeGPIssueingVol:
                simEnv.equalizeGreenPointIssuingVolumeForRetailers(setExpectedGPIssuedTo=EXPECTED_POINTS)
            return simEnv


    # def setSimulationParametersOnEnvInitializer(self, simulationId:str):
        
    #     self._envInitializer\
    #         .equalizeGreenPointIssuingVolumeForRetailers(setExpectedGPIssuedTo=EXPECTED_POINTS)
            # .adjustStrategyForOneRetailer(retailerName=retailerName,
            #                               retailerStrategy=retailerStrategy,
            #                               retailerSustainability=retailerSustainability)\
            # .recordRetailerStrategies()\
            # .mutliplyGPRewardsByRetailerStrategy(retailerName=retailerName)\
            # .adjustGPRewardsByRetailerSustainabilityBaseline()
            
        # return self._envInitializer
        
    def initAppEnv(self):
        # self.setSimulationParametersOnEnvInitializer()
        # return self, {**self._envInitializer.entities, **AppConfig.toJson()}
        self._initialised = True
        return self
    
    
    
    # @property
    # def active_simulation_environment(self):
    #     if self.initialised:
    #         return self._active_simulation_environment
    #     else:
    #         return None

    class IterationResultRunningAverage:
        def __init__(self, iterationNumber:int, maxNIterations:int,
                     runningSum:GreenPointsLoyaltyApp.IterationResult,
                     runningAverage:GreenPointsLoyaltyApp.IterationResult,
                     runningVariance:GreenPointsLoyaltyApp.IterationResult):
            self.iterationNumber = iterationNumber
            self.maxNIterations = maxNIterations
            self.runningSum = runningSum
            self.runningAverage = runningAverage
            self.runningVariance = runningVariance
            
        @staticmethod
        def initialIteration(iterationResult:GreenPointsLoyaltyApp.IterationResult, maxNIterations:int):
            return GreenPointsLoyaltyApp.IterationResultRunningAverage(
                    iterationNumber=1,
                maxNIterations=maxNIterations,
                    runningSum=iterationResult,
                    runningAverage=iterationResult,
                    runningVariance=GreenPointsLoyaltyApp.IterationResult(
                        salesCount=iterationResult.salesCount * 0.0,
                        greenPointsIssued=iterationResult.greenPointsIssued * 0.0,
                        marketShare=iterationResult.marketShare * 0.0,
                        totalSalesRevenue=iterationResult.totalSalesRevenue * 0.0,
                        # totalSalesRevenueByItem=iterationResult.totalSalesRevenueByItem * 0.0,
                        totalSalesRevenueLessGP=iterationResult.totalSalesRevenueLessGP * 0.0,
                    ),
                )
            
        def toJson(self):
            return {
                'iteration_number': self.iterationNumber,
                'maxNIterations': self.maxNIterations,
                'running_sum': self.runningSum.toDict(),
                'running_average': self.runningAverage.toDict(),
                'running_variance': self.runningVariance.toDict()
            }
        
        @staticmethod    
        def _calculateNextVariance(previous:GreenPointsLoyaltyApp.IterationResultRunningAverage,
                                   runningAverage:GreenPointsLoyaltyApp.IterationResult,
                                   result: GreenPointsLoyaltyApp.IterationResult):
             '''https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Welford's_online_algorithm'''
             assert previous.iterationNumber >= 1, "Previous iteration number must be >= 1"
             n = previous.iterationNumber + 1
             def _nextRVar(measureGetter:Callable[[GreenPointsLoyaltyApp.IterationResult],pd.Series]) -> pd.Series:
                 return (measureGetter(previous.runningVariance) + 
                             ((measureGetter(result) - measureGetter(previous.runningAverage)) * 
                              (measureGetter(result) - measureGetter(runningAverage)))) / (n - 1)
             return GreenPointsLoyaltyApp.IterationResult(
                 salesCount=_nextRVar(lambda ir: ir.salesCount),
                 greenPointsIssued=_nextRVar(lambda ir: ir.greenPointsIssued),
                 marketShare=_nextRVar(lambda ir: ir.marketShare),
                 totalSalesRevenue=_nextRVar(lambda ir: ir.totalSalesRevenue),
                #  totalSalesRevenueByItem=_nextRVar(lambda ir: ir.totalSalesRevenueByItem),
                 totalSalesRevenueLessGP=_nextRVar(lambda ir: ir.totalSalesRevenueLessGP),
             )
             
        
        @staticmethod
        def appendResult(previousIterationNumber:int, 
                         previous:GreenPointsLoyaltyApp.IterationResultRunningAverage,
                         result:GreenPointsLoyaltyApp.IterationResult):
            assert previousIterationNumber >= 1, "Previous iteration number must be >= 1"
            iterationNumber = previous.iterationNumber + 1
            
            runningSum = GreenPointsLoyaltyApp.IterationResult(
                salesCount=(previous.runningSum.salesCount + result.salesCount),
                greenPointsIssued=(previous.runningSum.greenPointsIssued + result.greenPointsIssued),
                marketShare=(previous.runningSum.marketShare +
                             result.marketShare),
                totalSalesRevenue=(previous.runningSum.totalSalesRevenue + result.totalSalesRevenue),
                # totalSalesRevenueByItem=(
                #     previous.runningSum.totalSalesRevenueByItem + result.totalSalesRevenueByItem),
                totalSalesRevenueLessGP=(previous.runningSum.totalSalesRevenueLessGP + result.totalSalesRevenueLessGP),
            )
            runningAverage = GreenPointsLoyaltyApp.IterationResult(
                salesCount=runningSum.salesCount.div(iterationNumber),
                greenPointsIssued=runningSum.greenPointsIssued.div(iterationNumber),
                marketShare=runningSum.marketShare.div(iterationNumber),
                totalSalesRevenue=runningSum.totalSalesRevenue.div(iterationNumber),
                # totalSalesRevenueByItem=runningSum.totalSalesRevenueByItem.div(
                #     iterationNumber),
                totalSalesRevenueLessGP=runningSum.totalSalesRevenueLessGP.div(
                    iterationNumber),
            )
            
            runningVariance = GreenPointsLoyaltyApp.IterationResultRunningAverage\
                ._calculateNextVariance(previous=previous,
                                        runningAverage=runningAverage,
                                        result=result)
            
            return GreenPointsLoyaltyApp.IterationResultRunningAverage(
                iterationNumber=iterationNumber,
                maxNIterations=previous.maxNIterations,
                runningSum=runningSum,
                runningAverage=runningAverage,
                runningVariance=runningVariance
                )
    
    
    class IterationResult:
        def __init__(self, 
                     salesCount: pd.Series[Numeric], 
                     greenPointsIssued: pd.Series[Numeric], 
                     marketShare: pd.Series[Numeric], 
                     totalSalesRevenue: pd.Series[Numeric], 
                    #  totalSalesRevenueByItem: pd.Series, 
                     totalSalesRevenueLessGP: pd.Series[Numeric]) -> None:
            self._salesCount = salesCount
            self._greenPointsIssued = greenPointsIssued
            self._marketShare = marketShare
            self._totalSalesRevenue = totalSalesRevenue
            # self._totalSalesRevenueByItem = totalSalesRevenueByItem
            self._totalSalesRevenueByItem = totalSalesRevenue
            self._totalSalesRevenueLessGP = totalSalesRevenueLessGP
            
        @property
        def salesCount(self):
            '''volume of sales recorded against each retailer'''
            return self._salesCount
        @property
        def greenPointsIssued(self):
            '''number of greenpoints issues per retailer'''
            return self._greenPointsIssued
        @property
        def marketShare(self):
            '''market share between 0 and 1 of retailer total sales volume vs the rest of the market'''
            return self._marketShare
        @property
        def totalSalesRevenue(self):
            '''Total amount of money recieved by the retailer for all sales'''
            return self._totalSalesRevenue
        @property
        def totalSalesRevenueLessGP(self):
            '''Total amount of money recieved by the retailer for all sales less the Gember Points issued to reward those sales'''
            return self._totalSalesRevenueLessGP
        @property
        def totalSalesRevenueByItem(self):
            '''Total amount of money recieved by the retailer for all sales indexed by retailer and then sub indexed by item name'''
            return self._totalSalesRevenueByItem
        
        def toDataFrame(self):
            return pd.DataFrame({
                GemberMeasureType.sales_count.value: self.salesCount,
                GemberMeasureType.GP_Issued.value: self._greenPointsIssued,
                GemberMeasureType.market_share.value: self._marketShare,
                GemberMeasureType.total_sales_revenue.value: self._totalSalesRevenue,
                # GemberMeasureType.total_sales_revenue_by_item.value: self._totalSalesRevenueByItem,
                GemberMeasureType.total_sales_revenue_less_gp.value: self._totalSalesRevenueLessGP,
            })
            
        def toJson(self):
            return self.toDataFrame().to_json()
        
        def toDict(self):
            return self.toDataFrame().to_dict()
            
        @staticmethod
        def fromRetailers(retailers:dict[str,Retailer], preferredCurrency:str|None=None):
            
            _preferredCurrency = 'GBP'
            if preferredCurrency is None:
                try:
                    intersectingCurrencies:list|None = None
                    for r in retailers.values():
                        for r2 in retailers.values():
                            if intersectingCurrencies is None:
                                intersectingCurrencies = r.intersectingCurrencies(r2)
                            else:    
                                intersectingCurrencies = list(set(intersectingCurrencies).intersection(r.intersectingCurrencies(r2)))
                    if not intersectingCurrencies:
                        raise Warning('No intersecting currencies between all retailers\' accounts')
                    else:
                        _preferredCurrency = intersectingCurrencies[0]
                except:
                    pass
            else:
                _preferredCurrency = preferredCurrency
                
            
            # Aggregate Customer Purchases to Gain Insight:
            dfAllSales = pd.DataFrame(
                data=[sale.toDict() for r in retailers.values() for sale in r._salesHistory])

            # Total Sales Count for each Retailer
            salesCount = {r.name: r.salesCount for r in retailers.values()}
            
            total_sales_count = sum(salesCount.values())
            
            marketShare = {r.name: (float(r.salesCount)/float(total_sales_count))
                           for r in retailers.values()}
            
            def retailerRevenue(r:Retailer):
                totalRevenue = sum([sale.item.cost.inCcy(
                    _preferredCurrency, throughBank=r.bank).amount for sale in r.salesHistory])
                # badTransactionsNotPaidToRetailer = [
                #     sale.transaction for sale in r.salesHistory if sale.transaction.accountTo.owner.id != r.id]
                # assert any(
                #     badTransactionsNotPaidToRetailer) == False, f'Some sales in the salesHistory of [r.name=\'{r.name}\'] have an accountTo on the sale that is not owned by the retailer; such as {badTransactionsNotPaidToRetailer[0]}'
                # totalRevenue = sum([sale.transaction.money for sale in r.salesHistory if sale.transaction.accountTo.owner.name == r.name])
                return totalRevenue
            
            def retailerRevenueForItem(r:Retailer, itemName:str='*'):
                totalRevenue = sum(
                    [sale.item.cost.inCcy(
                        _preferredCurrency, throughBank=r.bank).amount for sale in r.salesHistory
                     if (sale.item.name == itemName or itemName=='*')
                     ]
                    )
                return totalRevenue
            
            def retailerRevenueByItemName(r:Retailer):
                itemNames = list(set((sale.item.name for sale in r.salesHistory)))
                totalRevenueByItem = {itemName: retailerRevenueForItem(r,itemName) for itemName in itemNames}
                return totalRevenueByItem
            
            totalSalesRevenue = {
                r.name: retailerRevenue(r) for r in retailers.values()}
            
            totalSalesRevenueByItem = {
                r.name: retailerRevenueByItemName(r) for r in retailers.values()}
            
            # Total Vol. Green Points issued by each Retailer
            gpIssued = {r.name: sum(
                sale.greenPointsIssuedForItem.greenPoints.amount for sale in r._salesHistory) for r in retailers.values()}
            
            gpIssuedValueInPegged = {r.name: sum(
                sale.greenPointsIssuedForItem.greenPoints.valueInPeggedCurrency.amount for sale in r._salesHistory) for r in retailers.values()}

            totalSalesRevenueLessGP = {
                r.name: (totalSalesRevenue[r.name] - gpIssuedValueInPegged[r.name]) for r in retailers.values()}
            
            return GreenPointsLoyaltyApp.IterationResult(
                salesCount=pd.Series(salesCount),
                greenPointsIssued=pd.Series(gpIssued),
                marketShare=pd.Series(marketShare),
                totalSalesRevenue=pd.Series(totalSalesRevenue),
                # totalSalesRevenueByItem=pd.Series(totalSalesRevenueByItem),
                totalSalesRevenueLessGP=pd.Series(totalSalesRevenueLessGP),
                )
    
    
          
            
    class SimulationEnvironment:
        def __init__(self, simType:SimulationEnvType, initializer:GreenPointsLoyaltyApp.Initializer, simConfig:SimulationConfig|SimulationIterationConfig):
            self._initializer = initializer
            self.gpApp = initializer.gpApp
            self._simulationType = simType
            self._simConfig = simConfig
            self._simStamp = simulationId = SimStamp(
                str(uuid.uuid4()), time.time())
            
            self._out_df_template = pd.DataFrame(
                columns=self._initializer.retailerNames)

            self._retailers = self._retailersCreateCopy()
            self._customers = self._customersCreateCopy()
            
            # if controlRetailer is not None:
            #     if controlRetailer.name in self._retailers:
            #         self._controlRetailer = self._retailers[controlRetailer.name]
            #     else:
            #         logging.warning(f'Bad Control Retailer: attempted to apply control retailer to simulation environment with name: {controlRetailer}. We default to control retailer with name: {self._controlRetailer.name}')
            #         self._controlRetailer = list(self._retailers.values())[0]
            # else:
            #     self._controlRetailer = list(self._retailers.values())[0]
            
            self._bankEventNotifiers:list[Bank.BankEventNotifier]= []
            self.bankEventObserver = GreenPointsLoyaltyApp.BankEventObserver(gpApp=self.gpApp,simEnv=self)
            self._refreshBankEventNotifiers()
            
            
            self._df_strategized = initializer.df_strategized.copy(deep=True)
            self._initialised = True
            self.gpApp._initialised = True
            self.gpApp._emit_state_loaded()
            
            self.runningHistory:list[GreenPointsLoyaltyApp.IterationResultRunningAverage] = []
            self.numIterationsCalculated = 0
            
            self._retailerAdjustmentsQueue: queue.Queue = queue.Queue()
            
        @abc.abstractproperty
        def simulationType(self):
            return self._simulationType
        
        @property
        def simulationStamp(self):
            return self._simStamp
            
        @property
        def BASKET_FULL_SIZE(self):
            return self._simConfig.BASKET_FULL_SIZE
        @property
        def NUM_SHOP_TRIPS_PER_ITERATION(self):
            return self._simConfig.NUM_SHOP_TRIPS_PER_ITERATION
        @property
        def NUM_CUSTOMERS(self):
            return self._simConfig.NUM_CUSTOMERS
        @property
        def maxN(self):
            return self._simConfig.maxN if isinstance(self._simConfig,SimulationConfig) else 1
        @property
        def convergenceTH(self):
            return self._simConfig.convergenceTH if isinstance(self._simConfig,SimulationConfig) else 1.0
        @property
        def simulationConfig(self):
            return self._simConfig
            
        @property
        def banks_registered(self):
            retailer_banks = {r.bank.id: r.bank for r in self.retailers.values()}
            customer_banks = {
                r.bank.id: r.bank for r in self.customers if r.bank.id not in retailer_banks}
            return list({
                **retailer_banks,
                **customer_banks,
            }.values())
            
        @property
        def data(self):
            return {
                **self.entities,
                **self._simConfig.toJson()
            }

        @property
        def entities(self) -> dict[str, dict[str, TSTRUC_ALIAS]]:
            aggregatedBalance = sum(
                [r.balance for r in self.retailers.values()], start=BankAccountView.zero())
            return {
                'retailers': {rName: self.retailers[rName].toDictUI() for rName in self.retailers},
                'retailersCluster': {
                    "balance": aggregatedBalance.toDictUI(),
                    "balanceMoney": aggregatedBalance.combinedBalance.toDictUI(),
                    'salesHistory': [s.toDictUI() for r in self.retailers.values() for s in r.salesHistory],
                    'totalSales': sum((r.totalSales for r in self.retailers.values()), start=SalesAggregation.zero()).toDictUI()
                },
                'customers': {c.name: c.toDictUI() for c in self.customers}
            }

        @property
        def retailers(self):
            return self._retailers
        
        @property
        def retailerNames(self):
            return list(self._retailers.keys())

        @property
        def customers(self):
            return self._customers
        
        def reset_entities(self):
            self._retailers = self._retailersCreateCopy()
            self._customers = self._customersCreateCopy()
            self._refreshBankEventNotifiers()
            
        def _retailersCreateCopy(self):
            return {rname: rn.copyInstance(deepCopy=True) for rname, rn in self._initializer.retailers.items()}
        
        def _customersCreateCopy(self):
        #     return [rn.copyInstance(copyId=True) for rn in self._initializer.customers]
            # Declare Customers
            return [Customer(f'Customer[{i}]') for i in range(self.NUM_CUSTOMERS)]
        
            
        def _refreshBankEventNotifiers(self):
            for bank in self.banks_registered:
                if bank.bankEventNotifier not in self._bankEventNotifiers:
                    bank.bankEventNotifier.addObserver(self.bankEventObserver)
                    self._bankEventNotifiers.append(bank.bankEventNotifier)
            for notifier in self._bankEventNotifiers:
                if notifier.outer not in self.banks_registered:
                    notifier.deleteObserver(self.bankEventObserver)
        
        def _getEntity(self, entityId: str):
            retailer = next((r for r in self.retailers.values()
                            if r.id == entityId), None)
            if retailer:
                return retailer
            customer = next((r for r in self.customers if r.id == entityId), None)
            if customer:
                return customer

        def transactionsToEntity(self, entityId: str):
            entityMatch: Entity | None = next(
                (r for r in self.retailers.values() if r.id == entityId), None)
            if entityMatch is not None:
                return [t.toDictUI() for t in entityMatch.allTransactionsIn]
            entityMatch = next(
                (r for r in self.customers if r.id == entityId), None)
            if entityMatch is not None:
                return [t.toDictUI() for t in entityMatch.allTransactionsIn]
            return []

        def transactionsFromEntity(self, entityId: str):
            entityMatch: Entity | None = next(
                (r for r in self.retailers.values() if r.id == entityId), None)
            if entityMatch is not None:
                return [t.toDictUI() for t in entityMatch.allTransactionsOut]
            entityMatch = next(
                (r for r in self.customers if r.id == entityId), None)
            if entityMatch is not None:
                return [t.toDictUI() for t in entityMatch.allTransactionsOut]
            return []

        def salesForItem(self, itemName: str):
            return SerializableList([sale.toDictUI()
                                    for retailer in self.retailers
                                    for sale in self.retailers[retailer].salesHistory
                                    if sale.item.name.lower() == itemName.lower()
                                    ])
        
        def equalizeGreenPointIssuingVolumeForRetailers(self, setExpectedGPIssuedTo: int, debugShowDiff: bool = False):
            _old = None
            if debugShowDiff:
                _old = self._df_strategized.copy()
            # Get Expected Number Points per Retailer
            nItems = self._df_strategized.shape[0]
            self.expectedPoints = {r: (self._df_strategized[f'{r} GP'].astype(float).to_numpy()
                                       * self._df_strategized['Prob Customer Select']
                                       * (self.BASKET_FULL_SIZE/float(nItems))
                                       * self.NUM_SHOP_TRIPS_PER_ITERATION
                                       ).sum() for r in self.retailerNames}

            # Equalise Expected Number Points to 500
            _EXPECTED_POINTS = setExpectedGPIssuedTo  # 500.0
            for r in self.retailerNames:
                if self.expectedPoints[r] > 0:
                    self._df_strategized[f'{r} GP'] = self._df_strategized[f'{r} GP'] * \
                        (_EXPECTED_POINTS/self.expectedPoints[r])
            self._gpIssueingVolumeIsEqualisedBetweenRetailers = True

            # Record the effects of the normalisation transformation.
            self.expectedPointsUniformed = {r: (self._df_strategized[f'{r} GP'].astype(float).to_numpy()
                                                * self._df_strategized['Prob Customer Select']
                                                * (self.BASKET_FULL_SIZE/float(nItems))
                                                * self.NUM_SHOP_TRIPS_PER_ITERATION).sum() for r in self.retailerNames}
            if debugShowDiff:
                assert isinstance(_old, pd.DataFrame)
                logging.debug(pd_dataframe_explain_update(
                    _old, self._df_strategized))
            return self
            
        def _run_iteration(self, run_isolated_iteration: bool = False, iterationCounter: int | None = None, debug: bool = False):
            '''Run 1 iteration that simulates all customers doing AppConfig.NUM_SHOP_TRIPS_PER_ITERATION rounds of trips to the shops and selecting at most BASKET_FULL_SIZE items to purchase.
            
                Each iteration then returns an output of the current state of the customers and retailers post iteration.'''
            if run_isolated_iteration == True:
                assert iterationCounter is None, 'isolated iterations cannot be called as part of a simulation'
            self.reset_entities()
            retailersFixedForSimIteration = self._retailers
            retailerNames = list(retailersFixedForSimIteration.keys())
            
            # Run iteration of entire simulation
            for i in range(self.NUM_CUSTOMERS):
                customer = self._customers[i]
                df_shuffled = self._df_strategized.sample(frac=1).reset_index(drop=True)
                _ithRoundOfShopping = 0
                ithCustomerBasketSize = len(customer.basket)
                while ithCustomerBasketSize < self.BASKET_FULL_SIZE and \
                    _ithRoundOfShopping < self.NUM_SHOP_TRIPS_PER_ITERATION:
                    _ithRoundOfShopping += 1
                    if run_isolated_iteration:
                        #NOTE: Only allow update to retailer parameters in isolated iteration where we are simulating real life shoppping as opposed to trying to investigate convergence of a single set of parameters in a MC simulation.
                        #NOTE: Here we check if there has been a request to update the retailer strategies and apply the update if there has so that it is fixed for the iteration.
                        try:
                            updateRetailersCbTask = self._retailerAdjustmentsQueue.get(False) #non blocking
                            retailersFixedForSimIteration = updateRetailersCbTask()
                        except queue.Empty:
                            pass
                    for row_label, row in df_shuffled.iterrows():
                        try:
                            if Customer.choosesItem(pd.to_numeric(row['Prob Customer Select'])):
                                GPCols = row[[f'{r} GP' for r in retailerNames]]
                                MaxGPRetailer = list(retailersFixedForSimIteration.keys())[
                                    np.argmax(GPCols)]
                                customer\
                                    .buy(str(row['Item']))\
                                    .withCurrency(customer.accountForPayment(Money(0.0, str(row['Currency']))).fiatCurrency)\
                                    .forPrice(pd.to_numeric(row['Price']))\
                                    .withBaselineSustainabiltyRatingForItem(pd.to_numeric(row[f"{MaxGPRetailer} Relative Sustainability of Item Multiplier"]))\
                                    .fromRetailer(retailersFixedForSimIteration[MaxGPRetailer])\
                                    .withGreenPointRewards(pd.to_numeric(row[f'{MaxGPRetailer} GP']), retailer=MaxGPRetailer)\
                                    .withKGCo2(pd.to_numeric(row['KG Co2 / Unit']))\
                                    .usingAccount(bankAccount=customer.accountForPayment(Money(0.0, str(row['Currency']))))\
                                    .addToBasket()
                                self.gpApp._emit_customer_added_item_to_basket()
                                if len(customer.basket) >= self.BASKET_FULL_SIZE:
                                    customer\
                                        .checkout()
                                    self.gpApp._emit_customer_checked_out()
                                    if run_isolated_iteration:
                                        # Only allowed to insert delay for isolated_iteration
                                        # sleep for x:float seconds
                                        eventlet.sleep(round(self.gpApp.secondsBetweenPurchases))
                                    break
                        except Exception as e:
                            from colorama import Fore, Back, Style
                            # logging.debug(Fore.RED + 'some red text')
                            # logging.debug(Back.GREEN + 'and with a green background')
                            # logging.debug(Style.DIM + 'and in dim text')
                            # logging.debug(Style.RESET_ALL)
                            # logging.debug('back to normal now')
                            logging.debug(Fore.RED + Back.RESET +
                                  f'{GreenPointsLoyaltyApp.__name__}.{GreenPointsLoyaltyApp.SimulationEnvironment.__name__}._run_iteration errored in item purchase loop with exception: ' + 
                                  str(e))
                            import traceback
                            # import sys
                            traceback.print_exc()  # print_exception(*sys.exc_info(), limit, file)
                            logging.debug(e)
                            logging.debug(Style.RESET_ALL)
            debuggerHolder = 1
            return retailersFixedForSimIteration
        
        def summarise_isolated_iteration(self, retailersSnapshot:dict[str,Retailer], debug: bool = False):
            return GreenPointsLoyaltyApp.IterationResult.fromRetailers(
                retailers=retailersSnapshot,
            )
        
        def summarise_first_iteration(self, retailersSnapshot:dict[str,Retailer], maxNIterations:int, debug: bool = False):
            iterationResult = GreenPointsLoyaltyApp.IterationResult.fromRetailers(
                retailers=retailersSnapshot,   
            )
            return GreenPointsLoyaltyApp.IterationResultRunningAverage.\
                initialIteration(iterationResult=iterationResult,maxNIterations=maxNIterations)
             
        def summarise_subsequent_iteration(self,
                                            retailersSnapshot:dict[str,Retailer], 
                                            iterationCounter: int, 
                                            runningAverage: GreenPointsLoyaltyApp.IterationResultRunningAverage, 
                                            debug: bool = False):
            '''Summarize the end state of the retailers and customers from the simulation into a DataFrame of results'''

            assert iterationCounter >= 2, 'Iteration number must be >= 2 to calculate a running average'
            # gpIssuedByItem = {r:dfCustomers[dfCustomers['retailer']==r].groupby(['name'])['GP'].sum() for r in retailerNames}

            iterationResult = GreenPointsLoyaltyApp.IterationResult.fromRetailers(
                retailers=retailersSnapshot,
            )
            
            # self.gpApp._simulation_results.append(iterationResult)
            previousIterationNumber = iterationCounter - 1
            # if previousIterationNumber == 0:
            #     iterationRunningAverage = GreenPointsLoyaltyApp.IterationResultRunningAverage\
            #         .initialIteration(iterationResult=iterationResult)
            # else:    
            iterationRunningAverage = GreenPointsLoyaltyApp.IterationResultRunningAverage.appendResult(
                previousIterationNumber=previousIterationNumber,
                previous=runningAverage,
                result=iterationResult
                )
            # try:
            #     rname = next((r for r in self.retailers.keys() if r.lower().startswith('tesco')),next((r for r in self.retailers.keys())))
            #     logging.debug(Fore.YELLOW, iterationRunningAverage.runningAverage.salesCount[rname], Style.RESET_ALL)
            # except Exception as e:
            #     raise KeyError(e)
            return iterationRunningAverage
            
        def run_isolated_iteration(self, debug:bool=False):
            retailersFixedForSimIteration = self._run_iteration(run_isolated_iteration=True)
            sim_output = self._getSummaryDf(result=self.summarise_isolated_iteration(retailersSnapshot=retailersFixedForSimIteration, debug=debug), debug=debug).to_dict()
            self.gpApp._emit_event(event_name=WebSocketServerResponseEvent.simulation_ran,
                                   data=sim_output)
            return sim_output
            
        def run_simulation(self, betweenIterationCallback: Callable[[], None]):
            '''
            Run a Monte Carlo simulation with a maximum of N iterations & minimum of 2.
            @param: convergence_threshold:float stop the MC simulation once running variance of results drops below convergence_threshold.
            '''
            maxN = max(2,self.maxN)
            convergence_threshold = max(0.0, self.convergenceTH)
            self.numIterationsCalculated = 0
            
            #NOTE: Here we check if there has been a reques to update the retailer strategies and apply the update if there has so that it is fixed for the iteration.
            try:
                updateRetailersCbTask = self._retailerAdjustmentsQueue.get(
                    False)  # non blocking
                retailersFixedForSimIteration = updateRetailersCbTask()
            except queue.Empty:
                pass
            
            iterCounter = 1
            retailersFixedForSimIteration = self._run_iteration(run_isolated_iteration=False,
                                iterationCounter=iterCounter)
            runningAverage = self.summarise_first_iteration(retailersSnapshot=retailersFixedForSimIteration, maxNIterations=self.maxN, debug=False)
            self.numIterationsCalculated = iterCounter
            self.gpApp._emit_event(event_name=WebSocketServerResponseEvent.simulation_iteration_completed,
                                   data={**self.simulationConfig.toJson(), **runningAverage.toJson()})
            betweenIterationCallback()
            convergence_TH_not_reached = True
            while iterCounter < maxN and convergence_TH_not_reached:
                iterCounter = iterCounter + 1
                retailersFixedForSimIteration = self._run_iteration(run_isolated_iteration=False, iterationCounter=iterCounter)
                runningAverage = self.summarise_subsequent_iteration(retailersSnapshot=retailersFixedForSimIteration, 
                                                                     iterationCounter=iterCounter, 
                                                                     runningAverage=runningAverage, 
                                                                     debug=False)
                betweenIterationCallback()
                
                self.runningHistory.append(runningAverage)
                if iterCounter > 1 and \
                    (runningAverage.runningVariance.salesCount.max(axis=0) < convergence_threshold and
                    runningAverage.runningVariance.greenPointsIssued.max(axis=0) < convergence_threshold):
                        convergence_TH_not_reached = False
                else:
                    maxSalesCountRunningVar = runningAverage.runningVariance.salesCount.max(axis=0)
                    maxGPIssuedRunningVar = runningAverage.runningVariance.greenPointsIssued.max(
                        axis=0)
                    logging.debug(f'Running Variance for Sim: iter[{iterCounter}] ; SalesCount:{maxSalesCountRunningVar}; GPIssues:{maxGPIssuedRunningVar}')
                self.numIterationsCalculated = iterCounter
                self.gpApp._emit_event(event_name=WebSocketServerResponseEvent.simulation_iteration_completed,
                                       data={**self.simulationConfig.toJson(), **runningAverage.toJson()})
                # eventlet.sleep(5.0)
            sim_output = self.summarise_simulation_to_dict()
            self.gpApp._emit_event(event_name=WebSocketServerResponseEvent.simulation_ran,
                                   data=sim_output)
            return sim_output
            
        def summarise_simulation_to_df(self, debug:bool=False):
            '''
            Summary DF containing a salesCount row & GP Issued row
            ---
            Columns are indexed by retailer and contain the salesCounts/GP of the final runningAverage of all iterations
            '''
            finalRunningAverage = self.runningHistory[-1].runningAverage
            return self._getSummaryDf(result=finalRunningAverage, debug=debug)
            
        def summarise_simulation_to_dict(self, forRetailer:str|None=None, debug:bool=False):
            '''
            Summary DF containing a [GemberMeasureType.salesCount] row & [GemberMeasureType.GP_Issued] row
            ---
            Columns are indexed by measure and rows are indexed by retailer name. 
            The values contain the final runningAverage of all iterations.
            '''
            finalRunningAverage = self.runningHistory[-1].runningAverage
            if forRetailer is not None:
                if forRetailer in finalRunningAverage.toDataFrame().index.values:
                    finalRunningAverageDict = finalRunningAverage.toDataFrame(
                    ).loc[forRetailer].to_dict()
                    return finalRunningAverageDict
                elif forRetailer not in self.retailerNames:
                    raise Exception('Bad Simulation result as does not contain the full list of retailers')
                else:
                    raise Exception('Bad forRetailer passed to SimulationEnvironment.summarise_simulation_to_dict()')
            else:
                return {
                    'simulation_id': self.simulationStamp.id,
                    'started_at': self.simulationStamp.timestamp,
                    **finalRunningAverage.toDict(),
                }
        
        def _getSummaryDf(self, result:GreenPointsLoyaltyApp.IterationResult, debug:bool=False):
            out_df = self._out_df_template.copy()
            out_df.loc[GemberMeasureType.sales_count.value] = result.salesCount
            out_df.loc[GemberMeasureType.GP_Issued.value] = result.greenPointsIssued
            out_df.loc[GemberMeasureType.market_share.value] = result.marketShare
            out_df.loc[GemberMeasureType.total_sales_revenue.value] = result.totalSalesRevenue
            out_df.loc[GemberMeasureType.total_sales_revenue_by_item.value] = result.totalSalesRevenueByItem
            out_df.loc[GemberMeasureType.total_sales_revenue_less_gp.value] = result.totalSalesRevenueLessGP

            if debug:
                logging.debug(out_df)
            
            return out_df
        
        def isFullEnv(self) -> TypeGuard[GreenPointsLoyaltyApp.SimulationFullEnvironment]:
            return isinstance(self,GreenPointsLoyaltyApp.SimulationFullEnvironment)
        
        def isScenarioRunEnv(self) -> TypeGuard[GreenPointsLoyaltyApp.SimulationScenarioEnvironment]:
            return isinstance(self,GreenPointsLoyaltyApp.SimulationFullEnvironment)
        
        def isSingleIterationEnv(self) -> TypeGuard[GreenPointsLoyaltyApp.SimulationSingleIterationEnvironment]:
            return isinstance(self,GreenPointsLoyaltyApp.SimulationFullEnvironment)

    class SimulationFullEnvironment(SimulationEnvironment):
        def __init__(self, initializer: GreenPointsLoyaltyApp.Initializer, simConfig: SimulationConfig):
            super().__init__(simType=self.simulationType,
                             initializer=initializer, simConfig=simConfig)
            
        @property
        def simulationType(self):
            return SimulationEnvType.Full
    
    class SimulationScenarioEnvironment(SimulationEnvironment):
        def __init__(self, initializer:GreenPointsLoyaltyApp.Initializer, simConfig:SimulationConfig|SimulationIterationConfig):
            super().__init__(simType=self.simulationType,
                             initializer=initializer, simConfig=simConfig)

        @property
        def simulationType(self):
            return SimulationEnvType.Scenario
        
        def queueStrategyUpdateForOneRetailer(self, controlRetailer: ControlRetailer):
            '''Queue the update and depending on the type of simulation being run, this update will be applied at the next iteration of the simulation.'''
            self._retailerAdjustmentsQueue.put(lambda: self.adjustStrategyForOneRetailerNonBlock(
                controlRetailer=controlRetailer))
            return self
            
        def adjustStrategyForOneRetailerNonBlock(self, controlRetailer:ControlRetailer):
            retailers = self._retailers
            
            retailer = retailers[controlRetailer.name]
            # retailer.strategy = GPStrategyMultiplier.COMPETITIVE
            # retailer.sustainability = RetailerSustainabilityIntercept.LOW

            # Assign Strategy to Retailer
            retailer.strategy = controlRetailer.strategy
            retailer.sustainability = controlRetailer.sustainability
            
            logging.debug(Fore.RED + Back.LIGHTMAGENTA_EX + 'Emit the retailer asjustment DONE to clients' + Style.RESET_ALL)
            self.gpApp._emit_event(WebSocketServerResponseEvent.retailer_strategy_changed, {'data': {'name': controlRetailer.name,'stategy': controlRetailer.strategy.value}})
            self.gpApp._emit_event(WebSocketServerResponseEvent.retailer_sustainbility_changed, {
                                   'data': {'name': controlRetailer.name, 'sustainability': controlRetailer.sustainability.value}})
            
            #TODO: Check that client updates correctly.
            return retailers
    
    class SimulationSingleIterationEnvironment(SimulationEnvironment):
        def __init__(self, initializer:GreenPointsLoyaltyApp.Initializer, simConfig:SimulationConfig|SimulationIterationConfig):
            super().__init__(simType=self.simulationType, initializer=initializer,simConfig=simConfig)

        @property
        def simulationType(self):
            return SimulationEnvType.SingleIteration
    
    def initialised(self):
        return self._initialised

    @property
    def running(self):
        return self._running == True
    
    def initSimulationFullEnvironment(self, simConfig:SimulationConfig):
        
        simEnv = self._envInitializer.createSimulationFullEnvironment(simConfigParams=simConfig)
        simulationId = simEnv.simulationStamp
        self._simulationEnvironments[simulationId.id] = \
            (simulationId.timestamp, simEnv)
        return simulationId.id, self._simulationEnvironments[simulationId.id][1].simulationType
    
    def getSimulationDummyEnvironment(self):
        return self._envInitializer.createSimulationSingleIterationEnvironment(simConfigParams=SimulationIterationConfig())
        
    def initSimulationSingleIterationEnvironment(self, simConfig:SimulationIterationConfig):
        
        simEnv = self._envInitializer.createSimulationSingleIterationEnvironment(simConfigParams=simConfig)
        simulationId = simEnv.simulationStamp
        self._simulationEnvironments[simulationId.id] = \
            (simulationId.timestamp, 
             simEnv)
        return simulationId.id, self._simulationEnvironments[simulationId.id][1].simulationType
    
    def initSimulationScenarioRunEnvironment(self, simConfig: SimulationIterationConfig):
        
        simEnv = self._envInitializer.createSimulationScenarioRunEnvironment(
            simConfigParams=simConfig)
        simulationId = simEnv.simulationStamp
        self._simulationEnvironments[simulationId.id] = \
            (simulationId.timestamp, 
             simEnv)
        return simulationId.id, self._simulationEnvironments[simulationId.id][1].simulationType
    
    def getSimConfig(self, simulationId:str):
        simEnv = self.getSimulationEnvironment(simulationId=simulationId)
        
        if simEnv is not None:
            return simEnv.simulationConfig
        else:
            return None
    
    def adjustSimParameters(self,
                            simulationId:str,
                            controlRetailer: ControlRetailer,
                            blocking:bool=False):
        simEnv = self.getSimulationEnvironment(simulationId=simulationId)
        
        if simEnv is not None and isinstance(simEnv,GreenPointsLoyaltyApp.SimulationScenarioEnvironment):
            if not blocking:
                simEnv.queueStrategyUpdateForOneRetailer(controlRetailer=controlRetailer)
            else:
                simEnv.adjustStrategyForOneRetailerNonBlock(controlRetailer=controlRetailer)
            return True
        else:
            return False
            
    
    def getSimulationEnvironment(self, simulationId:str, throw:bool=False):
        if simulationId in self._simulationEnvironments.keys():
            return self._simulationEnvironments[simulationId][1]
        
        if throw:
            raise KeyError(
                f'Bad SimulationID passed. No Active Simulation Environment is registered to {simulationId}')
        return None
    
    def getSimulationEnvironmentUnsafe(self, simulationId:str):
        res = self.getSimulationEnvironment(simulationId=simulationId,throw=True)
        assert res is not None, 'Simulation Envirnment can\'t be None when fetched with throw=True'
        return res
        
        
    
    def run_full_simulation(self, simulationId: str, betweenIterationCallback: Callable[[],None]):
        
        if simulationId not in self._simulationEnvironments.keys():
            raise KeyError(f'Bad SimulationID passed. No Active Simulation Environment is registered to {simulationId}')
        try:
            if not self.initialised:
                self.initAppEnv()
            # assert self.active_simulation_environment is not None, 'Must init a new simulation before starting the app'
            self._running = True
            active_simulation_environment = self._simulationEnvironments[simulationId][1]
            resultDf = active_simulation_environment.run_simulation(
                betweenIterationCallback=betweenIterationCallback)
            self._simsRun += 1
            self._running = False
            self._simulationEnvironments.pop(simulationId)
            return resultDf
        except Exception as e:
            logging.debug(e)
            raise e
    
    def run_isolated_iteration(self, simulationId:str):
    
        if simulationId not in self._simulationEnvironments.keys():
            raise KeyError(f'Bad SimulationID passed. No Active Simulation Environment is registered to {simulationId}')
        try:
            if not self.initialised:
                self.initAppEnv()
            # assert self.active_simulation_environment is not None, 'Must init a new simulation before starting the app'
            self._running = True
            active_simulation_environment = self._simulationEnvironments[simulationId][1]
            
            resultDf = active_simulation_environment\
                .run_isolated_iteration()
            self._simsRun += 1
            
            self._running = False
            return resultDf, active_simulation_environment
        except Exception as e:
            logging.debug(e)
            raise e
        
    def initTestSimulation(self):
        self.initAppEnv()
        return None
    
    def start_isolated_iteration(self, simulationId:str):
        if self.initialised:
            (resultDict, simEnv) = self.run_isolated_iteration(simulationId=simulationId)
            return (resultDict, simEnv)
        return (None,None)
        
    def reset(self):
        self._df_strategized = None
        return
    
    @property
    def simulation_results(self):
        return [l.copy() for l in self._simulation_results]
    
    @property
    def latest_simulation_result(self):
        return self._simulation_results[-1].copy() if self._simsRun > 0 else pd.DataFrame()
    
    @property
    def simulationsRun(self):
        return self._simsRun

    def _emit_state_loaded(self):
        '''Emit: state_loaded'''
        self._emit_event(WebSocketServerResponseEvent.app_state_loaded)
        
    def _emit_customer_checked_out(self):
        self._emit_event(WebSocketServerResponseEvent.customer_checked_out)
    
    def _emit_customer_added_item_to_basket(self):
        self._emit_event(WebSocketServerResponseEvent.customer_added_item_to_basket)
    
    def _emit_event(self, event_name: WebSocketServerResponseEvent, *args, **kwargs):
        if isinstance(self.websocket,WebSocketsStack) and self.websocket.webSocketOpen:
            if 'data' in kwargs:
                data = kwargs['data']
                self.websocket.broadcast(event_name, data)
                logging.debug(Fore.YELLOW + Style.DIM + f'{GreenPointsLoyaltyApp.__name__} emitted event: {event_name}')
                # logging.debug(Fore.YELLOW + Style.DIM + f'{type(self).__name__}.websocket[{type(self.websocket).__name__}] emitted event: {event_name}' + Style.RESET_ALL)
            else:
                self.websocket.broadcast(event_name, 'empty')
                    

    

    class AppStream(Observable):
        def __init__(self, outer: GreenPointsLoyaltyApp):
            super().__init__()
            self._outer = outer

        def notifyListeners(self, **kwargs: dict):
            self.setChanged()
            super().notifyObservers(**kwargs)

        @property
        def outer(self):
            return self._outer




