import mysql.connector
import re
import time
from datetime import datetime
from decimal import Decimal
# Connect to MySQL database
db = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='Rash__Kabi@123',
    database="hotel_booking_db"
)
cursor = db.cursor()


# Utility function to generate a Booking ID
def generate_booking_id():
    prefix = "BK"
    suffix = str(time.time_ns())[-5:]
    return prefix + suffix


# 1. Display the Category-wise list of rooms and their Rate per day
def display_rooms_by_category():
    query = "SELECT c.name AS category, r.room_no, c.price_per_day, c.price_per_hour FROM rooms r JOIN category c ON r.category_id = c.id ORDER BY c.name;"
    cursor.execute(query)
    rooms = cursor.fetchall()
    for room in rooms:
        category, room_no, rate_per_day, rate_per_hour = room
        if rate_per_hour:
            print(
                f"Room No: {room_no}, Category: {category}, Rate per Day: {rate_per_day}, Rate per Hour: {rate_per_hour}")
        else:
            print(f"Room No: {room_no}, Category: {category}, Rate per Day: {rate_per_day}")


# 2. List all rooms occupied for the next two days
def list_occupied_rooms_next_two_days():
    query = """
    SELECT rooms.room_no, bookings.occupancy_date 
    FROM rooms 
    JOIN bookings ON rooms.id = bookings.room_id 
    WHERE bookings.occupancy_date BETWEEN CURDATE() AND CURDATE() + INTERVAL 2 DAY
    """
    cursor.execute(query)
    occupied_rooms = cursor.fetchall()
    for room_no, occupancy_date in occupied_rooms:
        print(f"Room No: {room_no}, Occupied on: {occupancy_date}")


# 3. Display the list of all rooms in their increasing order of rate per day
def display_rooms_by_rate():
    query="SELECT r.room_no,c.name AS category, c.price_per_day AS rate_per_day FROM rooms r JOIN category c ON r.category_id = c.id ORDER BY c.price_per_day ASC"
    cursor.execute(query)
    rooms = cursor.fetchall()
    for room_no, category, rate_per_day in rooms:
        print(f"Room No: {room_no}, Category: {category}, Rate per Day: {rate_per_day}")


# 4. Search Rooms based on BookingID and display the customer details
def search_room_by_booking_id(booking_id):
    query = """
    SELECT rooms.room_no, customers.first_name, customers.last_name, bookings.booking_date
    FROM bookings 
    JOIN rooms ON bookings.room_id = rooms.id 
    JOIN customers ON bookings.customer_id = customers.id 
    WHERE bookings.booking_id = %s
    """
    cursor.execute(query, (booking_id,))
    result = cursor.fetchone()
    if result:
        room_no, first_name, last_name, booking_date = result
        print(
            f"Booking ID: {booking_id}, Room No: {room_no}, Customer: {first_name} {last_name}, Booking Date: {booking_date}")
    else:
        print("No booking found with that ID.")


# 5. Display rooms which are not booked
def display_unbooked_rooms():
    query = """
    SELECT r.room_no, c.name AS category, c.price_per_day, c.price_per_hour
    FROM rooms r
    JOIN category c ON r.category_id = c.id
    WHERE r.status = 'unoccupied'
    """
    cursor.execute(query)
    unbooked_rooms = cursor.fetchall()
    for room_no, category, price_per_day, price_per_hour in unbooked_rooms:
        print(f"Room No: {room_no}, Category: {category}, Rate per day: {price_per_day}, Rate per hour: {price_per_hour if price_per_hour else 'N/A'}")


# 6. Update room when the customer leaves to Unoccupied
def update_room_to_unoccupied(room_no):
    query = "UPDATE rooms SET status = 'unoccupied' WHERE room_no = %s"
    cursor.execute(query, (room_no,))
    db.commit()
    print(f"Room {room_no} status updated to unoccupied.")


