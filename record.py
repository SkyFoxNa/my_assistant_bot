from field import Name, Phone, Email, Address, Birthday
from datetime import date, datetime, timedelta


class Record:
    def __init__(self, name: str) :
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.email = None
        self.address = None

    def add_phone(self, value: str) :
        phone = Phone(value)
        self.phones.append(phone)

    def add_email(self, value: str) :
        self.email = Email(value)

    def add_address(self, value: str) :
        self.address = Address(value)

    def add_birthday(self, birthday: str) :
        self.birthday = Birthday(birthday)

    def remove_phone(self, phone: str) :
        for item in self.phones :
            if item.value == phone :
                self.phones.remove(item)
                return f'The phone number: {phone} has been deleted.'
        return f'The phone number {phone} not found.'

    def edit_phone(self, old_phone: str, new_phone: str) :
        for phone in self.phones :
            if phone.value == old_phone :
                phone.value = new_phone
                return f'Phones: {"; ".join(p.value for p in self.phones)}'
        return None

    def find_phone(self, phone: str) :
        for item in self.phones :
            if item.value == phone :
                return item
        return None

    #  показывает сколько дней до дня рождения
    def days_to_birthday(self) :
        if self.birthday is None :
            return None
        date_today = date.today()
        birthday_date = self.birthday.value.replace(year = date_today.year)
        if date_today == birthday_date :
            return 'Birthday today'
        if birthday_date <= date_today - timedelta(days = 1) :
            birthday_date = birthday_date.replace(year = date_today.year + 1)
        day_to_birthday = (birthday_date - date_today).days
        return day_to_birthday

    def __str__(self) :

        return f'{self.name.value}, {"; ".join(p.value for p in self.phones)}, {self.birthday}, {self.email}, {self.address}, {self.days_to_birthday()}'


if __name__ == '__main__' :
    pass
