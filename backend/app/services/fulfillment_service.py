"""
Pharmacy Fulfillment Status Service
Tracks fulfillment status for out-of-stock and low-stock medications
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

# Import inventory service to get stock status
from backend.app.services.inventory_service import MEDICATION_INVENTORY, get_all_inventory

# Fulfillment status for medications
# In production, this would come from a database
FULFILLMENT_STATUS = {
    "Ibuprofen": {
        "medication_name": "Ibuprofen",
        "current_status": "out_of_stock",
        "fulfillment_status": "pending",
        "order_date": "2024-01-10",
        "expected_delivery": "2024-01-20",
        "quantity_ordered": 500,
        "supplier": "MedSupply Co.",
        "order_number": "ORD-2024-001",
        "notes": "Awaiting shipment from supplier"
    },
    "Sertraline": {
        "medication_name": "Sertraline",
        "current_status": "out_of_stock",
        "fulfillment_status": "in_transit",
        "order_date": "2024-01-12",
        "expected_delivery": "2024-01-18",
        "quantity_ordered": 300,
        "supplier": "PharmaDist Inc.",
        "order_number": "ORD-2024-003",
        "notes": "Shipped, expected delivery in 6 days"
    },
    "Amoxicillin": {
        "medication_name": "Amoxicillin",
        "current_status": "low_stock",
        "fulfillment_status": "ordered",
        "order_date": "2024-01-14",
        "expected_delivery": "2024-01-22",
        "quantity_ordered": 200,
        "supplier": "HealthMed Supplies",
        "order_number": "ORD-2024-005",
        "notes": "Order confirmed, processing"
    },
    "Albuterol": {
        "medication_name": "Albuterol",
        "current_status": "low_stock",
        "fulfillment_status": "delivered",
        "order_date": "2024-01-08",
        "expected_delivery": "2024-01-15",
        "delivery_date": "2024-01-15",
        "quantity_ordered": 50,
        "quantity_received": 50,
        "supplier": "Respiratory Meds Ltd.",
        "order_number": "ORD-2024-002",
        "notes": "Delivered successfully, restocked"
    },
    "Fluoxetine": {
        "medication_name": "Fluoxetine",
        "current_status": "low_stock",
        "fulfillment_status": "pending",
        "order_date": None,
        "expected_delivery": None,
        "quantity_ordered": 0,
        "supplier": None,
        "order_number": None,
        "notes": "Reorder required - not yet ordered"
    }
}

def get_fulfillment_status() -> List[Dict]:
    """
    Get fulfillment status for all out-of-stock and low-stock medications
    
    Returns:
        List of medications with fulfillment status
    """
    fulfillment_list = []
    
    # Get all inventory to check stock status
    all_inventory = get_all_inventory()
    
    # Process medications that are out of stock or low stock
    for med in all_inventory:
        if med["status"] in ["out_of_stock", "low_stock"]:
            med_name = med["name"]
            
            # Get fulfillment status if exists
            if med_name in FULFILLMENT_STATUS:
                fulfillment_data = FULFILLMENT_STATUS[med_name].copy()
            else:
                # Create default fulfillment status
                fulfillment_data = {
                    "medication_name": med_name,
                    "current_status": med["status"],
                    "fulfillment_status": "not_ordered",
                    "order_date": None,
                    "expected_delivery": None,
                    "quantity_ordered": 0,
                    "supplier": None,
                    "order_number": None,
                    "notes": "No order placed yet"
                }
            
            # Merge with inventory data
            fulfillment_item = {
                **med,  # Include all inventory data
                **fulfillment_data,  # Include fulfillment data
                "needs_fulfillment": True
            }
            
            fulfillment_list.append(fulfillment_item)
    
    # Sort by status priority: out_of_stock first, then low_stock
    # Then by fulfillment status: not_ordered, pending, ordered, in_transit, delivered
    status_priority = {"out_of_stock": 0, "low_stock": 1}
    fulfillment_priority = {
        "not_ordered": 0,
        "pending": 1,
        "ordered": 2,
        "in_transit": 3,
        "delivered": 4
    }
    
    fulfillment_list.sort(
        key=lambda x: (
            status_priority.get(x.get("status", "in_stock"), 2),
            fulfillment_priority.get(x.get("fulfillment_status", "not_ordered"), 5),
            x.get("medication_name", "")
        )
    )
    
    return fulfillment_list

def get_fulfillment_by_status(fulfillment_status: Optional[str] = None) -> List[Dict]:
    """
    Get fulfillment status filtered by fulfillment status
    
    Args:
        fulfillment_status: Optional filter by fulfillment status
        
    Returns:
        Filtered list of medications with fulfillment status
    """
    all_fulfillment = get_fulfillment_status()
    
    if not fulfillment_status or fulfillment_status == "all":
        return all_fulfillment
    
    return [item for item in all_fulfillment if item.get("fulfillment_status") == fulfillment_status]

def get_in_stock_medications() -> List[Dict]:
    """
    Get all medications that are currently in stock
    
    Returns:
        List of in-stock medications
    """
    all_inventory = get_all_inventory()
    return [med for med in all_inventory if med["status"] == "in_stock"]