# 7. Store all records in file and display from file
def store_records_in_file():
    query = "SELECT * FROM bookings"
    cursor.execute(query)
    bookings = cursor.fetchall()
    with open('bookings.txt', 'w') as f:
        for booking in bookings:
            f.write(str(booking) + '\n')
    print("Records stored in bookings.txt")


def display_records_from_file(db=None):
    try:


        # Query to select all records from the bookings table
        query = """
        SELECT booking_id, room_id, customer_id, booking_date, occupancy_date, no_of_days, advance_received, total_amount
        FROM bookings
        """
        cursor.execute(query)
        records = cursor.fetchall()

        # Write records to the file
        with open('bookings.txt', 'w') as f:
            for record in records:
                line = ", ".join(map(str, record))  # Convert each record to a string
                f.write(line + "\n")

        print("Bookings file created successfully.")

        # Display the records from the file
        with open('bookings.txt', 'r') as f:
            records = f.readlines()
            for record in records:
                # Split each record by comma and strip any leading/trailing whitespace
                fields = record.strip().split(", ")
                # Print each field
                print(f"Booking ID: {fields[0]}, Room ID: {fields[1]}, Customer ID: {fields[2]}, Booking Date: {fields[3]}, Occupancy Date: {fields[4]}, No. of Days: {fields[5]}, Advance Received: {fields[6]}, Total Amount: {fields[7]}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        if cursor:
            cursor.close()

# 8. Register a new customer

def register_customer(first_name, last_name, email, phone, username, password):
    try:
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format")

        # Validate phone number format
        if not re.match(r"^\d{10}$", phone):
            raise ValueError("Phone number should be 10 digits")

        # Validate username
        if not re.match(r"^[a-zA-Z0-9_]{5,20}$", username):
            raise ValueError(
                "Username should be 5-20 characters long and contain only letters, numbers, or underscores")

        # Validate password
        if len(password) < 8:
            raise ValueError("Password should be at least 8 characters long")

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert new customer into the database
        query = """
        INSERT INTO customers (first_name, last_name, email, phone, username, password)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (first_name, last_name, email, phone, username, hashed_password))
        db.commit()
        print("Customer registered successfully!")
    except mysql.connector.IntegrityError as e:
        if 'username' in str(e):
            print("Error: Username already exists.")
        elif 'email' in str(e):
            print("Error: Customer with this email already exists.")
    except ValueError as e:
        print(f"Validation Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



def pre_book_room(customer_id, room_no, occupancy_date, no_of_days, advance_received):
    try:
        # Query to get room details including category and rates
        query_room = """
        SELECT r.id, c.price_per_day, c.price_per_hour, c.name 
        FROM rooms r 
        JOIN category c ON r.category_id = c.id 
        WHERE r.room_no = %s
        """
        cursor.execute(query_room, (room_no,))
        room = cursor.fetchone()
        if not room:
            raise ValueError("Invalid room number")

        room_id, rate_per_day, rate_per_hour, category = room
        booking_id = generate_booking_id()

        # Define additional charges and tax rate
        additional_charges = Decimal('100.00')  # Fixed amount for tax, housekeeping, etc.
        tax_rate = Decimal('0.10')  # Example: 10% tax

        # Convert rate and occupancy to Decimal
        rate_per_day = Decimal(str(rate_per_day))


        # Calculate the base amount based on room category
        if category in ('convention_hall', 'ballroom'):
            base_amount = rate_per_hour * Decimal(no_of_days) * Decimal('24.00')
        else:
            base_amount = rate_per_day * Decimal(no_of_days)

        # Calculate the total amount including additional charges and tax
        total_amount = base_amount + additional_charges
        total_amount_with_tax = total_amount + (total_amount * tax_rate)

        # Insert booking record into the bookings table
        query_booking = """
        INSERT INTO bookings (booking_id, customer_id, room_id, booking_date, occupancy_date, no_of_days, advance_received, total_amount)
        VALUES (%s, %s, %s, CURDATE(), %s, %s, %s, %s)
        """
        cursor.execute(query_booking,
                       (booking_id, customer_id, room_id, occupancy_date, no_of_days, advance_received, total_amount_with_tax))

        # Update the room status to 'occupied'
        query_update_room = "UPDATE rooms SET status = 'occupied' WHERE id = %s"
        cursor.execute(query_update_room, (room_id,))
        db.commit()

        print(f"Room {room_no} pre-booked successfully with Booking ID: {booking_id}")
    except ValueError as e:
        print(f"Error: {e}")

# 10. Display Booking History for a Customer
def display_booking_history(customer_id):
    query = """
    SELECT bookings.booking_id, rooms.room_no, bookings.occupancy_date, bookings.no_of_days, bookings.total_amount
    FROM bookings 
    JOIN rooms ON bookings.room_id = rooms.id 
    WHERE bookings.customer_id = %s
    """
    cursor.execute(query, (customer_id,))
    history = cursor.fetchall()
    for booking_id, room_no, occupancy_date, no_of_days, total_amount in history:
        print(
            f"Booking ID: {booking_id}, Room No: {room_no}, Occupancy Date: {occupancy_date}, Duration: {no_of_days} days, Total Amount: {total_amount}")


# Admin Functionalities
def admin_menu():
    while True:
        print("\nAdmin Menu")
        print("1. View Rooms by Category")
        print("2. List Occupied Rooms for Next Two Days")
        print("3. List Rooms by Rate")
        print("4. Search Room by Booking ID")
        print("5. View Unbooked Rooms")
        print("6. Update Room to Unoccupied")
        print("7. View All Bookings")
        print("8. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            display_rooms_by_category()
        elif choice == '2':
            list_occupied_rooms_next_two_days()
        elif choice == '3':
            display_rooms_by_rate()
        elif choice == '4':
            booking_id = input("Enter Booking ID: ")
            search_room_by_booking_id(booking_id)
        elif choice == '5':
            display_unbooked_rooms()
        elif choice == '6':
            room_no = input("Enter Room Number: ")
            update_room_to_unoccupied(room_no)
        elif choice == '7':
            display_records_from_file()
        elif choice == '8':
            break
        else:
            print("Invalid choice. Please try again.")
def customer_menu1(customer_id):
    while True:
        print("\nCustomer Menu")
        print("1. View Available Rooms")
        print("2. Pre-book a Room")
        print("3. Make a Payment")
        print("4. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            display_unbooked_rooms()  # Display available rooms based on category
        elif choice == '2':
            room_no = input("Enter Room Number: ")
            occupancy_date = input("Enter Occupancy Date (YYYY-MM-DD): ")
            no_of_days = int(input("Enter Number of Days: "))
            advance_received = float(input("Enter Advance Received: "))
            pre_book_room(customer_id, room_no, occupancy_date, no_of_days, advance_received)
        elif choice == '3':
            booking_id = input("Enter Booking ID: ")
            make_payment(booking_id)
        elif choice =='4':
            return main()
        else:
            print("Invalid Option")

# Customer Functionalities
def customer_menu(customer_id):
    while True:
        print("\nCustomer Menu")
        print("1. View Available Rooms")
        print("2. Pre-book a Room")
        print("3. Make a Payment")
        print("4. View Booking History")
        print("5. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            display_unbooked_rooms()  # Display available rooms based on category
        elif choice == '2':
            room_no = input("Enter Room Number: ")
            occupancy_date = input("Enter Occupancy Date (YYYY-MM-DD): ")
            no_of_days = int(input("Enter Number of Days: "))
            advance_received = float(input("Enter Advance Received: "))
            pre_book_room(customer_id, room_no, occupancy_date, no_of_days, advance_received)
        elif choice == '3':
            booking_id = input("Enter Booking ID: ")
            make_payment(booking_id)
        elif choice == '4':
            display_booking_history(customer_id)
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")


# 11. Make a Payment for a Booking
def validate_card_details(card_number, expiry_date, cvv):
    # Validate card number (10-15 digits)
    if not re.match(r"^\d{10,15}$", card_number):
        raise ValueError("Invalid card number. Must be between 10 to 15 digits.")

    # Validate expiry date (MM/YY format and should be a future date)
    try:
        exp_date = datetime.strptime(expiry_date, "%m/%y")
        if exp_date < datetime.now():
            raise ValueError("Card expiry date is invalid or expired.")
    except ValueError:
        raise ValueError("Invalid expiry date format. Use MM/YY.")

    # Validate CVV (3 digits)
    if not re.match(r"^\d{3}$", cvv):
        raise ValueError("Invalid CVV. Must be 3 digits.")


def make_payment(booking_id):
    try:
        # Fetch the total amount and advance received for the given booking ID
        query = "SELECT total_amount, advance_received FROM bookings WHERE booking_id = %s"
        cursor.execute(query, (booking_id,))
        result = cursor.fetchone()

        if result:
            total_amount, advance_received = result
            remaining_amount = total_amount - advance_received

            if remaining_amount > 0:
                # Collect and validate payment details
                card_number = input("Enter your card number (10-15 digits): ")
                expiry_date = input("Enter your card expiry date (MM/YY): ")
                cvv = input("Enter your CVV (3 digits): ")

                try:
                    validate_card_details(card_number, expiry_date, cvv)
                except ValueError as e:
                    print(f"Payment failed: {e}")
                    return

                # Proceed with payment if card details are valid
                payment = float(input(f"Total amount due: {remaining_amount}. Enter payment amount: "))
                if payment >= remaining_amount:
                    query_update = "UPDATE bookings SET advance_received = %s WHERE booking_id = %s"
                    cursor.execute(query_update, (total_amount, booking_id))
                    db.commit()
                    print("Payment successful! Booking is now fully paid.")
                else:
                    print("Payment amount is less than the due amount.")
            else:
                print("No amount is due. The booking is already fully paid.")
        else:
            print("Invalid Booking ID.")
    except ValueError:
        print("Invalid input. Please enter a valid number.")


def get_customer_id(username):
    try:
        # Query to get customer ID from the database based on username
        query = "SELECT id FROM customers WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        # Check if a result was returned
        if result:
            return result[0]  # Return the customer ID
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None




import bcrypt

def login(username, password):
    try:
        # Query to get user credentials from the database
        query = "SELECT password FROM customers WHERE username = %s"
        cursor.execute(query, (username,))
        result = cursor.fetchone()

        # Check if a result was returned
        if result:
            hashed_password = result[0]
            # Verify the provided password against the hashed password
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                return True
        return False
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return False
def main():
    while True:
        print("\nHotel Booking System")
        print("1. Register Customer")
        print("2. Login (Admin/Customer)")
        print("3. View Rooms and Rates (Guest)")
        print("4. Exit")

        choice = input("Enter your choice: ")
        if choice == '1':
            first_name = input("Enter First Name: ")
            last_name = input("Enter Last Name: ")
            email = input("Enter Email: ")
            phone = input("Enter Phone Number: ")
            username = input("Create Username: ")
            password = input("Create Password: ")
            # Call the updated register_customer function
            register_customer(first_name, last_name, email, phone, username, password)
            return customer_menu1(customer_id=None)
        elif choice == '2':
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            user_type = input("Are you an Admin or Customer? (admin/customer): ").lower()

            if user_type == 'admin':
                # Explicit check for the admin credentials
                if username == 'Rashmi' and password == 'Rash@123':
                    admin_menu()
                else:
                    print("Invalid username or password.")
            elif user_type == 'customer':
                # Use the login function for customer verification
                if login(username, password):
                    customer_id = get_customer_id(username)  # Function to get customer ID based on username
                    if customer_id:
                        customer_menu(customer_id)
                    else:
                        print("Customer ID not found.")
                else:
                    print("Invalid username or password.")
            else:
                print("Invalid user type. Please try again.")
        elif choice == '3':
            display_unbooked_rooms()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
