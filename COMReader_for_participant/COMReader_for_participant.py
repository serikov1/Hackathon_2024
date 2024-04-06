import math
import struct
import keyboard
import serial
import os

USER_name = 'USER'

USER = serial.Serial(
    port="COM13", baudrate=115200, bytesize=8, timeout=100, stopbits=serial.STOPBITS_ONE
)

USER_data = f'{USER_name}_data'
serialStringUSER = ""
raw_string_USER = ""
raw_list_USER = [0] * 36
result_USER = [0] * 9
getUSER = 0

keyIsPressed = 0
main_dir = os.getcwd()
print('Ready to start, press r for getting data from your device')
while True:
    if keyboard.read_key() == 'r':
        keyIsPressed = 1
        USER.write(bytes('r', 'utf-8'))

    if keyboard.read_key() == 's':
        pass

    if USER.in_waiting > 0 and keyIsPressed and (not getUSER):
        serialStringUSER = USER.read(1)
        if serialStringUSER.hex(' ') == "02":
            serialStringUSER = USER.read(1)
            if serialStringUSER.hex(' ') == "00":
                serialStringUSER = USER.read(1)
                if serialStringUSER.hex(' ') == "a6":
                    serialStringUSER = USER.read(1)
                    if serialStringUSER.hex(' ') == "bd":
                        raw_string_USER = USER.read(36)
                        raw_list_USER = [elem - 256 if elem > 127 else elem for elem in list(raw_string_USER)]

                        for i in range(9):
                            result_USER[i] = struct.unpack('<f', struct.pack('4b', *raw_list_USER[4 * i: 4 + 4 * i]))[0]
                        if math.isnan not in result_USER:
                            print('Received data: \n')
                            print(result_USER)
                            getUSER = 1
                            USER.write(bytes('s', 'utf-8'))

    if getUSER:
        if not os.path.isdir(f'{USER_name}'):
            os.mkdir(f'{USER_name}')
        os.chdir(f'{USER_name}')
        with open(f'{USER_data}.txt', 'a') as fileUSER:
            for item in result_USER:
                fileUSER.write(str(item) + ' ')
            fileUSER.write('\n')
        getUSER = 0
    os.chdir(main_dir)
