import pandas as pd
from typing import Any, Callable
import numpy as np
import random
import logging

def pd_dataframe_explain_update(df_old: pd.DataFrame, df_new: pd.DataFrame):
    assert all((c in df_new.columns for c in df_old.columns)
               ), 'all columns in df_old must be present in df_new'
    assert df_old.index.values == df_new.index.values, 'df_old must have same index as df_new'

    def show_diff(val_old: Any, val_new: Any, formatter: Callable[[Any], str]|None = None):
        if val_old == val_new:
            return val_new
        elif formatter is not None:
            return f'{formatter(val_old)} -> {formatter(val_new)}'
        else:
            return f'{val_old} -> {val_new}'

    return pd.DataFrame(data={
        column: [show_diff(val_old, val_new) for (val_old, val_new) in list(
            zip(df_old[column].values, df_new[column].values))]
        for column in df_old.columns
    })


def simulateData(num_items: int = 15, num_retailers: int = 4):
    _itemNames = [f'Item{i+1}' for i in range(num_items)]
    _retailerNames = [f'Retailer{i+1}' for i in range(num_retailers)]
    _binarySells = {f'{rn} Sells': np.array(
        [1 for i in range(num_items)]) for rn in _retailerNames}
    # TODO LATER: Add ability to randomise:
    _impacts = np.array([1.5 for i in range(num_items)])
    _divisorFactorGP = 20.0
    df = pd.DataFrame(data={
        'Item': _itemNames,
        **_binarySells,
        "KG Co2 / Unit": _impacts,
        # TODO LATER: Add ability to randomise:
        'Price': [1.00 for i in range(num_items)],
        'Currency': ['GBP' for i in range(num_items)],
        **{f'{rn} Relative Sustainability of Item Multiplier': [random.normalvariate(0.5, (3.0/_divisorFactorGP)) for i in range(num_items)] for rn in _retailerNames},
        **{f'{rn} GP': (_binarySells[f'{rn} Sells']/_impacts*_divisorFactorGP) for rn in _retailerNames},
        # TODO LATER: Add ability to randomise:
        'Prob Customer Select': [0.2 for i in range(num_items)]
    })
    return df

def get_dataset(use_local_csv:bool=True):
    '''Get the data set of items for each retailer with Green points assigned, prices assigned etc...
    
        use_local_csv if true will use the local ./greenPointsSimulation.csv to populate the DataFrame, otherwise we simulate a load of items named Item1 to ItemN'''

    if use_local_csv:
        #FIXED: https://github.com/Dwonczykj/gember-points/issues/2 -> Cannot read a csv on the same thread that creates the socket server...
        df: pd.DataFrame = pd.read_csv(
            './GreenPointsSimulation.csv', iterator=False)  # type: ignore
        # assert isinstance(df,pd.DataFrame)
        logging.debug(f'Dataset {type(df)}: Used ->')
        logging.debug(df.head())
    else:
        df = simulateData()
        # logging.debug('Simulated Dataset: Not used ->')
        # logging.debug(df.head())
    return df


