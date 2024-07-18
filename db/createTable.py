from .connectDB import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create ENUM type query
    create_user_status_enum_query = """
    DO $$ BEGIN
        CREATE TYPE user_status AS ENUM ('inactive', 'active');
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """

    # Create table query
    create_users_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        uuid UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        status user_status DEFAULT 'inactive',
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    create_subscriptions_table_query = """
    CREATE TABLE IF NOT EXISTS subscriptions (
        uuid UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id VARCHAR(50) NOT NULL,
        customer_id VARCHAR(100) NOT NULL,
        price_id VARCHAR(255) NOT NULL,
        status VARCHAR(255) NOT NULL,
        start_date TIMESTAMP NOT NULL,
        end_date TIMESTAMP NOT NULL,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        # Execute the ENUM type creation query
        cursor.execute(create_user_status_enum_query)
        # Execute the table creation query
        cursor.execute(create_users_table_query)
        # Execute the table creation query
        cursor.execute(create_subscriptions_table_query)
        # Commit the transaction
        conn.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()
        conn.close()
