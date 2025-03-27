"""
Subdomain enumeration module for Astra
"""

import threading
import socket
import concurrent.futures
import dns.resolver
import subprocess
import os
import json
import platform
import tempfile
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

class SubdomainEnumerator(QObject):
    """Class for subdomain enumeration"""
    
    # Signal for result update
    result_update = pyqtSignal(str, str)
    
    # Signal for progress update
    progress_update = pyqtSignal(int)
    
    # Signal for completion
    enum_completed = pyqtSignal()
    
    # Signal for error
    enum_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 1
        self.resolver.lifetime = 1
        self._amass_available = self._check_amass_availability()
    
    def _check_amass_availability(self):
        """Check if amass is available on the system"""
        try:
            # Check if amass is in PATH
            if platform.system() == "Windows":
                amass_cmd = "where amass"
            else:
                amass_cmd = "which amass"
            
            result = subprocess.run(amass_cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_subdomain(self, subdomain, domain):
        """Check if a subdomain exists"""
        if self._stop_event.is_set():
            return None
        
        full_domain = f"{subdomain}.{domain}"
        try:
            ip = socket.gethostbyname(full_domain)
            return full_domain, ip
        except socket.gaierror:
            # Try to resolve with dns.resolver as fallback
            try:
                answers = self.resolver.resolve(full_domain, 'A')
                for answer in answers:
                    return full_domain, str(answer)
            except:
                pass
        except Exception:
            pass
        return None
    
    def _run_amass(self, domain, output_file):
        """Run amass command-line tool for advanced subdomain enumeration"""
        try:
            # Basic amass command for passive enumeration
            cmd = f"amass enum -passive -d {domain} -o {output_file}"
            
            # Run amass command
            subprocess.run(cmd, shell=True, check=True)
            
            # Read results
            found_subdomains = []
            with open(output_file, 'r') as f:
                for line in f:
                    subdomain = line.strip()
                    if subdomain:
                        found_subdomains.append(subdomain)
            
            return found_subdomains
            
        except Exception as e:
            self.enum_error.emit(f"Amass error: {str(e)}")
            return []
    
    def enumerate(self, domain, wordlist=None, max_threads=20, use_amass=False):
        """Enumerate subdomains for a domain using a wordlist"""
        try:
            # Reset stop event
            self._stop_event.clear()
            
            # Track total subdomains to process and found
            total_found = 0
            all_subdomains = []
            
            # If amass is available and user requested, use it
            if use_amass and self._amass_available:
                self.progress_update.emit(10)
                
                # Create a temporary file for amass output
                with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp:
                    amass_output = tmp.name
                
                try:
                    # Run amass and get results
                    self.progress_update.emit(15)
                    amass_subdomains = self._run_amass(domain, amass_output)
                    
                    # Process amass results
                    if amass_subdomains:
                        self.progress_update.emit(40)
                        
                        # Resolve IP for each subdomain
                        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                            tasks = {}
                            for subdomain in amass_subdomains:
                                if self._stop_event.is_set():
                                    break
                                
                                tasks[executor.submit(socket.gethostbyname, subdomain)] = subdomain
                            
                            for i, future in enumerate(concurrent.futures.as_completed(tasks)):
                                if self._stop_event.is_set():
                                    break
                                
                                subdomain = tasks[future]
                                try:
                                    ip = future.result()
                                    self.result_update.emit(subdomain, ip)
                                    total_found += 1
                                except Exception:
                                    # Failed to resolve, just show without IP
                                    self.result_update.emit(subdomain, "Could not resolve")
                                
                                # Update progress from 40% to 90%
                                progress = 40 + min(50, int((i / len(tasks)) * 50))
                                self.progress_update.emit(progress)
                    
                    # Continue with brute forcing if wordlist provided
                    if wordlist and not self._stop_event.is_set():
                        # Calculate new progress percentage
                        start_progress = 90
                        self.progress_update.emit(start_progress)
                        
                        # Use wordlist for brute force with reduced weight
                        self._brute_force_subdomains(domain, wordlist, max_threads, start_progress)
                    else:
                        self.progress_update.emit(100)
                    
                finally:
                    # Clean up temp file
                    try:
                        os.unlink(amass_output)
                    except:
                        pass
                        
            else:
                # Use default wordlist if none provided
                if wordlist is None:
                    # Small default list for testing
                    wordlist = [
                        "www", "mail", "remote", "blog", "webmail", "server", "ns1", "ns2",
                        "smtp", "secure", "vpn", "m", "shop", "ftp", "api", "admin", "dev",
                        "test", "portal", "gitlab", "cdn", "cloud", "images", "img", "app"
                    ]
                
                # Use the brute force method
                self._brute_force_subdomains(domain, wordlist, max_threads, 0)
            
            if not self._stop_event.is_set():
                self.enum_completed.emit()
        
        except Exception as e:
            self.enum_error.emit(str(e))
    
    def _brute_force_subdomains(self, domain, wordlist, max_threads, start_progress=0):
        """Brute force subdomains using a wordlist"""
        total = len(wordlist)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_subdomain = {
                executor.submit(self._check_subdomain, subdomain, domain): subdomain
                for subdomain in wordlist
            }
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_subdomain):
                if self._stop_event.is_set():
                    break
                
                result = future.result()
                if result:
                    subdomain, ip = result
                    self.result_update.emit(subdomain, ip)
                
                # Update progress
                completed += 1
                progress = start_progress + int(((100 - start_progress) * completed) / total)
                self.progress_update.emit(progress)
    
    def stop_enumeration(self):
        """Stop the enumeration process"""
        self._stop_event.set()
