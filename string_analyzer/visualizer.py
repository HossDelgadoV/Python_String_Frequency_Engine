# string_analyzer/visualizer.py
"""
Visualization utilities for the string analyzer package.
Provides functions for creating visual representations of text analysis results.
"""


import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import io
import base64
import logging
from typing import Dict, List, Tuple, Optional, Union, Any, cast
from matplotlib.text import Text
from matplotlib.patches import Wedge


# Configure logging
logger = logging.getLogger(__name__)

class StringVisualizer:
    """Class for creating visualizations of text analysis results"""
    
    def __init__(self, results: Optional[Dict[str, Any]] = None):
        """Initialize the visualizer with optional analysis results"""
        self.results = results or {}  # Use empty dict as default instead of None
        self.output_dir = Path("./visualizations")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
    
    def create_character_frequency_chart(self, 
                                        output_path: Optional[str] = None,
                                        return_base64: bool = False) -> Optional[str]:
        """
        Create a bar chart showing character frequency.
        
        Args:
            output_path: Path to save the chart image. If None, uses default path.
            return_base64: If True, returns a base64-encoded string of the image.
            
        Returns:
            Optional base64-encoded string of the image if return_base64 is True.
        """
        if "character_frequency" not in self.results:
            logger.warning("No character frequency data available for visualization")
            return None
            
        char_freq = self.results.get("character_frequency", {})
        if not char_freq:
            logger.warning("Character frequency data is empty")
            return None
            
        # Filter and prepare data
        # Display space characters in a readable way
        display_chars = []
        counts = []
        
        for char, count in char_freq.items():
            if char.isspace():
                if char == ' ':
                    display_char = "[space]"
                elif char == '\n':
                    display_char = "[newline]"
                elif char == '\t':
                    display_char = "[tab]"
                else:
                    display_char = f"[ASCII {ord(char)}]"
            else:
                display_char = char
                
            display_chars.append(display_char)
            counts.append(count)
        
        # Create the chart
        plt.figure(figsize=(10, 6))
        bars = plt.bar(display_chars, counts, color='skyblue')
        
        # Add data labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:,}',
                    ha='center', va='bottom', rotation=0)
        
        # Style the chart
        plt.title('Character Frequency Analysis', fontsize=16)
        plt.xlabel('Character', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save or return the chart
        if output_path:
            full_path = Path(output_path)
        else:
            full_path = self.output_dir / "character_frequency.png"
            
        plt.savefig(str(full_path), dpi=100)
        logger.info(f"Character frequency chart saved to {full_path}")
        
        # Return base64 if requested
        if return_base64:
            img_data = io.BytesIO()
            plt.savefig(img_data, format='png', dpi=100)
            img_data.seek(0)
            base64_image = base64.b64encode(img_data.read()).decode('utf-8')
            plt.close()
            return base64_image
            
        plt.close()
        return None
    
    def create_word_frequency_chart(self,
                                   max_words: int = 15,
                                   output_path: Optional[str] = None,
                                   return_base64: bool = False) -> Optional[str]:
        """
        Create a bar chart showing word frequency.
        
        Args:
            max_words: Maximum number of words to display
            output_path: Path to save the chart image. If None, uses default path.
            return_base64: If True, returns a base64-encoded string of the image.
            
        Returns:
            Optional base64-encoded string of the image if return_base64 is True.
        """
        if "word_frequency" not in self.results:
            logger.warning("No word frequency data available for visualization")
            return None
            
        word_freq = self.results.get("word_frequency", {})
        if not word_freq:
            logger.warning("Word frequency data is empty")
            return None
            
        # Limit to top N words
        words = list(word_freq.keys())[:max_words]
        counts = list(word_freq.values())[:max_words]
        
        # Create horizontal bar chart for better readability with long words
        plt.figure(figsize=(10, max(6, len(words) * 0.4)))  # Dynamic height based on word count
        bars = plt.barh(words, counts, color='lightgreen')
        
        # Add data labels
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{int(width):,}',
                    ha='left', va='center')
        
        # Style the chart
        plt.title(f'Top {len(words)} Word Frequency', fontsize=16)
        plt.xlabel('Frequency', fontsize=12)
        plt.ylabel('Word', fontsize=12)
        plt.tight_layout()
        
        # Save or return the chart
        if output_path:
            full_path = Path(output_path)
        else:
            full_path = self.output_dir / "word_frequency.png"
            
        plt.savefig(str(full_path), dpi=100)
        logger.info(f"Word frequency chart saved to {full_path}")
        
        # Return base64 if requested
        if return_base64:
            img_data = io.BytesIO()
            plt.savefig(img_data, format='png', dpi=100)
            img_data.seek(0)
            base64_image = base64.b64encode(img_data.read()).decode('utf-8')
            plt.close()
            return base64_image
            
        plt.close()
        return None
    
    def create_word_cloud(self,
                         output_path: Optional[str] = None,
                         return_base64: bool = False) -> Optional[str]:
        """
        Create a word cloud visualization of the text data.
        
        Args:
            output_path: Path to save the word cloud image. If None, uses default path.
            return_base64: If True, returns a base64-encoded string of the image.
            
        Returns:
            Optional base64-encoded string of the image if return_base64 is True.
        """
        try:
            from wordcloud import WordCloud
        except ImportError:
            logger.error("WordCloud package not installed. Install with: pip install wordcloud")
            return None
            
        if "word_frequency" not in self.results:
            logger.warning("No word frequency data available for word cloud")
            return None
            
        word_freq = self.results.get("word_frequency", {})
        if not word_freq:
            logger.warning("Word frequency data is empty")
            return None
            
        # Create word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=100,
            colormap='viridis',
            contour_width=1,
            contour_color='steelblue'
        ).generate_from_frequencies(word_freq)
        
        # Plot the word cloud
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        
        # Save or return the chart
        if output_path:
            full_path = Path(output_path)
        else:
            full_path = self.output_dir / "word_cloud.png"
            
        plt.savefig(str(full_path), dpi=150)
        logger.info(f"Word cloud saved to {full_path}")
        
        # Return base64 if requested
        if return_base64:
            img_data = io.BytesIO()
            plt.savefig(img_data, format='png', dpi=150)
            img_data.seek(0)
            base64_image = base64.b64encode(img_data.read()).decode('utf-8')
            plt.close()
            return base64_image
            
        plt.close()
        return None
        
    def create_distribution_chart(self,
                               output_path: Optional[str] = None,
                               return_base64: bool = False) -> Optional[str]:
        """
        Create a pie chart showing character type distribution.
        
        Args:
            output_path: Path to save the chart image. If None, uses default path.
            return_base64: If True, returns a base64-encoded string of the image.
            
        Returns:
            Optional base64-encoded string of the image if return_base64 is True.
        """
        if "character_count" not in self.results:
            logger.warning("No character count data available for visualization")
            return None
            
        if not self.results.get("text", ""):
            logger.warning("No text data available for character distribution analysis")
            return None
            
        # Analyze character distribution
        text = self.results.get("text", "")
        
        # Count character types
        alpha_count = sum(1 for c in text if c.isalpha())
        digit_count = sum(1 for c in text if c.isdigit())
        space_count = sum(1 for c in text if c.isspace())
        punct_count = sum(1 for c in text if c in ".,;:!?-\"'()[]{}")
        other_count = len(text) - alpha_count - digit_count - space_count - punct_count
        
        # Create data for pie chart
        labels = ['Alphabetic', 'Numeric', 'Whitespace', 'Punctuation', 'Other']
        sizes = [alpha_count, digit_count, space_count, punct_count, other_count]
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']
        
        # Remove empty categories
        filtered_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
        if filtered_data:
            labels, sizes, colors = zip(*filtered_data)
        else:
            logger.warning("No character distribution data to display")
            return None
        
        # Create pie chart
        plt.figure(figsize=(8, 8))
        pie_result = plt.pie(
            sizes, 
            labels=labels, 
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            shadow=True,
            explode=[0.05] * len(sizes)  # Explode all slices slightly
        )
        
        # Check what elements we have in the pie_result
        # Usually it returns (wedges, texts, autotexts), but this can vary
        # Handle different cases safely
        if len(pie_result) >= 2:  # We at least have wedges and texts
            # First items are the wedges
            # Second items are the texts (labels)
            label_texts = pie_result[1]
            
            # Set font size for labels
            for text_obj in label_texts:
                if hasattr(text_obj, 'set_fontsize'):
                    text_obj.set_fontsize(12)
            
            # If we have autotexts (percentage labels)
            if len(pie_result) >= 3:
                auto_texts = pie_result[2]
                for text_obj in auto_texts:
                    if hasattr(text_obj, 'set_fontsize'):
                        text_obj.set_fontsize(12)
                    if hasattr(text_obj, 'set_fontweight'):
                        text_obj.set_fontweight('bold')
            
        plt.axis('equal')
        plt.title('Character Type Distribution', fontsize=16)
        plt.tight_layout()
        
        # Save or return the chart
        if output_path:
            full_path = Path(output_path)
        else:
            full_path = self.output_dir / "char_distribution.png"
            
        plt.savefig(str(full_path), dpi=100)
        logger.info(f"Character distribution chart saved to {full_path}")
        
        # Return base64 if requested
        if return_base64:
            img_data = io.BytesIO()
            plt.savefig(img_data, format='png', dpi=100)
            img_data.seek(0)
            base64_image = base64.b64encode(img_data.read()).decode('utf-8')
            plt.close()
            return base64_image
            
        plt.close()
        return None

    def create_all_visualizations(self, 
                               output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Create all available visualizations and return paths.
        
        Args:
            output_dir: Directory to save visualizations. If None, uses default.
            
        Returns:
            Dictionary mapping visualization names to file paths.
        """
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(exist_ok=True)
            
        results = {}
        
        # Character frequency chart
        try:
            char_freq_path = self.output_dir / "character_frequency.png"
            self.create_character_frequency_chart(str(char_freq_path))
            results["character_frequency_chart"] = str(char_freq_path)
        except Exception as e:
            logger.error(f"Error creating character frequency chart: {str(e)}")
            
        # Word frequency chart
        try:
            word_freq_path = self.output_dir / "word_frequency.png"
            self.create_word_frequency_chart(output_path=str(word_freq_path))
            results["word_frequency_chart"] = str(word_freq_path)
        except Exception as e:
            logger.error(f"Error creating word frequency chart: {str(e)}")
            
        # Word cloud
        try:
            word_cloud_path = self.output_dir / "word_cloud.png"
            self.create_word_cloud(output_path=str(word_cloud_path))
            results["word_cloud"] = str(word_cloud_path)
        except Exception as e:
            logger.error(f"Error creating word cloud: {str(e)}")
            
        # Character distribution chart
        try:
            distribution_path = self.output_dir / "char_distribution.png"
            self.create_distribution_chart(output_path=str(distribution_path))
            results["character_distribution_chart"] = str(distribution_path)
        except Exception as e:
            logger.error(f"Error creating character distribution chart: {str(e)}")
            
        return results


# Usage example
if __name__ == "__main__":
    # Sample analysis results for testing
    sample_results = {
        "character_count": 100,
        "word_count": 20,
        "line_count": 5,
        "character_frequency": {
            "e": 12,
            "t": 9,
            "a": 8,
            "o": 7,
            "i": 7,
            "n": 6,
            "s": 6,
            "h": 6,
            "r": 5,
            " ": 15
        },
        "word_frequency": {
            "the": 3,
            "and": 2,
            "is": 2,
            "in": 2,
            "of": 2,
            "to": 1,
            "a": 1,
            "for": 1,
            "that": 1,
            "it": 1
        },
        "text": "This is a sample text for testing the visualizer component of the String Analyzer package."
    }
    
    # Create visualizer and generate all charts
    visualizer = StringVisualizer(sample_results)
    output_paths = visualizer.create_all_visualizations()
    
    print("Created visualizations:")
    for name, path in output_paths.items():
        print(f"- {name}: {path}")