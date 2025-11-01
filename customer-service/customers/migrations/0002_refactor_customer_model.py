# Generated migration for customer model refactoring
# This migration:
# 1. Clears existing customer data (integer user_ids incompatible with UUID)
# 2. Removes duplicate fields (email, name, phone - now in auth service)
# 3. Changes user_id from IntegerField to UUIDField
# 4. Adds structured address fields and business fields

import django.utils.timezone
from django.db import migrations, models


def clear_existing_customers(apps, schema_editor):
    """
    Clear existing customer data since integer user_ids cannot be converted to UUIDs.
    The old integer user_ids don't match the UUID structure used by the auth service.
    """
    Customer = apps.get_model('customers', 'Customer')
    count = Customer.objects.count()
    if count > 0:
        print(f"\n⚠️  Deleting {count} existing customer records...")
        print("   (Old integer user_ids incompatible with new UUID system)")
        Customer.objects.all().delete()
        print("   ✓ Old customer data cleared. Customers will need to recreate profiles.")


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        # Step 1: Clear existing data
        migrations.RunPython(
            clear_existing_customers,
            reverse_code=migrations.RunPython.noop,
        ),

        # Step 2: Update model metadata
        migrations.AlterModelOptions(
            name='customer',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Customer Profile',
                'verbose_name_plural': 'Customer Profiles'
            },
        ),

        # Step 3: Remove old indexes
        migrations.RemoveIndex(
            model_name='customer',
            name='customers_email_92e882_idx',
        ),
        migrations.RemoveIndex(
            model_name='customer',
            name='customers_phone_91048b_idx',
        ),
        migrations.RemoveIndex(
            model_name='customer',
            name='customers_last_na_89bb5f_idx',
        ),

        # Step 4: Remove duplicate fields (now in auth service)
        migrations.RemoveField(
            model_name='customer',
            name='address',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='email',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='phone',
        ),

        # Step 5: Add structured address fields
        migrations.AddField(
            model_name='customer',
            name='street_address',
            field=models.CharField(
                blank=True,
                max_length=255,
                help_text="Street address (e.g., '123 Main Street, Apt 4B')"
            ),
        ),
        migrations.AddField(
            model_name='customer',
            name='city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='customer',
            name='state',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='customer',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='customer',
            name='country',
            field=models.CharField(default='USA', max_length=100),
        ),

        # Step 6: Add business fields
        migrations.AddField(
            model_name='customer',
            name='business_type',
            field=models.CharField(
                blank=True,
                max_length=100,
                help_text="Type of business (e.g., 'Auto Repair', 'Fleet Management')"
            ),
        ),
        migrations.AddField(
            model_name='customer',
            name='tax_id',
            field=models.CharField(
                blank=True,
                max_length=50,
                help_text='Business tax ID or EIN'
            ),
        ),

        # Step 7: Add service tracking
        migrations.AddField(
            model_name='customer',
            name='total_services',
            field=models.IntegerField(
                default=0,
                help_text='Total number of completed services'
            ),
        ),

        # Step 8: Add preferences
        migrations.AddField(
            model_name='customer',
            name='preferred_contact_method',
            field=models.CharField(
                default='email',
                max_length=20,
                choices=[
                    ('email', 'Email'),
                    ('phone', 'Phone'),
                    ('sms', 'SMS')
                ]
            ),
        ),
        migrations.AddField(
            model_name='customer',
            name='notification_preferences',
            field=models.JSONField(
                default=dict,
                blank=True,
                help_text='Customer notification preferences (JSON)'
            ),
        ),

        # Step 9: Update existing fields
        migrations.AlterField(
            model_name='customer',
            name='customer_since',
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                help_text='Date when customer profile was created'
            ),
        ),
        migrations.AlterField(
            model_name='customer',
            name='is_verified',
            field=models.BooleanField(
                default=False,
                help_text='Whether customer has completed verification process'
            ),
        ),
        migrations.AlterField(
            model_name='customer',
            name='last_service_date',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text='Date of most recent service appointment'
            ),
        ),

        # Step 10: Change user_id from Integer to UUID
        # Since PostgreSQL can't cast integer to UUID, we must drop and recreate
        migrations.RemoveField(
            model_name='customer',
            name='user_id',
        ),
        migrations.AddField(
            model_name='customer',
            name='user_id',
            field=models.UUIDField(
                unique=True,
                help_text='UUID linking to authentication service CustomUser.id'
            ),
        ),

        # Step 11: Add new indexes
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(
                fields=['city', 'state'], name='customers_city_fdf47c_idx'),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['company_name'],
                               name='customers_company_c25c85_idx'),
        ),
    ]
