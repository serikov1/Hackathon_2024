import keyboard

while True:
    if keyboard.read_key() == 'r':
        print('yes')
    if keyboard.read_key() == 's':
        print('no')
