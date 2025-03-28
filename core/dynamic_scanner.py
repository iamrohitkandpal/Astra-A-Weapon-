"""
Dynamic scanner for detecting JavaScript-based vulnerabilities using Selenium
"""

import threading
import time
import re
import tempfile
import os
import json
import random
from urllib.parse import urljoin, urlparse, parse_qs
from PyQt6.QtCore import QObject, pyqtSignal

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import (
        TimeoutException, WebDriverException, StaleElementReferenceException,
        ElementNotInteractableException, InvalidArgumentException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Import AI modules
try:
    from core.ai_threat_detection import AIThreatDetector
    AI_THREAT_DETECTION_AVAILABLE = True
except ImportError:
    AI_THREAT_DETECTION_AVAILABLE = False

try:
    from core.ml_fuzzer import MLFuzzer
    ML_FUZZER_AVAILABLE = True
except ImportError:
    ML_FUZZER_AVAILABLE = False

class DynamicScanner(QObject):
    """
    Dynamic web scanner that uses Selenium to interact with JavaScript and detect dynamic vulnerabilities
    """
    
    # Signals
    progress_update = pyqtSignal(int)
    result_update = pyqtSignal(str, str, str, str)  # vulnerability, url, description, severity
    log_message = pyqtSignal(str)
    scan_completed = pyqtSignal()
    scan_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self.driver = None
        self.test_payloads = {
            'xss': [
                '<img src=x onerror=alert(1)>',
                '<svg onload=alert(1)>',
                '"><script>alert(1)</script>',
                '\'><script>alert(1)</script>',
                'javascript:alert(1)',
                '";alert(1);//',
                '\';alert(1);//',
                'onmouseover=alert(1)//',
                '<img src="x" onerror="alert(\'XSS\')">',
                '<body onload=alert(1)>',
                '<iframe src="javascript:alert(1)">',
                '<sCript>alert(1)</scRipt>',
                '<script>prompt(1)</script>',
                '<script>confirm(1)</script>',
                '<script>throw new Error("XSS Test")</script>'
            ],
            'dom_xss': [
                '?search=<img src=x onerror=alert(1)>',
                '?q=<svg onload=alert(1)>',
                '#<script>alert(1)</script>',
                '?name=<script>alert(1)</script>',
                '?id=<img src=x onerror=alert(1)>',
                '?value=<img src="x" onerror="alert(\'XSS\')">',
                '?input=<sCript>alert(1)</scRipt>'
            ],
            'open_redirect': [
                '//evil.com',
                'https://evil.com',
                '\\\\evil.com',
                'javascript:alert(1)',
                'data:text/html,<script>alert(1)</script>',
                '//google.com%252f@evil.com',
                '/\\evil.com',
                'https:evil.com'
            ],
            'file_inclusion': [
                '../../../etc/passwd',
                '../../../../windows/win.ini',
                '/etc/passwd',
                'C:\\Windows\\system.ini',
                'file:///etc/passwd',
                'php://filter/convert.base64-encode/resource=../config.php'
            ]
        }
        
        # Initialize AI modules if available
        self.ai_detector = None
        if AI_THREAT_DETECTION_AVAILABLE:
            try:
                self.ai_detector = AIThreatDetector()
                self.log_message.emit("AI Threat Detection initialized successfully")
            except Exception as e:
                self.log_message.emit(f"Failed to initialize AI Threat Detection: {e}")
        
        self.ml_fuzzer = None
        if ML_FUZZER_AVAILABLE:
            try:
                self.ml_fuzzer = MLFuzzer()
                # Connect fuzzer signals
                self.ml_fuzzer.fuzz_progress.connect(self._on_fuzz_progress)
                self.ml_fuzzer.fuzz_result.connect(self._on_fuzz_result)
                self.ml_fuzzer.fuzz_log.connect(self._on_fuzz_log)
                self.ml_fuzzer.fuzz_error.connect(self._on_fuzz_error)
                self.ml_fuzzer.fuzz_complete.connect(self._on_fuzz_complete)
                self.log_message.emit("ML-powered Fuzzer initialized successfully")
            except Exception as e:
                self.log_message.emit(f"Failed to initialize ML Fuzzer: {e}")
        
        # Detect if running in a container
        self.in_container = os.path.exists('/.dockerenv')
    
    # Signal handlers for ML fuzzer
    def _on_fuzz_progress(self, progress):
        """Handle fuzzer progress updates"""
        # Scale the progress to fit in our overall progress
        # Fuzzing is just one part of scanning, so it takes up a portion
        scaled_progress = 60 + int(progress * 0.3)  # 60-90% of overall progress
        self.progress_update.emit(min(scaled_progress, 90))
    
    def _on_fuzz_result(self, vulnerability_type, url, description, severity):
        """Handle fuzzer results"""
        # Add AI-suggested mitigations
        if self.ai_detector:
            try:
                # Extract the payload from the description if possible
                payload_match = re.search(r"payload: '(.*?)'", description)
                payload = payload_match.group(1) if payload_match else ""
                
                # Identify threat type from vulnerability type
                threat_type = self._map_vuln_to_threat_type(vulnerability_type)
                
                # Get suggested mitigations
                mitigations = self.ai_detector._generate_mitigations(threat_type, payload)
                
                # Calculate risk score
                risk_score = self._calculate_risk_score(vulnerability_type, severity, url)
                
                # Enhance description with mitigations and risk score
                enhanced_description = (
                    f"{description}\n\n"
                    f"🔍 Risk Score: {risk_score}/100\n\n"
                    f"🛡️ AI-Suggested Mitigations:\n"
                )
                
                for i, mitigation in enumerate(mitigations[:5], 1):  # Top 5 mitigations
                    enhanced_description += f"{i}. {mitigation}\n"
                
                # Forward the enhanced result
                self.result_update.emit(
                    vulnerability_type,
                    url,
                    enhanced_description,
                    severity
                )
            except Exception as e:
                # Fall back to original description if enhancement fails
                self.log_message.emit(f"Error enhancing result with AI: {str(e)}")
                self.result_update.emit(vulnerability_type, url, description, severity)
        else:
            # Just forward the original result if AI is not available
            self.result_update.emit(vulnerability_type, url, description, severity)
    
    def _on_fuzz_log(self, message):
        """Handle fuzzer log messages"""
        self.log_message.emit(f"[ML Fuzzer] {message}")
    
    def _on_fuzz_error(self, message):
        """Handle fuzzer errors"""
        self.log_message.emit(f"[ML Fuzzer] Error: {message}")
    
    def _on_fuzz_complete(self):
        """Handle fuzzer completion"""
        self.log_message.emit("ML-powered fuzzing completed")
    
    def _map_vuln_to_threat_type(self, vulnerability_type):
        """Map vulnerability types to AI detector threat types"""
        mapping = {
            "SQL Injection": "SQL Injection",
            "Cross-Site Scripting (XSS)": "Cross-Site Scripting (XSS)",
            "DOM-Based XSS": "Cross-Site Scripting (XSS)",
            "File Inclusion": "Path Traversal",
            "Open Redirect": "Open Redirect",
            "Command Injection": "Command Injection",
            "Potential Zero-Day Vulnerability": "Unknown/Other",
            "Server Error": "Unknown/Other",
            "Potential DOM Vulnerability": "Cross-Site Scripting (XSS)"
        }
        return mapping.get(vulnerability_type, "Unknown/Other")
    
    def _calculate_risk_score(self, vulnerability_type, severity, url):
        """Calculate a risk score from 0-100 based on various factors"""
        # Base score by severity
        base_score = {
            "LOW": 20,
            "MEDIUM": 50,
            "HIGH": 80,
            "CRITICAL": 95
        }.get(severity, 30)
        
        # Adjust based on vulnerability type
        type_modifier = {
            "SQL Injection": 20,
            "Cross-Site Scripting (XSS)": 15,
            "DOM-Based XSS": 15,
            "File Inclusion": 18,
            "Command Injection": 20,
            "Open Redirect": 10,
            "Server Error": 5,
            "Potential Zero-Day Vulnerability": 25,
            "Missing Security Header": 5,
            "Information Disclosure": 8
        }.get(vulnerability_type, 0)
        
        # URL context factors
        url_ctx_score = 0
        if "/admin" in url.lower():
            url_ctx_score += 15
        if "/login" in url.lower() or "/account" in url.lower() or "/user" in url.lower():
            url_ctx_score += 10
        if "/api" in url.lower():
            url_ctx_score += 8
        
        # Calculate final score with cap
        final_score = min(base_score + type_modifier + url_ctx_score, 100)
        return final_score
    
    def _init_selenium(self):
        """Initialize Selenium webdriver"""
        if not SELENIUM_AVAILABLE:
            self.log_message.emit("Selenium is not installed. Dynamic scanning disabled.")
            self.scan_error.emit("Selenium is not installed. Please install it with 'pip install selenium'")
            return False
        
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-notifications')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Create a directory for Chrome to write data
            self.temp_dir = tempfile.TemporaryDirectory()
            options.add_argument(f'--user-data-dir={self.temp_dir.name}')
            
            try:
                # Try creating a driver directly
                self.driver = webdriver.Chrome(options=options)
            except WebDriverException as e:
                if 'chromedriver' in str(e).lower():
                    # ChromeDriver not found or version issue
                    self.log_message.emit("ChromeDriver issue: trying to use ChromeDriverManager...")
                    try:
                        from webdriver_manager.chrome import ChromeDriverManager
                        service = Service(ChromeDriverManager().install())
                        self.driver = webdriver.Chrome(service=service, options=options)
                    except ImportError:
                        self.log_message.emit("webdriver_manager not installed. Please install it with 'pip install webdriver-manager'")
                        return False
                else:
                    raise
            
            # Set timeouts
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(5)
            
            # Add custom JavaScript error detection
            self.driver.execute_script("""
                window.jsErrors = [];
                window.addEventListener('error', function(e) {
                    window.jsErrors.push({
                        message: e.message,
                        source: e.filename,
                        lineno: e.lineno,
                        colno: e.colno,
                        stack: e.error ? e.error.stack : ''
                    });
                });
            """)
            
            return True
            
        except Exception as e:
            self.log_message.emit(f"Failed to initialize Selenium: {str(e)}")
            self.scan_error.emit(f"Failed to initialize Selenium: {str(e)}")
            return False
    
    def scan(self, url, scan_options=None):
        """
        Perform a dynamic scan of the target URL
        
        Args:
            url (str): The URL to scan
            scan_options (dict): Options for the scan
        """
        if not url:
            self.scan_error.emit("No URL provided")
            return
        
        # Reset stop event
        self._stop_event.clear()
        
        # Initialize scan options
        if scan_options is None:
            scan_options = {
                'check_xss': True,
                'check_open_redirect': True,
                'check_file_inclusion': True,
                'use_ai_detection': AI_THREAT_DETECTION_AVAILABLE,
                'use_ml_fuzzing': ML_FUZZER_AVAILABLE,
                'max_scan_depth': 2,
                'max_pages': 20,
                'max_forms': 10
            }
        
        # Initialize Selenium
        if not self._init_selenium():
            return
        
        # Start scanning
        try:
            self.log_message.emit(f"Starting dynamic scan of {url}")
            self.progress_update.emit(5)
            
            # Load the initial page
            self.driver.get(url)
            self.log_message.emit("Successfully loaded initial page")
            
            # Wait for page to be loaded
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check for JavaScript errors
            self._check_js_errors(url)
            
            # Find forms and links for testing
            forms = self._find_forms()
            links = self._find_links()
            
            # Progress tracker
            total_items = (
                (len(forms) if scan_options['check_xss'] else 0) +
                (len(links) if scan_options['check_open_redirect'] else 0) +
                (len(forms) if scan_options['check_file_inclusion'] else 0)
            )
            
            if total_items == 0:
                total_items = 1  # Avoid division by zero
                
            current_progress = 5
            items_processed = 0
            
            # Test for DOM XSS via URL parameters
            if scan_options['check_xss']:
                self._test_dom_xss_in_url(url)
            
            # Test forms for XSS
            if scan_options['check_xss'] and forms:
                self.log_message.emit(f"Testing {len(forms)} forms for XSS vulnerabilities")
                for i, form in enumerate(forms[:scan_options['max_forms']]):
                    if self._stop_event.is_set():
                        break
                        
                    try:
                        self._test_form_xss(form, url)
                    except Exception as e:
                        self.log_message.emit(f"Error testing form {i+1}: {str(e)}")
                    
                    # Update progress
                    items_processed += 1
                    new_progress = current_progress + int((items_processed / total_items) * 60)  # First 60% for basic tests
                    self.progress_update.emit(min(new_progress, 60))
            
            # Test for open redirects
            if scan_options['check_open_redirect'] and links:
                self.log_message.emit(f"Testing {len(links)} links for open redirect vulnerabilities")
                for i, link in enumerate(links[:scan_options['max_pages']]):
                    if self._stop_event.is_set():
                        break
                        
                    try:
                        self._test_open_redirect(link, url)
                    except Exception as e:
                        self.log_message.emit(f"Error testing link {i+1}: {str(e)}")
                    
                    # Update progress
                    items_processed += 1
                    new_progress = current_progress + int((items_processed / total_items) * 60)
                    self.progress_update.emit(min(new_progress, 60))
            
            # Test for file inclusion
            if scan_options['check_file_inclusion'] and forms:
                self.log_message.emit(f"Testing {len(forms)} forms for file inclusion vulnerabilities")
                for i, form in enumerate(forms[:scan_options['max_forms']]):
                    if self._stop_event.is_set():
                        break
                        
                    try:
                        self._test_file_inclusion(form, url)
                    except Exception as e:
                        self.log_message.emit(f"Error testing form {i+1} for file inclusion: {str(e)}")
                    
                    # Update progress
                    items_processed += 1
                    new_progress = current_progress + int((items_processed / total_items) * 60)
                    self.progress_update.emit(min(new_progress, 60))
            
            # Run AI-powered payload analysis if enabled
            if scan_options['use_ai_detection'] and self.ai_detector:
                self.log_message.emit("Running AI analysis on user inputs...")
                
                # Collect input fields for AI analysis
                input_elements = []
                if forms:
                    for form in forms[:scan_options['max_forms']]:
                        try:
                            inputs = self._find_inputs(form)
                            input_elements.extend(inputs)
                        except Exception:
                            pass
                
                # Analyze inputs with AI
                self._analyze_inputs_with_ai(input_elements, url)
                
                # Progress update
                self.progress_update.emit(70)  # Up to 70% after AI analysis
            
            # Run ML-powered fuzzing if enabled
            if scan_options['use_ml_fuzzing'] and self.ml_fuzzer:
                self.log_message.emit("Starting ML-powered fuzzing for zero-day vulnerabilities...")
                
                # Run the fuzzer asynchronously
                try:
                    # Get cookies and headers from selenium session to pass to fuzzer
                    cookies = {}
                    for cookie in self.driver.get_cookies():
                        cookies[cookie['name']] = cookie['value']
                    
                    # Run fuzzing with a shallow depth to avoid taking too long
                    self.ml_fuzzer.fuzz(
                        url=url,
                        depth=scan_options.get('max_scan_depth', 2),
                        request_limit=100
                    )
                    
                    # Progress update happens through fuzzer signals
                except Exception as e:
                    self.log_message.emit(f"Error during ML-powered fuzzing: {str(e)}")
                    
                # Progress update
                self.progress_update.emit(90)  # Up to 90% after fuzzing
            
            # Set final progress
            self.progress_update.emit(100)
            self.log_message.emit("Dynamic scan completed")
            self.scan_completed.emit()
            
        except Exception as e:
            self.log_message.emit(f"Error during dynamic scan: {str(e)}")
            self.scan_error.emit(f"Error during dynamic scan: {str(e)}")
        finally:
            # Clean up
            self._cleanup()
    
    def _analyze_inputs_with_ai(self, input_elements, base_url):
        """Analyze input elements with AI to predict potential vulnerabilities"""
        if not self.ai_detector or not input_elements:
            return
            
        try:
            # Get attributes and properties that might indicate vulnerability
            for input_elem in input_elements:
                try:
                    input_type = input_elem.get_attribute("type") or "text"
                    input_name = input_elem.get_attribute("name") or ""
                    input_id = input_elem.get_attribute("id") or ""
                    placeholder = input_elem.get_attribute("placeholder") or ""
                    
                    # Skip files, checkboxes, etc.
                    if input_type in ["checkbox", "radio", "submit", "button", "hidden"]:
                        continue
                    
                    # Create context string for analysis
                    context = f"Input field - Type: {input_type}, Name: {input_name}, ID: {input_id}, Placeholder: {placeholder}"
                    
                    # Analyze the context for potential vulnerabilities
                    analysis_result = self.ai_detector.analyze_payload(context, base_url)
                    
                    # If the AI thinks this might be vulnerable, report it
                    pattern_result = analysis_result.get('pattern_detection', {})
                    if pattern_result.get('is_malicious', False) and pattern_result.get('confidence', 0) > 0.6:
                        # High confidence detection
                        pattern_type = pattern_result.get('pattern_type', 'Unknown')
                        
                        # Get suggested mitigations
                        mitigations = analysis_result.get('suggested_mitigations', [])
                        mitigations_text = "\n".join([f"- {m}" for m in mitigations[:5]])
                        
                        # Calculate risk score
                        risk_score = analysis_result.get('risk_score', 50)
                        
                        # Report as potential vulnerability
                        description = (
                            f"AI-detected potential vulnerability in input field: '{input_name or input_id}'\n"
                            f"This field appears to be vulnerable to {pattern_type} attacks.\n\n"
                            f"🔍 Risk Score: {risk_score}/100\n\n"
                            f"🛡️ AI-Suggested Mitigations:\n{mitigations_text}"
                        )
                        
                        self.result_update.emit(
                            f"Potential {pattern_type}",
                            base_url,
                            description,
                            "MEDIUM"  # Medium severity for AI predictions to avoid false positives
                        )
                        
                        self.log_message.emit(f"AI detected potential {pattern_type} vulnerability in {input_name or input_id}")
                        
                except Exception as e:
                    self.log_message.emit(f"Error analyzing input with AI: {str(e)}")
                    
        except Exception as e:
            self.log_message.emit(f"Error during AI input analysis: {str(e)}")
    
    def stop(self):
        """Stop the scanning process"""
        self._stop_event.set()
        self.log_message.emit("Stopping dynamic scan...")
        
        # Stop ML fuzzer if running
        if self.ml_fuzzer:
            try:
                self.ml_fuzzer.stop()
            except Exception as e:
                self.log_message.emit(f"Error stopping ML fuzzer: {str(e)}")
    
    def _cleanup(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            if hasattr(self, 'temp_dir'):
                self.temp_dir.cleanup()
        except Exception as e:
            self.log_message.emit(f"Error cleaning up resources: {str(e)}")
    
    def _find_forms(self):
        """Find forms on the page"""
        try:
            return self.driver.find_elements(By.TAG_NAME, "form")
        except Exception as e:
            self.log_message.emit(f"Error finding forms: {str(e)}")
            return []
    
    def _find_links(self):
        """Find links on the page"""
        try:
            return self.driver.find_elements(By.TAG_NAME, "a")
        except Exception as e:
            self.log_message.emit(f"Error finding links: {str(e)}")
            return []
    
    def _find_inputs(self, form):
        """Find input elements in a form"""
        try:
            return form.find_elements(By.TAG_NAME, "input")
        except Exception as e:
            self.log_message.emit(f"Error finding inputs in form: {str(e)}")
            return []
    
    def _test_form_xss(self, form, base_url):
        """Test a form for XSS vulnerabilities"""
        inputs = self._find_inputs(form)
        text_inputs = [
            input_elem for input_elem in inputs 
            if input_elem.get_attribute("type") in ["text", "search", "url", "tel", "email", None]
        ]
        
        if not text_inputs:
            return
        
        # Capture initial URL before form submission
        initial_url = self.driver.current_url
        
        # Test with XSS payloads
        for payload in self.test_payloads['xss'][:5]:  # Limit to first 5 payloads
            if self._stop_event.is_set():
                break
                
            try:
                # Reset page state
                self.driver.get(initial_url)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Re-find the form and inputs after page reload
                forms = self._find_forms()
                if not forms:
                    self.log_message.emit("Cannot find the form after page reload")
                    break
                    
                # Try to find the same form
                new_form = None
                for f in forms:
                    if f.get_attribute("action") == form.get_attribute("action") and \
                       f.get_attribute("method") == form.get_attribute("method"):
                        new_form = f
                        break
                
                if not new_form:
                    new_form = forms[0]  # Just use the first form if we can't match
                
                # Get new inputs    
                inputs = self._find_inputs(new_form)
                text_inputs = [
                    input_elem for input_elem in inputs 
                    if input_elem.get_attribute("type") in ["text", "search", "url", "tel", "email", None]
                ]
                
                if not text_inputs:
                    break
                
                # Fill all text inputs with the payload
                for input_elem in text_inputs:
                    try:
                        # Clear existing value
                        input_elem.clear()
                        # Input the XSS payload
                        input_elem.send_keys(payload)
                    except (ElementNotInteractableException, StaleElementReferenceException):
                        # Skip if we can't interact with the element
                        continue
                
                # Submit the form
                try:
                    submit_button = new_form.find_element(By.XPATH, ".//input[@type='submit'] | .//button[@type='submit'] | .//button")
                    submit_button.click()
                except Exception:
                    # Try submitting the form with JS if we can't find a submit button
                    self.driver.execute_script("arguments[0].submit();", new_form)
                
                # Wait for page to load
                time.sleep(2)
                
                # Check for XSS execution
                if self._check_xss_success():
                    # Get the URL where XSS was detected
                    vulnerable_url = self.driver.current_url
                    
                    # Report the vulnerability
                    description = f"XSS vulnerability detected using payload: {payload}"
                    self.result_update.emit(
                        "Cross-Site Scripting (XSS)", 
                        vulnerable_url, 
                        description, 
                        "HIGH"
                    )
                    
                    # Log the finding
                    self.log_message.emit(f"XSS vulnerability found in form with payload: {payload}")
                    
                    # Only report one vulnerability per form to avoid spam
                    break
                    
            except Exception as e:
                self.log_message.emit(f"Error testing form for XSS: {str(e)}")
    
    def _test_dom_xss_in_url(self, base_url):
        """Test for DOM-based XSS via URL parameters"""
        # Parse the URL to detect existing parameters
        parsed_url = urlparse(base_url)
        existing_params = parse_qs(parsed_url.query)
        
        # Create test URLs
        test_urls = []
        
        # If there are existing parameters, modify them
        if existing_params:
            for param, values in existing_params.items():
                for payload in self.test_payloads['dom_xss'][:3]:  # Limit to first 3 to avoid too many tests
                    # Get payload without the parameter part
                    if '=' in payload:
                        _, payload_value = payload.split('=', 1)
                    else:
                        payload_value = payload
                    
                    # Create a new params dictionary
                    new_params = existing_params.copy()
                    new_params[param] = [payload_value]
                    
                    # Reconstruct the query string
                    from urllib.parse import urlencode
                    query_string = urlencode(new_params, doseq=True)
                    
                    # Construct the test URL
                    test_url = parsed_url._replace(query=query_string).geturl()
                    test_urls.append(test_url)
        else:
            # No existing parameters, try common parameter names
            common_params = ['q', 'search', 'id', 'query', 'page', 'name', 'input']
            
            for param in common_params:
                for payload in self.test_payloads['dom_xss'][:2]:  # Limit to first 2 payloads
                    # Get payload without the parameter part
                    if '=' in payload:
                        _, payload_value = payload.split('=', 1)
                    else:
                        payload_value = payload
                    
                    # Add parameter to URL
                    if '?' in base_url:
                        test_url = f"{base_url}&{param}={payload_value}"
                    else:
                        test_url = f"{base_url}?{param}={payload_value}"
                    
                    test_urls.append(test_url)
        
        # Also try URL fragment attacks
        for payload in self.test_payloads['dom_xss'][:2]:  # Limit to first 2 payloads
            if '#' in payload:
                fragment = payload.split('#', 1)[1]
                test_urls.append(f"{base_url}#{fragment}")
        
        # Test each URL
        for test_url in test_urls:
            if self._stop_event.is_set():
                break
                
            try:
                # Load the URL
                self.driver.get(test_url)
                
                # Wait for page to load
                time.sleep(2)
                
                # Check for XSS execution
                if self._check_xss_success():
                    # Report the vulnerability
                    description = f"DOM-based XSS vulnerability detected in URL: {test_url}"
                    self.result_update.emit(
                        "DOM-Based XSS", 
                        test_url, 
                        description, 
                        "HIGH"
                    )
                    
                    # Log the finding
                    self.log_message.emit(f"DOM-based XSS vulnerability found in URL: {test_url}")
                    
                    # Don't break here - continue testing other parameters
                    
            except Exception as e:
                self.log_message.emit(f"Error testing URL for DOM XSS: {str(e)}")
    
    def _test_open_redirect(self, link, base_url):
        """Test a link for open redirect vulnerabilities"""
        link_href = link.get_attribute("href")
        if not link_href:
            return
            
        # Skip links that are clearly not redirect endpoints
        if link_href.startswith("javascript:") or link_href.startswith("mailto:") or link_href.startswith("tel:"):
            return
            
        # Parse the link URL
        parsed_link = urlparse(link_href)
        
        # Check if the link has redirect-like parameters
        redirect_params = ['redirect', 'url', 'next', 'target', 'redir', 'destination', 'return', 'returnto', 'goto', 'link']
        
        # Get query parameters
        from urllib.parse import parse_qs
        query_params = parse_qs(parsed_link.query)
        
        # If there's a parameter that looks like a redirect, test it
        for param_name in redirect_params:
            if param_name in query_params:
                self._test_redirect_param(link_href, param_name, query_params[param_name][0])
                break
    
    def _test_redirect_param(self, url, param_name, original_value):
        """Test a redirect parameter for open redirect vulnerabilities"""
        for payload in self.test_payloads['open_redirect'][:3]:  # Limit to first 3 payloads
            if self._stop_event.is_set():
                break
                
            try:
                # Create the test URL by replacing the parameter value
                test_url = url.replace(f"{param_name}={original_value}", f"{param_name}={payload}")
                
                # Store the current URL
                current_url = self.driver.current_url
                
                # Navigate to the test URL
                self.driver.get(test_url)
                
                # Wait for any redirect to occur
                time.sleep(3)
                
                # Check if we've been redirected to an unexpected URL
                final_url = self.driver.current_url
                
                # Check if the redirect happened
                if payload in final_url or "evil.com" in final_url:
                    # Report the vulnerability
                    description = f"Open redirect vulnerability detected using parameter '{param_name}' with payload '{payload}'"
                    self.result_update.emit(
                        "Open Redirect", 
                        url, 
                        description, 
                        "MEDIUM"
                    )
                    
                    # Log the finding
                    self.log_message.emit(f"Open redirect vulnerability found in URL: {url} using parameter: {param_name}")
                    
                    # Only report one vulnerability per URL
                    break
                    
            except Exception as e:
                self.log_message.emit(f"Error testing redirect parameter: {str(e)}")
    
    def _test_file_inclusion(self, form, base_url):
        """Test a form for file inclusion vulnerabilities"""
        inputs = self._find_inputs(form)
        text_inputs = [
            input_elem for input_elem in inputs 
            if input_elem.get_attribute("type") in ["text", "search", "url", "file", None]
        ]
        
        if not text_inputs:
            return
        
        # Capture initial URL before form submission
        initial_url = self.driver.current_url
        
        # Test with file inclusion payloads
        for payload in self.test_payloads['file_inclusion'][:3]:  # Limit to first 3 payloads
            if self._stop_event.is_set():
                break
                
            try:
                # Reset page state
                self.driver.get(initial_url)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Re-find the form and inputs after page reload
                forms = self._find_forms()
                if not forms:
                    break
                
                # Try to find the same form
                new_form = None
                for f in forms:
                    if f.get_attribute("action") == form.get_attribute("action") and \
                       f.get_attribute("method") == form.get_attribute("method"):
                        new_form = f
                        break
                
                if not new_form:
                    new_form = forms[0]  # Just use the first form if we can't match
                
                # Get new inputs
                inputs = self._find_inputs(new_form)
                text_inputs = [
                    input_elem for input_elem in inputs 
                    if input_elem.get_attribute("type") in ["text", "search", "url", "file", None]
                ]
                
                if not text_inputs:
                    break
                
                # Try each input with the payload
                for input_elem in text_inputs:
                    try:
                        # Clear existing value
                        input_elem.clear()
                        # Input the file inclusion payload
                        input_elem.send_keys(payload)
                    except (ElementNotInteractableException, StaleElementReferenceException):
                        # Skip if we can't interact with the element
                        continue
                
                # Submit the form
                try:
                    submit_button = new_form.find_element(By.XPATH, ".//input[@type='submit'] | .//button[@type='submit'] | .//button")
                    submit_button.click()
                except Exception:
                    # Try submitting the form with JS if we can't find a submit button
                    self.driver.execute_script("arguments[0].submit();", new_form)
                
                # Wait for page to load
                time.sleep(2)
                
                # Check for file inclusion success
                if self._check_file_inclusion_success():
                    # Get the URL where file inclusion was detected
                    vulnerable_url = self.driver.current_url
                    
                    # Report the vulnerability
                    description = f"Potential file inclusion vulnerability detected using payload: {payload}"
                    self.result_update.emit(
                        "File Inclusion", 
                        vulnerable_url, 
                        description, 
                        "HIGH"
                    )
                    
                    # Log the finding
                    self.log_message.emit(f"File inclusion vulnerability found with payload: {payload}")
                    
                    # Only report one vulnerability per form
                    break
                    
            except Exception as e:
                self.log_message.emit(f"Error testing form for file inclusion: {str(e)}")
    
    def _check_xss_success(self):
        """Check if XSS attack was successful by looking for JavaScript alerts or errors"""
        try:
            # Check for JavaScript errors related to XSS
            js_errors = self.driver.execute_script("return window.jsErrors;")
            
            # If we have JS errors, check if they're related to XSS payloads
            if js_errors:
                for error in js_errors:
                    # Check for common XSS error patterns
                    if "XSS" in error.get('message', '') or "alert" in error.get('message', ''):
                        return True
            
            # Check for XSS markers in the page
            alerts = self.driver.execute_script("""
                if (window.alert) {
                    var originalAlert = window.alert;
                    window.alert = function(msg) {
                        document.body.setAttribute('data-xss-alert', msg);
                        return true;
                    };
                    return document.body.getAttribute('data-xss-alert');
                }
                return null;
            """)
            
            if alerts:
                return True
                
            # Check for alert messages in the DOM
            alert_attrs = self.driver.execute_script("""
                return document.body.getAttribute('data-xss-alert');
            """)
            
            if alert_attrs:
                return True
                
            return False
            
        except Exception as e:
            self.log_message.emit(f"Error checking XSS success: {str(e)}")
            return False
    
    def _check_file_inclusion_success(self):
        """Check if file inclusion attack was successful"""
        try:
            # Look for common patterns that indicate successful file inclusion
            page_source = self.driver.page_source.lower()
            
            # Unix passwd file signatures
            if "root:x:0:0" in page_source or "nobody:x:" in page_source:
                return True
                
            # Windows file signatures
            if "windows nt" in page_source and "[fonts]" in page_source:
                return True
                
            # PHP file inclusion signatures
            if "<?php" in page_source or "define('db_name'" in page_source:
                return True
                
            # Configuration file signatures
            if "db_password" in page_source or "database_password" in page_source:
                return True
                
            # Base64 encoded content (common with php://filter exploits)
            if re.search(r'PD9waH[A-Za-z0-9+/=]{100,}', page_source):
                return True
                
            return False
            
        except Exception as e:
            self.log_message.emit(f"Error checking file inclusion success: {str(e)}")
            return False
    
    def _check_js_errors(self, url):
        """Check for JavaScript errors and report possible vulnerabilities"""
        try:
            # Get any JavaScript errors that occurred
            js_errors = self.driver.execute_script("return window.jsErrors;")
            
            if js_errors:
                for error in js_errors:
                    # Report each error
                    self.log_message.emit(f"JavaScript error: {error.get('message', 'Unknown error')}")
                    
                    # Check if error might indicate a vulnerability
                    if ('undefined' in error.get('message', '').lower() and 
                        'property' in error.get('message', '').lower()):
                        # This might be a DOM-based vulnerability
                        description = (
                            f"Potential DOM vulnerability detected: {error.get('message', 'Unknown error')} "
                            f"on line {error.get('lineno', '?')} of {error.get('source', 'unknown')}"
                        )
                        
                        self.result_update.emit(
                            "Potential DOM Vulnerability",
                            url,
                            description,
                            "MEDIUM"
                        )
                        
        except Exception as e:
            self.log_message.emit(f"Error checking JavaScript errors: {str(e)}")
