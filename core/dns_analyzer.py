"""
DNS analysis module for Astra
"""

import dns.resolver
import threading
from PyQt6.QtCore import QObject, pyqtSignal

class DNSAnalyzer(QObject):
    """DNS analyzer class for querying DNS records"""
    
    # Signal for result update
    result_update = pyqtSignal(str, str, str)
    
    # Signal for error
    query_error = pyqtSignal(str)
    
    # Signal for completion
    query_completed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 3
        self.resolver.lifetime = 3
    
    def _query_record(self, domain, record_type):
        """Query a specific record type for a domain"""
        try:
            answers = self.resolver.resolve(domain, record_type)
            for answer in answers:
                if self._stop_event.is_set():
                    break
                self.result_update.emit(domain, record_type, str(answer))
        except dns.resolver.NoAnswer:
            self.result_update.emit(domain, record_type, "No records found")
        except dns.resolver.NXDOMAIN:
            self.result_update.emit(domain, record_type, "Domain does not exist")
        except Exception as e:
            self.result_update.emit(domain, record_type, f"Error: {str(e)}")
    
    def analyze(self, domain, record_types=None):
        """Analyze DNS records for a domain"""
        try:
            # Reset stop event
            self._stop_event.clear()
            
            if record_types is None:
                record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
            
            for record_type in record_types:
                if self._stop_event.is_set():
                    break
                self._query_record(domain, record_type)
            
            if not self._stop_event.is_set():
                self.query_completed.emit()
                
        except Exception as e:
            self.query_error.emit(str(e))
    
    def stop_analysis(self):
        """Stop the DNS analysis"""
        self._stop_event.set()
