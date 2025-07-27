import psycopg2

def authenticate_db(filepath='secrets.txt'):
    """
    Authenticates and returns a PostgreSQL connection and cursor.
    Raises an exception if connection fails.
    """
    creds = {}
    with open(filepath, 'r') as file:
        for line in file:
            if '=' in line:
                k, v = line.strip().split('=', 1)
                creds[k] = v
    try:
        conn = psycopg2.connect(
            dbname=creds.get('POSTGRES_DB_NAME', 'stock_data'),
            user=creds.get('POSTGRES_USER', 'postgres'),
            password=creds.get('POSTGRES_PASSWORD', ''),
            host=creds.get('POSTGRES_HOST', 'localhost'),
            port=creds.get('POSTGRES_PORT', '5432')
        )
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        raise ConnectionError(f"Failed to connect to PostgreSQL: {e}")