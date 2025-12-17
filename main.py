import mysql.connector
from tkinter import *
from tkinter import messagebox
from datetime import datetime

# -------------------- DATABASE CONNECTION --------------------
conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='1234',  # Change your MySQL password
    database='hotel_db'
)
cursor = conn.cursor()

# -------------------- FUNCTIONS --------------------

# ----- Customer Management -----
def add_customer():
    name = entry_name.get()
    email = entry_email.get()
    phone = entry_phone.get()
    if name and email and phone:
        cursor.execute("INSERT INTO Customers (name,email,phone) VALUES (%s,%s,%s)", (name,email,phone))
        conn.commit()
        messagebox.showinfo("Success","Customer added successfully!")
        entry_name.delete(0,END)
        entry_email.delete(0,END)
        entry_phone.delete(0,END)
        view_customers()
    else:
        messagebox.showerror("Error","All fields required!")

def view_customers():
    list_customers.delete(0,END)
    cursor.execute("SELECT * FROM Customers")
    for row in cursor.fetchall():
        list_customers.insert(END, row)

# ----- Room View -----
def view_rooms():
    list_rooms.delete(0,END)
    cursor.execute("SELECT * FROM Rooms")
    for row in cursor.fetchall():
        list_rooms.insert(END, row)

# ----- Booking -----
def book_room():
    try:
        cust_id = int(entry_booking_cust.get())
        room_id = int(entry_booking_room.get())
        check_in = entry_checkin.get()
        check_out = entry_checkout.get()

        # Check if room is available
        cursor.execute("SELECT status, price FROM Rooms WHERE room_id=%s", (room_id,))
        room = cursor.fetchone()
        if not room:
            messagebox.showerror("Error","Room does not exist")
            return
        if room[0]=='Booked':
            messagebox.showerror("Error","Room already booked")
            return

        price = room[1]
        nights = (datetime.strptime(check_out,'%Y-%m-%d') - datetime.strptime(check_in,'%Y-%m-%d')).days
        if nights<=0:
            messagebox.showerror("Error","Check-out must be after Check-in")
            return
        total = price * nights

        cursor.execute("INSERT INTO Bookings (customer_id,room_id,check_in,check_out,total_amount) VALUES (%s,%s,%s,%s,%s)",
                       (cust_id, room_id, check_in, check_out, total))
        cursor.execute("UPDATE Rooms SET status='Booked' WHERE room_id=%s",(room_id,))
        conn.commit()
        messagebox.showinfo("Success",f"Room booked! Total amount: {total}")
        entry_booking_cust.delete(0,END)
        entry_booking_room.delete(0,END)
        entry_checkin.delete(0,END)
        entry_checkout.delete(0,END)
        view_bookings()
        view_rooms()
    except Exception as e:
        messagebox.showerror("Error",str(e))

def view_bookings():
    list_bookings.delete(0,END)
    cursor.execute("SELECT booking_id, customer_id, room_id, check_in, check_out, total_amount FROM Bookings")
    for row in cursor.fetchall():
        list_bookings.insert(END,row)
# ----- Selected Booking Helper -----
def selected_booking():
    try:
        index = list_bookings.curselection()[0]
        return list_bookings.get(index)[0]  # booking_id
    except IndexError:
        messagebox.showerror("Error","No booking selected")
        return None

# ----- Delete Booking -----
def delete_booking():
    booking_id = selected_booking()
    if booking_id:
        # First, get room_id to free up room
        cursor.execute("SELECT room_id FROM Bookings WHERE booking_id=%s", (booking_id,))
        room = cursor.fetchone()
        if room:
            room_id = room[0]
            cursor.execute("UPDATE Rooms SET status='Available' WHERE room_id=%s", (room_id,))

        # Delete booking
        cursor.execute("DELETE FROM Bookings WHERE booking_id=%s", (booking_id,))
        conn.commit()
        messagebox.showinfo("Success", f"Booking ID {booking_id} deleted successfully")
        view_bookings()
        view_rooms()

# ----- Analytics -----
def show_revenue():
    cursor.execute("SELECT SUM(total_amount) FROM Bookings")
    revenue = cursor.fetchone()[0]
    messagebox.showinfo("Revenue",f"Total Revenue: {revenue}")

def room_occupancy():
    cursor.execute("SELECT Rooms.room_type, COUNT(Bookings.room_id) FROM Bookings JOIN Rooms ON Bookings.room_id = Rooms.room_id GROUP BY Rooms.room_type")
    data = cursor.fetchall()
    text = ""
    for row in data:
        text += f"Room Type: {row[0]}, Booked: {row[1]}\n"
    messagebox.showinfo("Room Occupancy",text)

# -------------------- GUI --------------------
root = Tk()
root.title("Hotel Management System")
root.geometry("900x600")

# --- Customer Frame ---
frame_cust = LabelFrame(root,text="Customer Management", padx=10,pady=10)
frame_cust.place(x=10,y=10,width=400,height=200)

Label(frame_cust,text="Name").grid(row=0,column=0)
Label(frame_cust,text="Email").grid(row=1,column=0)
Label(frame_cust,text="Phone").grid(row=2,column=0)

entry_name = Entry(frame_cust)
entry_email = Entry(frame_cust)
entry_phone = Entry(frame_cust)
entry_name.grid(row=0,column=1)
entry_email.grid(row=1,column=1)
entry_phone.grid(row=2,column=1)

Button(frame_cust,text="Add Customer",command=add_customer).grid(row=3,column=0,columnspan=2,pady=5)
list_customers = Listbox(frame_cust,width=50)
list_customers.grid(row=4,column=0,columnspan=2)
view_customers()

# --- Room Frame ---
frame_room = LabelFrame(root,text="Rooms", padx=10,pady=10)
frame_room.place(x=450,y=10,width=430,height=200)
list_rooms = Listbox(frame_room,width=60)
list_rooms.pack()
view_rooms()

# --- Booking Frame ---
frame_book = LabelFrame(root,text="Booking", padx=10,pady=10)
frame_book.place(x=10,y=220,width=400,height=200)

Label(frame_book,text="Customer ID").grid(row=0,column=0)
Label(frame_book,text="Room ID").grid(row=1,column=0)
Label(frame_book,text="Check-In YYYY-MM-DD").grid(row=2,column=0)
Label(frame_book,text="Check-Out YYYY-MM-DD").grid(row=3,column=0)

entry_booking_cust = Entry(frame_book)
entry_booking_room = Entry(frame_book)
entry_checkin = Entry(frame_book)
entry_checkout = Entry(frame_book)
entry_booking_cust.grid(row=0,column=1)
entry_booking_room.grid(row=1,column=1)
entry_checkin.grid(row=2,column=1)
entry_checkout.grid(row=3,column=1)

Button(frame_book,text="Book Room",command=book_room).grid(row=4,column=0,columnspan=2,pady=5)
list_bookings = Listbox(frame_book,width=50)
list_bookings.grid(row=5,column=0,columnspan=2)
Button(frame_book,text="Delete Booking",command=delete_booking).grid(row=4,column=1,padx=5,pady=5)
view_bookings()

# --- Analytics Frame ---
frame_analytics = LabelFrame(root,text="Analytics", padx=10,pady=10)
frame_analytics.place(x=450,y=220,width=430,height=200)
Button(frame_analytics,text="Total Revenue",command=show_revenue,width=20).pack(pady=10)
Button(frame_analytics,text="Room Occupancy",command=room_occupancy,width=20).pack(pady=10)

root.mainloop()
