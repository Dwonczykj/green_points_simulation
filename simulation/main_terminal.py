import logging
import os
import uuid
from enum import Enum
from functools import wraps
from typing import Any, Callable, Generic, Tuple, Type, TypeAlias, TypeVar

import cachetools
import matplotlib.pyplot as plt
import numpy as np
from app_config import SimulationConfig, SimulationIterationConfig
from app_globals import flaskHttpAppConfig as appConfig
from app_globals import gpApp
from dotenv import load_dotenv
from event_names import WebSocketClientEvent, WebSocketServerResponseEvent
from Observer import Observable, Observer

from Bank import (ControlRetailer, InvalidRetailerReason,
                  RetailerStrategyGPMultiplier,
                  RetailerSustainabilityIntercept)
from GreenPointsSimulation import GreenPointsLoyaltyApp

load_dotenv()

# ----- Script Globals -----------------------------

FOCUS_METRIC = 'totalSalesRevenueLessGP'
def get_focus_metric(x:GreenPointsLoyaltyApp.IterationResult):
    '''the metric to focus on'''
    # return x.salesCount
    # return x.marketShare
    # return x.totalSalesRevenue
    return x.totalSalesRevenueLessGP
    # return x.greenPointsIssued

BASKET_FULL_SIZE = 3
NUM_SHOP_TRIPS_PER_ITERATION = 2
NUM_CUSTOMERS = 4
maxN = 10
convergenceTH = 1
controlRetailerName = 'Tescos'
strategy = RetailerStrategyGPMultiplier.MAX
sustainabilityBaseline = RetailerSustainabilityIntercept.HIGH


# ----- Matplotlib setup Figure -----------------------------




simulation_cache:dict[str,dict[str,list[Tuple[float,float]]]] = {} # store by simulation config_str, <metric is implicity from the one being focused on for this run of the script>, then by retailer

    
# ----- Observer pattern -----------------------------

# class GPAppTerminalObserver(Observer):
#     def __init__(self) -> None:
#         super().__init__()
        
#     def update(self, observable:Observable, **kwargs:Any):
#         '''App has emitted an event, get the event name and the data from the kwargs and use them to update our matplots etc
        
#         the data returned in simulation_iteration_completed (kwargs['data']) has shape:
#             - {
#                 'BASKET_FULL_SIZE': self.BASKET_FULL_SIZE,
#                 'NUM_SHOP_TRIPS_PER_ITERATION': self.NUM_SHOP_TRIPS_PER_ITERATION,
#                 'NUM_CUSTOMERS': self.NUM_CUSTOMERS,
#                 'strategy': self.strategy.value,
#                 'sustainability': self.sustainabilityBaseline.value,
#                 'controlRetailerName': self.controlRetailerName,
#                 'maxN': self.maxN,
#                 'convergenceTH': self.convergenceTH,
#                 'iteration_number': self.iterationNumber,
#                 'maxNIterations': self.maxNIterations,
#                 'running_sum': self.runningSum.toDict(),
#                 'running_average': self.runningAverage.toDict(),
#                 'running_variance': self.runningVariance.toDict()
#             }
#         '''
#         eventName:WebSocketServerResponseEvent = kwargs['event_name']
#         data:Any = kwargs['data']
        
