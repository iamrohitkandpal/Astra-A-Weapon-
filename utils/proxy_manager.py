"""
Proxy management utility for Astra
"""

import os
import sys
import subprocess
import threading
import time
import socket
import tempfile
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

class ProxyManager(QObject):
    """
    Proxy manager class for handling different proxy configurations
    and Tor connectivity
    """
    
    # Signals
    status_update = pyqtSignal(str)
    proxy_changed = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_proxy = "direct"  # direct, manual, tor
        self.proxy_type = "http"       # http, socks4, socks5
        self.proxy_host = ""
        self.proxy_port = 0
        self.proxy_username = None
        self.proxy_password = None
        
        # Tor process variables
        self.tor_process = None
        self.tor_config_file = None
        self.tor_control_port = 9051
        self.tor_socks_port = 9050
        
        # Apply proxy settings to Python's urllib and requests
        self._apply_to_env()
    
    def setup_direct_connection(self):
        """Setup direct connection without proxy"""
        self.current_proxy = "direct"
        self.proxy_type = None
        self.proxy_host = None
        self.proxy_port = None
        self.proxy_username = None
        self.proxy_password = None
        
        self._apply_to_env()
        self.status_update.emit("Direct connection established")
        self.proxy_changed.emit("direct")
        return True
    
    def setup_manual_proxy(self, proxy_type, host, port, username=None, password=None):
        """Setup manual proxy configuration"""
        if not host or not port:
            self.error_occurred.emit("Invalid proxy settings: Host and port are required")
            return False
        
        self.current_proxy = "manual"
        self.proxy_type = proxy_type.lower()
        self.proxy_host = host
        self.proxy_port = int(port)
        self.proxy_username = username
        self.proxy_password = password
        
        # Verify connection
        if self._check_proxy_connection():
            self._apply_to_env()
            self.status_update.emit(f"Connected to {proxy_type.upper()} proxy at {host}:{port}")
            self.proxy_changed.emit("manual")
            return True
        else:
            self.error_occurred.emit(f"Failed to connect to {proxy_type.upper()} proxy at {host}:{port}")
            self.setup_direct_connection()  # Fallback to direct
            return False
    
    def start_tor(self):
        """Start Tor process and configure it as a proxy"""
        if self.tor_process:
            self.status_update.emit("Tor is already running")
            return True
        
        # Check if Tor is installed
        tor_path = self._find_tor_executable()
        if not tor_path:
            self.error_occurred.emit("Tor not found. Please install Tor.")
            return False
        
        try:
            # Create temporary Tor config file
            self.tor_config_file = self._create_tor_config()
            
            # Start Tor process
            self.tor_process = subprocess.Popen(
                [tor_path, "-f", self.tor_config_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor Tor output in a separate thread
            threading.Thread(target=self._monitor_tor_output, daemon=True).start()
            
            # Wait for Tor to bootstrap
            time.sleep(5)  # Simple wait, could be improved to check for "Bootstrapped 100%"
            
            # Check if Tor is running and the SOCKS proxy is accessible
            if self._check_tor_connection():
                self.current_proxy = "tor"
                self.proxy_type = "socks5"
                self.proxy_host = "127.0.0.1"
                self.proxy_port = self.tor_socks_port
                
                self._apply_to_env()
                self.status_update.emit("Connected to Tor network")
                self.proxy_changed.emit("tor")
                return True
            else:
                # Clean up and report failure
                self.stop_tor()
                self.error_occurred.emit("Failed to start Tor proxy")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Error starting Tor: {str(e)}")
            self.stop_tor()
            return False
    
    def stop_tor(self):
        """Stop the Tor process"""
        if self.tor_process:
            # Terminate Tor process
            self.tor_process.terminate()
            try:
                self.tor_process.wait(timeout=5)  # Wait for it to terminate
            except subprocess.TimeoutExpired:
                self.tor_process.kill()  # Force kill if it doesn't terminate
            
            self.tor_process = None
            
            # Clean up config file
            if self.tor_config_file and os.path.exists(self.tor_config_file):
                try:
                    os.unlink(self.tor_config_file)
                except:
                    pass
                
            self.tor_config_file = None
            
            # Revert to direct connection
            self.setup_direct_connection()
            return True
        
        return False
    
    def renew_tor_identity(self):
        """Request a new identity from Tor (new exit node)"""
        if self.current_proxy != "tor" or not self.tor_process:
            self.error_occurred.emit("Tor is not running")
            return False
        
        try:
            # We would typically use stem library here, but for simplicity
            # we're just restarting the Tor process
            self.status_update.emit("Obtaining new Tor identity...")
            
            # Stop and restart Tor
            self.stop_tor()
            time.sleep(1)
            success = self.start_tor()
            
            if success:
                self.status_update.emit("New Tor identity obtained")
                return True
            else:
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Error renewing Tor identity: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up resources before exiting"""
        self.stop_tor()
    
    def _apply_to_env(self):
        """Apply proxy settings to environment variables"""
        # Reset proxy environment variables
        for env_var in ['http_proxy', 'https_proxy', 'ftp_proxy', 'all_proxy',
                        'HTTP_PROXY', 'HTTPS_PROXY', 'FTP_PROXY', 'ALL_PROXY',
                        'SOCKS_PROXY', 'socks_proxy']:
            if env_var in os.environ:
                del os.environ[env_var]
        
        # Set new proxy environment variables if using a proxy
        if self.current_proxy != "direct":
            proxy_url = None
            
            if self.proxy_type == "http":
                proxy_scheme = "http"
            elif self.proxy_type == "socks4":
                proxy_scheme = "socks4"
            elif self.proxy_type == "socks5":
                proxy_scheme = "socks5"
            else:
                proxy_scheme = "http"  # Default
            
            # Build proxy URL with authentication if needed
            if self.proxy_username and self.proxy_password:
                proxy_url = f"{proxy_scheme}://{self.proxy_username}:{self.proxy_password}@{self.proxy_host}:{self.proxy_port}"
            else:
                proxy_url = f"{proxy_scheme}://{self.proxy_host}:{self.proxy_port}"
            
            # Set environment variables
            os.environ['http_proxy'] = proxy_url
            os.environ['https_proxy'] = proxy_url
            os.environ['all_proxy'] = proxy_url
            
            # Uppercase variants
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
            os.environ['ALL_PROXY'] = proxy_url
            
            if 'socks' in proxy_scheme:
                os.environ['SOCKS_PROXY'] = proxy_url
    
    def _check_proxy_connection(self):
        """Check if the proxy connection is working"""
        try:
            # For a simple check, just try to connect to the proxy server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((self.proxy_host, self.proxy_port))
            return True
        except Exception:
            return False
    
    def _check_tor_connection(self):
        """Check if Tor SOCKS proxy is accessible"""
        try:
            # Try to connect to the Tor SOCKS proxy port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect(("127.0.0.1", self.tor_socks_port))
            return True
        except Exception:
            return False
    
    def _find_tor_executable(self):
        """Find the Tor executable path"""
        # Common Tor locations
        if sys.platform == 'win32':
            tor_paths = [
                r"C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
                r"C:\Program Files (x86)\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
                r"C:\Tor\tor.exe"
            ]
            for path in tor_paths:
                if os.path.exists(path):
                    return path
            
            # Try to find Tor in PATH
            try:
                result = subprocess.run(["where", "tor"], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip().split("\n")[0]
            except:
                pass
        else:
            # Linux/Mac
            tor_paths = [
                "/usr/bin/tor",
                "/usr/local/bin/tor"
            ]
            for path in tor_paths:
                if os.path.exists(path):
                    return path
            
            # Try to find Tor in PATH
            try:
                result = subprocess.run(["which", "tor"], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                pass
        
        return None
    
    def _create_tor_config(self):
        """Create a temporary Tor configuration file"""
        config_content = f"""
SOCKSPort {self.tor_socks_port}
ControlPort {self.tor_control_port}
DataDirectory {tempfile.gettempdir()}/tor_data
Log notice stdout
ExitNodes {{us}}
StrictNodes 1
"""
        
        # Create temp file
        fd, path = tempfile.mkstemp(suffix=".torrc")
        with os.fdopen(fd, 'w') as f:
            f.write(config_content)
        
        return path
    
    def _monitor_tor_output(self):
        """Monitor and process Tor output"""
        while self.tor_process:
            line = self.tor_process.stdout.readline()
            if not line:
                break
                
            # Check for bootstrap progress
            if "Bootstrapped" in line:
                self.status_update.emit(line.strip())
                
            # Check for errors
            if "ERR" in line:
                self.error_occurred.emit(line.strip())
