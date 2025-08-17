# seed_db.py

import os
import django
from datetime import datetime

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_customers():
    customers_data = [
        {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol", "email": "carol@example.com"}
    ]

    created = []
    for data in customers_data:
        if not Customer.objects.filter(email=data["email"]).exists():
            customer = Customer(**data)
            customer.save()
            created.append(customer)
    print(f"{len(created)} customers created.")
    return created

def seed_products():
    products_data = [
        {"name": "Laptop", "price": 999.99, "stock": 10},
        {"name": "Mouse", "price": 25.50, "stock": 50},
        {"name": "Keyboard", "price": 45.00, "stock": 30}
    ]

    created = []
    for data in products_data:
        product, created_flag = Product.objects.get_or_create(name=data["name"], defaults=data)
        if created_flag:
            created.append(product)
    print(f"{len(created)} products created.")
    return Product.objects.all()

def seed_orders(customers, products):
    if not customers or not products:
        print("No customers or products to create orders.")
        return

    order = Order.objects.create(
        customer=customers[0],
        total_amount=sum(p.price for p in products),
        order_date=datetime.now()
    )
    order.products.set(products)
    order.save()
    print("1 order created.")

if __name__ == "__main__":
    print("📦 Seeding CRM database...")
    customers = seed_customers()
    products = seed_products()
    seed_orders(customers, products)
    print("✅ Done seeding.")
