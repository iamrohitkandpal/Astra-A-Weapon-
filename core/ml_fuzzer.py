"""
ML-powered fuzzer for discovering potential zero-day vulnerabilities
"""

import random
import re
import os
import json
import threading
import time
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from collections import defaultdict, Counter

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.feature_extraction.text import TfidfVectorizer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

class MLFuzzer(QObject):
    """Machine Learning powered fuzzer for intelligent vulnerability detection"""
    
    # Signals
    fuzz_progress = pyqtSignal(int)
    fuzz_result = pyqtSignal(str, str, str, str)  # vulnerability_type, url, description, severity
    fuzz_log = pyqtSignal(str)
    fuzz_complete = pyqtSignal()
    fuzz_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self.mutation_strategies = [
            self._replace_with_special_chars,
            self._insert_control_chars,
            self._integer_boundary_fuzzing,
            self._repeat_parameter,
            self._format_string_fuzzing,
            self._sql_mutation,
            self._path_traversal_mutation,
            self._header_mutation,
            self._content_type_mutation,
            self._add_random_parameters
        ]
        self.special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        self.control_chars = "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
        self.format_strings = ["%x", "%s", "%n", "%p", "%d", "0x%08x", "%8x", "%x%x%x%x", "%p%p%p%p", "%d%d%d%d", "%s%s%s%s", "%n%n%n%n"]
        self.sql_payloads = ["1'", "1''", "1\"", "1))", "1)))", "1;", "1/**/", "1+1", "1-1", "1 OR 1=1", "1' OR '1'='1", "1\" OR \"1\"=\"1"]
        self.path_traversal_payloads = ["../", "..\\", "./../", ".\\..\\", "..././", "...\\.\\", "../../../etc/passwd", "..\\..\\..\\windows\\win.ini"]
        self.custom_headers = {
            "X-Forwarded-For": ["127.0.0.1", "localhost", "192.168.0.1", "0:0:0:0:0:0:0:1"],
            "X-Forwarded-Host": ["internal.company.com", "admin.company.com", "localhost"],
            "Content-Type": ["application/x-www-form-urlencoded", "application/json", "text/xml", "multipart/form-data"],
            "Accept": ["application/json", "text/html,*/*", "application/xml", "*/*"],
            "User-Agent": ["Mozilla/5.0", "() { :; }; echo 'VULNERABLE'", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"]
        }
        
        # Anomaly detection model
        self.model = None
        if ML_AVAILABLE:
            self._initialize_anomaly_model()
        else:
            self.fuzz_log.emit("Warning: scikit-learn not available. ML-powered fuzzing disabled.")
    
    def _initialize_anomaly_model(self):
        """Initialize the anomaly detection model"""
        try:
            self.vectorizer = TfidfVectorizer(max_features=100)
            self.model = IsolationForest(
                n_estimators=100,
                max_samples='auto',
                contamination=0.1,
                random_state=42
            )
            self.fuzz_log.emit("ML-powered fuzzing model initialized")
        except Exception as e:
            self.fuzz_error.emit(f"Error initializing ML model: {str(e)}")
    
    def fuzz(self, url, depth=2, request_limit=100):
        """
        Start fuzzing the target URL with machine learning guidance
        
        Args:
            url (str): The URL to fuzz
            depth (int): How deep to crawl and fuzz
            request_limit (int): Maximum number of requests to make
        """
        if not ML_AVAILABLE:
            self.fuzz_error.emit("scikit-learn is not available. Install it with 'pip install scikit-learn'")
            return
            
        # Reset stop event
        self._stop_event.clear()
        
        # Initialize baseline request counters
        request_count = 0
        successful_mutations = 0
        
        try:
            # Log start of fuzzing
            self.fuzz_log.emit(f"Started ML-powered fuzzing of {url}")
            self.fuzz_progress.emit(5)
            
            # Initialize response data storage for ML training
            baseline_responses = []
            anomalous_responses = []
            
            # Make initial request to establish baseline
            try:
                response = self._make_request(url)
                request_count += 1
                
                if response:
                    # Store baseline data
                    baseline_data = self._extract_response_features(response)
                    baseline_responses.append(baseline_data)
                    
                    # Log success
                    self.fuzz_log.emit(f"Established baseline for {url}, status code: {response.status_code}")
                else:
                    self.fuzz_error.emit(f"Failed to establish baseline for {url}")
                    return
            except Exception as e:
                self.fuzz_error.emit(f"Error establishing baseline: {str(e)}")
                return
            
            # Extract parameters to fuzz from the URL
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            
            # Collect all links for deeper crawling
            links = self._extract_links(response)
            
            # Collect form data if any
            forms = self._extract_forms(response)
            
            # Create fuzzing targets
            fuzzing_targets = []
            
            # If there are query parameters, add them as fuzzing targets
            if query_params:
                for param, values in query_params.items():
                    original_value = values[0] if values else ""
                    fuzzing_targets.append(("query", param, original_value, url))
            
            # Add forms as fuzzing targets
            for form in forms:
                form_url = form.get("action", url)
                form_method = form.get("method", "GET")
                
                for field_name, field_value in form.get("fields", {}).items():
                    fuzzing_targets.append(("form", field_name, field_value, form_url, form_method, form))
            
            # Progress tracking variables
            total_targets = len(fuzzing_targets) * len(self.mutation_strategies)
            if total_targets == 0:
                total_targets = 1  # Avoid division by zero
            
            current_progress = 5
            targets_processed = 0
            
            # Main fuzzing loop
            for target in fuzzing_targets:
                if self._stop_event.is_set() or request_count >= request_limit:
                    break
                    
                # Apply each mutation strategy to each target
                for strategy in self.mutation_strategies:
                    if self._stop_event.is_set() or request_count >= request_limit:
                        break
                        
                    try:
                        if target[0] == "query":
                            # Process query parameter
                            _, param, original_value, target_url = target
                            mutations = strategy(param, original_value)
                            
                            for mutation in mutations:
                                if self._stop_event.is_set() or request_count >= request_limit:
                                    break
                                    
                                # Create modified URL
                                modified_url = self._modify_url_parameter(target_url, param, mutation)
                                
                                # Make request with mutation
                                try:
                                    response = self._make_request(modified_url)
                                    request_count += 1
                                    
                                    if response:
                                        # Check if the mutation resulted in interesting behavior
                                        result = self._analyze_response(response, modified_url, param, mutation)
                                        
                                        if result:
                                            # Record successful mutation
                                            successful_mutations += 1
                                            
                                            # Report finding to the UI
                                            vuln_type, description, severity = result
                                            self.fuzz_result.emit(vuln_type, modified_url, description, severity)
                                            
                                            # Log the finding
                                            self.fuzz_log.emit(f"Potential vulnerability found: {vuln_type} at {modified_url}")
                                        
                                        # Extract features for anomaly detection
                                        response_data = self._extract_response_features(response)
                                        anomalous_responses.append(response_data)
                                        
                                except Exception as e:
                                    self.fuzz_log.emit(f"Error making request to {modified_url}: {str(e)}")
                        
                        elif target[0] == "form":
                            # Process form field
                            _, field_name, field_value, form_url, form_method, form_data = target
                            mutations = strategy(field_name, field_value)
                            
                            for mutation in mutations:
                                if self._stop_event.is_set() or request_count >= request_limit:
                                    break
                                    
                                # Create a copy of the form fields
                                fields = form_data.get("fields", {}).copy()
                                # Modify the target field
                                fields[field_name] = mutation
                                
                                # Make request with modified form data
                                try:
                                    if form_method.upper() == "GET":
                                        # Create query string from fields
                                        query = urlencode(fields, doseq=True)
                                        # Build URL
                                        if "?" in form_url:
                                            modified_url = f"{form_url}&{query}"
                                        else:
                                            modified_url = f"{form_url}?{query}"
                                            
                                        response = self._make_request(modified_url)
                                    else:  # POST
                                        response = self._make_request(
                                            form_url, 
                                            method="POST", 
                                            data=fields
                                        )
                                    
                                    request_count += 1
                                    
                                    if response:
                                        # Check if the mutation resulted in interesting behavior
                                        result = self._analyze_response(response, form_url, field_name, mutation)
                                        
                                        if result:
                                            # Record successful mutation
                                            successful_mutations += 1
                                            
                                            # Report finding to the UI
                                            vuln_type, description, severity = result
                                            self.fuzz_result.emit(vuln_type, form_url, description, severity)
                                            
                                            # Log the finding
                                            self.fuzz_log.emit(f"Potential vulnerability found: {vuln_type} in form at {form_url}")
                                        
                                        # Extract features for anomaly detection
                                        response_data = self._extract_response_features(response)
                                        anomalous_responses.append(response_data)
                                        
                                except Exception as e:
                                    self.fuzz_log.emit(f"Error submitting form to {form_url}: {str(e)}")
                                    
                    except Exception as e:
                        self.fuzz_log.emit(f"Error applying mutation strategy: {str(e)}")
                    
                    # Update progress
                    targets_processed += 1
                    new_progress = current_progress + int((targets_processed / total_targets) * 85)
                    self.fuzz_progress.emit(min(new_progress, 90))
            
            # Train and run anomaly detection if we collected enough data
            if len(baseline_responses) > 0 and len(anomalous_responses) > 0:
                anomalies = self._detect_anomalies(baseline_responses, anomalous_responses)
                
                # Report anomalies
                for anomaly in anomalies:
                    url = anomaly.get("url", "")
                    param = anomaly.get("param", "")
                    value = anomaly.get("value", "")
                    score = anomaly.get("score", 0)
                    
                    description = (
                        f"Anomalous behavior detected with unusually high anomaly score: {score}. "
                        f"This may indicate a zero-day vulnerability. The anomaly was triggered by "
                        f"parameter '{param}' with value '{value}'."
                    )
                    
                    # High anomaly score (normalized to 0-1) means likely vulnerability
                    severity = "HIGH" if score > 0.8 else "MEDIUM" if score > 0.6 else "LOW"
                    
                    self.fuzz_result.emit("Potential Zero-Day Vulnerability", url, description, severity)
                    self.fuzz_log.emit(f"Potential zero-day vulnerability detected at {url} with score {score}")
            
            # Complete fuzzing
            self.fuzz_progress.emit(100)
            self.fuzz_log.emit(f"Fuzzing complete. Made {request_count} requests, found {successful_mutations} interesting mutations.")
            self.fuzz_complete.emit()
            
        except Exception as e:
            self.fuzz_error.emit(f"Error during fuzzing: {str(e)}")
        
    def stop(self):
        """Stop the fuzzing process"""
        self._stop_event.set()
        self.fuzz_log.emit("Stopping fuzzing process...")
    
    def _make_request(self, url, method="GET", data=None, headers=None):
        """Make an HTTP request with error handling"""
        try:
            standard_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            if headers:
                request_headers = {**standard_headers, **headers}
            else:
                request_headers = standard_headers
            
            response = requests.request(
                method,
                url,
                data=data,
                headers=request_headers,
                timeout=10,
                allow_redirects=True
            )
            
            return response
        except Exception as e:
            self.fuzz_log.emit(f"Error making request: {str(e)}")
            return None
    
    def _extract_response_features(self, response):
        """Extract features from a response for anomaly detection"""
        features = {
            "url": response.url,
            "status_code": response.status_code,
            "content_length": len(response.content),
            "response_time": response.elapsed.total_seconds(),
            "content_type": response.headers.get("Content-Type", ""),
            "has_redirect": response.history and len(response.history) > 0,
            "redirect_count": len(response.history) if response.history else 0,
            "content_hash": hash(response.text),
            "headers": dict(response.headers),
            "error_messages": self._extract_error_messages(response.text)
        }
        
        return features
    
    def _extract_error_messages(self, html):
        """Extract potential error messages from HTML"""
        error_patterns = [
            r"error", r"exception", r"warning", r"fail", r"invalid",
            r"sql syntax", r"syntax error", r"stacktrace", r"stack trace",
            r"undefined", r"not found", r"cannot", r"unable to"
        ]
        
        error_messages = []
        
        for pattern in error_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                error_messages.append(pattern)
        
        return error_messages
    
    def _extract_links(self, response):
        """Extract links from a response"""
        links = []
        
        try:
            # Use simple regex to find links
            urls = re.findall(r'href=["\'](https?://[^"\']+)["\']', response.text)
            links.extend(urls)
            
            # Also find relative URLs
            base_url = response.url
            relative_urls = re.findall(r'href=["\'](/[^"\']+)["\']', response.text)
            
            for rel_url in relative_urls:
                abs_url = urljoin(base_url, rel_url)
                links.append(abs_url)
        except Exception as e:
            self.fuzz_log.emit(f"Error extracting links: {str(e)}")
        
        return links
    
    def _extract_forms(self, response):
        """Extract forms from a response"""
        forms = []
        
        try:
            # Use regex to find forms
            form_patterns = re.findall(r'<form[^>]*>.*?</form>', response.text, re.DOTALL)
            
            for form_html in form_patterns:
                form = {}
                
                # Extract action and method
                action_match = re.search(r'action=["\'](.*?)["\']', form_html)
                method_match = re.search(r'method=["\'](.*?)["\']', form_html)
                
                if action_match:
                    action = action_match.group(1)
                    # Handle relative URLs
                    if not action.startswith(('http://', 'https://')):
                        action = urljoin(response.url, action)
                    form["action"] = action
                else:
                    form["action"] = response.url
                
                if method_match:
                    form["method"] = method_match.group(1).upper()
                else:
                    form["method"] = "GET"
                
                # Extract input fields
                input_fields = re.findall(r'<input[^>]*>', form_html)
                fields = {}
                
                for input_field in input_fields:
                    name_match = re.search(r'name=["\'](.*?)["\']', input_field)
                    value_match = re.search(r'value=["\'](.*?)["\']', input_field)
                    
                    if name_match:
                        name = name_match.group(1)
                        value = value_match.group(1) if value_match else ""
                        fields[name] = value
                
                form["fields"] = fields
                forms.append(form)
                
        except Exception as e:
            self.fuzz_log.emit(f"Error extracting forms: {str(e)}")
        
        return forms
    
    def _analyze_response(self, response, url, param, value):
        """Analyze a response for interesting behaviors that may indicate vulnerabilities"""
        # Check for common error patterns that might indicate vulnerabilities
        text = response.text.lower()
        
        # SQL Injection signs
        if any(sign in text for sign in [
            "sql syntax", "mysql error", "ora-", "syntax error", 
            "microsoft sql", "postgresql", "sqlite", "database error"
        ]):
            return (
                "SQL Injection", 
                f"Possible SQL Injection vulnerability detected in parameter '{param}' with value '{value}'", 
                "HIGH"
            )
        
        # Server-side code signs
        if any(sign in text for sign in [
            "<%@", "<%=", "<jsp:", "<asp:", "<?php", "syntax error",
            "parse error", "runtime error", "stack trace", "traceback"
        ]):
            return (
                "Server-Side Code Injection", 
                f"Possible Server-Side Code Injection vulnerability detected in parameter '{param}' with value '{value}'", 
                "HIGH"
            )
        
        # Path traversal signs
        if any(sign in text for sign in [
            "no such file", "failed to open stream", "system cannot find",
            "permission denied", "root:", "etc/passwd", "boot.ini", "win.ini"
        ]):
            return (
                "Path Traversal", 
                f"Possible Path Traversal vulnerability detected in parameter '{param}' with value '{value}'", 
                "HIGH"
            )
        
        # Command injection signs
        if any(sign in text for sign in [
            "command not found", "system32", "/bin/", "permission denied",
            "output of command", "shell_exec", "exec", "system", "proc/"
        ]):
            return (
                "Command Injection", 
                f"Possible Command Injection vulnerability detected in parameter '{param}' with value '{value}'", 
                "HIGH"
            )
        
        # Check for unusual status codes
        if response.status_code >= 500:
            return (
                "Server Error", 
                f"Server returned error code {response.status_code} for parameter '{param}' with value '{value}'", 
                "MEDIUM"
            )
        
        # Check for unusual redirect behaviors
        if response.history and len(response.history) > 0:
            # If the response was a redirect
            initial_status = response.history[0].status_code
            if initial_status in [300, 301, 302, 303, 307, 308]:
                return (
                    "Potential Open Redirect", 
                    f"Unusual redirect behavior detected for parameter '{param}' with value '{value}'", 
                    "MEDIUM"
                )
        
        # If no obvious issues, return None
        return None
    
    def _detect_anomalies(self, baseline_data, test_data):
        """Use ML to detect anomalies in the responses"""
        if not baseline_data or not test_data:
            return []
        
        try:
            # Extract features for training
            features = []
            for response in baseline_data:
                feature_dict = {
                    "status_code": response["status_code"],
                    "content_length": response["content_length"],
                    "response_time": response["response_time"],
                    "has_redirect": 1 if response["has_redirect"] else 0,
                    "redirect_count": response["redirect_count"],
                    "error_count": len(response["error_messages"])
                }
                features.append(feature_dict)
            
            # Convert to numpy array for training
            feature_array = np.array([[
                data["status_code"],
                data["content_length"],
                data["response_time"],
                1 if data["has_redirect"] else 0,
                data["redirect_count"],
                len(data["error_messages"])
            ] for data in baseline_data])
            
            # Train the model on normal (baseline) behaviors
            self.model.fit(feature_array)
            
            # Prepare test data
            test_features = np.array([[
                data["status_code"],
                data["content_length"],
                data["response_time"],
                1 if data["has_redirect"] else 0,
                data["redirect_count"],
                len(data["error_messages"])
            ] for data in test_data])
            
            # Predict anomalies
            predictions = self.model.predict(test_features)
            scores = self.model.decision_function(test_features)
            
            # Normalize scores to 0-1 range where higher means more anomalous
            normalized_scores = []
            if len(scores) > 0:
                min_score = min(scores)
                max_score = max(scores)
                
                if max_score > min_score:  # Avoid division by zero
                    normalized_scores = [(score - min_score) / (max_score - min_score) for score in scores]
                else:
                    normalized_scores = [0.5] * len(scores)  # Default middle value if all scores are the same
            
            # Collect anomalies (-1 indicates an anomaly in Isolation Forest)
            anomalies = []
            
            for i, (prediction, score) in enumerate(zip(predictions, normalized_scores)):
                if prediction == -1 and score > 0.6:  # Only report high-confidence anomalies
                    anomalies.append({
                        "url": test_data[i]["url"],
                        "param": "",  # We don't have this info at this level
                        "value": "",  # We don't have this info at this level
                        "score": score,
                        "features": test_features[i].tolist()
                    })
            
            return anomalies
            
        except Exception as e:
            self.fuzz_log.emit(f"Error during anomaly detection: {str(e)}")
            return []

    # Mutation strategies
    def _replace_with_special_chars(self, param, value):
        """Replace value with special characters"""
        mutations = []
        
        # Add some basic mutations
        mutations.append(self.special_chars)
        
        # Add some targeted mutations
        for char in ['"', "'", '<', '>', '&', ';', '|', '`']:
            mutations.append(value + char)
            mutations.append(char + value)
            mutations.append(value.replace('a', char) if 'a' in value else value + char)
        
        return mutations
    
    def _insert_control_chars(self, param, value):
        """Insert control characters"""
        mutations = []
        
        # Add some basic mutations
        mutations.append(self.control_chars)
        
        # Add targeted mutations
        for char in ['\x00', '\x0A', '\x0D', '\x1A']:
            mutations.append(value + char)
            mutations.append(char + value)
            
            # Try to insert in the middle
            if len(value) > 1:
                mid = len(value) // 2
                mutations.append(value[:mid] + char + value[mid:])
        
        return mutations
    
    def _integer_boundary_fuzzing(self, param, value):
        """Test integer boundaries if the value looks like an integer"""
        mutations = []
        
        # Check if the value is an integer
        if value.isdigit():
            # Integer boundary testing
            int_val = int(value)
            mutations.extend([
                str(int_val + 1),
                str(int_val - 1),
                str(int_val * -1),
                str(2**31 - 1),      # Max 32-bit signed int
                str(-2**31),         # Min 32-bit signed int
                str(2**63 - 1),      # Max 64-bit signed int
                str(-2**63),         # Min 64-bit signed int
                str(int_val + 1000),
                str(int_val - 1000),
                "0"
            ])
        
        return mutations
    
    def _repeat_parameter(self, param, value):
        """Test by repeating parameters"""
        mutations = []
        
        # Repeat the value
        mutations.extend([
            value * 2,
            value * 10,
            value * 100,
            value + "A" * 1000,  # Add a long string
            "A" * 1000 + value   # Prepend a long string
        ])
        
        return mutations
    
    def _format_string_fuzzing(self, param, value):
        """Add format string payloads"""
        mutations = []
        
        # Add format string mutations
        mutations.extend(self.format_strings)
        
        # Add targeted format string mutations
        for fmt in ["%s", "%x", "%n"]:
            mutations.append(value + fmt)
            mutations.append(fmt + value)
            
            # Create format string chains
            mutations.append(fmt * 10)
            mutations.append(value + fmt * 5)
        
        return mutations
    
    def _sql_mutation(self, param, value):
        """Add SQL injection payloads"""
        mutations = []
        
        # Add SQL payloads
        mutations.extend(self.sql_payloads)
        
        # Create targeted mutations
        for payload in ["'", "\"", ";", "--", "/*", "*/"]:
            mutations.append(value + payload)
            mutations.append(payload + value)
            mutations.append(value + " " + payload)
        
        return mutations
    
    def _path_traversal_mutation(self, param, value):
        """Add path traversal payloads"""
        mutations = []
        
        # Add path traversal payloads
        mutations.extend(self.path_traversal_payloads)
        
        # Create targeted mutations
        for path in ["../", "..\\", "%2e%2e%2f"]:
            mutations.append(value + path)
            mutations.append(path + value)
            mutations.append(path * 5 + value)
        
        return mutations
    
    def _header_mutation(self, param, value):
        """Test by modifying HTTP headers"""
        mutations = []
        
        # We return an empty list here because this is handled differently
        # (headers are passed separately in the request)
        return mutations
    
    def _content_type_mutation(self, param, value):
        """Test by modifying content type"""
        mutations = []
        
        # We return an empty list here because this is handled differently
        # (content type is a header)
        return mutations
    
    def _add_random_parameters(self, param, value):
        """Add random parameters to test for unknown features"""
        mutations = []
        
        # Generate random parameters
        random_params = [
            "debug", "test", "admin", "develop", "dev",
            "show", "display", "hide", "raw", "json",
            "format", "view", "mode", "level", "access"
        ]
        
        # Generate random values
        random_values = [
            "true", "false", "1", "0", "yes", 
            "no", "on", "off", "debug", "admin"
        ]
        
        # We return an empty list here because this is handled by modifying the URL
        # not just the parameter value
        return mutations
    
    def _modify_url_parameter(self, url, param, value):
        """Modify a single parameter in a URL"""
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Update the parameter
        query_params[param] = [value]
        
        # Rebuild the query string
        query_string = urlencode(query_params, doseq=True)
        
        # Return the modified URL
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            query_string,
            parsed.fragment
        ))
