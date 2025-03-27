"""
Web crawler implementation with improved performance and stability
"""
import re
import time
import queue
import threading
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from PyQt6.QtCore import QObject, pyqtSignal, QThread

class WebCrawlerWorker(QObject):
    """Worker for web crawling operations"""
    
    # Signals
    progress_updated = pyqtSignal(int)  # Progress percentage
    url_discovered = pyqtSignal(str)    # New URL discovered
    log_message = pyqtSignal(str)       # Log message
    error_occurred = pyqtSignal(str)    # Error message
    crawl_complete = pyqtSignal(dict)   # Results dictionary
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.stop_requested = False
        self.results = {
            'visited_urls': set(),
            'discovered_urls': set(),
            'external_links': set(),
            'resources': {
                'images': set(),
                'scripts': set(),
                'stylesheets': set(),
                'documents': set()
            },
            'page_titles': {},
            'status_codes': {}
        }
        
        # Configure requests session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Configure threading and rate limiting
        self.url_queue = queue.Queue()
        self.processing_urls = set()
        self.max_threads = 3  # Limit to prevent overloading sites
        self.rate_limit = 1.0  # Time in seconds between requests
        self.last_request_time = {}  # Per domain rate limiting
        
        # Thread tracking
        self.active_threads = 0
        self.threads_lock = threading.Lock()
    
    def start_crawl(self, start_url, max_urls=100, max_depth=3, stay_within_domain=True):
        """Start the crawling process"""
        if self.running:
            self.log_message.emit("Already running a crawl operation")
            return
        
        # Reset state
        self.running = True
        self.stop_requested = False
        self.results = {
            'visited_urls': set(),
            'discovered_urls': set(),
            'external_links': set(),
            'resources': {
                'images': set(),
                'scripts': set(),
                'stylesheets': set(),
                'documents': set()
            },
            'page_titles': {},
            'status_codes': {}
        }
        
        # Parse the starting URL
        try:
            start_url = start_url.strip()
            if not start_url.startswith(('http://', 'https://')):
                start_url = 'https://' + start_url
                
            # Test the URL
            self.log_message.emit(f"Testing connection to {start_url}")
            response = self.session.head(start_url, timeout=10)
            if response.status_code >= 400:
                self.error_occurred.emit(f"Initial URL returned status code {response.status_code}")
                self.running = False
                return
                
            parsed_url = urlparse(start_url)
            self.base_domain = parsed_url.netloc
            
            # Add the start URL to the queue
            self.url_queue.put((start_url, 0))  # (url, depth)
            self.results['discovered_urls'].add(start_url)
            
            self.log_message.emit(f"Starting crawl from {start_url}")
            self.log_message.emit(f"Settings: max URLs={max_urls}, max depth={max_depth}, stay within domain={stay_within_domain}")
            
            # Start worker threads
            self.worker_threads = []
            for i in range(self.max_threads):
                thread = threading.Thread(
                    target=self._crawl_worker,
                    args=(max_urls, max_depth, stay_within_domain),
                    daemon=True
                )
                thread.start()
                self.worker_threads.append(thread)
                
            # Start monitor thread
            self.monitor_thread = threading.Thread(
                target=self._monitor_progress, 
                args=(max_urls,),
                daemon=True
            )
            self.monitor_thread.start()
            
        except Exception as e:
            self.error_occurred.emit(f"Error starting crawl: {str(e)}")
            self.running = False
    
    def stop_crawl(self):
        """Stop the crawling process"""
        if not self.running:
            return
            
        self.log_message.emit("Stopping crawl...")
        self.stop_requested = True
        
        # Wait for threads to finish
        for thread in self.worker_threads:
            if thread.is_alive():
                thread.join(timeout=2.0)
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
            
        self.running = False
        self.log_message.emit("Crawl stopped")
        
        # Send final results
        self.crawl_complete.emit(self._get_results_dict())
    
    def _get_results_dict(self):
        """Convert sets to lists for JSON serialization"""
        results = {
            'visited_urls': list(self.results['visited_urls']),
            'discovered_urls': list(self.results['discovered_urls']),
            'external_links': list(self.results['external_links']),
            'resources': {
                'images': list(self.results['resources']['images']),
                'scripts': list(self.results['resources']['scripts']),
                'stylesheets': list(self.results['resources']['stylesheets']),
                'documents': list(self.results['resources']['documents'])
            },
            'page_titles': self.results['page_titles'],
            'status_codes': self.results['status_codes']
        }
        return results
    
    def _monitor_progress(self, max_urls):
        """Monitor crawling progress and update UI"""
        while self.running and not self.stop_requested:
            time.sleep(0.5)  # Check every half second
            
            # Calculate progress
            visited_count = len(self.results['visited_urls'])
            progress = min(int((visited_count / max_urls) * 100), 100)
            
            # Emit progress signal
            self.progress_updated.emit(progress)
            
            # Check if we're done
            if visited_count >= max_urls or (visited_count > 0 and self.url_queue.empty() and self.active_threads == 0):
                self.log_message.emit(f"Crawl complete. Visited {visited_count} URLs.")
                self.crawl_complete.emit(self._get_results_dict())
                self.running = False
                break
    
    def _crawl_worker(self, max_urls, max_depth, stay_within_domain):
        """Worker thread for crawling URLs"""
        try:
            with self.threads_lock:
                self.active_threads += 1
                
            while self.running and not self.stop_requested:
                # Check if we've reached the limit
                if len(self.results['visited_urls']) >= max_urls:
                    break
                
                try:
                    # Get a URL from the queue with timeout
                    try:
                        url, depth = self.url_queue.get(timeout=2.0)
                    except queue.Empty:
                        # If the queue is empty and no URLs are being processed, we might be done
                        if self.active_threads <= 1:  # Only this thread is active
                            break
                        continue
                    
                    # Check if we already processed this URL
                    if url in self.results['visited_urls'] or url in self.processing_urls:
                        self.url_queue.task_done()
                        continue
                    
                    # Mark as being processed
                    self.processing_urls.add(url)
                    
                    # Apply rate limiting
                    self._apply_rate_limit(url)
                    
                    # Process the URL
                    self._process_url(url, depth, max_depth, stay_within_domain)
                    
                    # Mark as done
                    self.processing_urls.remove(url)
                    self.url_queue.task_done()
                    
                except Exception as e:
                    self.log_message.emit(f"Error processing URL: {str(e)}")
        finally:
            with self.threads_lock:
                self.active_threads -= 1
    
    def _apply_rate_limit(self, url):
        """Apply rate limiting per domain"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Check if we need to wait for rate limiting
        current_time = time.time()
        if domain in self.last_request_time:
            time_since_last = current_time - self.last_request_time[domain]
            if time_since_last < self.rate_limit:
                time.sleep(self.rate_limit - time_since_last)
        
        # Update the last request time
        self.last_request_time[domain] = time.time()
    
    def _process_url(self, url, depth, max_depth, stay_within_domain):
        """Process a single URL"""
        try:
            # Don't process if we've reached max URLs
            if len(self.results['visited_urls']) >= max_depth:
                return
                
            # Skip if already visited
            if url in self.results['visited_urls']:
                return
                
            # Parse URL
            parsed_url = urlparse(url)
            
            # Skip non-HTTP/HTTPS URLs
            if parsed_url.scheme not in ('http', 'https'):
                return
                
            # Skip if we need to stay within domain
            if stay_within_domain and parsed_url.netloc != self.base_domain:
                self.results['external_links'].add(url)
                return
                
            # Check resource file types - don't download large files
            path = parsed_url.path.lower()
            if any(path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.exe']):
                self._categorize_resource(url)
                return
            
            # Fetch the URL
            self.log_message.emit(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            # Store status code
            self.results['status_codes'][url] = response.status_code
            
            # Skip non-successful responses
            if response.status_code != 200:
                self.log_message.emit(f"Skipping URL with status code {response.status_code}: {url}")
                return
                
            # Check content type
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('text/html'):
                self._categorize_resource(url, content_type)
                return
                
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract page title
            title_tag = soup.find('title')
            if title_tag and title_tag.string:
                self.results['page_titles'][url] = title_tag.string.strip()
            
            # Mark as visited
            self.results['visited_urls'].add(url)
            self.url_discovered.emit(url)
            
            # Don't proceed further if we've reached max depth
            if depth >= max_depth:
                return
                
            # Extract links
            self._extract_links(soup, url, depth, stay_within_domain)
            
            # Extract resources
            self._extract_resources(soup, url)
            
        except requests.RequestException as e:
            self.log_message.emit(f"Request error for {url}: {str(e)}")
        except Exception as e:
            self.log_message.emit(f"Error processing {url}: {str(e)}")
    
    def _extract_links(self, soup, base_url, current_depth, stay_within_domain):
        """Extract links from the HTML soup"""
        parsed_base = urlparse(base_url)
        
        # Find all <a> tags
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            
            # Skip empty, javascript, and anchor links
            if (not href or 
                href.startswith(('javascript:', '#', 'mailto:', 'tel:'))):
                continue
                
            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)
            
            # Parse the URL
            parsed_url = urlparse(absolute_url)
            
            # Clean the URL (remove fragments)
            clean_url = parsed_url._replace(fragment='').geturl()
            
            # Check if it's an external link
            is_external = parsed_url.netloc != parsed_base.netloc
            
            # Add to appropriate set
            if is_external:
                if stay_within_domain:
                    self.results['external_links'].add(clean_url)
                else:
                    # Only add external if we're allowed to crawl outside
                    self.results['discovered_urls'].add(clean_url)
                    if clean_url not in self.results['visited_urls']:
                        self.url_queue.put((clean_url, current_depth + 1))
            else:
                # Internal link
                if clean_url not in self.results['visited_urls'] and clean_url not in self.results['discovered_urls']:
                    self.results['discovered_urls'].add(clean_url)
                    self.url_queue.put((clean_url, current_depth + 1))
    
    def _extract_resources(self, soup, base_url):
        """Extract resource links from the HTML soup"""
        # Images
        for img in soup.find_all('img', src=True):
            src = img['src'].strip()
            if src:
                absolute_url = urljoin(base_url, src)
                self.results['resources']['images'].add(absolute_url)
        
        # Scripts
        for script in soup.find_all('script', src=True):
            src = script['src'].strip()
            if src:
                absolute_url = urljoin(base_url, src)
                self.results['resources']['scripts'].add(absolute_url)
        
        # Stylesheets
        for link in soup.find_all('link', rel='stylesheet', href=True):
            href = link['href'].strip()
            if href:
                absolute_url = urljoin(base_url, href)
                self.results['resources']['stylesheets'].add(absolute_url)
                
        # Other documents
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            if any(href.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']):
                absolute_url = urljoin(base_url, href)
                self.results['resources']['documents'].add(absolute_url)
    
    def _categorize_resource(self, url, content_type=None):
        """Categorize a URL as a resource based on extension or content type"""
        path = urlparse(url).path.lower()
        
        if path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp')):
            self.results['resources']['images'].add(url)
        elif path.endswith(('.js')):
            self.results['resources']['scripts'].add(url)
        elif path.endswith(('.css')):
            self.results['resources']['stylesheets'].add(url)
        elif path.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx')):
            self.results['resources']['documents'].add(url)
        elif content_type:
            if 'image/' in content_type:
                self.results['resources']['images'].add(url)
            elif 'javascript' in content_type:
                self.results['resources']['scripts'].add(url)
            elif 'css' in content_type:
                self.results['resources']['stylesheets'].add(url)
            elif any(doc_type in content_type for doc_type in ['pdf', 'msword', 'vnd.ms-', 'vnd.openxmlformats']):
                self.results['resources']['documents'].add(url)
