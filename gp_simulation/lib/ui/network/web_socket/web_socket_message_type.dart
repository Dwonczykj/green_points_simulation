class WebSocketClientEvent {
  static String get connection_success_event => 'connection success event';
  static String get message => 'message';
  static String get start_new_simulation => 'start new simulation';
  static String get get_purchase_delay => 'get purchase delay';
  static String get change_purchase_delay => 'change purchase delay';
  static String get change_retailer_strategy => 'change retailer strategy';
  static String get change_retailer_sustainability_multiplier =>
      'change retailer sustainability multiplier';
  static String get change_customer_stickyness_factor =>
      'change customer stickyness factor';

  static List<String> get all_members => <String>[
        connection_success_event,
        message,
        start_new_simulation,
        get_purchase_delay,
        change_purchase_delay,
        change_retailer_strategy,
        change_retailer_sustainability_multiplier,
        change_customer_stickyness_factor,
      ];
}

class WebSocketServerResponseEvent {
  static String get simulation_initialised => 'simulation initialised';
  static String get simulation_iteration_completed =>
      'simulation iteration completed';
  static String get simulation_ran => 'simulation ran';
  static String get simulation_already_running => 'simulation already running';
  static String get unknown_client_event_response =>
      'unknown client event response';
  static String get message => 'message';
  static String get message_received => 'message received';
  static String get purchase_delay => 'purchase delay';

  static String get app_state_loaded => 'app state loaded';

  static String get entity_updated => 'entity updated';

  static String get bank_transaction_created => 'bank transaction created';
  static String get bank_transaction_completed => 'bank transaction completed';
  static String get bank_transaction_failed => 'bank transaction failed';
  static String get bank_account_added => 'bank account added';

  static String get crypto_transfer_requested => 'crypto transfer requested';
  static String get crypto_transfer_completed => 'crypto transfer completed';

  static String get customer_checked_out => 'customer checked out';
  static String get customer_added_item_to_basket =>
      'customer added item to basket';

  static String get retailer_strategy_changed => 'retailer strategy changed';
  static String get retailer_sustainbility_changed =>
      'retailer sustainbility changed';

  static String get pong => 'pong';
      

  static List<String> get all_members => <String>[
        simulation_initialised,
        simulation_ran,
        simulation_already_running,
        unknown_client_event_response,
        message_received,
        purchase_delay,
        app_state_loaded,
        entity_updated,
        bank_transaction_created,
        bank_transaction_completed,
        bank_transaction_failed,
        bank_account_added,
        crypto_transfer_requested,
        crypto_transfer_completed,
        customer_checked_out,
        customer_added_item_to_basket,
        retailer_strategy_changed,
        retailer_sustainbility_changed,
        pong,
      ];
}
