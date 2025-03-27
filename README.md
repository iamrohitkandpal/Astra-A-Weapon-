# Astra - Ethical Hacking Toolkit

<p align="center">
  <img src="docs/images/astra_logo.png" alt="Astra Logo" width="200"/>
</p>

An educational desktop application for ethical hacking practice and network security assessment. Astra provides a comprehensive suite of tools for penetration testing, vulnerability scanning, and security analysis in a user-friendly GUI environment.

## 🛡️ Features

- **Network Analysis**
  - Port scanning with real-time results and service detection
  - DNS record information gathering and analysis
  - Subdomain enumeration and discovery with amass integration

- **Web Security Testing**
  - Web vulnerability scanning for XSS, SQL Injection, and more
  - SSL/TLS certificate validation and security assessment
  - Missing security headers detection

- **Advanced Security Tools**
  - Brute force modules for SSH and web login forms
  - Reverse shell generation and listener
  - CVE checking against NVD database

- **User Experience**
  - Modern, intuitive PyQt6-based interface
  - Customizable themes (Dark, Light, Hacker)
  - Theme editor for creating custom themes
  - Multi-threaded operations for responsive UI during scans

## 📸 Screenshots

<p align="center">
  <img src="docs/images/port_scanner.png" alt="Port Scanner" width="400"/>
  <img src="docs/images/vulnerability_scanner.png" alt="Vulnerability Scanner" width="400"/>
  <img src="docs/images/theme_editor.png" alt="Theme Editor" width="400"/>
  <img src="docs/images/ssl_checker.png" alt="SSL Checker" width="400"/>
</p>

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)
- pip (Python package installer)

### Option 1: Setup with Script

1. Clone the repository:
```bash
git clone https://github.com/yourusername/astra.git
cd astra
```

2. Run the setup script:
```bash
python setup.py
```

3. Activate the virtual environment:
   - **Windows:** `venv\Scripts\activate`
   - **Linux/macOS:** `source venv/bin/activate`

4. Run Astra:
```bash
python main.py
```

### Option 2: Manual Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/astra.git
cd astra
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - **Windows:** `venv\Scripts\activate`
   - **Linux/macOS:** `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run Astra:
```bash
python main.py
```

## 🧰 Tool Guide

### Port Scanner
Scan target systems for open ports and identify running services:
- Enter a hostname or IP address
- Specify port range (1-65535)
- Set timeout value
- View color-coded results (green for open ports, red for closed)

### DNS Analyzer
Analyze DNS records for a domain:
- Enter a domain name
- Select record types to query (A, AAAA, MX, TXT, etc.)
- View detailed results for each record type

### Subdomain Enumeration
Discover subdomains of a target domain:
- Enter a domain name
- Use default or custom wordlist
- Adjust thread count for performance
- View discovered subdomains with IP addresses

### Web Vulnerability Scanner
Scan websites for common security vulnerabilities:
- Enter a URL to scan
- Select vulnerability types to check
- View detected vulnerabilities with severity ratings
- Get remediation recommendations

### SSL/TLS Checker
Validate SSL/TLS configuration:
- Enter a hostname
- Specify port (default: 443)
- View certificate details, expiration, and security assessment
- Get security recommendations

### Theme Editor
Customize application appearance:
- Select from built-in themes (Dark, Light, Hacker)
- Create new custom themes
- Adjust colors, fonts, and UI elements
- Save, export, and import themes

## 📂 Project Structure

- `/core` - Core functionalities for security tools
- `/modules` - Individual hacking tool scripts
- `/utils` - Helper functions and utilities
- `/docs` - Documentation and images
- `/config` - Configuration files and themes
- `/ui` - UI components and pages

## ⚠️ Disclaimer

This project is intended for educational purposes only. Use responsibly and only on systems you have permission to test. Unauthorized testing of systems is illegal and unethical.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
