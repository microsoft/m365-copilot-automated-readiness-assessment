"""
DefenderInsights - Pre-computed security metrics from Defender client
Similar to pp_insights pattern for Power Platform
"""

class DefenderInsights:
    """
    Pre-computes all security metrics from defender_client once.
    Provides clean properties for recommendation functions to use.
    """
    
    def __init__(self, defender_client):
        """Initialize and pre-compute all metrics"""
        self.defender_client = defender_client
        self.available = False
        
        if not defender_client:
            return
        
        # Check availability
        self.graph_security_available = hasattr(defender_client, 'graph_security_available') and defender_client.graph_security_available
        self.defender_api_available = defender_client.available if hasattr(defender_client, 'available') else False
        self.available = self.graph_security_available or self.defender_api_available
        
        if not self.available:
            return
        
        # Pre-compute all metrics
        self._compute_oauth_metrics()
        self._compute_alert_metrics()
        self._compute_incident_metrics()
        self._compute_identity_metrics()
    
    def _compute_oauth_metrics(self):
        """Extract OAuth app risk metrics"""
        oauth = self.defender_client.oauth_risk_summary
        self.oauth_high_risk = oauth.get('high_risk', 0)
        self.oauth_over_privileged = oauth.get('over_privileged', 0)
        self.oauth_total = oauth.get('total_apps', 0)
        
        # Build metrics text
        self.oauth_metrics = []
        self.oauth_recommendation = ""
        
        if self.oauth_high_risk > 0:
            self.oauth_metrics.append(f"{self.oauth_high_risk} high-risk OAuth apps")
            self.oauth_recommendation = f"Review {self.oauth_high_risk} high-risk app permissions"
        elif self.oauth_over_privileged > 0:
            self.oauth_metrics.append(f"{self.oauth_over_privileged} over-privileged apps")
    
    def _compute_alert_metrics(self):
        """Extract alert metrics by category"""
        alerts = self.defender_client.alert_summary
        by_cat = alerts.get('by_category', {})
        
        self.alert_total = alerts.get('total', 0)
        self.alert_phishing = by_cat.get('Phishing', 0)
        self.alert_malware = by_cat.get('Malware', 0)
        
        # Build metrics text for different scenarios
        self.phishing_malware_metrics = []
        if self.alert_phishing > 0:
            self.phishing_malware_metrics.append(f"{self.alert_phishing} phishing alerts")
        if self.alert_malware > 0:
            self.phishing_malware_metrics.append(f"{self.alert_malware} malware alerts")
    
    def _compute_incident_metrics(self):
        """Extract incident metrics"""
        inc = self.defender_client.incident_summary
        
        self.incident_total = inc.get('total', 0)
        self.incident_active = inc.get('active', 0)
        self.incident_high_severity = inc.get('high_severity', 0)
        
        # Build metrics and recommendation
        self.incident_metrics = []
        self.incident_recommendation = ""
        
        if self.incident_total > 0:
            if self.incident_high_severity > 0:
                self.incident_metrics.append(f"{self.incident_active} incidents ({self.incident_high_severity} high-severity)")
                self.incident_recommendation = f"Investigate {self.incident_high_severity} high-severity incident(s)"
            elif self.incident_active > 0:
                self.incident_metrics.append(f"{self.incident_active} active incidents")
                self.incident_recommendation = f"Review {self.incident_active} active incident(s)"
    
    def _compute_identity_metrics(self):
        """Extract identity risk metrics"""
        risky = self.defender_client.risky_users_summary
        sign_ins = self.defender_client.risky_sign_ins_summary
        
        self.risky_users_total = risky.get('total', 0)
        self.risky_users_high = risky.get('high', 0)
        self.risky_users_compromised = risky.get('confirmed_compromised', 0)
        self.risky_sign_ins_high = sign_ins.get('high_risk', 0)
        
        # Build metrics and recommendation
        self.identity_metrics = []
        self.identity_recommendation = ""
        
        if self.risky_users_total > 0:
            if self.risky_users_compromised > 0:
                self.identity_metrics.append(f"{self.risky_users_total} risky users ({self.risky_users_compromised} compromised)")
                self.identity_recommendation = f"Revoke access for {self.risky_users_compromised} compromised account(s)"
            elif self.risky_users_high > 0:
                self.identity_metrics.append(f"{self.risky_users_total} risky users ({self.risky_users_high} high-risk)")
                self.identity_recommendation = f"Review {self.risky_users_high} high-risk identity(ies)"
            else:
                self.identity_metrics.append(f"{self.risky_users_total} risky users")
        
        if self.risky_sign_ins_high > 0:
            self.identity_metrics.append(f"{self.risky_sign_ins_high} high-risk sign-ins")
    
    def has_oauth_risks(self):
        """Check if there are OAuth risks"""
        return len(self.oauth_metrics) > 0 if self.available else False
    
    def has_email_threats(self):
        """Check if there are email threats"""
        return len(self.phishing_malware_metrics) > 0 if self.available else False
    
    def has_incidents(self):
        """Check if there are incidents"""
        return len(self.incident_metrics) > 0 if self.available else False
    
    def has_identity_risks(self):
        """Check if there are identity risks"""
        return len(self.identity_metrics) > 0 if self.available else False


