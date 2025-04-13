String Frequency Analyzer
A modern text analysis tool that combines a Rust GUI frontend with a Python backend for powerful text pattern and frequency analysis. This project demonstrates effective integration between Rust's performance and Python's data processing capabilities.
Features

✨ Modern, customizable GUI built with Rust and the iced library
📊 Advanced text analysis via Python backend with visualization capabilities
🔍 Comprehensive analysis including character/word frequency, n-grams, and readability metrics
🎨 Customizable themes with RGB color pickers
📈 Data visualization for frequency patterns
📁 File support for analyzing text documents

Screenshots
[Screenshots would be displayed here]
Installation
Prerequisites

Rust (2021 edition or newer)
Python 3.8+
Cargo package manager

Quick Install

Clone this repository:
bashgit clone https://github.com/HossDelgadoV/Python_String_Frequency_Engine.git
cd Python_String_Frequency_Engine

Install Python dependencies:
bashpip install -r requirements.txt

Build and run the application:
bashcargo run


For detailed setup instructions, see the Development Environment Setup Guide.
Dependencies
Rust Dependencies
The frontend is built using the following Rust crates:
DependencyVersionPurposeLicenseiced0.9GUI frameworkMITtokio1.32.0Async runtimeMITserde, serde_json1.0.188, 1.0.107Data serializationMITimage0.24.7Image processingMITdirs5.0.1File system operationsMIT/Apache-2.0log, env_logger0.4.20, 0.10.0LoggingMIT/Apache-2.0thiserror, anyhow1.0.48, 1.0.75Error handlingMITwinapi (Windows only)0.3.9Windows system integrationMIT/Apache-2.0
To review all dependencies and their exact versions, see Cargo.toml.
Python Dependencies
The backend analysis engine uses the following Python packages:
DependencyVersionPurposeLicensenumpy1.26.3Numerical operationsBSDpandas2.1.4Data manipulation and analysisBSDmatplotlib3.8.2Data visualizationBSDnltk3.8.1Natural language processingApache 2.0scikit-learn1.4.0Machine learning techniquesBSDwordcloud1.9.3Word cloud generationMIT
To install all Python dependencies:
bashpip install -r requirements.txt
Architecture
Overview
The application follows a frontend-backend architecture:

Rust Frontend (GUI):

Handles user interface using the iced library
Manages user input and theme customization
Communicates with Python backend


Python Backend (Analysis Engine):

Performs text analysis and processing
Generates frequency data and statistics
Creates visualizations



Communication Flow
┌─────────────────┐      File-based      ┌─────────────────┐
│                 │     Communication     │                 │
│   Rust Frontend ├─────────────────────►│ Python Backend  │
│   (iced GUI)    │                      │ (Analysis)      │
│                 │◄─────────────────────┤                 │
└─────────────────┘                      └─────────────────┘

User enters text in the Rust GUI
Rust writes the text to a file (input.txt)
Rust spawns a Python process to analyze the text
Python reads the input file, processes it, and outputs results
Rust captures the Python output and displays it in the GUI

Usage

Launch the application
Enter or paste text in the input area
Click "Analyze Text"
View the analysis results
Customize the theme using the RGB sliders if desired

Analysis Features

Basic Statistics: Character count, word count, line count
Frequency Analysis: Most common characters and words
Pattern Detection: Identifies emails, URLs, dates, etc.
N-grams: Analysis of character and word sequences
Readability Metrics: Sentence complexity and reading ease scores

Development
Project Structure
├── src/                      # Rust frontend source
│   ├── main.rs               # Main entry point
│   └── ui/                   # UI components
│
├── string_analyzer/          # Python backend package
│   ├── __init__.py           # Package initialization
│   ├── analyzer.py           # Core analysis functionality
│   ├── visualizer.py         # Visualization components
│   └── utils.py              # Utility functions
│
├── tests/                    # Test suites
│
├── Cargo.toml                # Rust dependencies
├── requirements.txt          # Python dependencies
├── setup.py                  # Python package setup
└── README.md                 # This file
Adding Features
To add new analysis features:

Extend the Python backend in string_analyzer/analyzer.py
Update the results formatting in the Python code
Update the Rust frontend to display new result types

Running Tests
bash# Run Rust tests
cargo test

# Run Python tests
pytest
Contributing
Contributions are welcome! Here's how you can contribute:

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add some amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

Please make sure to update tests as appropriate.
License
This project is licensed under the MIT License - see the LICENSE file for details.
Contact
Hoss Delgado - @HossDelgadoV
Project Link: https://github.com/HossDelgadoV/Python_String_Frequency_Engine