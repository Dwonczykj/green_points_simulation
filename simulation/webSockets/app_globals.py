
from GreenPointsSimulation import GreenPointsLoyaltyApp
from app_config import flaskHttpAppConfig
from socketio_init import socketio

import pandas as pd
import os
pardir = os.path.basename(os.getcwd())
if os.path.basename(os.getcwd()) == 'simulation':
    pardir = ''
elif os.path.basename(os.getcwd()) == 'GreenPoint':
    pardir = '/simulation'
else:
    cwd = os.getcwd()
    raise Exception(f'{cwd} should be simulation /Users/joeyd/Documents/JoeyDCareer/GitHub/Gember/GreenPoint/simulation')
df = pd.read_csv(f'.{pardir}/GreenPointsSimulation.csv', iterator=False)
gpApp = GreenPointsLoyaltyApp.getInstance(
    data=df,
    socketio=socketio,
    debug=flaskHttpAppConfig['DEBUG_APP'])

if flaskHttpAppConfig.get('APP_LAZY_LOAD',True) == False:
    '''Dont wait for someone to call /init route, load GPAppEnvironment on server start:'''
    gpApp.initAppEnv()
