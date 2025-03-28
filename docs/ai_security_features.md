# AI-Powered Security Analysis in Astra

This document explains the new AI and ML-powered security features added to Astra and how to use them effectively.

## Setup & Installation

To use the AI-powered security features, you need to install additional dependencies:

```bash
# Run the setup script
python setup_ai_security.py

# Or install dependencies manually
pip install scikit-learn selenium webdriver-manager fpdf numpy beautifulsoup4 lxml jinja2 matplotlib
```

For advanced deep learning models, you can optionally install TensorFlow:

```bash
pip install tensorflow
```

## Features Overview

### 1. AI-Based Threat Detection

Astra now includes machine learning models to detect potential security threats:

- **Anomaly Detection**: Uses scikit-learn's Isolation Forest algorithm to identify unusual patterns that might indicate zero-day vulnerabilities
- **Pattern Recognition**: Trained on common attack patterns to identify SQL injections, XSS, and other vulnerabilities

### 2. Dynamic Scanning with Selenium

- **JavaScript-Based Vulnerability Detection**: Detects vulnerabilities in dynamic web applications that require JavaScript execution
- **DOM-Based XSS Detection**: Finds DOM-based XSS vulnerabilities by executing JavaScript and monitoring for execution
- **Form Interaction**: Automatically fills and submits forms to test for vulnerabilities

### 3. ML-Powered Fuzzing

- **Intelligent Fuzzing**: Uses machine learning to guide fuzzing efforts toward promising attack vectors
- **Zero-Day Detection**: Can identify previously unknown vulnerabilities through anomaly detection
- **Adaptive Testing**: Adjusts testing strategies based on application responses

### 4. Enhanced Reporting

- **Risk Scoring System**: Each vulnerability is assigned a risk score from 0-100
- **AI-Suggested Mitigations**: Provides specific remediation strategies for each vulnerability
- **Executive Summaries**: Automatically generates high-level summaries of scan results
- **Enhanced Reports**: Detailed HTML and PDF reports with risk scores and mitigation strategies

## Using the Features

### Web Vulnerability Scanner

1. Navigate to the Web Vulnerability Scanner in Astra
2. Check the "Use AI Analysis" option
3. Enable "Dynamic Scanning" to use Selenium for JavaScript-based testing
4. Run your scan and view the enhanced results

### Viewing AI-Enhanced Reports

1. After a scan completes, click "Generate Enhanced PDF Report" or "Generate Enhanced HTML Report"
2. The report will include:
   - Executive summary with overall risk assessment
   - Risk scores for each vulnerability
   - AI-suggested mitigation strategies
   - Severity breakdowns and statistics

## Troubleshooting

If you encounter issues with Selenium-based scanning:

1. Ensure you have Chrome installed
2. If you see ChromeDriver errors, the application will attempt to download the correct version
3. For more persistent issues, install chromedriver manually: `pip install webdriver-manager`

For TensorFlow-related issues:

1. TensorFlow is optional and only needed for advanced deep learning models
2. If you experience memory issues, try running with reduced model complexity

## Contributing ML Models

If you'd like to contribute improved ML models:

1. Models are stored in the `models/` directory
2. Training data can be placed in `data/training/`
3. Submit a pull request with your improved model and training code
