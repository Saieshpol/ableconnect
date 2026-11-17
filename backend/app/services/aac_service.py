import re
from typing import List, Dict, Any

class AACService:
    """
    Handles natural AAC sentence construction, grammar smoothing,
    and speech phrase formatting for student picture communication cards.
    """

    PRONOUNS = {"i": "I", "me": "me", "you": "you", "we": "we", "he": "he", "she": "she", "they": "they"}
    
    SPECIAL_COMBOS = {
        ("i", "need", "help"): "I need help.",
        ("i", "need", "break"): "I need a break.",
        ("i", "need", "water"): "I need water, please.",
        ("i", "need", "washroom"): "I need to use the washroom.",
        ("i", "am", "hungry"): "I am hungry.",
        ("i", "am", "thirsty"): "I am thirsty.",
        ("i", "am", "tired"): "I am feeling tired.",
        ("i", "feel", "happy"): "I feel happy.",
        ("i", "feel", "sad"): "I feel sad.",
        ("i", "feel", "confused"): "I feel confused.",
        ("i", "feel", "scared"): "I feel scared.",
        ("i", "have", "question"): "I have a question.",
        ("i", "dont", "understand"): "I don't understand.",
        ("please", "repeat"): "Please repeat that.",
        ("i", "finished"): "I have finished my work.",
        ("more", "time"): "I need more time, please.",
    }

    @classmethod
    def synthesize_sentence(cls, symbol_labels: List[str]) -> Dict[str, str]:
        if not symbol_labels:
            return {
                "sentence": "",
                "spoken_text": "",
                "category": "empty"
            }

        cleaned = [s.strip().lower() for s in symbol_labels if s.strip()]
        
        # Check special direct tuples
        key = tuple(cleaned)
        if key in cls.SPECIAL_COMBOS:
            full = cls.SPECIAL_COMBOS[key]
            return {
                "sentence": full,
                "spoken_text": full,
                "category": "phrase"
            }

        # Otherwise synthesize grammatically
        processed = []
        for i, word in enumerate(cleaned):
            if word in cls.PRONOUNS:
                processed.append(cls.PRONOUNS[word])
            else:
                processed.append(word)

        raw = " ".join(processed)
        
        # Smoothing common AAC gaps
        raw = re.sub(r"\bI need washroom\b", "I need to use the washroom", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\bI need break\b", "I need a break", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\bI have question\b", "I have a question", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\bI need more time\b", "I need more time, please", raw, flags=re.IGNORECASE)

        # Capitalize first letter and add punctuation
        sentence = raw[0].upper() + raw[1:] if len(raw) > 1 else raw.upper()
        if not sentence.endswith((".", "!", "?")):
            sentence += "."

        return {
            "sentence": sentence,
            "spoken_text": sentence,
            "category": "constructed"
        }
