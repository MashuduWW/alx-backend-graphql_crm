#!/usr/bin/env python3
"""
Test script for the GraphQL stock alert mutation
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Product
from crm.cron import update_low_stock

def test_stock_alert():
    """Test the stock alert functionality"""
    
    # Create some test products with low stock
    Product.objects.create(name="Test Product 1", price=10.00, stock=5)
    Product.objects.create(name="Test Product 2", price=20.00, stock=3)
    Product.objects.create(name="Test Product 3", price=15.00, stock=15)  # This should not be updated
    
    print("Created test products:")
    for product in Product.objects.all():
        print(f"  {product.name}: Stock {product.stock}")
    
    print("\nRunning stock alert update...")
    
    # Run the cron job function
    result = update_low_stock()
    print(f"Result: {result['success']}")
    print(f"Updated products: {result['updated_products']}")
    
    print("\nAfter update:")
    for product in Product.objects.all():
        print(f"  {product.name}: Stock {product.stock}")
    
    # Check if log file was created
    if os.path.exists('low_stock_updates_log.txt'):
        print("\nLog file contents:")
        with open('low_stock_updates_log.txt', 'r') as f:
            print(f.read())
    else:
        print("\nLog file not found at low_stock_updates_log.txt")

if __name__ == "__main__":
    test_stock_alert() 