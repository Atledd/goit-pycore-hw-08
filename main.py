from collections import UserDict
import re
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass  # Додаткової логіки не потрібно, просто успадковуємо Field

class Phone(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

    @staticmethod
    def validate(value):
        return bool(re.fullmatch(r'\d{10}', value))

class Birthday(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
            # Перетворюємо рядок на об'єкт datetime
        self.value = datetime.strptime(value, "%d.%m.%Y")
    
    @staticmethod
    def validate(value):
        return bool(re.fullmatch(r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(\d{4})$', value))

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if p.value != phone_number]

    def edit_phone(self, old_number, new_number):
        self.remove_phone(old_number)
        self.add_phone(new_number)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.now()
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if today <= birthday_this_year < today + timedelta(days=7):
                    upcoming_birthdays.append(record.name.value)
        return upcoming_birthdays
    
    #Серіалізація, десеріалізація
    def save_to_file(self, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self, f)

    #Доцільно використати класовий метод, адже ми взаємодіємо із самим класом для створення екземпляру на основі збережених у файлі даних
    @classmethod    
    def load_from_file(cls, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return cls()       # Повертаємо нову адресну книгу, якщо файл не знайдено


#Декоратор для обробки помилок
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, IndexError) as e:
            return str(e)
    return inner

#Функції для обробки команд
@input_error
def add_birthday(args, book):
    name, date = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    record.add_birthday(date)
    return f"Birthday added for {name}."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    return record.show_birthday()

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays."
    return f"Upcoming birthdays: {', '.join(upcoming_birthdays)}."

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return f"Phone number changed from {old_phone} to {new_phone}."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    return f"Phones for {name}: {', '.join(phone.value for phone in record.phones)}"

@input_error
def show_all_contacts(book):
    if not book.data:
        return "No contacts in the address book."
    return "\n".join(str(record) for record in book.data.values())

#Головна функція
def main():
    book = AddressBook.load_from_file()  #Завантажуємо адресну книгу
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = user_input.split()

        if command in ["close", "exit"]:
            book.save_to_file()  #Збереження перед виходом із програми
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
            pass
        elif command == "phone":
            print(show_phone(args, book))
            pass
        elif command == "all":
            print(show_all_contacts(book))
            pass
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()