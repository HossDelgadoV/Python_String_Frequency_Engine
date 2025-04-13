String Frequency Analyzer - Development Environment Setup
This guide walks through setting up a complete development environment for the String Frequency Analyzer project, which combines a Rust frontend with a Python backend.

Prerequisites
Before starting, make sure you have the following installed:

Git: For version control
VS Code: Recommended IDE with extensions for Rust and Python
Rust and Cargo: For building the frontend
Python 3.8+: For the backend analysis engine
Step 1: Install Required Tools
Rust Setup
Install Rust using rustup (the Rust toolchain installer):
Windows: Download and run rustup-init.exe from https://rustup.rs/
macOS/Linux: Run curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
Verify the installation:
bash
rustc --version
cargo --version
Update Rust (if needed):
bash
rustup update
Python Setup
Install Python 3.8 or newer:
Windows: Download from https://www.python.org/downloads/
macOS: brew install python3
Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv
Verify the installation:
bash
python3 --version
pip3 --version
Set up a virtual environment (recommended):
bash
python3 -m venv venv
Activate the virtual environment:
Windows: venv\Scripts\activate
macOS/Linux: source venv/bin/activate
Step 2: Clone the Repository
bash
git clone https://github.com/HossDelgadoV/Python_String_Frequency_Engine.git
cd Python_String_Frequency_Engine
Step 3: Install Python Dependencies
With your virtual environment activated:

bash
pip install -r requirements.txt
Step 4: Build the Rust Frontend
bash
cargo build
For a release build:

bash
cargo build --release
Step 5: Run the Application
bash
cargo run
VS Code Setup (Recommended)
Install these extensions for the best development experience:

Rust Analyzer: Provides intelligent code completion and analysis for Rust
Python: Microsoft's Python extension with IntelliSense and debugging
TOML: For editing Cargo.toml files
CodeLLDB: For debugging Rust applications
Better TOML: Improved syntax highlighting for TOML files
Project Structure Overview
Python_String_Frequency_Engine/
│
├── src/                     # Rust frontend source code
│   ├── main.rs              # Main entry point
│   ├── ui/                  # UI components
│   │   └── ...
│   └── python_bridge/       # Communication with Python backend
│
├── string_analyzer/         # Python backend
│   ├── __init__.py
│   ├── analyzer.py
│   └── ...
│
├── Cargo.toml               # Rust dependencies
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
Troubleshooting
Common Issues with Rust
Compilation errors with iced:
Ensure you have the latest version of Rust
Try cargo clean followed by cargo build
Missing Windows dependencies:
Install the Visual C++ Build Tools
Common Issues with Python
Module not found errors:
Ensure your virtual environment is activated
Verify all dependencies are installed: pip list
Matplotlib errors:
On Linux, install system dependencies: sudo apt-get install python3-tk
On macOS with M1/M2, use Miniforge for ARM-compatible packages
Development Workflow
Make changes to the code
Run tests: cargo test and pytest
Format code: cargo fmt and black string_analyzer/
Check for linting issues: cargo clippy and flake8 string_analyzer/
Build and run the application: cargo run
Deployment
For deployment, build a release version:

bash
cargo build --release
The executable will be in target/release/.

