#!/usr/bin/env python3
import json
import sys
from difflib import get_close_matches

class LocalDictionary:
    def __init__(self, json_file='dictionary_compact.json'):
        print("Loading dictionary...")
        with open(json_file, 'r') as f:
            self.data = json.load(f)
        print(f"Loaded {len(self.data)} words.")
    
    def lookup(self, word):
        word = word.lower()
        if word in self.data:
            return self.data[word]
        
        # Suggest close matches
        matches = get_close_matches(word, self.data.keys(), n=3, cutoff=0.7)
        return {"error": "not_found", "suggestions": matches}
    
    def display(self, word, result):
        if isinstance(result, dict) and result.get("error"):
            print(f"\n❌ '{word}' not found.")
            if result.get("suggestions"):
                print("Did you mean:")
                for suggestion in result['suggestions']:
                    print(f"  • {suggestion}")
            return
        
        print(f"\n📖 {word.upper()}")
        print(f"📝 Definition:")
        if isinstance(result, list):
            for i, defn in enumerate(result[:3], 1):
                print(f"  {i}. {defn}")
        else:
            print(f"  {result}")

def main():
    try:
        app = LocalDictionary()
    except FileNotFoundError:
        print("Error: dictionary_compact.json not found.")
        print("Download it from: https://github.com/matthewreagan/WebstersEnglishDictionary")
        sys.exit(1)
    
    print("=" * 50)
    print("📚 Local English Dictionary (Offline)")
    print("=" * 50)
    
    while True:
        word = input("\nEnter word (or 'quit'): ").strip()
        if word.lower() in ['quit', 'exit', 'q']:
            break
        
        result = app.lookup(word)
        app.display(word, result)

if __name__ == "__main__":
    main()