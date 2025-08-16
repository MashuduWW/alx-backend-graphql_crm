import graphene
from graphene_django import DjangoObjectType
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from crm.models import Customer, Product, Order

# -------------------
# GraphQL Types
# -------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# -------------------
# Create Customer
# -------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, name, email, phone=None):
        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            return CreateCustomer(customer=None, message="Invalid email format")

        # Ensure unique email
        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(customer=None, message="Email already exists")

        # Validate phone (basic)
        if phone and not (phone.startswith("+") or phone.replace("-", "").isdigit()):
            return CreateCustomer(customer=None, message="Invalid phone format")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully")


# -------------------
# Bulk Create Customers
# -------------------
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(
            graphene.JSONString, required=True, description="List of customers"
        )

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for idx, data in enumerate(input):
                name = data.get("name")
                email = data.get("email")
                phone = data.get("phone")

                # Validation
                try:
                    validate_email(email)
                except ValidationError:
                    errors.append(f"Row {idx+1}: Invalid email {email}")
                    continue

                if Customer.objects.filter(email=email).exists():
                    errors.append(f"Row {idx+1}: Email already exists ({email})")
                    continue

                if phone and not (phone.startswith("+") or phone.replace("-", "").isdigit()):
                    errors.append(f"Row {idx+1}: Invalid phone format ({phone})")
                    continue

                # Create valid customer
                customer = Customer.objects.create(name=name, email=email, phone=phone)
                created_customers.append(customer)

        return BulkCreateCustomers(customers=created_customers, errors=errors)


# -------------------
# Create Product
# -------------------
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False, default_value=0)

    product = graphene.Field(ProductType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, name, price, stock=0):
        if price <= 0:
            return CreateProduct(product=None, message="Price must be positive")
        if stock < 0:
            return CreateProduct(product=None, message="Stock cannot be negative")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product, message="Product created successfully")


# -------------------
# Create Order
# -------------------
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(order=None, message=f"Invalid customer ID {customer_id}")

        products = Product.objects.filter(pk__in=product_ids)
        if not products.exists():
            return CreateOrder(order=None, message="No valid products found")

        if len(products) != len(product_ids):
            return CreateOrder(order=None, message="Some product IDs are invalid")

        # Calculate total
        total_amount = sum(p.price for p in products)

        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date or None,
        )
        order.products.set(products)

        return CreateOrder(order=order, message="Order created successfully")


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

