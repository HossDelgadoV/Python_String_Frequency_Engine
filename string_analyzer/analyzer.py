# string_analyzer/analyzer.py
import re
import collections

class StringAnalyzer:
    """Class for analyzing text frequency and patterns"""
    
    def __init__(self, text=""):
        self.text = text
        self.results = {}
        
    def analyze(self):
        """Perform basic analysis on the text"""
        if not self.text:
            return {}
            
        # Basic stats
        self.results["character_count"] = len(self.text)
        self.results["word_count"] = len(re.findall(r'\b\w+\b', self.text))
        self.results["line_count"] = self.text.count('\n') + 1
        
        # Character frequency
        char_freq = collections.Counter(self.text.lower())
        self.results["character_frequency"] = {char: count for char, count in char_freq.most_common(10)}
        
        # Word frequency
        words = re.findall(r'\b\w+\b', self.text.lower())
        word_freq = collections.Counter(words)
        self.results["word_frequency"] = {word: count for word, count in word_freq.most_common(10)}
        
        return self.results
    
    def format_results(self):
        """Format results for display"""
        if not self.results:
            return "No analysis results available."
        
        output = []
        
        # Basic stats
        output.append("=== BASIC STATISTICS ===")
        output.append(f"Total Characters: {self.results['character_count']}")
        output.append(f"Total Words: {self.results['word_count']}")
        output.append(f"Total Lines: {self.results['line_count']}")
        
        # Character frequency
        if "character_frequency" in self.results:
            output.append("\n=== CHARACTER FREQUENCY ===")
            for char, count in self.results["character_frequency"].items():
                char_display = char
                if char.isspace():
                    if char == ' ':
                        char_display = "[space]"
                    elif char == '\n':
                        char_display = "[newline]"
                    elif char == '\t':
                        char_display = "[tab]"
                output.append(f"  '{char_display}': {count}")
        
        # Word frequency
        if "word_frequency" in self.results:
            output.append("\n=== WORD FREQUENCY ===")
            for word, count in self.results["word_frequency"].items():
                output.append(f"  '{word}': {count}")
        
        return "\n".join(output)