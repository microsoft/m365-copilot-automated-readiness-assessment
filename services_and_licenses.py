"""
Thread-safe data structure for collecting service plans from multiple services.
This module provides a shared container that can be safely accessed by multiple
async functions running in parallel.
"""
import asyncio
from typing import Dict, List, Any, Optional


class ServicesAndLicenses:
    """
    Thread-safe container for collecting service plans and license information
    from multiple M365 services running in parallel.
    
    Stores licenses in a unified structure with service categorization to avoid
    redundant storage of the same license across multiple service categories.
    """
    
    def __init__(self):
        """Initialize the container with empty collections and a lock for thread safety."""
        self._lock = asyncio.Lock()
        # Unified license storage - each license stored once with service categorization
        self._licenses = {}  # Key: sku_id, Value: license data with service_categories
        # Raw API data cache
        self._raw_subscribed_skus = None
    
    async def set_raw_subscribed_skus(self, subscribed_skus):
        """
        Store the raw subscribed SKUs data from Graph API.
        This is fetched once and shared across all service functions.
        
        Args:
            subscribed_skus: Raw response from client.subscribed_skus.get()
        """
        async with self._lock:
            self._raw_subscribed_skus = subscribed_skus
    
    async def get_raw_subscribed_skus(self):
        """Get the cached raw subscribed SKUs data."""
        async with self._lock:
            return self._raw_subscribed_skus
    
    async def add_license(self, sku_id: str, license_data: Dict[str, Any], 
                         service_categories: List[str], validation_info: Optional[Dict] = None):
        """
        Add or update a license with service categorization.
        
        Args:
            sku_id: The SKU ID
            license_data: License information (sku_part_number, enabled, consumed, etc.)
            service_categories: List of service categories this license belongs to
            validation_info: Optional validation results (missing plans, expected plans, etc.)
        """
        async with self._lock:
            if sku_id in self._licenses:
                # License exists, add new service categories
                existing_categories = set(self._licenses[sku_id].get('service_categories', []))
                existing_categories.update(service_categories)
                self._licenses[sku_id]['service_categories'] = list(existing_categories)
                
                # Merge validation info if provided
                if validation_info:
                    if 'validation' not in self._licenses[sku_id]:
                        self._licenses[sku_id]['validation'] = {}
                    self._licenses[sku_id]['validation'].update(validation_info)
            else:
                # New license
                self._licenses[sku_id] = {
                    **license_data,
                    'service_categories': service_categories,
                    'validation': validation_info or {}
                }
    
    async def append_service_data(self, service_name: str, data: Any):
        """
        Append data for a specific service in a thread-safe manner.
        Prevents duplicates based on sku_id.
        
        Args:
            service_name: Name of the service ('m365', 'entra', 'purview', 'defender', 
                         'power_platform', 'copilot_studio')
            data: Data to append (can be a single item or list of items)
        """
        valid_services = ['m365', 'entra', 'purview', 'defender', 'power_platform', 'copilot_studio']
        if service_name not in valid_services:
            raise ValueError(f"Unknown service name: {service_name}")
        
        # Process data and add to unified storage
        items_to_process = data if isinstance(data, list) else [data]
        
        for item in items_to_process:
            if isinstance(item, dict) and 'sku_id' in item:
                sku_id = item['sku_id']
                await self.add_license(
                    sku_id=sku_id,
                    license_data=item,
                    service_categories=[service_name]
                )
    
    async def get_service_data(self, service_name: str) -> List[Any]:
        """
        Get data for a specific service in a thread-safe manner.
        Returns licenses that have the specified service category.
        
        Args:
            service_name: Name of the service
            
        Returns:
            List of license data items for the specified service
        """
        async with self._lock:
            return [
                lic.copy() for lic in self._licenses.values()
                if service_name in lic.get('service_categories', [])
            ]
    
    async def get_all_licenses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all licenses in unified storage.
        
        Returns:
            Dictionary mapping sku_id to license data
        """
        async with self._lock:
            return {sku_id: lic.copy() for sku_id, lic in self._licenses.items()}
    
    async def get_all_data(self) -> Dict[str, List[Any]]:
        """
        Get all collected data organized by service category (legacy format).
        
        Returns:
            Dictionary containing all service data organized by category
        """
        async with self._lock:
            result = {
                'm365': [],
                'entra': [],
                'purview': [],
                'defender': [],
                'power_platform': [],
                'copilot_studio': []
            }
            
            for lic in self._licenses.values():
                for category in lic.get('service_categories', []):
                    if category in result:
                        result[category].append(lic.copy())
            
            return result
    
    def get_all_data_sync(self) -> Dict[str, List[Any]]:
        """
        Get all collected data synchronously (use only when not in async context).
        
        Returns:
            Dictionary containing all service data organized by category
        """
        result = {
            'm365': [],
            'entra': [],
            'purview': [],
            'defender': [],
            'power_platform': [],
            'copilot_studio': []
        }
        
        for lic in self._licenses.values():
            for category in lic.get('service_categories', []):
                if category in result:
                    result[category].append(lic.copy())
        
        return result
