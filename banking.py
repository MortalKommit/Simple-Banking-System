import random
import sqlite3

conn = sqlite3.connect("card.s3db")
random.seed()
cur = conn.cursor()


class Card:
    def __init__(self):
        """
        Generate card number and pin number
        """
        card_digits = str(400000000000000 + random.randrange(0, 1000000000))
        self.card_number = card_digits + gen_luhn_sum(card_digits)
        self.pin_number = str(random.randrange(0, 10000))
        self.balance = 0

    def __str__(self):
        return f"Your card number:\n{self.card_number}\nYour card PIN:\n{self.pin_number.zfill(4)}"

    def get_balance(self):
        return self.balance

    def add_income(self, amt):
        self.balance += amt


def gen_luhn_sum(number):
    """
    generates luhn algorithm checksum
    :param number: number to be checked
    :return: checksum digit (string)
    """
    chk_sum = 0
    # Count only 2nd digits from end of number
    for i, digit in enumerate(map(int, reversed(number))):
        if not i % 2:
            if digit * 2 < 9:
                chk_sum += digit * 2
            else:
                chk_sum += digit * 2 - 9
        else:
            chk_sum += digit

    return str(9 * chk_sum % 10)


def transfer_amt(card_sender, card_receiver, amt):
    if amt > cur.execute("SELECT balance FROM card WHERE number = ?", (card_sender,)).fetchone()[0]:
        print('Not enough money!')
        return
    try:
        cur.execute("UPDATE card SET balance = balance - ? WHERE number = ?", (amt, card_sender))
        cur.execute("UPDATE card SET balance = balance + ? WHERE number = ?", (amt, card_receiver))
        conn.commit()
        print('Success')
    except ValueError:
        print("Error occurred while writing to DB")


def card_login(card_number, pin_number):
    if (card_number, pin_number) not in conn.execute("SELECT number, pin FROM card").fetchall():
        print("Wrong card number or PIN!")
    else:
        print("You have successfully logged in!\n")
        sub_option = ""
        while sub_option not in ("0", "4", "5"):
            sub_option = input("1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log "
                               "out\n0. Exit\n")
            if sub_option == "1":
                balance_query = conn.execute("SELECT balance FROM card WHERE number = ?",
                                             (card_number,)).fetchone()[0]
                print(f"Balance : {balance_query}")
            elif sub_option == "2":
                deposit_amt = input("Enter income:")
                try:
                    deposit_amt = float(deposit_amt)

                    conn.execute('UPDATE card SET balance = balance + ? WHERE number = ?',
                                 (deposit_amt, card_number))
                    conn.commit()
                    if deposit_amt <= 0:
                        raise ValueError("Invalid deposit amount!")
                except ValueError as ve:
                    print(ve, "Please enter a positive number!")
            elif sub_option == "3":
                transfer_acct = input("Transfer\nEnter card number:")

                if gen_luhn_sum(transfer_acct[:-1]) == transfer_acct[-1]:
                    if (transfer_acct,) not in cur.execute("SELECT number FROM card").fetchall():
                        print("Such a card does not exist.")
                    else:
                        try:
                            amount = float(input("Enter transfer amount:"))
                            if amount <= 0:
                                raise ValueError("Invalid transfer amount!")
                            transfer_amt(card_sender=card_number, card_receiver=transfer_acct, amt=amount)
                        except ValueError as ve:
                            print(ve, 'Please enter a valid positive number!')
                else:
                    print("You probably made a mistake in the card number. Please try again!")

            elif sub_option == "4":
                conn.execute("DELETE FROM card WHERE number=?", (card_number,))
                conn.commit()
                print("Your account has been deleted!\n")
                break
            if sub_option == "0":
                exit()


def card_banking():
    """
    Entry point to other functions, card generation, transfer, balance inquiry
    :return: None
    """
    option = ""
    card_id = 0

    cur.execute('''DROP TABLE IF EXISTS card ''')

    cur.execute('''CREATE TABLE card(
                   id INTEGER,
                   number TEXT,
                   pin TEXT,
                   balance INTEGER DEFAULT 0)''')
    conn.commit()
    while option != "0":
        option = input('''1. Create an account\n2. Log into account\n0. Exit\n''')

        if option == "1":
            new_card = Card()
            card_id += 1
            print("Your card has been created\n", new_card)
            conn.execute("INSERT INTO card(id, number, pin) values (?, ?, ?) ",
                         (card_id, new_card.card_number, new_card.pin_number.zfill(4)))
            conn.commit()

        elif option == "2":
            if conn.execute("SELECT COUNT(*) FROM card").fetchone()[0] <= 0:
                print("No cards exist!")
            else:
                card_number = input("Enter your card number:\n")
                pin_number = input("Enter your PIN:\n")
                card_login(card_number, pin_number)


if __name__ == "__main__":
    card_banking()
    print("\nBye!")
    cur.close()
    conn.close()
