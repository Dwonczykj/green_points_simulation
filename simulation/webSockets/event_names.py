from enum import Enum
from typing import Any

class MySocketIONamespaces(Enum):
    global_namespace = '/'
    transactions = '/transactions'
    simulation = '/simulation'
    
class WebSocketClientEvent(Enum):
    connection_success_event = 'connection success event'
    message = 'message'
    start_new_simulation = 'start new simulation'
    start_isolated_simulation = 'start isolated simulation'
    get_purchase_delay = 'get purchase delay'
    change_purchase_delay = 'change purchase delay'
    change_retailer_strategy = 'change retailer strategy'
    change_retailer_sustainability_multiplier = 'change retailer sustainability multiplier'
    change_customer_stickyness_factor = 'change customer stickyness factor'
    num_customers_requested = 'num customers requested'
    basket_full_size_requested = 'basket full size requested'
    num_shop_trips_requested = 'num shop trips requested'
    
    def __eq__(self, o:Any):
        if isinstance(o,type(self)):
            return self.value == o.value
        elif isinstance(o,str):
            return self.value == o
        return False
    

class WebSocketServerResponseEvent(Enum):
    gpApp_initialised = 'gpApp initialised'
    
    simulation_initialised = 'simulation initialised'
    simulation_iteration_completed = 'simulation iteration completed'
    simulation_ran = 'simulation ran'
    simulation_already_running = 'simulation already running'
    
    unknown_client_event_response = 'unknown client event response'
    
    message_received = 'message received'
    
    purchase_delay = 'purchase delay'
    
    app_state_loaded = 'app state loaded'
    
    entity_updated = 'entity updated'
        
    bank_transaction_created = 'bank transaction created'
    bank_transaction_completed = 'bank transaction completed'
    bank_transaction_failed = 'bank transaction failed'
    bank_account_added = 'bank account added'
    
    crypto_transfer_requested = 'crypto transfer requested'
    crypto_transfer_completed = 'crypto transfer completed'
    
    customer_checked_out = 'customer checked out'
    customer_added_item_to_basket = 'customer added item to basket'
    
    retailer_strategy_changed = 'retailer strategy changed'
    retailer_sustainbility_changed = 'retailer sustainbility changed'
    
    num_customers_requested = 'num customers requested'
    basket_full_size_requested = 'basket full size requested'
    num_shop_trips_requested = 'num shop trips requested'
    
    def __eq__(self, o: Any):
        if isinstance(o, type(self)):
            return self.value == o.value
        elif isinstance(o, str):
            return self.value == o
        return False
