#!/usr/bin/env python3
"""
Command-line interface for the String Analyzer package.
Provides command-line access to text analysis functionality.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path to enable imports when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from string_analyzer.analyzer import StringAnalyzer
except ImportError:
    # Fallback import if running the module directly
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from analyzer import StringAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("StringAnalyzer.CLI")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='String Frequency Analyzer - Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a file and print results to console
  python cli.py --input input.txt
  
  # Analyze text from stdin
  cat input.txt | python cli.py
  
  # Analyze a file and save results to a JSON file
  python cli.py --input input.txt --output results.json --format json
  
  # Analyze a specific string
  python cli.py --text "This is a sample text to analyze."
"""
    )
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input', '-i', 
        type=str, 
        help='Input file path'
    )
    input_group.add_argument(
        '--text', '-t', 
        type=str, 
        help='Text string to analyze'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file path (default: print to stdout)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--charts', '-c',
        action='store_true',
        help='Generate charts (requires matplotlib)'
    )
    
    return parser.parse_args()

def get_input_text(args):
    """Get the input text from file, stdin, or direct text argument."""
    if args.text:
        return args.text
    
    if args.input:
        if args.input == '-':
            # Read from stdin
            return sys.stdin.read()
        else:
            # Read from file
            try:
                with open(args.input, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading file '{args.input}': {str(e)}")
                sys.exit(1)
    
    return None

def write_output(output_data, args):
    """Write output to file or stdout."""
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_data)
                logger.info(f"Results written to '{args.output}'")
        except Exception as e:
            logger.error(f"Error writing to file '{args.output}': {str(e)}")
            sys.exit(1)
    else:
        # Print to stdout
        print(output_data)

def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get input text
    input_text = get_input_text(args)
    if not input_text:
        logger.error("No input text provided")
        sys.exit(1)
    
    # Analyze text
    analyzer = StringAnalyzer(input_text)
    results = analyzer.analyze()
    
    # Generate output
    if args.format == 'json':
        output_data = json.dumps(results, indent=2)
    else:
        output_data = analyzer.format_results()
    
    # Write output
    write_output(output_data, args)
    
    # Generate charts if requested
    if args.charts:
        try:
            import matplotlib.pyplot as plt
            
            # Generate character frequency chart
            char_freq = results.get("character_frequency", {})
            if char_freq:
                # Filter printable characters
                printable_chars = {k: v for k, v in char_freq.items() 
                                  if k.isprintable() and not k.isspace()}
                
                plt.figure(figsize=(12, 6))
                plt.bar(printable_chars.keys(), printable_chars.values())
                plt.title('Character Frequency')
                plt.xlabel('Character')
                plt.ylabel('Frequency')
                
                chart_path = 'char_frequency_chart.png'
                plt.savefig(chart_path)
                logger.info(f"Character frequency chart saved to '{chart_path}'")
                plt.close()
            
            # Generate word frequency chart
            word_freq = results.get("word_frequency", {})
            if word_freq:
                plt.figure(figsize=(12, 6))
                plt.bar(list(word_freq.keys())[:10], list(word_freq.values())[:10])
                plt.title('Top 10 Word Frequency')
                plt.xlabel('Word')
                plt.ylabel('Frequency')
                plt.xticks(rotation=45)
                
                chart_path = 'word_frequency_chart.png'
                plt.savefig(chart_path)
                logger.info(f"Word frequency chart saved to '{chart_path}'")
                plt.close()
                
        except ImportError:
            logger.warning("Matplotlib not installed - charts not generated")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())