

from datetime import datetime
import json
from app_globals import gpApp as appInstance


if __name__ == '__main__':
    
    (outputDf, simEnv) = appInstance.start_isolated_iteration()
    if simEnv is not None:
        ds = datetime.strftime(datetime.now(), '%Y%m%d_%H%M')
        if input('Create output files for testing: y/n?') == 'y':
            with open(f'output_entities_{ds}.json', 'w') as f:
                json.dump(simEnv.entities, f, indent=4,
                        separators=(',', ': '), sort_keys=False)
            item_name_example = 'Chicken'
            with open(f'output_sales_for_item_{item_name_example.lower()}_{ds}.json', 'w') as f:
                json.dump(simEnv.salesForItem(item_name_example), f, indent=4,
                        separators=(',', ': '), sort_keys=False)
            example_entity = simEnv.entities['retailers']['Tescos']
            assert isinstance(example_entity, dict)
            with open(f'output_transactions_from_entity_tescos_{ds}.json', 'w') as f:
                json.dump(simEnv.transactionsFromEntity(str(example_entity['id'])), f, indent=4,
                        separators=(',', ': '), sort_keys=False)
            with open(f'output_transactions_to_entity_tescos_{ds}.json', 'w') as f:
                json.dump(simEnv.transactionsToEntity(str(example_entity['id'])), f, indent=4,
                        separators=(',', ': '), sort_keys=False)
    else:
        pass


pass