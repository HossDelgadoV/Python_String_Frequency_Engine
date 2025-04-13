from setuptools import setup, find_packages

# Read the contents of README.md file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read the contents of requirements.txt file
with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="string-frequency-analyzer",
    version="0.2.0",
    description="A powerful text analysis tool for frequency and pattern detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Hoss Delgado V",
    author_email="example@example.com",  # Replace with actual email
    url="https://github.com/HossDelgadoV/Python_String_Frequency_Engine",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "string-analyzer=string_analyzer.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)