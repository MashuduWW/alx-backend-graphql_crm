# GraphQL Product Stock Alerts

This document explains the implementation of the GraphQL mutation for product stock alerts that runs every 12 hours via cron.

## Implementation Overview

### 1. GraphQL Mutation (`crm/schema.py`)

The `UpdateLowStockProducts` mutation:
- **Queries products with stock < 10**: Uses `Product.objects.filter(stock__lt=10)`
- **Increments their stock by 10**: Simulates restocking by adding 10 to each product's stock
- **Returns a list of updated products and a success message**: Provides feedback on what was updated

### 2. Cron Job (`crm/cron.py`)

The `update_low_stock()` function:
- **Executes the UpdateLowStockProducts mutation via the GraphQL endpoint**: Uses the `gql` library to call the mutation
- **Logs updated product names and new stock levels**: Writes to `/tmp/low_stock_updates_log.txt` with timestamps

### 3. Cron Configuration (`crm/settings.py`)

The CRONJOBS entry:
```python
CRONJOBS = [
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]
```
This runs the job every 12 hours (at 00:00 and 12:00).

## Testing the Implementation

### Method 1: Manual Testing
1. Start your Django server: `python manage.py runserver`
2. Create some products with low stock in the admin or via GraphQL
3. Run the cron job manually: `python manage.py shell -c "from crm.cron import update_low_stock; update_low_stock()"`
4. Check the log file: `cat /tmp/low_stock_updates_log.txt`

### Method 2: Using the Test Script
1. Run the provided test script: `python test_stock_alert.py`
2. This will create test products and run the stock alert function

### Method 3: Setting up the Cron Job
1. Add the cron job: `python manage.py crontab add`
2. Check if it's added: `python manage.py crontab show`
3. The job will run automatically every 12 hours

## GraphQL Mutation Example

You can also test the mutation directly via GraphQL:

```graphql
mutation {
  updateLowStockProducts {
    success
    updatedProducts
  }
}
```

## Expected Output

The mutation will return:
```json
{
  "data": {
    "updateLowStockProducts": {
      "success": "Low stock products updated successfully!",
      "updatedProducts": [
        "Product A (Stock: 15)",
        "Product B (Stock: 13)"
      ]
    }
  }
}
```

And the log file will contain:
```
25/12/2024-14:30:00 - Low stock products updated successfully!
Product A (Stock: 15)
Product B (Stock: 13)
```

## Requirements Met

✅ **crm/schema.py includes the UpdateLowStockProducts mutation**  
✅ **crm/cron.py defines update_low_stock and logs to /tmp/low_stock_updates_log.txt**  
✅ **crm/settings.py has the correct CRONJOBS entry**  
✅ **Mutation queries products with stock < 10**  
✅ **Mutation increments their stock by 10 (simulating restocking)**  
✅ **Mutation returns a list of updated products and a success message** 