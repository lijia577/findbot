import os
import psycopg2
from data_models import Items, Item

def get_db_connection():
    # Use DATABASE_URL environment variable for connection
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    return conn

def store_item_details(items: Items) -> None:
    """Store item details from an Items instance into the SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create a table to store item details
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS item_location (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        location TEXT
    )
    ''')

    for item_detail in items.items:
        item = item_detail.item
        location = item_detail.location

        cursor.execute('''
        INSERT INTO item_location (item, location)
        VALUES (%s, %s)
        ''', (item, location))

    conn.commit()
    cursor.close()
    conn.close()


def retrieve_all_item_and_location() -> Items:
    """Retrieve item details from the PostgreSQL database and return as an Items instance."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT item, location FROM item_location')
    rows = cursor.fetchall()

    items_list = [Item(item=row[0], location=row[1]) for row in rows]

    cursor.close()
    conn.close()

    return Items(items=items_list)


def retrieve_items() -> [str]:
    """Retrieve items only from the PostgreSQL database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve all item details from the database
    cursor.execute('SELECT item FROM item_location')
    rows = cursor.fetchall()

    # Create a list of items from the retrieved rows
    items_list = [row[0] for row in rows]

    # Close the connection
    cursor.close()
    conn.close()

    return items_list



def retrieve_location_by_item(item_name: str) -> Items:
    """Retrieve locations for a given item from the PostgreSQL database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    items_list = []

    try:
        # Retrieve the location for the specified item
        cursor.execute('SELECT location FROM item_location WHERE item = %s', (item_name,))
        rows = cursor.fetchall()

        items_list.extend([Item(item=item_name, location=row[0]) for row in rows])

    finally:
        # Ensure the connection is closed even if an error occurs
        cursor.close()
        conn.close()

    return Items(items=items_list)

def drop_all_items():
    """Delete all records from the item_location table in the PostgreSQL database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Execute a command to delete all records from the item_location table
    cursor.execute('DELETE FROM item_location')

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    drop_all_items()
    items_to_store = Items(items=[
        Item(item='pair of leather gloves with fur', location='bedroom drawer'),
        Item(item='keys', location='living room desk')
    ])

    store_item_details(items_to_store)
    print(retrieve_items())

    items = retrieve_location_by_item('keys')
    print(items)