#         if eventName == WebSocketServerResponseEvent.simulation_iteration_completed:
#             simConfig = SimulationConfig()
#             simConfig.loadFromDict(data)
#             simData = GreenPointsLoyaltyApp.IterationResultRunningAverage(
#                 iterationNumber=data['iteration_number'],
#                 maxNIterations=data['maxNIterations'],
#                 runningSum=GreenPointsLoyaltyApp.IterationResult.fromDict(data['running_sum']),
#                 runningAverage=GreenPointsLoyaltyApp.IterationResult.fromDict(data['running_average']),
#                 runningVariance=GreenPointsLoyaltyApp.IterationResult.fromDict(data['running_variance']),
#             )
#             if str(simConfig) not in simulation_cache:
#                 simulation_cache[str(simConfig)] = {}
#             latest:dict[str,float] = get_focus_metric(simData.runningAverage).to_dict()
#             _d = simulation_cache[str(simConfig)]
#             for retailer,value in latest.items():
#                 if retailer not in _d:
#                     _d[retailer] = []
#                 _d[retailer].append((simData.iterationNumber,value))
                    
                
#             xs = np.arange(start=1,stop=simData.iterationNumber,step=1)
#             # TODO: add individual lines for each retailer rather than merging into one array, if was one array, would need to repeat the xs for the number of times of retailers there are.
#             # ! We could use plt.fill_between(x, y1, y2) to show the variance bounds around the running_average
#             # ax.clear()
#             for retailer, values in simulation_cache[str(simConfig)].items():
#                 _xs, _ys = zip(*values)
#                 ax.plot(_xs, _ys, label=retailer)
#             fig.canvas.draw_idle()
#             fig.canvas.flush_events()
            
#         else:
#             pass
        

# # register event handlers to the gpapp event emitter:
# gpAppObserver = GPAppTerminalObserver() 
# gpApp.observableAppEndPoint.addObserver(gpAppObserver)


# ----- Script logic -----------------------------

def ignore_pass():
    '''write updates to live_simulation to the matplotlib stream'''
    # 
    pass

def plot_sim_result(simResult:list[GreenPointsLoyaltyApp.IterationResultRunningAverage]):
    '''Pull simulation history from the current simulation environment and plot the lines.'''
    retailers = list(set([str(r) for iterResult in simResult for r in get_focus_metric(iterResult.runningAverage).index]))
    d:dict[str,list[Tuple[int,float]]] = {}
    _xs = []
    logging.info(retailers)
    for r in retailers:
        d[r] = [(iterResult.iterationNumber,get_focus_metric(iterResult.runningAverage)[r])
                for iterResult in simResult]
        
    fig = plt.figure(figsize=(11.69, 8.27))
    ax: plt.Axes = fig.gca()
    
    for r in d:
        lt = d[r]
        _xs, _ys = zip(*(lt))
        _xs = list(_xs)
        _ys = list(_ys)
        ax.plot(_xs, _ys, label=r)
        strys = ','.join([str(y) for y in _ys])
        logging.info(f'Plot for {r} xs:[{min(_xs)}->{max(_xs)}] ys:[{strys}]')
    
    fig.canvas.draw_idle()
    fig.canvas.flush_events()
    
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(FOCUS_METRIC)
    ax.set_ylabel('iteration')
    ax.set_title(f'{FOCUS_METRIC} by retailer')
    
    ax.legend()

    fig.tight_layout()
    
    
    return d


def run_simulation():
    '''Initialise a new single iteration simulation environment and start it.
        --
        Required query params: 
            - simulation configuration params
        '''
    gpApp.initAppEnv()
    
    
    simConfig = SimulationConfig.createFromDict({
            'BASKET_FULL_SIZE': BASKET_FULL_SIZE,
            'NUM_SHOP_TRIPS_PER_ITERATION': NUM_SHOP_TRIPS_PER_ITERATION,
            'NUM_CUSTOMERS': NUM_CUSTOMERS,
            'strategy': strategy.value,
            'sustainability': sustainabilityBaseline.value,
            'controlRetailerName': controlRetailerName,
            'maxN': maxN,
            'convergenceTH': convergenceTH,
        })

    simId, simType = gpApp.initSimulationFullEnvironment(
        simConfig=simConfig,
    )

    simEnv = gpApp.getSimulationEnvironmentUnsafe(simulationId=simId)
    simData = simEnv.data

    
    gpApp.run_full_simulation(
        simulationId=simId, 
        betweenIterationCallback=ignore_pass, 
        )
    
    running_history = simEnv.runningHistory
    
    plot_sim_result(simResult=running_history)
    
    plt.show()
    
    
if __name__ == '__main__':
    
    run_simulation()
    
    # gpApp.observableAppEndPoint.deleteObserver(gpAppObserver)
        
