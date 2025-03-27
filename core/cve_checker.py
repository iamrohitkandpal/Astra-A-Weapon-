"""
CVE Checking module for Astra
"""

import threading
import nvdlib
from datetime import datetime, timedelta
import re
from PyQt6.QtCore import QObject, pyqtSignal

class CVEChecker(QObject):
    """Class for checking CVEs using NVD database"""
    
    # Signal for result update
    result_update = pyqtSignal(dict)
    
    # Signal for progress update
    progress_update = pyqtSignal(int)
    
    # Signal for completion
    check_completed = pyqtSignal()
    
    # Signal for error
    check_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        
    def _validate_cpe_format(self, cpe_string):
        """Validate CPE string format"""
        # Basic CPE format validation, should start with "cpe:"
        if not cpe_string.startswith("cpe:"):
            return False
        
        # More detailed validation could be added here
        return True
    
    def _process_cve_data(self, cve_item):
        """Process CVE data to extract important information"""
        try:
            cve_data = {
                'id': cve_item.id,
                'published': cve_item.published.strftime("%Y-%m-%d"),
                'description': '',
                'cvss_v3': None,
                'cvss_v2': None,
                'severity': 'Unknown',
                'references': []
            }
            
            # Get description
            if hasattr(cve_item, 'descriptions') and cve_item.descriptions:
                for desc in cve_item.descriptions:
                    if desc.lang == 'en':
                        cve_data['description'] = desc.value
                        break
            
            # Get CVSS scores
            if hasattr(cve_item, 'metrics'):
                if hasattr(cve_item.metrics, 'cvssMetricV31'):
                    metrics = cve_item.metrics.cvssMetricV31[0]
                    cve_data['cvss_v3'] = metrics.cvssData.baseScore
                    cve_data['severity'] = metrics.cvssData.baseSeverity
                elif hasattr(cve_item.metrics, 'cvssMetricV30'):
                    metrics = cve_item.metrics.cvssMetricV30[0]
                    cve_data['cvss_v3'] = metrics.cvssData.baseScore
                    cve_data['severity'] = metrics.cvssData.baseSeverity
                elif hasattr(cve_item.metrics, 'cvssMetricV2'):
                    metrics = cve_item.metrics.cvssMetricV2[0]
                    cve_data['cvss_v2'] = metrics.cvssData.baseScore
                    
                    # Map score to severity if V3 severity not available
                    if cve_data['severity'] == 'Unknown':
                        score = metrics.cvssData.baseScore
                        if score >= 7.0:
                            cve_data['severity'] = 'HIGH'
                        elif score >= 4.0:
                            cve_data['severity'] = 'MEDIUM'
                        else:
                            cve_data['severity'] = 'LOW'
            
            # Get references
            if hasattr(cve_item, 'references'):
                for ref in cve_item.references:
                    cve_data['references'].append(ref.url)
            
            return cve_data
            
        except Exception as e:
            print(f"Error processing CVE {cve_item.id}: {str(e)}")
            # Return a minimal data structure
            return {
                'id': cve_item.id if hasattr(cve_item, 'id') else 'Unknown',
                'published': 'Unknown date',
                'description': 'Error processing CVE data',
                'cvss_v3': None,
                'cvss_v2': None,
                'severity': 'Unknown',
                'references': []
            }
    
    def search_cve_by_product(self, product, vendor=None, version=None, max_results=100):
        """Search CVEs by product name"""
        try:
            # Reset stop event
            self._stop_event.clear()
            
            # Emit initial progress
            self.progress_update.emit(10)
            
            # Set up search parameters
            params = {
                'keywordSearch': product,
                'resultsPerPage': max_results
            }
            
            # Add vendor if provided
            if vendor:
                params['keywordSearch'] += f" {vendor}"
            
            # Search for CVEs
            self.progress_update.emit(30)
            cve_results = nvdlib.searchCVE(**params)
            
            # Process results
            processed_results = []
            for i, cve in enumerate(cve_results):
                if self._stop_event.is_set():
                    break
                
                # Process the CVE data
                cve_data = self._process_cve_data(cve)
                
                # Filter by version if specified
                if version and not self._filter_by_version(cve, version):
                    continue
                
                # Add to results
                processed_results.append(cve_data)
                
                # Update progress
                progress = 30 + int((i / len(cve_results)) * 60)
                self.progress_update.emit(progress)
                
                # Emit result update
                self.result_update.emit(cve_data)
            
            # Complete the process
            if not self._stop_event.is_set():
                self.progress_update.emit(100)
                self.check_completed.emit()
                
        except Exception as e:
            self.check_error.emit(str(e))
    
    def _filter_by_version(self, cve, version):
        """Check if the CVE applies to the specified version"""
        try:
            # This is a simplified version check method
            # A more comprehensive version would parse CPE strings
            # and do proper version comparison
            
            # Convert version to string if it's not already
            version_str = str(version)
            
            # Check if version appears in the description
            if hasattr(cve, 'descriptions'):
                for desc in cve.descriptions:
                    if version_str in desc.value:
                        return True
            
            # Check CPE configurations
            if hasattr(cve, 'configurations'):
                for node in cve.configurations.nodes:
                    for cpe_match in node.cpeMatch:
                        if hasattr(cpe_match, 'criteria') and version_str in cpe_match.criteria:
                            return True
            
            return False
            
        except Exception:
            # If anything goes wrong with filtering, include the CVE to be safe
            return True
    
    def search_cve_by_cpe(self, cpe_string, max_results=100):
        """Search CVEs by CPE string"""
        try:
            # Reset stop event
            self._stop_event.clear()
            
            # Validate CPE format
            if not self._validate_cpe_format(cpe_string):
                self.check_error.emit("Invalid CPE format. CPE should start with 'cpe:'")
                return
            
            # Emit initial progress
            self.progress_update.emit(10)
            
            # Search for CVEs using CPE
            self.progress_update.emit(30)
            cve_results = nvdlib.searchCVE(cpeName=cpe_string, resultsPerPage=max_results)
            
            # Process results
            for i, cve in enumerate(cve_results):
                if self._stop_event.is_set():
                    break
                
                # Process the CVE data
                cve_data = self._process_cve_data(cve)
                
                # Update progress
                progress = 30 + int((i / len(cve_results)) * 60)
                self.progress_update.emit(progress)
                
                # Emit result update
                self.result_update.emit(cve_data)
            
            # Complete the process
            if not self._stop_event.is_set():
                self.progress_update.emit(100)
                self.check_completed.emit()
                
        except Exception as e:
            self.check_error.emit(str(e))
    
    def search_latest_cves(self, days_back=30, max_results=100):
        """Search for the latest CVEs published in the last X days"""
        try:
            # Reset stop event
            self._stop_event.clear()
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Format dates for NVD API
            pub_start_date = start_date.strftime("%Y-%m-%dT00:00:00.000")
            pub_end_date = end_date.strftime("%Y-%m-%dT23:59:59.999")
            
            # Emit initial progress
            self.progress_update.emit(10)
            
            # Search for CVEs in date range
            self.progress_update.emit(30)
            cve_results = nvdlib.searchCVE(
                pubStartDate=pub_start_date,
                pubEndDate=pub_end_date,
                resultsPerPage=max_results
            )
            
            # Process results
            for i, cve in enumerate(cve_results):
                if self._stop_event.is_set():
                    break
                
                # Process the CVE data
                cve_data = self._process_cve_data(cve)
                
                # Update progress
                progress = 30 + int((i / len(cve_results)) * 60)
                self.progress_update.emit(progress)
                
                # Emit result update
                self.result_update.emit(cve_data)
            
            # Complete the process
            if not self._stop_event.is_set():
                self.progress_update.emit(100)
                self.check_completed.emit()
                
        except Exception as e:
            self.check_error.emit(str(e))
    
    def stop_check(self):
        """Stop the CVE checking process"""
        self._stop_event.set()