def get_oauth_metrics(defender_client):
    """
    Extract OAuth risk metrics from defender_client.
    Returns: (metrics_list, recommendation_text)
    """
    if not defender_client:
        return [], ""
    
    oauth = defender_client.oauth_risk_summary
    metrics = []
    recommendation = ""
    
    if oauth.get('high_risk', 0) > 0:
        metrics.append(f"{oauth['high_risk']} high-risk OAuth apps")
        recommendation = f"Review {oauth['high_risk']} high-risk app permissions"
    elif oauth.get('over_privileged', 0) > 0:
        metrics.append(f"{oauth['over_privileged']} over-privileged apps")
    
    return metrics, recommendation


def get_alert_metrics(defender_client, categories=None):
    """
    Extract alert metrics from defender_client by category.
    
    Args:
        defender_client: DefenderClient instance
        categories: List of category names to extract (e.g., ['Phishing', 'Malware'])
    
    Returns: (metrics_list, has_threats)
    """
    if not defender_client:
        return [], False
    
    metrics = []
    by_cat = defender_client.alert_summary.get('by_category', {})
    
    if categories:
        for category in categories:
            count = by_cat.get(category, 0)
            if count > 0:
                metrics.append(f"{count} {category.lower()} alerts")
    
    return metrics, len(metrics) > 0


def get_incident_metrics(defender_client):
    """
    Extract incident metrics from defender_client.
    Returns: (metrics_list, recommendation_text)
    """
    if not defender_client:
        return [], ""
    
    inc = defender_client.incident_summary
    if inc.get('total', 0) == 0:
        return [], ""
    
    metrics = []
    recommendation = ""
    
    active = inc.get('active', 0)
    high = inc.get('high_severity', 0)
    
    if high > 0:
        metrics.append(f"{active} incidents ({high} high-severity)")
        recommendation = f"Investigate {high} high-severity incident(s)"
    elif active > 0:
        metrics.append(f"{active} active incidents")
        recommendation = f"Review {active} active incident(s)"
    
    return metrics, recommendation


def get_identity_metrics(defender_client):
    """
    Extract identity risk metrics from defender_client.
    Returns: (metrics_list, recommendation_text)
    """
    if not defender_client:
        return [], ""
    
    metrics = []
    recommendation = ""
    
    # Risky users
    if defender_client.risky_users_summary.get('total', 0) > 0:
        risky = defender_client.risky_users_summary
        total = risky.get('total', 0)
        high = risky.get('high', 0)
        compromised = risky.get('confirmed_compromised', 0)
        
        if compromised > 0:
            metrics.append(f"{total} risky users ({compromised} compromised)")
            recommendation = f"Revoke access for {compromised} compromised account(s)"
        elif high > 0:
            metrics.append(f"{total} risky users ({high} high-risk)")
            recommendation = f"Review {high} high-risk identity(ies)"
        else:
            metrics.append(f"{total} risky users")
    
    # Risky sign-ins
    if defender_client.risky_sign_ins_summary.get('total', 0) > 0:
        sign_ins = defender_client.risky_sign_ins_summary
        if sign_ins.get('high_risk', 0) > 0:
            metrics.append(f"{sign_ins['high_risk']} high-risk sign-ins")
    
    return metrics, recommendation


def build_observation(base_text, metrics, clean_status_text):
    """
    Build observation text with metrics or clean status.
    
    Args:
        base_text: Base observation (e.g., "Feature is active, protecting Copilot workloads")
        metrics: List of metric strings
        clean_status_text: Text to show when no metrics (e.g., "No incidents detected")
    
    Returns: Complete observation text
    """
    if metrics:
        return base_text + ". " + ", ".join(metrics)
    else:
        return base_text + ". " + clean_status_text
