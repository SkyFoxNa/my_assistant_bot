from datetime import date, datetime, timedelta
import re


class Field:
    def __init__(self, value) :
        self.__value = None
        self.value = value

    @property
    def value(self) :
        return self.__value

    @value.setter
    def value(self, value) :
        self.__value = value

    def __str__(self) :
        return str(self.__value)


class Name(Field):
    pass


class Address(Field) :
    @property
    def value(self) :
        return self.__value

    @value.setter
    def value(self, value: str) :
        self.__value = value

    def __str__(self) :
        return str(self.__value)


class Email(Field) :
    @property
    def value(self) :
        return self.__value

    @value.setter
    def value(self, value: str) :
        pattern = r"^[a-zA-Z0-9._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if (bool(re.search(pattern, value))) is False :
            raise ValueError('\033[91mInvalid email format.\033[0m')
        self.__value = value

    def __str__(self) :
        return str(self.__value)


class Birthday(Field):
    @property
    def value(self) :
        return self.__value

    @value.setter
    def value(self, value: str) :
        try :
            self.__value = datetime.strptime(value, '%Y.%m.%d').date()
        except ValueError :
            raise ValueError('\033[91mInvalid date format. Correct format: YYYY.MM.DD\033[0m')

    def __str__(self) :
        return self.__value.strftime('%Y.%m.%d')


class Phone(Field) :
    @property
    def value(self) :
        return self.__value

    @value.setter
    def value(self, value) :
        if len(value) != 10 or not value.isdigit() :
            raise ValueError('\033[91mThe phone number should be digits only and have 10 symbols.\033[0m')
        self.__value = value

    def __str__(self) :
        return (str(self.__value))

if __name__ == '__main__' :
    pass
