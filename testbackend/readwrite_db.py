import sqlite3
from data_models import Items, Item


def store_item_details(items: Items) -> None:
    """Store item details from an Items instance into the SQLite database."""
    conn = sqlite3.connect('../items.db')
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
        VALUES (?, ?)
        ''', (item, location))

    conn.commit()
    conn.close()


def retrieve_all_item_and_location() -> Items:
    """Retrieve item details from the SQLite database and return as an Items instance."""
    # Connect to SQLite database
    conn = sqlite3.connect('../items.db')
    cursor = conn.cursor()

    # Retrieve all item details from the database
    cursor.execute('SELECT item, location FROM item_location')
    rows = cursor.fetchall()

    # Create Item instances from the retrieved rows
    items_list = [Item(item=row[0], location=row[1]) for row in rows]

    # Close the connection
    conn.close()

    # Return an Items instance containing the list of Item instances
    return Items(items=items_list)


def retrieve_items() -> [str]:
    """Retrieve items only from the SQLite database and return as an Items instance."""
    # Connect to SQLite database
    conn = sqlite3.connect('../items.db')
    cursor = conn.cursor()

    # Retrieve all item details from the database
    cursor.execute('SELECT item FROM item_location')  # Retrieve both item and location
    rows = cursor.fetchall()

    # Create Item instances from the retrieved rows
    l = [row[0] for row in rows]  # Include location

    # Close the connection
    conn.close()

    # Return an Items instance containing the list of Item instances
    return l


def retrieve_location_by_item(item_name: str) -> Items:
    """Retrieve locations for a given item from the SQLite database."""
    # Connect to SQLite database
    conn = sqlite3.connect('../items.db')
    cursor = conn.cursor()

    items_list = []

    try:
        # Retrieve the location for the specified item
        cursor.execute('SELECT location FROM item_location WHERE item = ?', (item_name,))
        rows = cursor.fetchall()

        items_list.extend([Item(name=item_name, location=row[0], item=item_name) for row in rows])

    finally:
        # Ensure the connection is closed even if an error occurs
        conn.close()

    # Return an Items object containing the list of Item objects
    return Items(items=items_list)


def drop_all_items():
    # Connect to SQLite database
    conn = sqlite3.connect('../items.db')
    cursor = conn.cursor()

    # Execute a command to delete all records from the item_location table
    cursor.execute('DELETE FROM item_location')

    # Commit the changes and close the connection
    conn.commit()
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
