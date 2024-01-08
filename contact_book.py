from collections import UserDict, defaultdict
import cmd
from datetime import date, datetime, timedelta
import pickle
import os
import re
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.table import Table
from field import Phone, Address, Birthday, Email, Name
from record import Record


class Search:
    def __init__(self, address_book):
        self.address_book = address_book

    def search(self, value: str):
        if len(value) < 3:
            return '\033[91mYou need at least 3 letters to search by name or 3 digits to search by phone number.\033[0m'
        result = ''
        for name, rec in self.address_book.items():
            if value.lower() in name.lower():
                result += f'{str(rec)}\n'
            for item in rec.phones:
                if value in item.value:
                    result += f'{str(rec)}'
        if len(result) != 0:
            return result
        else:
            return None


class AddressBook(UserDict) :
    def __init__(self) :
        super().__init__()
        self.file = 'Phone_Book.bin'

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        if name in self.data:
            return self.data[name]
        return None

    def search(self, value: str):
        my_search = Search(self.data)
        return my_search.search(value)

    def delete(self, name: str):
        if name in self.data:
            self.data.pop(name)
            return f'The contact {name} has been deleted.'
        else:
            return f'The contact {name} not found.'

    def write_to_file(self):
        with open(self.file, 'wb') as file :
            pickle.dump(self.data, file)

    def read_from_file(self) :
        with open(self.file, 'rb') as file :
            self.data = pickle.load(file)
        return self.data


# class Controller(cmd.Cmd) :
#     def exit(self) :
#         self.book.dump()
#         return True


def input_error(func) :
    def inner(*args, **kwargs) :
        try :
            result = func(*args, **kwargs)
            return result
        except KeyError :
            return 'No user with this name'
        except ValueError :
            return 'Incorrect information entered'
        except IndexError :
            return 'Enter user name'

    return inner


class TableAction:
    def __init__(self):
        self.table = Table(title="Search results", style="cyan", title_style="bold magenta", width=140)
        self.table.add_column("Name", style="red", justify="center")
        self.table.add_column("Phones", style="bold blue", justify="center")
        self.table.add_column("Birthday", style="bold green", justify="center")
        self.table.add_column("Email", style="bold blue", justify="center")
        self.table.add_column("Address", style="yellow", justify="center")
        self.table.add_column("Days to birthday", style="yellow", justify="center")
        self.console = Console()

    def add_row(self, name, phones, birthday, email, address, days_to_birthday):
        self.table.add_row(name, phones, birthday, email, address, days_to_birthday)

    def print_table(self):
        self.console.print(self.table)

'''эта часть кода отвечает за выполнение команд'''


