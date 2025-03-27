"""
Port scanning module for Astra
"""

import socket
import threading
import ipaddress
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtCore import QObject, pyqtSignal

class PortScanner(QObject):
    """Port scanner class that emits signals for GUI updates"""
    
    # Signal to update progress
    progress_update = pyqtSignal(int)
    
    # Signal to update results (port, state, service)
    result_update = pyqtSignal(int, bool, str)
    
    # Signal for completion
    scan_completed = pyqtSignal()
    
    # Signal for errors
    scan_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self._common_ports = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            115: "SFTP",
            135: "RPC",
            139: "NetBIOS",
            143: "IMAP",
            194: "IRC",
            443: "HTTPS",
            445: "SMB",
            1433: "MSSQL",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            8080: "HTTP-Proxy"
        }
        self._scan_method = "asyncio"  # Default scan method (asyncio/threading)
    
    def set_scan_method(self, method):
        """Set the scanning method (asyncio or threading)"""
        if method in ["asyncio", "threading"]:
            self._scan_method = method

    def scan_port(self, target, port, timeout=1):
        """Scan a single port and return if it's open (using socket)"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((target, port))
                is_open = (result == 0)
                service = self._common_ports.get(port, "Unknown")
                return port, is_open, service
        except Exception as e:
            return port, False, str(e)
    
    async def async_scan_port(self, target, port, timeout=1):
        """Scan a single port asynchronously"""
        try:
            # Create a future that will run the socket connect in a thread pool
            loop = asyncio.get_running_loop()
            future = loop.run_in_executor(
                None, 
                self.scan_port, 
                target, 
                port, 
                timeout
            )
            
            # Wait for the result
            result = await future
            return result
        except Exception as e:
            return port, False, str(e)
    
    async def _async_scan(self, target, port_range, timeout):
        """Perform an asynchronous port scan"""
        start_port, end_port = port_range
        total_ports = end_port - start_port + 1
        
        # Create a list of tasks for each port
        tasks = []
        for port in range(start_port, end_port + 1):
            if self._stop_event.is_set():
                break
            tasks.append(self.async_scan_port(target, port, timeout))
        
        # Create batches of tasks to avoid creating too many at once
        batch_size = 100
        completed = 0
        
        for i in range(0, len(tasks), batch_size):
            if self._stop_event.is_set():
                break
                
            batch = tasks[i:i+batch_size]
            for result in await asyncio.gather(*batch):
                if self._stop_event.is_set():
                    break
                    
                port, is_open, service = result
                self.result_update.emit(port, is_open, service)
                
                # Update progress
                completed += 1
                progress = int((completed / total_ports) * 100)
                self.progress_update.emit(progress)
    
    def scan(self, target, port_range=(1, 1024), thread_count=50, timeout=1):
        """Scan a range of ports on the target"""
        try:
            # Reset stop event
            self._stop_event.clear()
            
            # Check if target is valid
            try:
                socket.gethostbyname(target)
            except socket.gaierror:
                self.scan_error.emit(f"Cannot resolve hostname: {target}")
                return
            
            # Choose scan method
            if self._scan_method == "asyncio":
                # Use asyncio for scanning
                try:
                    asyncio.run(self._async_scan(target, port_range, timeout))
                    if not self._stop_event.is_set():
                        self.scan_completed.emit()
                except Exception as e:
                    self.scan_error.emit(f"Asyncio scan error: {str(e)}")
            else:
                # Use threading for scanning (original method)
                start_port, end_port = port_range
                total_ports = end_port - start_port + 1
                
                with ThreadPoolExecutor(max_workers=thread_count) as executor:
                    futures = []
                    
                    for port in range(start_port, end_port + 1):
                        if self._stop_event.is_set():
                            break
                        futures.append(executor.submit(self.scan_port, target, port, timeout))
                    
                    completed = 0
                    for future in futures:
                        if self._stop_event.is_set():
                            break
                        port, is_open, service = future.result()
                        self.result_update.emit(port, is_open, service)
                        
                        # Update progress
                        completed += 1
                        progress = int((completed / total_ports) * 100)
                        self.progress_update.emit(progress)
                
                if not self._stop_event.is_set():
                    self.scan_completed.emit()
        
        except Exception as e:
            self.scan_error.emit(str(e))
    
    def stop_scan(self):
        """Stop the scanning process"""
        self._stop_event.set()
