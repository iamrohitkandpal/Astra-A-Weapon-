"""
AI-powered report enhancement module for vulnerability reporting
"""
import os
import json
import random
from datetime import datetime
from PyQt6.QtGui import QColor

class AIReportEnhancer:
    """
    Enhances vulnerability reports with AI-suggested mitigations and risk scoring
    """
    
    def __init__(self):
        self.risk_thresholds = {
            "CRITICAL": (90, 100, QColor(128, 0, 0)),  # Dark red
            "HIGH": (70, 89, QColor(255, 0, 0)),       # Red
            "MEDIUM": (40, 69, QColor(255, 153, 0)),   # Orange
            "LOW": (20, 39, QColor(255, 255, 0)),      # Yellow
            "INFO": (0, 19, QColor(0, 170, 0))         # Green
        }
        
        # Load pre-defined mitigations for common vulnerabilities
        self.mitigation_templates = self._load_mitigation_templates()
    
    def _load_mitigation_templates(self):
        """Load mitigation templates from file or provide defaults"""
        templates_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 
            'mitigation_templates.json'
        )
        
        default_templates = {
            "SQL Injection": [
                "Use parameterized queries or prepared statements",
                "Apply input validation and sanitization",
                "Use an ORM (Object-Relational Mapping) with safe defaults",
                "Apply the principle of least privilege to database accounts",
                "Consider using a Web Application Firewall (WAF)"
            ],
            "Cross-Site Scripting (XSS)": [
                "Implement context-sensitive output encoding",
                "Use Content-Security-Policy (CSP) header",
                "Sanitize user inputs before rendering",
                "Use modern frameworks with automatic XSS protection",
                "Implement X-XSS-Protection header"
            ],
            "Open Redirect": [
                "Implement a whitelist of allowed destinations",
                "Avoid using user-controlled input for redirect destinations",
                "Use indirect reference maps (mapping ID to URL)",
                "Validate URLs against a regular expression pattern",
                "If redirection is necessary, redirect to a warning page first"
            ],
            "Path Traversal": [
                "Use canonicalized file paths",
                "Implement proper access controls",
                "Whitelist allowed file paths instead of blacklisting bad ones",
                "Use dedicated APIs for file operations that limit access",
                "Avoid putting user input directly into file operations"
            ],
            "Server Error": [
                "Implement proper error handling",
                "Use try-catch blocks to handle exceptions gracefully",
                "Configure custom error pages",
                "Don't reveal sensitive information in error messages",
                "Log errors for internal review but sanitize public messages"
            ],
            "Missing Security Header": [
                "Implement all recommended security headers",
                "Use security header analyzers to verify implementation",
                "Configure headers in web server or application level",
                "Stay current with header recommendations",
                "Use secure defaults for all headers"
            ]
        }
        
        try:
            if os.path.exists(templates_path):
                with open(templates_path, 'r') as f:
                    return json.load(f)
            else:
                # Create the data directory if it doesn't exist
                os.makedirs(os.path.dirname(templates_path), exist_ok=True)
                
                # Save default templates for future use
                with open(templates_path, 'w') as f:
                    json.dump(default_templates, f, indent=2)
                    
                return default_templates
        except Exception:
            return default_templates
    
    def get_risk_color(self, score):
        """Get color based on risk score"""
        for severity, (min_val, max_val, color) in self.risk_thresholds.items():
            if min_val <= score <= max_val:
                return color
        return QColor(128, 128, 128)  # Gray for unknown
    
    def get_severity_from_score(self, score):
        """Get severity level from risk score"""
        for severity, (min_val, max_val, _) in self.risk_thresholds.items():
            if min_val <= score <= max_val:
                return severity
        return "UNKNOWN"
    
    def enhance_vulnerability_report(self, vulnerability_type, url, description, severity):
        """
        Enhance a vulnerability report with AI-suggested mitigations and risk scoring
        
        Returns:
            tuple: (description, risk_score, risk_color)
        """
        # Extract risk score if it exists in the description
        risk_score = None
        if "Risk Score:" in description:
            try:
                score_text = description.split("Risk Score:")[1].split("/")[0].strip()
                risk_score = float(score_text)
            except (ValueError, IndexError):
                # If we can't extract it, calculate it
                risk_score = self._calculate_risk_score(vulnerability_type, severity, url)
        else:
            # Calculate risk score
            risk_score = self._calculate_risk_score(vulnerability_type, severity, url)
        
        # Check if mitigations are already present
        if "AI-Suggested Mitigations:" not in description:
            # Get mitigations
            mitigations = self._get_mitigations(vulnerability_type, description)
            
            # Add to description
            description += f"\n\n🔍 Risk Score: {risk_score}/100\n\n"
            description += "🛡️ AI-Suggested Mitigations:\n"
            
            for i, mitigation in enumerate(mitigations[:5], 1):
                description += f"{i}. {mitigation}\n"
        
        # Get color based on risk score
        risk_color = self.get_risk_color(risk_score)
        
        return (description, risk_score, risk_color)
    
    def _calculate_risk_score(self, vulnerability_type, severity, url):
        """Calculate a risk score from 0-100 based on various factors"""
        # Base score by severity
        base_score = {
            "LOW": 20,
            "MEDIUM": 50,
            "HIGH": 80,
            "CRITICAL": 95
        }.get(severity, 30)
        
        # Adjust based on vulnerability type
        type_modifier = {
            "SQL Injection": 20,
            "Cross-Site Scripting (XSS)": 15,
            "DOM-Based XSS": 15,
            "File Inclusion": 18,
            "Command Injection": 20,
            "Open Redirect": 10,
            "Server Error": 5,
            "Potential Zero-Day Vulnerability": 25,
            "Missing Security Header": 5,
            "Information Disclosure": 8
        }.get(vulnerability_type, 0)
        
        # URL context factors
        url_ctx_score = 0
        if "/admin" in url.lower():
            url_ctx_score += 15
        if "/login" in url.lower() or "/account" in url.lower() or "/user" in url.lower():
            url_ctx_score += 10
        if "/api" in url.lower():
            url_ctx_score += 8
        
        # Calculate final score with cap
        final_score = min(base_score + type_modifier + url_ctx_score, 100)
        return final_score
    
    def _get_mitigations(self, vulnerability_type, description):
        """Get mitigations for a vulnerability type"""
        # Look for mitigations in templates
        if vulnerability_type in self.mitigation_templates:
            mitigations = self.mitigation_templates[vulnerability_type]
        else:
            # Use generic mitigations if specific ones aren't available
            mitigations = [
                "Implement input validation and output encoding",
                "Apply the principle of least privilege",
                "Keep all software and libraries updated",
                "Use a Web Application Firewall (WAF)",
                "Conduct regular security audits and code reviews",
                "Follow secure coding practices and guidelines"
            ]
            
            # Shuffle for variation
            random.shuffle(mitigations)
        
        return mitigations
    
    def generate_executive_summary(self, vulnerabilities):
        """
        Generate an executive summary of vulnerabilities found
        
        Args:
            vulnerabilities: List of vulnerability tuples (type, url, description, severity)
        
        Returns:
            str: Executive summary
        """
        if not vulnerabilities:
            return "No vulnerabilities were detected during the scan."
        
        # Count vulnerabilities by severity
        severity_counts = {}
        for v_type, _, _, severity in vulnerabilities:
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Generate summary
        summary = f"Executive Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        summary += f"Total vulnerabilities found: {len(vulnerabilities)}\n\n"
        
        # Add severity breakdown
        summary += "Severity breakdown:\n"
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            count = severity_counts.get(severity, 0)
            summary += f"- {severity}: {count}\n"
        
        # Calculate overall risk
        if severity_counts.get("CRITICAL", 0) > 0:
            risk_level = "CRITICAL"
        elif severity_counts.get("HIGH", 0) > 0:
            risk_level = "HIGH"
        elif severity_counts.get("MEDIUM", 0) > 0:
            risk_level = "MEDIUM"
        elif severity_counts.get("LOW", 0) > 0:
            risk_level = "LOW"
        else:
            risk_level = "INFO"
        
        summary += f"\nOverall risk level: {risk_level}\n\n"
        
        # Add top vulnerabilities
        summary += "Top vulnerabilities:\n"
        for i, (v_type, url, _, severity) in enumerate(vulnerabilities[:5], 1):
            summary += f"{i}. {v_type} ({severity}) at {url}\n"
        
        # Add recommendations
        summary += "\nKey recommendations:\n"
        
        # Get unique vulnerability types
        vuln_types = set([v[0] for v in vulnerabilities])
        
        # Get recommendations for each type
        all_recommendations = []
        for v_type in vuln_types:
            if v_type in self.mitigation_templates:
                recommendations = self.mitigation_templates[v_type][:2]  # Top 2 recommendations per type
                all_recommendations.extend(recommendations)
        
        # If we have recommendations, add them
        if all_recommendations:
            for i, rec in enumerate(all_recommendations[:5], 1):  # Top 5 overall
                summary += f"{i}. {rec}\n"
        else:
            # Generic recommendations
            summary += "1. Conduct a comprehensive security review of the application\n"
            summary += "2. Implement secure coding practices and training\n"
            summary += "3. Establish a security testing process before deployment\n"
        
        return summary
