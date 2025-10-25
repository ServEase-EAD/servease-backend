# Custom migration to recreate custom_user table with UUID primary key

import uuid
from django.db import migrations, models


def recreate_table_with_uuid(apps, schema_editor):
    """
    Drop and recreate the custom_user table with UUID primary key
    """
    with schema_editor.connection.cursor() as cursor:
        # Drop the existing table and all its constraints
        cursor.execute("DROP TABLE IF EXISTS custom_user CASCADE")


def reverse_recreate_table(apps, schema_editor):
    """
    Reverse operation - this would be complex, so we'll just pass
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_customuser_options_customuser_created_at_and_more'),
    ]

    operations = [
        # First drop the existing table
        migrations.RunPython(recreate_table_with_uuid, reverse_recreate_table),
        
        # Then recreate it with the correct UUID structure
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('user_role', models.CharField(choices=[('customer', 'Customer'), ('employee', 'Employee'), ('admin', 'Admin')], default='customer', help_text='The role of the user in the system', max_length=10)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'db_table': 'custom_user',
            },
            managers=[
                ('objects', models.Manager()),
            ],
        ),
    ]