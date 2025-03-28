"""
AI-powered threat detection module for Astra using machine learning
"""
import numpy as np
import os
import pickle
import re
import json
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline

class AIThreatDetector:
    """Machine learning model for web security threats detection"""
    
    def __init__(self):
        self.models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Pattern detection model
        self.pattern_model_path = os.path.join(self.models_dir, 'pattern_classifier.pkl')
        self.pattern_model = None
        self._load_or_train_pattern_model()
        
        # Anomaly detection model
        self.anomaly_model_path = os.path.join(self.models_dir, 'anomaly_detector.pkl')
        self.anomaly_model = None
        self._load_or_train_anomaly_model()
        
        # Feature extraction
        self.vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 3))
    
    def _load_or_train_pattern_model(self):
        """Load existing pattern detection model or train a new one"""
        if os.path.exists(self.pattern_model_path):
            try:
                with open(self.pattern_model_path, 'rb') as f:
                    self.pattern_model = pickle.load(f)
                return
            except Exception as e:
                print(f"Error loading pattern model: {e}. Will train a new one.")
        
        # Train a new model
        print("Training new pattern detection model...")
        self._train_pattern_model()
    
    def _load_or_train_anomaly_model(self):
        """Load existing anomaly detection model or train a new one"""
        if os.path.exists(self.anomaly_model_path):
            try:
                with open(self.anomaly_model_path, 'rb') as f:
                    self.anomaly_model = pickle.load(f)
                return
            except Exception as e:
                print(f"Error loading anomaly model: {e}. Will train a new one.")
        
        # Train a new model
        print("Training new anomaly detection model...")
        self._train_anomaly_model()
    
    def _train_pattern_model(self):
        """Train a classification model for vulnerability detection"""
        # Load sample data from internal dataset
        data = self._load_training_data()
        
        if not data or len(data) < 10:
            # Not enough data, create a basic model
            self.pattern_model = Pipeline([
                ('vectorizer', TfidfVectorizer(max_features=5000, ngram_range=(1, 3))),
                ('classifier', RandomForestClassifier(n_estimators=50, random_state=42))
            ])
            # Minimal training data
            X = [
                "' OR 1=1 --", "admin' --", "1' OR '1'='1", "<script>alert(1)</script>",
                "../../etc/passwd", "../../../windows/win.ini", "<img src=x onerror=alert(1)>",
                "/?id=1+AND+1=1", "/?id=1+AND+sleep(5)", "/?id=1+UNION+SELECT+1,2,3",
                "normal query", "contact?email=user@example.com", "search?q=normal+search",
                "products?category=electronics", "article?id=123", "page?id=about"
            ]
            y = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0]  # 1 for malicious, 0 for benign
            
            self.pattern_model.fit(X, y)
        else:
            # We have enough data for a proper model
            X = data['input']
            y = data['is_malicious']
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            self.pattern_model = Pipeline([
                ('vectorizer', TfidfVectorizer(max_features=10000, ngram_range=(1, 3))),
                ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
            ])
            
            self.pattern_model.fit(X_train, y_train)
            
            # Evaluate on test set
            y_pred = self.pattern_model.predict(X_test)
            print("Pattern Model Evaluation:")
            print(classification_report(y_test, y_pred))
        
        # Save the model
        with open(self.pattern_model_path, 'wb') as f:
            pickle.dump(self.pattern_model, f)
    
    def _train_anomaly_model(self):
        """Train an anomaly detection model for unusual patterns"""
        # Load sample data
        data = self._load_training_data(anomaly=True)
        
        # Create and train the model
        if not data or len(data) < 10:
            # Simple vectorization and model
            vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 3))
            
            # Example benign requests for training
            X = [
                "normal query", "contact?email=user@example.com", "search?q=normal+search",
                "products?category=electronics", "article?id=123", "page?id=about",
                "login?username=user1", "register?email=test@example.com",
                "reset-password?token=abc123", "profile?user=john", "settings",
                "dashboard", "report?month=january", "stats?year=2023",
                "blog?category=technology", "post?id=42", "comment?post=123"
            ]
            
            X_transformed = vectorizer.fit_transform(X)
            
            # Train isolation forest model
            self.anomaly_model = IsolationForest(
                n_estimators=100,
                max_samples='auto',
                contamination=0.1,
                random_state=42
            )
            self.anomaly_model.fit(X_transformed.toarray())
            
            # Save vectorizer with the model
            with open(self.anomaly_model_path, 'wb') as f:
                pickle.dump((vectorizer, self.anomaly_model), f)
        else:
            # We have real data
            X = data['input']
            
            # Create TF-IDF features
            vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 3))
            X_transformed = vectorizer.fit_transform(X)
            
            # Train isolation forest model
            self.anomaly_model = IsolationForest(
                n_estimators=100,
                max_samples='auto',
                contamination=0.05,  # Assuming 5% of the data is anomalous
                random_state=42
            )
            self.anomaly_model.fit(X_transformed.toarray())
            
            # Save vectorizer with the model
            with open(self.anomaly_model_path, 'wb') as f:
                pickle.dump((vectorizer, self.anomaly_model), f)
    
    def _load_training_data(self, anomaly=False):
        """Load training data from the data directory"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        data_file = os.path.join(data_dir, 'security_training_data.json')
        
        if not os.path.exists(data_file):
            return None
        
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
                
            if anomaly:
                # For anomaly detection, we only need benign examples
                benign_data = [item for item in data if not item.get('is_malicious', False)]
                return pd.DataFrame(benign_data) if benign_data else None
            else:
                return pd.DataFrame(data)
        except Exception as e:
            print(f"Error loading training data: {e}")
            return None
    
    def detect_patterns(self, input_text):
        """Detect malicious patterns in input text using the classification model"""
        if not self.pattern_model:
            self._load_or_train_pattern_model()
        
        # Predict
        try:
            prediction = self.pattern_model.predict([input_text])[0]
            probability = self.pattern_model.predict_proba([input_text])[0][1]  # Probability of being malicious
            
            return {
                'is_malicious': bool(prediction),
                'confidence': float(probability),
                'pattern_type': self._identify_threat_type(input_text)
            }
        except Exception as e:
            print(f"Error in pattern detection: {e}")
            return {
                'is_malicious': False,
                'confidence': 0.0,
                'pattern_type': 'unknown'
            }
    
    def detect_anomalies(self, input_text):
        """Detect anomalies in input text using the anomaly detection model"""
        if not self.anomaly_model:
            self._load_or_train_anomaly_model()
        
        try:
            # Unpack the loaded model
            if isinstance(self.anomaly_model, tuple):
                vectorizer, model = self.anomaly_model
            else:
                with open(self.anomaly_model_path, 'rb') as f:
                    vectorizer, model = pickle.load(f)
                self.anomaly_model = (vectorizer, model)
            
            # Transform input and predict
            X_transformed = vectorizer.transform([input_text]).toarray()
            prediction = model.predict(X_transformed)[0]
            score = model.score_samples(X_transformed)[0]
            
            # In Isolation Forest, -1 indicates an anomaly, 1 indicates normal
            is_anomaly = prediction == -1
            
            # Convert score to a 0-1 range where higher means more anomalous
            normalized_score = 1.0 - (score - model.offset_) / (np.max(model.score_samples(X_transformed)) - model.offset_)
            
            return {
                'is_anomaly': bool(is_anomaly),
                'anomaly_score': float(normalized_score),
                'description': self._describe_anomaly(input_text) if is_anomaly else None
            }
        except Exception as e:
            print(f"Error in anomaly detection: {e}")
            return {
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'description': None
            }
    
    def analyze_payload(self, payload, url=None):
        """Comprehensive analysis of a payload"""
        results = {
            'pattern_detection': self.detect_patterns(payload),
            'anomaly_detection': self.detect_anomalies(payload),
            'url_context': url,
            'risk_score': 0.0,
            'suggested_mitigations': []
        }
        
        # Calculate risk score (0-100)
        pattern_score = results['pattern_detection']['confidence'] * 80  # 0-80 points
        anomaly_score = results['anomaly_detection']['anomaly_score'] * 20  # 0-20 points
        results['risk_score'] = pattern_score + anomaly_score
        
        # Generate mitigations
        if results['pattern_detection']['is_malicious'] or results['anomaly_detection']['is_anomaly']:
            results['suggested_mitigations'] = self._generate_mitigations(
                results['pattern_detection']['pattern_type'],
                payload
            )
        
        return results
    
    def _identify_threat_type(self, input_text):
        """Identify the type of threat based on patterns"""
        input_lower = input_text.lower()
        
        # SQL Injection patterns
        sql_patterns = [
            "' or ", "or 1=1", "union select", "select *", "--", "drop table",
            "1=1", "1 = 1", "information_schema", "sleep(", "waitfor", "benchmark(",
            "pg_sleep", "' and ", "and 1=1", "order by", "group by", "having "
        ]
        
        # XSS patterns
        xss_patterns = [
            "<script", "javascript:", "onerror=", "onload=", "onmouseover",
            "alert(", "prompt(", "confirm(", "eval(", "document.cookie",
            "document.location", "<img", "<iframe", "<svg", "onblur=", "onfocus="
        ]
        
        # Path traversal patterns
        path_patterns = [
            "../", "..\\", "/..", "\\..", "/etc/passwd", "boot.ini",
            "win.ini", "/etc/shadow", "c:\\windows", "/var/www", "wp-config.php",
            ".htaccess", ".git", "file://", "file:///"
        ]
        
        # Command injection patterns
        cmd_patterns = [
            ";", "&&", "||", "|", "`", "$(",
            "system(", "exec(", "shell_exec", "cmd.exe",
            "powershell", "bash", "/bin/sh", "/bin/bash"
        ]
        
        # Check each pattern type
        for pattern in sql_patterns:
            if pattern in input_lower:
                return "SQL Injection"
        
        for pattern in xss_patterns:
            if pattern in input_lower:
                return "Cross-Site Scripting (XSS)"
        
        for pattern in path_patterns:
            if pattern in input_lower:
                return "Path Traversal"
        
        for pattern in cmd_patterns:
            if pattern in input_lower:
                return "Command Injection"
        
        # No specific pattern identified
        return "Unknown/Other"
    
    def _describe_anomaly(self, input_text):
        """Generate a description for an anomalous input"""
        # Check length
        if len(input_text) > 500:
            return "Unusually long input data"
        
        # Check special characters ratio
        special_chars = re.findall(r'[^a-zA-Z0-9\s]', input_text)
        special_ratio = len(special_chars) / len(input_text) if len(input_text) > 0 else 0
        
        if special_ratio > 0.3:
            return "High concentration of special characters"
        
        # Check for hex or encoded characters
        encoded_pattern = re.findall(r'%[0-9a-fA-F]{2}', input_text)
        if len(encoded_pattern) > 5:
            return "Contains multiple URL-encoded characters"
        
        # Check for unusual character repetition
        repeated_chars = re.findall(r'(.)\1{5,}', input_text)
        if repeated_chars:
            return f"Contains unusual repetition of characters"
        
        return "Structure deviates from normal patterns"
    
    def _generate_mitigations(self, threat_type, payload):
        """Generate mitigation strategies based on the threat type"""
        mitigations = []
        
        if threat_type == "SQL Injection":
            mitigations = [
                "Use parameterized queries or prepared statements instead of dynamic SQL",
                "Implement input validation that rejects suspicious SQL characters",
                "Apply the principle of least privilege to database accounts",
                "Use ORM libraries that automatically sanitize inputs",
                "Consider implementing a web application firewall (WAF)"
            ]
        
        elif threat_type == "Cross-Site Scripting (XSS)":
            mitigations = [
                "Implement proper output encoding for the correct context (HTML, JavaScript, CSS, etc.)",
                "Use Content-Security-Policy (CSP) headers to restrict script execution",
                "Validate and sanitize all user inputs",
                "Use modern frameworks that automatically escape outputs",
                "Implement X-XSS-Protection headers"
            ]
        
        elif threat_type == "Path Traversal":
            mitigations = [
                "Validate and sanitize file paths before processing",
                "Use a whitelist approach for file operations",
                "Avoid putting user-supplied input directly into file paths",
                "Implement proper access controls on files and directories",
                "Consider using dedicated libraries for safe file operations"
            ]
        
        elif threat_type == "Command Injection":
            mitigations = [
                "Avoid using shell commands with user input",
                "If shell commands are necessary, use whitelisting for allowed commands",
                "Implement strict input validation for command parameters",
                "Use built-in language functions instead of executing commands",
                "Apply the principle of least privilege for command execution"
            ]
        
        else:  # Unknown/Other
            mitigations = [
                "Implement comprehensive input validation",
                "Follow the principle of least privilege",
                "Keep all software and dependencies updated",
                "Use a web application firewall for additional protection",
                "Implement rate limiting to prevent abuse"
            ]
        
        # Add specific payload mitigation
        if payload:
            if "'" in payload or "\"" in payload:
                mitigations.append("Sanitize or escape single and double quotes in user inputs")
            
            if "<" in payload or ">" in payload:
                mitigations.append("Ensure HTML tags are properly sanitized or encoded")
            
            if ";" in payload or "|" in payload or "&" in payload:
                mitigations.append("Filter command shell metacharacters from user inputs")
        
        return mitigations
