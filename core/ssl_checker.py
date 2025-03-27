"""
SSL/TLS security checker module for Astra
"""

import socket
import threading
import ssl
import datetime
from PyQt6.QtCore import QObject, pyqtSignal

class SSLChecker(QObject):
    """Class for checking SSL/TLS security"""
    
    # Signal for result update
    result_update = pyqtSignal(dict)
    
    # Signal for error
    check_error = pyqtSignal(str)
    
    # Signal for completion
    check_completed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
    
    def _get_certificate_info(self, cert):
        """Extract and format certificate information"""
        info = {}
        
        # Subject information
        subject = cert['subject']
        if subject:
            info['subject'] = subject
        
        # Issuer information
        issuer = cert['issuer']
        if issuer:
            info['issuer'] = issuer
        
        # Validity
        not_before = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
        not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        now = datetime.datetime.now()
        
        info['valid_from'] = not_before.strftime('%Y-%m-%d')
        info['valid_until'] = not_after.strftime('%Y-%m-%d')
        info['days_left'] = (not_after - now).days
        info['is_expired'] = now > not_after
        
        # Version
        info['version'] = cert['version']
        
        # Serial Number
        info['serial_number'] = cert['serialNumber']
        
        # Algorithm
        info['signature_algorithm'] = cert['signatureAlgorithm']
        
        return info
    
    def check(self, hostname, port=443):
        """Check SSL/TLS security for a hostname"""
        try:
            # Reset stop event
            self._stop_event.clear()
            
            context = ssl.create_default_context()
            results = {}
            
            with socket.create_connection((hostname, port)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get certificate
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    protocol = ssock.version()
                    
                    # Process certificate information
                    cert_info = self._get_certificate_info(cert)
                    
                    # Add to results
                    results['certificate'] = cert_info
                    results['protocol'] = protocol
                    results['cipher_suite'] = cipher[0]
                    results['cipher_bits'] = cipher[1]
                    results['hostname'] = hostname
                    results['port'] = port
                    
                    # Check if protocol is secure
                    results['secure_protocol'] = protocol not in ['SSLv2', 'SSLv3', 'TLSv1', 'TLSv1.1']
                    
                    # Emit results
                    self.result_update.emit(results)
            
            if not self._stop_event.is_set():
                self.check_completed.emit()
        
        except Exception as e:
            self.check_error.emit(str(e))
    
    def stop_check(self):
        """Stop the SSL/TLS check"""
        self._stop_event.set()
