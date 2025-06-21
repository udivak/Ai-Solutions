import intent_logic.intent_matcher
from DB import data_access

# message = 'תראי לי את כל ההזמנות'
# best_intent = intent_logic.intent_matcher.detect_intent(message)
# print(best_intent)

def main():
    items = [{ "item_name": "קרטון לארג גדול", "quantity": 2 }, { "item_name": "קרטון סמול קטן", "quantity": 2 }]
    # print(data_access.map_item_names_to_ids(items))
    print(data_access.find_upsells(items, 1))


if __name__ == "__main__":
    main()