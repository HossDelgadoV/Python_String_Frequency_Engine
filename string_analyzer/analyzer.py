# string_analyzer/analyzer.py
import re
import collections
import math
from typing import Dict, List, Any, Optional, Tuple, Union

class StringAnalyzer:
    """Enhanced class for analyzing text frequency and patterns"""
    
    def __init__(self, text=""):
        self.text = text
        self.results = {}
        
    def analyze(self) -> Dict[str, Any]:
        """Perform comprehensive analysis on the text"""
        if not self.text:
            return {}
            
        # Basic stats
        self.results["character_count"] = len(self.text)
        self.results["word_count"] = len(re.findall(r'\b\w+\b', self.text))
        self.results["line_count"] = self.text.count('\n') + 1
        self.results["sentence_count"] = len(re.split(r'[.!?]+', self.text.strip())) - 1
        self.results["paragraph_count"] = len(re.split(r'\n\s*\n', self.text.strip())) if self.text.strip() else 0
        self.results["average_word_length"] = self._calculate_avg_word_length()
        
        # Character frequency
        char_freq = collections.Counter(self.text.lower())
        self.results["character_frequency"] = {char: count for char, count in char_freq.most_common(15)}
        
        # Word frequency
        words = re.findall(r'\b\w+\b', self.text.lower())
        word_freq = collections.Counter(words)
        self.results["word_frequency"] = {word: count for word, count in word_freq.most_common(20)}
        
        # N-grams analysis
        self.results["bigrams"] = self._analyze_ngrams(2)
        self.results["trigrams"] = self._analyze_ngrams(3)
        
        # Pattern detection
        self.results["patterns"] = self._detect_patterns()
        
        # Readability metrics
        self.results["readability"] = self._calculate_readability()
        
        # Token type analysis
        self.results["token_types"] = self._analyze_token_types()
        
        # Word length distribution
        self.results["word_length_distribution"] = self._calculate_word_length_distribution()
        
        # Case analysis
        self.results["case_analysis"] = self._analyze_case()
        
        # Special characters analysis
        self.results["special_characters"] = self._analyze_special_characters()
        
        return self.results
    
    def _calculate_avg_word_length(self) -> float:
        """Calculate average word length"""
        words = re.findall(r'\b\w+\b', self.text)
        if not words:
            return 0.0
        
        total_length = sum(len(word) for word in words)
        return round(total_length / len(words), 2)
    
    def _analyze_ngrams(self, n: int) -> Dict[str, int]:
        """Analyze n-grams in the text"""
        words = re.findall(r'\b\w+\b', self.text.lower())
        
        if len(words) < n:
            return {}
            
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = ' '.join(words[i:i+n])
            ngrams.append(ngram)
            
        ngram_freq = collections.Counter(ngrams)
        return {ngram: count for ngram, count in ngram_freq.most_common(10)}
    
    def _detect_patterns(self) -> Dict[str, List[str]]:
        """Detect common patterns in the text"""
        patterns = {
            "emails": [],
            "urls": [],
            "phone_numbers": [],
            "dates": [],
            "ip_addresses": [],
            "hashtags": [],
            "mentions": []
        }
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        patterns["emails"] = re.findall(email_pattern, self.text)
        
        # URL pattern
        url_pattern = r'https?://[^\s]+'
        patterns["urls"] = re.findall(url_pattern, self.text)
        
        # Phone number pattern (simplistic)
        phone_pattern = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        patterns["phone_numbers"] = re.findall(phone_pattern, self.text)
        
        # Date pattern (simplistic)
        date_pattern = r'\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b'
        patterns["dates"] = re.findall(date_pattern, self.text)
        
        # IP address pattern
        ip_pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
        patterns["ip_addresses"] = re.findall(ip_pattern, self.text)
        
        # Hashtag pattern
        hashtag_pattern = r'#\w+'
        patterns["hashtags"] = re.findall(hashtag_pattern, self.text)
        
        # Mention pattern
        mention_pattern = r'@\w+'
        patterns["mentions"] = re.findall(mention_pattern, self.text)
        
        # Filter out empty pattern types
        return {k: v for k, v in patterns.items() if v}
    
    def _calculate_readability(self) -> Dict[str, Union[float, str]]:
        """Calculate various readability metrics"""
        # Count sentences, words, and syllables
        sentences = re.split(r'[.!?]+', self.text.strip())
        sentences = [s for s in sentences if s]  # Remove empty strings
        
        words = re.findall(r'\b\w+\b', self.text.lower())
        total_words = len(words)
        
        # Estimate syllables (simplistic approach)
        def count_syllables(word):
            word = word.lower()
            # Count vowel groups
            count = len(re.findall(r'[aeiouy]+', word))
            # Adjust for silent 'e' at the end
            if word.endswith('e'):
                count -= 1
            # Ensure minimum syllable count
            return max(1, count)
        
        total_syllables = sum(count_syllables(word) for word in words)
        
        # Calculate metrics
        if not words or not sentences:
            return {"error": "Insufficient text for readability calculation"}
        
        # Average words per sentence
        words_per_sentence = total_words / len(sentences)
        
        # Average syllables per word
        syllables_per_word = total_syllables / total_words
        
        # Flesch Reading Ease
        flesch_reading_ease = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
        flesch_reading_ease = max(0, min(100, flesch_reading_ease))  # Clamp to 0-100
        
        # Flesch-Kincaid Grade Level
        flesch_kincaid_grade = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
        flesch_kincaid_grade = max(0, flesch_kincaid_grade)  # Ensure non-negative
        
        readability = {
            "words_per_sentence": round(words_per_sentence, 2),
            "syllables_per_word": round(syllables_per_word, 2),
            "flesch_reading_ease": round(flesch_reading_ease, 2),
            "flesch_kincaid_grade": round(flesch_kincaid_grade, 2),
            "reading_level": self._get_reading_level(flesch_reading_ease)
        }
        
        return readability
    
    def _get_reading_level(self, score: float) -> str:
        """Convert Flesch Reading Ease score to reading level description"""
        if score >= 90:
            return "Very Easy (5th grade)"
        elif score >= 80:
            return "Easy (6th grade)"
        elif score >= 70:
            return "Fairly Easy (7th grade)"
        elif score >= 60:
            return "Standard (8th-9th grade)"
        elif score >= 50:
            return "Fairly Difficult (10th-12th grade)"
        elif score >= 30:
            return "Difficult (College level)"
        else:
            return "Very Difficult (College graduate level)"
    
    def _analyze_token_types(self) -> Dict[str, int]:
        """Analyze different types of tokens in the text"""
        # Characters by type
        alpha_count = sum(1 for c in self.text if c.isalpha())
        digit_count = sum(1 for c in self.text if c.isdigit())
        space_count = sum(1 for c in self.text if c.isspace())
        punct_count = sum(1 for c in self.text if c in ".,;:!?-\"'()[]{}")
        other_count = len(self.text) - alpha_count - digit_count - space_count - punct_count
        
        # Words by type
        words = re.findall(r'\b\w+\b', self.text)
        
        numeric_words = sum(1 for w in words if w.isdigit())
        alpha_words = sum(1 for w in words if w.isalpha())
        alphanumeric_words = len(words) - numeric_words - alpha_words
        
        return {
            "alphabetic_chars": alpha_count,
            "numeric_chars": digit_count,
            "space_chars": space_count,
            "punctuation_chars": punct_count,
            "other_chars": other_count,
            "alphabetic_words": alpha_words,
            "numeric_words": numeric_words,
            "alphanumeric_words": alphanumeric_words
        }
    
    def _calculate_word_length_distribution(self) -> Dict[int, int]:
        """Calculate distribution of word lengths"""
        words = re.findall(r'\b\w+\b', self.text)
        
        length_dist = {}
        for word in words:
            length = len(word)
            length_dist[length] = length_dist.get(length, 0) + 1
            
        # Sort by key (word length)
        return dict(sorted(length_dist.items()))
    
    def _analyze_case(self) -> Dict[str, int]:
        """Analyze case usage in the text"""
        words = re.findall(r'\b\w+\b', self.text)
        
        uppercase_words = sum(1 for w in words if w.isupper())
        lowercase_words = sum(1 for w in words if w.islower())
        title_case_words = sum(1 for w in words if w.istitle())
        mixed_case_words = len(words) - uppercase_words - lowercase_words - title_case_words
        
        return {
            "uppercase_words": uppercase_words,
            "lowercase_words": lowercase_words,
            "title_case_words": title_case_words,
            "mixed_case_words": mixed_case_words
        }
    
    def _analyze_special_characters(self) -> Dict[str, int]:
        """Analyze special character usage"""
        special_chars = {
            "parentheses": sum(1 for c in self.text if c in "()"),
            "brackets": sum(1 for c in self.text if c in "[]"),
            "braces": sum(1 for c in self.text if c in "{}"),
            "quotes": sum(1 for c in self.text if c in "\"'"),
            "hyphens_dashes": sum(1 for c in self.text if c in "-–—"),
            "math_symbols": sum(1 for c in self.text if c in "+*/=^"),
            "currency_symbols": sum(1 for c in self.text if c in "$€£¥"),
            "hashtags": self.text.count('#'),
            "at_signs": self.text.count('@'),
            "ampersands": self.text.count('&'),
            "forward_slashes": self.text.count('/'),
            "backslashes": self.text.count('\\')
        }
        
        # Filter out zeros
        return {k: v for k, v in special_chars.items() if v > 0}
    
    def format_results(self) -> str:
        """Format results for display"""
        if not self.results:
            return "No analysis results available."
        
        output = []
        
        # Basic stats
        output.append("=== BASIC STATISTICS ===")
        output.append(f"Total Characters: {self.results.get('character_count', 0)}")
        output.append(f"Total Words: {self.results.get('word_count', 0)}")
        output.append(f"Total Lines: {self.results.get('line_count', 0)}")
        output.append(f"Total Sentences: {self.results.get('sentence_count', 0)}")
        output.append(f"Total Paragraphs: {self.results.get('paragraph_count', 0)}")
        output.append(f"Average Word Length: {self.results.get('average_word_length', 0)} characters")
        
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
        
        # N-grams
        if "bigrams" in self.results and self.results["bigrams"]:
            output.append("\n=== COMMON WORD PAIRS (BIGRAMS) ===")
            for bigram, count in self.results["bigrams"].items():
                output.append(f"  '{bigram}': {count}")
                
        if "trigrams" in self.results and self.results["trigrams"]:
            output.append("\n=== COMMON WORD TRIPLETS (TRIGRAMS) ===")
            for trigram, count in self.results["trigrams"].items():
                output.append(f"  '{trigram}': {count}")
        
        # Patterns
        if "patterns" in self.results and self.results["patterns"]:
            output.append("\n=== PATTERNS DETECTED ===")
            for pattern_type, instances in self.results["patterns"].items():
                if instances:
                    pattern_name = pattern_type.replace("_", " ").title()
                    output.append(f"  {pattern_name}: {len(instances)} found")
                    # Display up to 5 examples
                    for i, instance in enumerate(instances[:5]):
                        output.append(f"    - {instance}")
                    if len(instances) > 5:
                        output.append(f"    - ... and {len(instances) - 5} more")
        
        # Readability
        if "readability" in self.results:
            output.append("\n=== READABILITY METRICS ===")
            readability = self.results["readability"]
            if "error" in readability:
                output.append(f"  {readability['error']}")
            else:
                output.append(f"  Words per Sentence: {readability.get('words_per_sentence', 0)}")
                output.append(f"  Syllables per Word: {readability.get('syllables_per_word', 0)}")
                output.append(f"  Flesch Reading Ease: {readability.get('flesch_reading_ease', 0)} " +
                             f"({readability.get('reading_level', 'Unknown')})")
                output.append(f"  Flesch-Kincaid Grade Level: {readability.get('flesch_kincaid_grade', 0)}")
        
        # Token Types
        if "token_types" in self.results:
            output.append("\n=== TOKEN TYPE ANALYSIS ===")
            token_types = self.results["token_types"]
            output.append("  Character Types:")
            output.append(f"    - Alphabetic: {token_types.get('alphabetic_chars', 0)}")
            output.append(f"    - Numeric: {token_types.get('numeric_chars', 0)}")
            output.append(f"    - Space: {token_types.get('space_chars', 0)}")
            output.append(f"    - Punctuation: {token_types.get('punctuation_chars', 0)}")
            output.append(f"    - Other: {token_types.get('other_chars', 0)}")
            
            output.append("  Word Types:")
            output.append(f"    - Alphabetic: {token_types.get('alphabetic_words', 0)}")
            output.append(f"    - Numeric: {token_types.get('numeric_words', 0)}")
            output.append(f"    - Alphanumeric: {token_types.get('alphanumeric_words', 0)}")
        
        # Word Length Distribution
        if "word_length_distribution" in self.results and self.results["word_length_distribution"]:
            output.append("\n=== WORD LENGTH DISTRIBUTION ===")
            for length, count in self.results["word_length_distribution"].items():
                output.append(f"  {length} character words: {count}")
        
        # Case Analysis
        if "case_analysis" in self.results:
            output.append("\n=== CASE ANALYSIS ===")
            case_analysis = self.results["case_analysis"]
            output.append(f"  Uppercase Words: {case_analysis.get('uppercase_words', 0)}")
            output.append(f"  Lowercase Words: {case_analysis.get('lowercase_words', 0)}")
            output.append(f"  Title Case Words: {case_analysis.get('title_case_words', 0)}")
            output.append(f"  Mixed Case Words: {case_analysis.get('mixed_case_words', 0)}")
        
        # Special Characters
        if "special_characters" in self.results and self.results["special_characters"]:
            output.append("\n=== SPECIAL CHARACTER USAGE ===")
            for char_type, count in self.results["special_characters"].items():
                char_display = char_type.replace("_", " ").title()
                output.append(f"  {char_display}: {count}")
        
        return "\n".join(output)