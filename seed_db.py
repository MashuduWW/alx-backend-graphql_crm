import os
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order

def run():
    # Clear existing data (optional for dev/demo only!)
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()

    # Create Customers
    alice = Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
    bob = Customer.objects.create(name="Bob", email="bob@example.com")

    # Create Products
    laptop = Product.objects.create(name="Laptop", price=Decimal("999.99"), stock=10)
    phone = Product.objects.create(name="Phone", price=Decimal("499.99"), stock=20)

    # Create Order for Alice
    order = Order.objects.create(customer=alice, total_amount=laptop.price + phone.price)
    order.products.set([laptop, phone])

    print("✅ Database seeded successfully!")

if __name__ == "__main__":
    run()
