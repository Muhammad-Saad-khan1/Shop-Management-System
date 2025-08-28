import json
import os

class Customer:
    def __init__(self, name, phone, customer_id, billing_info=0):
        self.name = name
        self.phone = phone
        self.id = customer_id
        self.billing_info = billing_info

    def to_dict(self):
        return {
            "Name": self.name,
            "Phone": self.phone,
            "id": self.id,
            "Billing_Info": self.billing_info
        }


class Item:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def to_dict(self): 
        return {
            "Item_Name": self.name,
            "Item_Price": self.price,
            "Item_Quantity": self.quantity
        }

class Data_Management:
    def save_information(self):
        with open("credentials.json", "w") as file:
            json.dump(self.admin, file)
        with open("customer.json", "w") as file:
            json.dump([c.to_dict() for c in self.customers], file)
        with open("items.json", "w") as file:
            json.dump([i.to_dict() for i in self.items], file)

    def load_information(self):
        try:
            with open("credentials.json", "r") as file:
                self.admin = json.load(file)
            with open("customer.json", "r") as file:
                self.customers = [
                    Customer(
                        name=c["Name"],
                        phone=c["Phone"],
                        customer_id=c["id"],
                        billing_info=c.get("Billing_Info", 0)
                    ) for c in json.load(file)
                ]
            with open("items.json", "r") as file:
                self.items = [
                    Item(
                        name=i["Item_Name"],
                        price=i["Item_Price"],
                        quantity=i["Item_Quantity"]
                    ) for i in json.load(file)
                ]
        except FileNotFoundError:
            print("No saved data found. Using defaults.")

class Shop(Data_Management):
    def __init__(self):
        self.admin = {"Name": "admin", "Password": "admin123", "Shop_Name": "MyShop"}
        self.customers = []
        self.items = []
        self.default_name = "admin"
        self.default_pass = "admin123"
        
    # - Admin Management -
    def change_shop_name(self):
        print(f"Your current shop name is: {self.admin['Shop_Name']}")
        if input("Do you want to change it? (yes/no): ").strip().lower() == "yes":
            self.admin["Shop_Name"] = input("Enter new shop name: ")

    def first_time_setup(self):
        print("First-time setup: Create new credentials.")
        self.admin["Name"] = input("Enter your name: ")
        self.admin["Password"] = input("Enter your password: ")
        self.change_shop_name()
        self.save_information()

    def login(self):
        while True:
            username = input("Enter your name: ")
            password = input("Enter your password: ")
            if username == self.admin["Name"] and password == self.admin["Password"]:
                print("Login successful.")
                break
            else:
                print("Invalid credentials. Try again.")

    def user_information(self):
        self.load_information()
        if self.admin["Name"] == self.default_name and self.admin["Password"] == self.default_pass:
            self.first_time_setup()
        else:
            print("Please log in to access the shop.")
            self.login()

    # - Customer Management -
    def phone_check(self):
        while True:
            phone = input("Enter customer phone: ")
            if phone.isdigit() and len(phone) == 11:
                return phone
            print("Invalid phone number! Must be 11 digits.")

    def add_customer(self):
        name = input("Enter customer name: ")
        phone = self.phone_check()
        if any(c.phone == phone for c in self.customers):
            print("Customer with this phone number already exists.")
            return
        last_id = self.customers[-1].id if self.customers else 0
        new_customer = Customer(name, phone, last_id + 1)
        self.customers.append(new_customer)
        print(f"Your Id: {new_customer.id}")
        print("Customer added successfully.")
        if input("Do you willing to buy something? (yes/no): ").strip().lower() == "yes":
            self.generate_bill()

    def customer_details(self):
        for c in self.customers:
            print(f"Name: {c.name}, Phone: {c.phone}, ID: {c.id}, Billing Info: {c.billing_info}")
            print("-" * 20)

    # - Item Management -
    def add_item(self):
        name = input("Enter item name: ")
        if any(i.name.lower() == name.lower() for i in self.items):
            print("Item with this name already exists.")
            return
        try:
            price = float(input("Enter item price: "))
            quantity = int(input("Enter item quantity: "))
        except ValueError:
            print("Invalid price or quantity.")
            return
        new_item = Item(name, price, quantity)
        self.items.append(new_item)
        print("Item added successfully.")

    def item_details(self):
        for i in self.items:
            print(f"Name: {i.name}, Price: {i.price}, Quantity: {i.quantity}")
            print("-" * 20)

    def update_item(self):
        item_name = input("Enter the item name to update: ").lower()
        for i in self.items:
            if i.name.lower() == item_name:
                if input("Change price? (yes/no): ").lower() == "yes":
                    try:
                        i.price = float(input("Enter new price: "))
                    except ValueError:
                        print("Invalid price.")
                        return
                try:
                    i.quantity += int(input("Enter quantity to add: "))
                except ValueError:
                    print("Invalid quantity.")
                    return
                print("Item updated successfully.")
                return
        print("Item not found.")

    # - Billing -
    def shopping(self):
        billing_items = []
        while True:
            item_name = input("Enter item name (or 'done'): ").lower()
            if item_name == "done":
                return billing_items
            found = False
            for i in self.items:
                if i.name.lower() == item_name:
                    input_quantity = int(input(f"Enter quantity for {i.name} (available: {i.quantity}): "))
                    if 0 < input_quantity <= i.quantity:
                        i.quantity -= input_quantity
                        billing_items.append(Item(i.name, i.price * input_quantity, input_quantity))
                    else:
                        print("Invalid quantity.")
                    found = True
                    break
            if not found:
                print("Item not found.")
                if input("Add this item? (yes/no): ").lower() == "yes":
                    self.add_item()
    
    def bill(self, name):
        billing_items = self.shopping()
        total = sum(i.price for i in billing_items)
        print(f"+++++ {self.admin['Shop_Name']} +++++")
        for i in billing_items:
            print(f"{i.name} ----> {i.quantity} ----> {i.price}")
        print(f"Total: {total}")
        print(f"Thank you {name}!")
    
    def generate_bill(self):
        if not self.customers:
            name = input("Enter your name: ")
            self.bill(name)
        else:
            try:
                id = int(input("Enter customer ID: "))
            except ValueError:
                print("Invalid customer ID.")
                return
            for c in self.customers:
                if c.id == id:
                    self.bill(c.name)
                    return
            print("Customer not found.")

    # - Main Menu -
    def menu(self):
        self.load_information()
        print(f"\n {'-' * 10} Welcome to {self.admin['Shop_Name']}! {'-' * 10} \n\n")
        self.user_information()
        while True:
            print("\n1: Add Customer")
            print("2: Add Item")
            print("3: Update Item")
            print("4: Show Items")
            print("5: Show Customers")
            print("6: Generate Bill")
            print("7: Change shop name.")
            print("8: Exit")
            choice = input("Choice: ")
            match choice:
                case "1": self.add_customer()
                case "2": self.add_item()
                case "3": self.update_item()
                case "4": self.item_details()
                case "5": self.customer_details()
                case "6": self.generate_bill()
                case "7": self.change_shop_name()
                case "8":
                    self.save_information()
                    print("Exiting...")
                    break
                case _: print("Invalid choice.")
            self.save_information()


if __name__ == "__main__":
    shop = Shop()
    shop.menu()
