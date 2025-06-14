import intent_logic.intent_matcher


message = 'תראי לי את כל ההזמנות'
best_intent = intent_logic.intent_matcher.detect_intent(message)
print(best_intent)