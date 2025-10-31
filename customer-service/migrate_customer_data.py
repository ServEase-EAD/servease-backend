"""
Data Migration Script for Customer Service Refactoring

This script helps migrate existing customer data from the old structure
to the new refactored structure.

IMPORTANT: 
- Backup your database before running this script
- Test in development environment first
- Adjust the address parsing logic based on your data format

Usage:
    python migrate_customer_data.py
"""

from customers.models import Customer
import os
import sys
import django
import re
from uuid import UUID

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'customer_service.settings')
django.setup()


def parse_address(address_text):
    """
    Parse old address text field into structured components.

    Adjust this function based on your address format.

    Examples:
    - "123 Main St, Portland, OR, 97201, USA"
    - "456 Oak Ave, Apt 2B, Seattle, WA, 98101"
    """
    if not address_text:
        return {
            'street_address': '',
            'city': '',
            'state': '',
            'postal_code': '',
            'country': 'USA'
        }

    # Split by comma
    parts = [p.strip() for p in address_text.split(',')]

    result = {
        'street_address': '',
        'city': '',
        'state': '',
        'postal_code': '',
        'country': 'USA'
    }

    if len(parts) >= 1:
        result['street_address'] = parts[0]

    if len(parts) >= 2:
        result['city'] = parts[1]

    if len(parts) >= 3:
        # State might include postal code
        state_postal = parts[2].strip()
        # Try to extract postal code
        postal_match = re.search(r'\d{5}(-\d{4})?', state_postal)
        if postal_match:
            result['postal_code'] = postal_match.group()
            result['state'] = state_postal.replace(
                result['postal_code'], '').strip()
        else:
            result['state'] = state_postal

    if len(parts) >= 4:
        # Check if this part is a postal code or country
        if parts[3].strip().isdigit() or re.match(r'\d{5}(-\d{4})?', parts[3].strip()):
            result['postal_code'] = parts[3].strip()
        else:
            result['country'] = parts[3].strip()

    if len(parts) >= 5:
        result['country'] = parts[4].strip()

    return result


def convert_user_id_to_uuid(user_id):
    """
    Convert integer user_id to UUID format.

    Options:
    1. If you have a mapping table from old IDs to new UUIDs
    2. If auth service already has UUIDs, fetch them
    3. Generate new UUIDs (not recommended unless coordinating with auth service)
    """
    # TODO: Implement your user_id conversion logic here
    # This is a placeholder that you need to customize

    # Example: Fetch from auth service
    # from customers.authentication import get_user_data_from_auth_service
    # user_data = get_user_data_from_auth_service(user_id)
    # return user_data['id']

    # For now, raise an error to prevent accidental execution
    raise NotImplementedError(
        "You must implement user_id to UUID conversion logic. "
        "This requires coordination with the authentication service."
    )


def migrate_customer_data(dry_run=True):
    """
    Migrate customer data from old structure to new structure.

    Args:
        dry_run: If True, print changes without saving
    """
    print("=" * 80)
    print("Customer Data Migration Script")
    print("=" * 80)
    print()

    if dry_run:
        print("DRY RUN MODE - No changes will be saved")
    else:
        print("LIVE MODE - Changes will be saved to database")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Migration cancelled.")
            return

    print()

    # Get all customers
    customers = Customer.objects.all()
    total = customers.count()

    print(f"Found {total} customers to migrate")
    print()

    success_count = 0
    error_count = 0
    errors = []

    for i, customer in enumerate(customers, 1):
        print(f"[{i}/{total}] Processing customer ID: {customer.id}")

        try:
            # Parse old address field
            if hasattr(customer, 'address'):
                address_data = parse_address(customer.address)

                print(f"  Old address: {customer.address}")
                print(f"  New address:")
                print(f"    Street: {address_data['street_address']}")
                print(f"    City: {address_data['city']}")
                print(f"    State: {address_data['state']}")
                print(f"    Postal: {address_data['postal_code']}")
                print(f"    Country: {address_data['country']}")

                if not dry_run:
                    customer.street_address = address_data['street_address']
                    customer.city = address_data['city']
                    customer.state = address_data['state']
                    customer.postal_code = address_data['postal_code']
                    customer.country = address_data['country']

            # Convert user_id if needed
            if isinstance(customer.user_id, int):
                print(f"  Converting user_id from int to UUID")
                # new_uuid = convert_user_id_to_uuid(customer.user_id)
                # customer.user_id = new_uuid
                print(f"  ⚠️  UUID conversion not implemented - skipping")

            # Save if not dry run
            if not dry_run:
                customer.save()
                print(f"  ✓ Saved")
            else:
                print(f"  ✓ Would be saved (dry run)")

            success_count += 1

        except Exception as e:
            error_count += 1
            error_msg = f"Customer {customer.id}: {str(e)}"
            errors.append(error_msg)
            print(f"  ✗ Error: {e}")

        print()

    # Summary
    print("=" * 80)
    print("Migration Summary")
    print("=" * 80)
    print(f"Total customers: {total}")
    print(f"Successful: {success_count}")
    print(f"Errors: {error_count}")

    if errors:
        print()
        print("Errors encountered:")
        for error in errors:
            print(f"  - {error}")

    if dry_run:
        print()
        print("This was a DRY RUN - no changes were saved.")
        print("Run with dry_run=False to apply changes.")


def verify_migration():
    """
    Verify the migration was successful.
    """
    print("=" * 80)
    print("Migration Verification")
    print("=" * 80)
    print()

    customers = Customer.objects.all()
    total = customers.count()

    print(f"Total customers: {total}")
    print()

    # Check for empty required fields
    missing_street = customers.filter(street_address='').count()
    missing_city = customers.filter(city='').count()
    missing_state = customers.filter(state='').count()

    print("Fields check:")
    print(f"  Missing street_address: {missing_street}")
    print(f"  Missing city: {missing_city}")
    print(f"  Missing state: {missing_state}")
    print()

    # Check UUID user_ids
    uuid_count = 0
    int_count = 0

    for customer in customers:
        try:
            UUID(str(customer.user_id))
            uuid_count += 1
        except (ValueError, AttributeError):
            int_count += 1

    print("User ID types:")
    print(f"  UUID format: {uuid_count}")
    print(f"  Integer format: {int_count}")
    print()

    # Sample records
    print("Sample customer records (first 3):")
    for customer in customers[:3]:
        print(f"  ID: {customer.id}")
        print(
            f"  User ID: {customer.user_id} (type: {type(customer.user_id).__name__})")
        print(
            f"  Address: {customer.street_address}, {customer.city}, {customer.state}")
        print(f"  Company: {customer.company_name or '(none)'}")
        print()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Migrate customer data')
    parser.add_argument('--live', action='store_true',
                        help='Run in live mode (actually save changes)')
    parser.add_argument('--verify', action='store_true',
                        help='Verify migration results')

    args = parser.parse_args()

    if args.verify:
        verify_migration()
    else:
        dry_run = not args.live
        migrate_customer_data(dry_run=dry_run)
