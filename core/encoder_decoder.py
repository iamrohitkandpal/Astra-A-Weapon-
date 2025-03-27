"""
Encoding and decoding module for Astra
"""

import base64
import hashlib
import html
import urllib.parse
import json
import binascii
import codecs
from PyQt6.QtCore import QObject, pyqtSignal

class EncoderDecoder(QObject):
    """Class for encoding and decoding data in various formats"""
    
    # Signal for error
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Define available encoders
        self.encoders = {
            "base64": self._encode_base64,
            "url": self._encode_url,
            "html": self._encode_html,
            "hex": self._encode_hex,
            "binary": self._encode_binary,
            "rot13": self._encode_rot13,
            "md5": self._hash_md5,
            "sha1": self._hash_sha1,
            "sha256": self._hash_sha256,
            "sha512": self._hash_sha512
        }
        
        # Define available decoders
        self.decoders = {
            "base64": self._decode_base64,
            "url": self._decode_url,
            "html": self._decode_html,
            "hex": self._decode_hex,
            "binary": self._decode_binary,
            "rot13": self._decode_rot13
        }
    
    def get_encoder_types(self):
        """Return list of available encoder types"""
        return list(self.encoders.keys())
    
    def get_decoder_types(self):
        """Return list of available decoder types"""
        return list(self.decoders.keys())
    
    def encode(self, text, encoder_type):
        """Encode text using the specified encoder"""
        if not text:
            return ""
            
        if encoder_type not in self.encoders:
            self.error.emit(f"Unknown encoder type: {encoder_type}")
            return None
        
        try:
            return self.encoders[encoder_type](text)
        except Exception as e:
            self.error.emit(f"Encoding error: {str(e)}")
            return None
    
    def decode(self, text, decoder_type):
        """Decode text using the specified decoder"""
        if not text:
            return ""
            
        if decoder_type not in self.decoders:
            self.error.emit(f"Unknown decoder type: {decoder_type}")
            return None
        
        try:
            return self.decoders[decoder_type](text)
        except Exception as e:
            self.error.emit(f"Decoding error: {str(e)}")
            return None
    
    # Encoder methods
    def _encode_base64(self, text):
        """Encode text to Base64"""
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
    
    def _encode_url(self, text):
        """Encode text for URL"""
        return urllib.parse.quote_plus(text)
    
    def _encode_html(self, text):
        """Encode text to HTML entities"""
        return html.escape(text)
    
    def _encode_hex(self, text):
        """Encode text to hexadecimal"""
        return binascii.hexlify(text.encode('utf-8')).decode('utf-8')
    
    def _encode_binary(self, text):
        """Encode text to binary"""
        return ' '.join(format(ord(char), '08b') for char in text)
    
    def _encode_rot13(self, text):
        """Encode text with ROT13"""
        return codecs.encode(text, 'rot_13')
    
    # Hash methods (one-way encoding)
    def _hash_md5(self, text):
        """Hash text with MD5"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _hash_sha1(self, text):
        """Hash text with SHA-1"""
        return hashlib.sha1(text.encode('utf-8')).hexdigest()
    
    def _hash_sha256(self, text):
        """Hash text with SHA-256"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _hash_sha512(self, text):
        """Hash text with SHA-512"""
        return hashlib.sha512(text.encode('utf-8')).hexdigest()
    
    # Decoder methods
    def _decode_base64(self, text):
        """Decode Base64 to text"""
        return base64.b64decode(text.encode('utf-8')).decode('utf-8')
    
    def _decode_url(self, text):
        """Decode URL-encoded text"""
        return urllib.parse.unquote_plus(text)
    
    def _decode_html(self, text):
        """Decode HTML entities to text"""
        return html.unescape(text)
    
    def _decode_hex(self, text):
        """Decode hexadecimal to text"""
        # Remove any whitespace
        text = ''.join(text.split())
        return binascii.unhexlify(text).decode('utf-8')
    
    def _decode_binary(self, text):
        """Decode binary to text"""
        # Remove any extra whitespace
        binary_values = text.split()
        return ''.join(chr(int(binary, 2)) for binary in binary_values)
    
    def _decode_rot13(self, text):
        """Decode ROT13 text"""
        return codecs.encode(text, 'rot_13')  # ROT13 is symmetric
