import intent_logic.intent_matcher
from DB import orders_data_access
from utils.item_processing_utils import *
from DB.items_data_access import *
# message = 'תראי לי את כל ההזמנות'
# best_intent = intent_logic.intent_matcher.detect_intent(message)
# print(best_intent)

def main():
    # items = [{"item_name": "קרטון לארג גדול", "quantity": 2}, {"item_name": "קרטון סמול קטן", "quantity": 2}]
    # # print(orders_data_access.map_item_names_to_ids(items))
    # print(orders_data_access.find_upsells(items, 1))
    result = map_item_names_to_ids([{"item_name": "חמוצים", "quantity": "1"}])
    print(result)

if __name__ == "__main__":
    main()
