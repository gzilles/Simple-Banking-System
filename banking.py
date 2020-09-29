import sqlite3
from random import randint


def create_card_number():
    can = ""
    inn = "400000"
    for i in range(9):
        can += str(randint(0, 9))
    return inn + can + checksum(inn + can)


def create_pin():
    client_pin = ""
    for i in range(4):
        client_pin += str(randint(0, 9))
    return client_pin


def checksum(card_number):
    odd = 1
    sum = 0
    for char in card_number:
        char = int(char)
        if odd % 2 != 0:
            char *= 2
            if char > 9:
                char -= 9
        odd += 1
        sum += char
    return "0" if sum % 10 == 0 else str(10 - sum % 10)


def create_db():
    conn = sqlite3.connect('card.s3db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS
              card
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              number TEXT UNIQUE NOT NULL,
              pin TEXT NOT NULL,
              balance INTEGER DEFAULT 0)''')
    conn.commit()
    c.close()
    conn.close()


def insert_data(card_number, pin_number):
    conn = sqlite3.connect('card.s3db')
    c = conn.cursor()
    c.execute("INSERT INTO card (number, pin) VALUES (?,?)", (card_number, pin_number))
    last_id = c.lastrowid
    conn.commit()
    c.close()
    conn.close()
    return last_id


def update_data(id_number, new_balance):
    conn = sqlite3.connect('card.s3db')
    c = conn.cursor()
    c.execute("UPDATE card SET balance = ? WHERE id = ?", (new_balance, id_number))
    conn.commit()
    c.close()
    conn.close()


def delete_data(id_number):
    conn = sqlite3.connect('card.s3db')
    c = conn.cursor()
    c.execute("DELETE FROM card WHERE id = ?", (id_number,))
    conn.commit()
    c.close()
    conn.close()


def select_id_data(id):
    conn = sqlite3.connect('card.s3db')
    c = conn.cursor()
    c.execute("SELECT * FROM card WHERE id = ?", (id,))
    data = c.fetchone()
    conn.commit()
    c.close()
    conn.close()
    return data


def select_card_data(card_number):
    conn = sqlite3.connect('card.s3db')
    c = conn.cursor()
    c.execute("SELECT * FROM card WHERE number = ?", (card_number,))
    data = c.fetchone()
    conn.commit()
    c.close()
    conn.close()
    return data


def select_data(card_number, pin_number):
    conn = sqlite3.connect('card.s3db')
    c = conn.cursor()
    c.execute("SELECT * FROM card WHERE number = ? and pin = ?", (card_number, pin_number))
    data = c.fetchone()
    conn.commit()
    c.close()
    conn.close()
    return data


def menu():
    index = True
    while index:
        print('\n1. Create an account\n2. Log into account\n0. Exit')
        user_input = int(input('> '))
        if user_input == 1:
            last_id = insert_data(create_card_number(), create_pin())
            print('Your card has been created\nYour card number:\n{}'.format(str(select_id_data(last_id)[1])))
            print('Your card PIN:\n{}'.format(select_id_data(last_id)[2]))
        elif user_input == 2:
            number_input = input('\nEnter your card number: ')
            # if checksum(number_input[0:15]) == number_input[15:]:
            pin_input = input('Enter your PIN: ')
            if select_data(number_input, pin_input):
                user_id = select_data(number_input, pin_input)[0]
                print('\nYou have successfully logged in!')
                while index:
                    print('\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
                    user_input = int(input('> '))
                    if user_input == 1:
                        print('\nBalance = {}'.format(select_id_data(user_id)[3]))
                    elif user_input == 2:
                        income = int(input('\nEnter income: '))
                        update_data(user_id, select_id_data(user_id)[3] + income)
                        print('\nIncome was added!')
                    elif user_input == 3:
                        transfer_card = input('\nTransfer\nEnter card number: ')
                        if checksum(transfer_card[0:15]) != transfer_card[15:]:
                            print('Probably you made a mistake in the card number. Please try again!')
                        elif not select_card_data(transfer_card):
                            print('Such a card does not exist.')
                        elif transfer_card == number_input:
                            print("You can't transfer money to the same account!")
                        else:
                            transfer_value = int(input('Enter how much money you want to transfer: '))
                            if transfer_value <= select_id_data(user_id)[3]:
                                update_data(user_id, select_id_data(user_id)[3] - transfer_value)
                                update_data(select_card_data(transfer_card)[0],
                                            select_card_data(transfer_card)[3] + transfer_value)
                                print('Success!')
                            else:
                                print('Not enough money!')
                    elif user_input == 4:
                        delete_data(user_id)
                        print('The account has been closed!')
                        break
                    elif user_input == 5:
                        print("\nYou have successfully logged out!")
                        break
                    else:
                        index = False
            else:
                print('\nWrong card number or PIN!')
        # else:
        #     print('Probably you made a mistake in the card number. Please try again!')
        else:
            index = False


create_db()
menu()