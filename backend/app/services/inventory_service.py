"""
Pharmacy Inventory Service
Manages medication inventory and stock status
"""
from typing import Dict, List, Optional
from datetime import datetime
import random

# Sample inventory data
# In production, this would come from a database
MEDICATION_INVENTORY = {
    "Lisinopril": {
        "name": "Lisinopril",
        "dosage": "10mg",
        "stock_quantity": 450,
        "unit": "tablets",
        "status": "in_stock",
        "reorder_level": 100,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Amlodipine": {
        "name": "Amlodipine",
        "dosage": "5mg",
        "stock_quantity": 320,
        "unit": "tablets",
        "status": "in_stock",
        "reorder_level": 100,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Metformin": {
        "name": "Metformin",
        "dosage": "500mg",
        "stock_quantity": 680,
        "unit": "tablets",
        "status": "in_stock",
        "reorder_level": 150,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Amoxicillin": {
        "name": "Amoxicillin",
        "dosage": "500mg",
        "stock_quantity": 45,
        "unit": "capsules",
        "status": "low_stock",
        "reorder_level": 50,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Ibuprofen": {
        "name": "Ibuprofen",
        "dosage": "400mg",
        "stock_quantity": 0,
        "unit": "tablets",
        "status": "out_of_stock",
        "reorder_level": 200,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Acetaminophen": {
        "name": "Acetaminophen",
        "dosage": "500mg",
        "stock_quantity": 520,
        "unit": "tablets",
        "status": "in_stock",
        "reorder_level": 200,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Albuterol": {
        "name": "Albuterol",
        "dosage": "90mcg",
        "stock_quantity": 28,
        "unit": "inhalers",
        "status": "low_stock",
        "reorder_level": 30,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Montelukast": {
        "name": "Montelukast",
        "dosage": "10mg",
        "stock_quantity": 180,
        "unit": "tablets",
        "status": "in_stock",
        "reorder_level": 100,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Atorvastatin": {
        "name": "Atorvastatin",
        "dosage": "20mg",
        "stock_quantity": 290,
        "unit": "tablets",
        "status": "in_stock",
        "reorder_level": 100,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Simvastatin": {
        "name": "Simvastatin",
        "dosage": "20mg",
        "stock_quantity": 210,
        "unit": "tablets",
        "status": "in_stock",
        "reorder_level": 100,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Sertraline": {
        "name": "Sertraline",
        "dosage": "50mg",
        "stock_quantity": 0,
        "unit": "tablets",
        "status": "out_of_stock",
        "reorder_level": 100,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Fluoxetine": {
        "name": "Fluoxetine",
        "dosage": "20mg",
        "stock_quantity": 95,
        "unit": "capsules",
        "status": "low_stock",
        "reorder_level": 100,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Omeprazole": {
        "name": "Omeprazole",
        "dosage": "20mg",
        "stock_quantity": 340,
        "unit": "capsules",
        "status": "in_stock",
        "reorder_level": 100,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Pantoprazole": {
        "name": "Pantoprazole",
        "dosage": "40mg",
        "stock_quantity": 260,
        "unit": "tablets",
        "status": "in_stock",
        "reorder_level": 100,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Cetirizine": {
        "name": "Cetirizine",
        "dosage": "10mg",
        "stock_quantity": 420,
        "unit": "tablets",
        "status": "in_stock",
        "reorder_level": 200,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Loratadine": {
        "name": "Loratadine",
        "dosage": "10mg",
        "stock_quantity": 380,
        "unit": "tablets",
        "status": "in_stock",
        "reorder_level": 200,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Azithromycin": {
        "name": "Azithromycin",
        "dosage": "500mg",
        "stock_quantity": 125,
        "unit": "tablets",
        "status": "in_stock",
        "reorder_level": 50,
        "last_updated": "2024-01-15T10:30:00"
    },
    "Glipizide": {
        "name": "Glipizide",
        "dosage": "5mg",
        "stock_quantity": 155,
        "unit": "tablets",
        "status": "in_stock",
        "reorder_level": 100,
        "last_updated": "2024-01-15T10:30:00"
    }
}

def check_medication_stock(medication_name: str) -> Optional[Dict]:
    """
    Check if a medication is in stock
    
    Args:
        medication_name: Name of the medication to check
        
    Returns:
        Dictionary with stock information or None if not found
    """
    if not medication_name or not medication_name.strip():
        return {
            "name": medication_name or "",
            "found": False,
            "status": "not_found",
            "message": "Please enter a medication name",
            "search_term": medication_name or ""
        }
    
    medication_name_lower = medication_name.lower().strip()
    
    # Direct exact match (case-insensitive)
    for med_name, med_data in MEDICATION_INVENTORY.items():
        if med_name.lower() == medication_name_lower:
            return {
                **med_data,
                "found": True,
                "search_term": medication_name
            }
    
    # Partial match - check if search term is contained in medication name
    for med_name, med_data in MEDICATION_INVENTORY.items():
        med_name_lower = med_name.lower()
        if medication_name_lower in med_name_lower:
            return {
                **med_data,
                "found": True,
                "search_term": medication_name
            }
    
    # Reverse partial match - check if medication name is contained in search term
    for med_name, med_data in MEDICATION_INVENTORY.items():
        med_name_lower = med_name.lower()
        if med_name_lower in medication_name_lower and len(med_name_lower) >= 4:  # Only if medication name is substantial
            return {
                **med_data,
                "found": True,
                "search_term": medication_name
            }
    
    # Not found - return helpful message with available medications
    # Get all medication names as suggestions
    all_medications = list(MEDICATION_INVENTORY.keys())
    # Show first 8 as suggestions
    available_meds = all_medications[:8]
    
    return {
        "name": medication_name,
        "found": False,
        "status": "not_found",
        "message": f"Medication '{medication_name}' not found in inventory.",
        "search_term": medication_name,
        "suggestions": available_meds,
        "total_available": len(all_medications)
    }

def get_all_inventory() -> List[Dict]:
    """
    Get all medication inventory
    
    Returns:
        List of all medications with stock information
    """
    inventory_list = []
    for med_name, med_data in MEDICATION_INVENTORY.items():
        inventory_list.append({
            **med_data,
            "found": True
        })
    
    # Sort by status (out_of_stock first, then low_stock, then in_stock)
    status_order = {"out_of_stock": 0, "low_stock": 1, "in_stock": 2}
    inventory_list.sort(key=lambda x: (status_order.get(x.get("status", "in_stock"), 2), x["name"]))
    
    return inventory_list

def search_inventory(search_term: str) -> List[Dict]:
    """
    Search inventory by medication name
    
    Args:
        search_term: Search term to match against medication names
        
    Returns:
        List of matching medications
    """
    if not search_term or not search_term.strip():
        return get_all_inventory()
    
    search_term_lower = search_term.lower().strip()
    results = []
    
    for med_name, med_data in MEDICATION_INVENTORY.items():
        if search_term_lower in med_name.lower():
            results.append({
                **med_data,
                "found": True
            })
    
    # Sort by status
    status_order = {"out_of_stock": 0, "low_stock": 1, "in_stock": 2}
    results.sort(key=lambda x: (status_order.get(x.get("status", "in_stock"), 2), x["name"]))
    
    return results