class AssistantBot:
    def __init__(self) :
        self.console = Console()
        self.phone_book = AddressBook()
        if os.path.isfile(self.phone_book.file) :  # запуск файла с сохранеными контактами!!!
            self.phone_book.read_from_file()

    # вывод в таблицу rich
    def table_print(self, record: Record) :
        table = TableAction()
        phone_str = "\n".join(
            "; ".join(p.value for p in record.phones[i :i + 2]) for i in range(0, len(record.phones), 2))
        # {'; '.join(p.value for p in self.phones)}
        table.add_row(
            str(record.name.value),
            str(phone_str),
            str(record.birthday),
            str(record.email),
            str(record.address),
            str(record.days_to_birthday())
        )
        table.print_table()
        # return

    # отдельная функция по поиску рекорд, чтобы избежать ошибку с несущестующим контактом
    @input_error
    def find_record(self) :
        print('=' * 150)
        completer = WordCompleter(list(self.phone_book.keys()), ignore_case = True)
        name = prompt('Enter the name of an existing contact=> ', completer = completer)
        record: Record = self.phone_book.find(name)
        if record :
            return record

    # добавление нового контакта
    @input_error
    def add_contact(self) :
        name = input('Enter name=> ')
        record = Record(name)
        self.add_phone(record)
        self.add_birthday(record)
        self.add_email(record)
        self.add_address(record)
        self.phone_book.add_record(record)
        contact = self.table_print(record)
        self.phone_book.write_to_file()
        print(f'\033[92mYou have created a new contact:\033[0m')
        self.console.print(contact)
        return

    # добавление номера телефона
    @input_error
    def add_phone(self, record) :
        count_phone = 1
        while True :
            try :
                print(
                    f'\033[38;2;10;235;190mPlease enter the Phone Number {count_phone}, or press ENTER to skip.\033[0m')
                phone = input('Enter phone=> ')
                if phone :
                    record.add_phone(phone)
                    self.phone_book.add_record(record)
                    print(f'\033[38;2;10;235;190mThe phone number {phone} has been added.\033[0m')
                    count_phone += 1
                else :
                    return
            except ValueError as e :
                print(e)

    @input_error
    def add_phone_menu(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found.\033[0m')
                return
            self.add_phone(record)
            self.console.print(self.table_print(record))
            return

    # добавление даты дня рождения
    def add_birthday(self, record: Record) :
        while True :
            try :
                print(f'\033[38;2;10;235;190mEnter the date of birth or press ENTER to skip.\033[0m')
                birth = input('Enter date of birth. Correct format: YYYY.MM.DD=> ')
                if birth :
                    record.add_birthday(birth)
                    self.phone_book.add_record(record)
                    print(f'\033[38;2;10;235;190mThe date of birth {birth} has been added.\033[0m')
                    return
                else :
                    return
            except ValueError as e :
                print(e)

    @input_error
    def add_birthday_menu(self):
        while True:
            record = self.find_record()
            if not record:
                print('\033[91mThe contact was not found.\033[0m')
                return
            elif record.birthday is None:
                self.add_birthday(record)
                self.console.print(self.table_print(record))
                return
            else :
                print('\033[91mThis contact has date of birth.\033[0m')
                return

    # добаваление email
    @input_error
    def add_email(self, record: Record) :
        while True :
            try :
                print(f'\033[38;2;10;235;190mEnter the email or press ENTER to skip.\033[0m')
                email = input('Enter email=> ')
                if email :
                    record.add_email(email)
                    self.phone_book.add_record(record)
                    print(f'\033[38;2;10;235;190mThe email {email} has been added.\033[0m')
                    return
                else :
                    return
            except ValueError as e :
                print(e)

    @input_error
    def add_email_menu(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found.\033[0m')
                return
            elif record.email is None:
                self.add_email(record)
                self.console.print(self.table_print(record))
                return
            else :
                print('\033[91mThis contact has email.\033[0m')
                return

    # добавление адреса
    @input_error
    def add_address(self, record: Record) :
        print(f'\033[38;2;10;235;190mEnter your address or press ENTER to skip.\033[0m')
        address = input('Enter address=> ')
        if address :
            record.add_address(address)
            self.phone_book.add_record(record)
            print(f'\033[38;2;10;235;190mThe address {address} has been added.\033[0m')
            return
        else :
            return

    @input_error
    def add_address_menu(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found\033[0m')
                return
            elif record.address is None :
                self.add_address(record)
                self.console.print(self.table_print(record))
                return
            else :
                print('\033[91mThis contact has address.\033[0m')
                return

    # изменение телефона
    @input_error
    def edit_phone(self, record: Record) :
        old_phone = input('Enter the phone number you want to change=> ')
        new_phone = input('Enter the new phone number=> ')
        result = record.edit_phone(old_phone, new_phone)
        if result is None :
            print(f'\033[91mPhone: {old_phone} not found!\033[0m')
            return
        self.phone_book.add_record(record)
        print(f'\033[38;2;10;235;190mYou changed the contact:\n\033[0m')
        self.console.print(self.table_print(record))
        return

    @input_error
    def edit_phone_menu(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found.\033[0m')
                return
            self.console.print(self.table_print(record))
            self.edit_phone(record)
            return

    # изменение email
    @input_error
    def edit_email(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found.\033[0m')
                return
            self.add_email(record)
            self.phone_book.add_record(record)
            print(f'\033[38;2;10;235;190mYou changed the contact:\n\033[0m')
            self.console.print(self.table_print(record))
            return

    @input_error
    def edit_address(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found.\033[0m')
                return
            self.add_address(record)
            self.phone_book.add_record(record)
            print(f'\033[38;2;10;235;190mYou changed the contact:\n\033[0m')
            self.console.print(self.table_print(record))
            return

    # изменение имени
    @input_error
    def edit_name(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found.\033[0m')
                return
            new_name = input('Enter new name=> ')
            if new_name :
                old_name = record.name.value
                self.phone_book.data[new_name] = self.phone_book.data.pop(old_name)
                record.name.value = new_name
                self.phone_book.add_record(record)
                print(f'\033[38;2;10;235;190mName changed successfully from {old_name} to {new_name}.\n\033[0m')
                self.console.print(self.table_print(record))
                break
            else :
                break

    # изменение даты рождения
    @input_error
    def edit_birthday_menu(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found.\033[0m')
                return
            self.console.print(self.table_print(record))
            self.add_birthday(record)
            self.phone_book.add_record(record)
            print(f'\033[38;2;10;235;190mYou changed the contact:\n\033[0m')
            self.console.print(self.table_print(record))
            return

    # удаление номера
    @input_error
    def delete_phone(self, record: Record) :
        phone = input('Enter phone=> ')
        result = record.remove_phone(phone)
        print(f'\033[38;2;10;235;190mThe phone number {phone} was removed.\033[0m')
        return result

    @input_error
    def delete_phone_menu(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found.\033[0m')
                return
            self.console.print(self.table_print(record))
            self.delete_phone(record)
            self.phone_book.add_record(record)
            print(f'\033[38;2;10;235;190mYou changed the contact:\n.\033[0m')
            self.console.print(self.table_print(record))
            return

    # удаление даты рождения
    @input_error
    def delete_birthday_menu(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found.\033[0m')
                return
            record.birthday = None
            self.phone_book.add_record(record)
            print(f'\033[38;2;10;235;190mThe date of birth was removed.\033[0m')
            self.console.print(self.table_print(record))
            return

    # удаление email
    @input_error
    def delete_email_menu(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found.\033[0m')
                return
            record.email = None
            self.phone_book.add_record(record)
            print(f'\033[38;2;10;235;190mThe email was removed.\033[0m')
            self.console.print(self.table_print(record))
            return

    # удаление адреса
    @input_error
    def delete_address_menu(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found.\033[0m')
                return
            record.address = None
            self.phone_book.add_record(record)
            print(f'\033[38;2;10;235;190mThe address was removed.\033[0m')
            self.console.print(self.table_print(record))
            return

    # удаление контакта
    @input_error
    def delete_contact_menu(self) :
        while True :
            record = self.find_record()
            if not record :
                print('\033[91mThe contact was not found.\033[0m')
                return
            self.console.print(self.table_print(record))
            print(
                '\033[91mDo you really want to delete this contact? Please enter the number: 1.YES or press ENTER to skip.\033[0m')
            res = input('Enter your text=>  ').lower()
            if res in ('1', 'yes') :
                self.phone_book.delete(record.name.value)
                print(f'\033[38;2;10;235;190mThe contact {record.name.value} was removed.\033[0m')
                return
            else :
                return

    # поиск по имени и по совпадениям
    @input_error
    def search(self) :
        table = TableAction()
        while True :
            print('=' * 100)
            print(f'\033[38;2;10;235;190mEnter at least 3 letters or numbers to search or press ENTER to exit.\033[0m')
            res = input('Enter your text=>  ').lower()
            if res :
                result = self.phone_book.search(res).split('\n')
                if result :
                    for item in result :
                        record = item.split(',')
                        table.add_row(record[0], record[1], record[2], record[3], record[4], record[5])
                        table.print_table()
                print(f'\033[38;2;10;235;190mNo matches found.\033[0m')
            else :
                break

    # работа через интератор
    def show_all(self) :
        while True :
            table = TableAction()
            print('=' * 100)
            print(f'\033[38;2;10;235;190mEnter how many records to display or press ENTER to skip.\033[0m')
            item_number = input('Enter number=> ')
            if item_number.isdigit() :
                if self.phone_book :
                    # Введено число
                    item_number = int(item_number)
                    metka = 0
                    # phones = 'Contacts:\n'
                    iteration_count = 0
                    for name, record in self.phone_book.data.items() :
                        phone_str = "\n".join(
                            "; ".join(p.value for p in record.phones[i :i + 2]) for i in
                            range(0, len(record.phones), 2))
                        table.add_row(str(record.name.value),
                                      str(phone_str),
                                      str(record.birthday),
                                      str(record.email),
                                      str(record.address),
                                      str(record.days_to_birthday())
                                      )
                        table.hline = True  # добавить горизонтальные линии между строками
                        iteration_count += 1
                        metka = 1

                        if iteration_count % item_number == 0 :
                            table.print_table()
                            metka = 0
                            table = TableAction()
                    if metka == 1 :
                        table.print_table()
                    return
                else :
                    print(f'\033[91mNo contacts.\033[0m')
            elif item_number.isalpha() :
                # Введены буквы
                print(f'You entered letters: {item_number}')
            else :
                if self.phone_book :
                    for name, record in self.phone_book.data.items() :
                        phone_str = "\n".join(
                            "; ".join(p.value for p in record.phones[i :i + 2]) for i in
                            range(0, len(record.phones), 2))
                        table.add_row(str(record.name.value),
                                      str(phone_str),
                                      str(record.birthday),
                                      str(record.email),
                                      str(record.address),
                                      str(record.days_to_birthday())
                                      )
                    table.print_table()
                    return
                else :
                    print(f'\033[91mNo contacts.\033[0m')

    # выход из програмы и сохранение файла!
    def exit(self) :
        self.phone_book.write_to_file()
        return


if __name__ == "__main__" :
    pass
