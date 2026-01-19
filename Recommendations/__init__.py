"""
Recommendations package for M365 Copilot and Agent Adoption

This package contains feature-specific recommendations organized by service:
- entra: Identity and access management features
- defender: Security and threat protection features
- purview: Compliance and data governance features
- power_platform: Low-code development and automation features
- copilot_studio: Conversational AI and agent building features
- m365: Core Microsoft 365 productivity features

Each service folder contains individual Python files for specific features,
providing tailored observations and recommendations focused on how each
feature supports M365 Copilot and agent adoption.
"""

__all__ = [
    'entra',
    'defender',
    'purview',
    'power_platform',
    'copilot_studio',
    'm365'
]
