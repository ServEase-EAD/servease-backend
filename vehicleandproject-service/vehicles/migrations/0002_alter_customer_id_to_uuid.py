# Custom migration to change customer_id from IntegerField to UUIDField safely
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vehicles", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        """
                        -- Drop existing index if any (name may vary from auto-generated); ignore errors
                        DO $$ BEGIN
                            IF EXISTS (
                                SELECT 1 FROM pg_indexes WHERE tablename = 'vehicles' AND indexname = 'vehicles_custome_a752bc_idx'
                            ) THEN
                                EXECUTE 'DROP INDEX IF EXISTS vehicles_custome_a752bc_idx';
                            END IF;
                        END $$;

                        -- Drop old column and add new UUID column as NULLABLE first
                        ALTER TABLE vehicles DROP COLUMN IF EXISTS customer_id;
                        ALTER TABLE vehicles ADD COLUMN customer_id uuid;

                        -- Backfill existing rows with a sentinel UUID to satisfy NOT NULL later
                        UPDATE vehicles SET customer_id = '00000000-0000-0000-0000-000000000000' WHERE customer_id IS NULL;

                        -- Enforce NOT NULL
                        ALTER TABLE vehicles ALTER COLUMN customer_id SET NOT NULL;

                        -- Recreate index
                        CREATE INDEX IF NOT EXISTS vehicles_customer_id_idx ON vehicles (customer_id);
                        """
                    ),
                    reverse_sql=(
                        """
                        -- Reverse: drop UUID column and create integer column
                        DO $$ BEGIN
                            IF EXISTS (
                                SELECT 1 FROM pg_indexes WHERE tablename = 'vehicles' AND indexname = 'vehicles_customer_id_idx'
                            ) THEN
                                EXECUTE 'DROP INDEX IF EXISTS vehicles_customer_id_idx';
                            END IF;
                        END $$;

                        ALTER TABLE vehicles DROP COLUMN IF EXISTS customer_id;
                        ALTER TABLE vehicles ADD COLUMN customer_id integer NOT NULL;
                        CREATE INDEX IF NOT EXISTS vehicles_custome_a752bc_idx ON vehicles (customer_id);
                        """
                    ),
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='vehicle',
                    name='customer_id',
                    field=models.UUIDField(
                        help_text='Reference to customer who owns this vehicle',
                        db_index=True,
                    ),
                ),
            ],
        ),
    ]
