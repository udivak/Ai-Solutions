import intent_logic.intent_matcher
from DB import data_access

message = 'תראי לי את כל ההזמנות'
best_intent = intent_logic.intent_matcher.detect_intent(message)
print(best_intent)

def main():
    item = { "item_name": "טרופיות", "quantity": 2 }
    print(data_access.map_item_names_to_ids([item]))



if __name__ == "__main__":
    main()