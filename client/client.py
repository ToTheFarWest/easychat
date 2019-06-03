from framework import EasyChat
from datetime import datetime

def display_menu():
    print("EasyChat Alpha\n")

def register(app):
    username = raw_input("Username: ")
    password = raw_input('Password: ')
    confirm_password = raw_input('Confirm Password: ')
    if password != confirm_password:
        print('Passwords did not match, try again!')
        register(app)
    r = app.register(username, password)
    if not r:
        print('Something went wrong, try again')
        register(app)

def login(app):
    username = raw_input("Username: ")
    password = raw_input('Password: ') 
    r = app.login(username, password)
    if not r:
        print('Incorrect username or password')
        login(app)

def get_all_users(app):
    users = app.get_all_users()
    if not users:
        print('Something has gone wrong! Try again later')
        return
    for u in users:
        print('Username: ' + u['username'])

def send_message(app):
    print('Who do you want to message?')
    username = raw_input()
    u_id = app.get_user_id(username)
    message = raw_input('Enter message: ')
    m = app.send_message(u_id, message)
    if not m:
        print('Something has gone wrong! Is that username correct?')
    else:
        print(m['content'])

def get_messages_from_user(app):
    print('Which conversation would you like to view?')
    username = raw_input()
    u_id = app.get_user_id(username)
    messages = app.get_messages_from_user(u_id)
    for m in messages:
        sender = username if m['sender'] == u_id else 'You'
        print(sender + ': '  + m['content'])
    
def handle_choice(app, choice):
    switcher = {
        '1': get_all_users,
        '2': send_message,
        '3': get_messages_from_user
    }

    return switcher[choice](app)

#Event Loop
def main():
    app = EasyChat('http://127.0.0.1:5000/')
    while True:
        if app.token == '':
            print('You are not signed in!')
            print('Press 1 to register new user, or 2 to login')
            choice = input()
            if choice == 1:
                register(app)
            elif choice == 2:
                login(app)
            else:
                'Invalid choice, try again'
        display_menu()
        choice = raw_input()
        handle_choice(app, choice)

if __name__ == '__main__':
    main()