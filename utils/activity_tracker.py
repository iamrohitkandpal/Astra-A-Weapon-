"""
Activity tracker to record and display recent user actions
"""
import time
import json
import os
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

class ActivityType:
    """Enumeration of activity types"""
    SCAN = "scan"
    SEARCH = "search"
    ANALYSIS = "analysis"
    REPORT = "report"
    TOOL_USAGE = "tool_usage"
    EXPORT = "export"
    OTHER = "other"

class ActivityTracker(QObject):
    """
    Activity tracker to record user actions and provide recent activities list
    """
    
    # Signal emitted when activities are updated
    activities_updated = pyqtSignal()
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ActivityTracker, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        super().__init__()
        self._initialized = True
        self.max_activities = 50
        self.activities = []
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing activities
        self.load_activities()
    
    def log_activity(self, activity_type, description, details=None, tool_id=None):
        """
        Log a new user activity
        
        Args:
            activity_type (str): Type of activity (from ActivityType)
            description (str): Short description of the activity
            details (dict, optional): Additional details about the activity
            tool_id (str, optional): ID of the tool used, if applicable
        """
        timestamp = time.time()
        formatted_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        activity = {
            "type": activity_type,
            "description": description,
            "timestamp": timestamp,
            "formatted_time": formatted_time,
            "details": details or {},
        }
        
        if tool_id:
            activity["tool_id"] = tool_id
        
        # Add to activities list
        self.activities.insert(0, activity)
        
        # Trim list if too long
        if len(self.activities) > self.max_activities:
            self.activities = self.activities[:self.max_activities]
        
        # Save activities
        self.save_activities()
        
        # Emit signal
        self.activities_updated.emit()
    
    def get_recent_activities(self, limit=10):
        """Get list of recent activities"""
        return self.activities[:limit]
    
    def clear_activities(self):
        """Clear all activities"""
        self.activities = []
        self.save_activities()
        self.activities_updated.emit()
    
    def save_activities(self):
        """Save activities to file"""
        activities_file = os.path.join(self.data_dir, "recent_activities.json")
        try:
            with open(activities_file, 'w') as f:
                json.dump(self.activities, f)
        except Exception as e:
            print(f"Error saving activities: {e}")
    
    def load_activities(self):
        """Load activities from file"""
        activities_file = os.path.join(self.data_dir, "recent_activities.json")
        if os.path.exists(activities_file):
            try:
                with open(activities_file, 'r') as f:
                    self.activities = json.load(f)
            except Exception as e:
                print(f"Error loading activities: {e}")
                self.activities = []
        else:
            self.activities = []
