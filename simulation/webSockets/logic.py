
import logging
from app_globals import GreenPointsLoyaltyApp 


def process_connection_success(data):
    if GreenPointsLoyaltyApp.debug:
        logging.debug(f'Client WSS message for event: {data}')
    
def handle_message(gpApp:GreenPointsLoyaltyApp, message:str):
    if GreenPointsLoyaltyApp.debug:
        logging.debug(
            f'Client: [{message}], Server: [Message recieved, Simulations run: ({gpApp.simulationsRun})]')
    
def init_new_simulation(gpApp:GreenPointsLoyaltyApp):
    if gpApp.initialised == False:
        gpApp.initTestSimulation()
        return None
        
def start_isolated_simulation(gpApp:GreenPointsLoyaltyApp, simulationId:str):
    if gpApp.running == False:
        outputJson, simEnv = gpApp.run_isolated_iteration(simulationId=simulationId)
        return outputJson
    else:
        return None
    