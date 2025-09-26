# Generated initial migration for Customer service models

from django.db import migrations, models
import django.core.validators
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4,
                 editable=False, primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(
                    help_text='Links to authentication service user ID', unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=17, validators=[django.core.validators.RegexValidator(
                    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('secondary_phone', models.CharField(blank=True, max_length=17, validators=[django.core.validators.RegexValidator(
                    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('street_address', models.TextField()),
                ('apartment_unit', models.CharField(blank=True, max_length=10)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('zip_code', models.CharField(max_length=10)),
                ('country', models.CharField(default='United States', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('customer_since', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('company_name', models.CharField(blank=True, max_length=200)),
                ('business_tax_id', models.CharField(blank=True, max_length=50)),
                ('is_business_customer', models.BooleanField(default=False)),
                ('emergency_contact_name', models.CharField(
                    blank=True, max_length=200)),
                ('emergency_contact_phone', models.CharField(blank=True, max_length=17, validators=[django.core.validators.RegexValidator(
                    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{9,15}$')])),
                ('emergency_contact_relationship',
                 models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_service_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'customers',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4,
                 editable=False, primary_key=True, serialize=False)),
                ('make', models.CharField(max_length=50)),
                ('model', models.CharField(max_length=100)),
                ('year', models.IntegerField()),
                ('color', models.CharField(max_length=30)),
                ('vin', models.CharField(
                    help_text='Vehicle Identification Number', max_length=17, unique=True)),
                ('license_plate', models.CharField(max_length=15)),
                ('state_registered', models.CharField(default='', max_length=50)),
                ('engine_size', models.CharField(blank=True, max_length=20)),
                ('fuel_type', models.CharField(choices=[('gasoline', 'Gasoline'), ('diesel', 'Diesel'), ('hybrid', 'Hybrid'), ('electric', 'Electric'), (
                    'plug_in_hybrid', 'Plug-in Hybrid'), ('natural_gas', 'Natural Gas'), ('other', 'Other')], default='gasoline', max_length=20)),
                ('transmission', models.CharField(choices=[('manual', 'Manual'), ('automatic', 'Automatic'), (
                    'cvt', 'CVT'), ('semi_automatic', 'Semi-Automatic')], default='automatic', max_length=20)),
                ('current_mileage', models.IntegerField(default=0)),
                ('purchase_date', models.DateField(blank=True, null=True)),
                ('purchase_mileage', models.IntegerField(blank=True, null=True)),
                ('insurance_company', models.CharField(blank=True, max_length=100)),
                ('insurance_policy_number', models.CharField(
                    blank=True, max_length=50)),
                ('insurance_expiry_date', models.DateField(blank=True, null=True)),
                ('registration_expiry_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_under_warranty', models.BooleanField(default=False)),
                ('warranty_expiry_date', models.DateField(blank=True, null=True)),
                ('last_service_date', models.DateTimeField(blank=True, null=True)),
                ('last_service_mileage', models.IntegerField(blank=True, null=True)),
                ('next_service_due_date', models.DateField(blank=True, null=True)),
                ('next_service_due_mileage',
                 models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=models.deletion.CASCADE,
                 related_name='vehicles', to='customers.customer')),
            ],
            options={
                'db_table': 'customer_vehicles',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CustomerPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('email_notifications', models.BooleanField(default=True)),
                ('sms_notifications', models.BooleanField(default=True)),
                ('push_notifications', models.BooleanField(default=True)),
                ('phone_call_notifications', models.BooleanField(default=False)),
                ('postal_mail_notifications', models.BooleanField(default=False)),
                ('preferred_contact_method', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS'), (
                    'phone', 'Phone Call'), ('app', 'Mobile App'), ('mail', 'Postal Mail')], default='email', max_length=10)),
                ('preferred_service_time', models.TimeField(blank=True, null=True)),
                ('preferred_service_day', models.CharField(blank=True, choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), (
                    'thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], max_length=10)),
                ('preferred_language', models.CharField(choices=[('en', 'English'), ('es', 'Spanish'), ('fr', 'French'), (
                    'de', 'German'), ('zh', 'Chinese'), ('ja', 'Japanese'), ('ko', 'Korean')], default='en', max_length=5)),
                ('timezone', models.CharField(default='UTC', max_length=50)),
                ('currency', models.CharField(default='USD', max_length=3)),
                ('marketing_emails', models.BooleanField(default=False)),
                ('promotional_sms', models.BooleanField(default=False)),
                ('service_reminders', models.BooleanField(default=True)),
                ('appointment_reminders', models.BooleanField(default=True)),
                ('data_sharing_consent', models.BooleanField(default=False)),
                ('analytics_consent', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.OneToOneField(on_delete=models.deletion.CASCADE,
                 related_name='preferences', to='customers.customer')),
            ],
            options={
                'db_table': 'customer_preferences',
            },
        ),
        migrations.CreateModel(
            name='CustomerDocument',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4,
                 editable=False, primary_key=True, serialize=False)),
                ('document_type', models.CharField(choices=[('license', "Driver's License"), ('insurance', 'Insurance Document'), ('registration', 'Vehicle Registration'), (
                    'warranty', 'Warranty Document'), ('service_history', 'Service History'), ('invoice', 'Invoice'), ('receipt', 'Receipt'), ('other', 'Other')], max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('file_path', models.FileField(
                    upload_to='customer_documents/%Y/%m/')),
                ('file_size', models.PositiveIntegerField(
                    help_text='File size in bytes')),
                ('mime_type', models.CharField(max_length=100)),
                ('is_sensitive', models.BooleanField(default=False)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=models.deletion.CASCADE,
                 related_name='documents', to='customers.customer')),
                ('vehicle', models.ForeignKey(blank=True, null=True,
                 on_delete=models.deletion.CASCADE, related_name='documents', to='customers.vehicle')),
            ],
            options={
                'db_table': 'customer_documents',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='CustomerNote',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4,
                 editable=False, primary_key=True, serialize=False)),
                ('note_type', models.CharField(choices=[('general', 'General'), ('service', 'Service Related'), ('billing', 'Billing Related'), (
                    'complaint', 'Complaint'), ('compliment', 'Compliment'), ('follow_up', 'Follow Up')], default='general', max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('is_important', models.BooleanField(default=False)),
                ('is_private', models.BooleanField(default=False)),
                ('created_by', models.IntegerField(
                    help_text='Employee ID who created the note')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(on_delete=models.deletion.CASCADE,
                 related_name='notes', to='customers.customer')),
            ],
            options={
                'db_table': 'customer_notes',
                'ordering': ['-created_at'],
            },
        ),
        # Add indexes
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['user_id'],
                               name='customers_user_id_idx'),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['email'], name='customers_email_idx'),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(fields=['phone'], name='customers_phone_idx'),
        ),
        migrations.AddIndex(
            model_name='customer',
            index=models.Index(
                fields=['last_name', 'first_name'], name='customers_name_idx'),
        ),
        migrations.AddIndex(
            model_name='vehicle',
            index=models.Index(fields=['customer'],
                               name='vehicles_customer_idx'),
        ),
        migrations.AddIndex(
            model_name='vehicle',
            index=models.Index(fields=['vin'], name='vehicles_vin_idx'),
        ),
        migrations.AddIndex(
            model_name='vehicle',
            index=models.Index(
                fields=['license_plate'], name='vehicles_plate_idx'),
        ),
        migrations.AddIndex(
            model_name='vehicle',
            index=models.Index(
                fields=['make', 'model', 'year'], name='vehicles_make_model_year_idx'),
        ),
        migrations.AddIndex(
            model_name='customerdocument',
            index=models.Index(fields=['customer'],
                               name='documents_customer_idx'),
        ),
        migrations.AddIndex(
            model_name='customerdocument',
            index=models.Index(fields=['vehicle'],
                               name='documents_vehicle_idx'),
        ),
        migrations.AddIndex(
            model_name='customerdocument',
            index=models.Index(
                fields=['document_type'], name='documents_type_idx'),
        ),
        migrations.AddIndex(
            model_name='customernote',
            index=models.Index(fields=['customer'], name='notes_customer_idx'),
        ),
        migrations.AddIndex(
            model_name='customernote',
            index=models.Index(fields=['note_type'], name='notes_type_idx'),
        ),
        migrations.AddIndex(
            model_name='customernote',
            index=models.Index(fields=['is_important'],
                               name='notes_important_idx'),
        ),
    ]
