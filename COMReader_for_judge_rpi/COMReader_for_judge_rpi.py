import math
import struct
import keyboard
import serial
import os

USER_name = 'FAKI'

CDMK = serial.Serial(
    port="/dev/ttyUSB0", baudrate=115200, bytesize=8, timeout=100, stopbits=serial.STOPBITS_ONE
)
USER = serial.Serial(
    port="/dev/ttyUSB1", baudrate=115200, bytesize=8, timeout=100, stopbits=serial.STOPBITS_ONE
)
CDMK_data = f'{USER_name}_CDMK_data'
USER_data = f'{USER_name}_data'
deviation_data = f'{USER_name}_deviation_result'

serialStringCDMK = ""
serialStringUSER = ""

raw_string_CDMK = ""
raw_string_USER = ""

var_list = ['Bx', 'By', 'Bz', 'gx', 'gy', 'gz', 'wx', 'wy', 'wz']

raw_list_CDMK = [0] * 144
raw_list_USER = [0] * 36

result_CDMK = [0] * 9
result_USER = [0] * 9
deviation_list = [0] * 9

getCDMK = 0
getUSER = 0

keyIsPressed = 0
amountOfNaN = 0
main_dir = os.getcwd()
print('Ready to start \n')

if not os.path.isdir(f'{USER_name}'):
    os.mkdir(f'{USER_name}')
os.chdir(f'{USER_name}')
with open(f'{USER_data}.txt', 'w') as fileUSER:
    pass
os.chdir(main_dir)

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
                            print(f'Data from {USER_name} group device: \n')
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

    if CDMK.in_waiting > 0 and (not getCDMK):
        while keyIsPressed:
            serialStringCDMK = CDMK.read(1)
            if serialStringCDMK.hex(' ') == "02":
                serialStringCDMK = CDMK.read(1)
                if serialStringCDMK.hex(' ') == "00":
                    serialStringCDMK = CDMK.read(1)
                    if serialStringCDMK.hex(' ') == "a6":
                        serialStringCDMK = CDMK.read(1)
                        if serialStringCDMK.hex(' ') == "bd":
                            raw_string_CDMK = CDMK.read(144)
                            raw_list_CDMK = [elem - 256 if elem > 127 else elem for elem in list(raw_string_CDMK)]

                            amountOfNaN = 0
                            for i in range(9):
                                result_CDMK[i] = struct.unpack('<f', struct.pack('4b', *raw_list_CDMK[60 + 4 * i: 64 + 4 * i]))[0]
                                if math.isnan(result_CDMK[i]) or abs(result_CDMK[i]) > 10000 or abs(result_CDMK[i]) < 0.000001:
                                    amountOfNaN += 1
                            if amountOfNaN == 0:
                                print('\nData from CDMK: \n')
                                print(result_CDMK)
                                getCDMK = 1
                                keyIsPressed = 0

    if getCDMK:
        if not os.path.isdir(f'{USER_name}'):
            os.mkdir(f'{USER_name}')
        os.chdir(f'{USER_name}')
        with open(f'{CDMK_data}.txt', 'a') as fileCDMK:
            for item in result_CDMK:
                fileCDMK.write(str(item) + ' ')
            fileCDMK.write('\n')
        getCDMK = 0

    with open(f'{deviation_data}.txt', 'w') as fDEV, open(f'{USER_data}.txt', 'r') as fUSER, open(f'{CDMK_data}.txt', 'r') as fCDMK:
        a1 = list(map(lambda x: float(x), fUSER.read().split()))
        a2 = list(map(lambda x: float(x), fCDMK.read().split()))
        result = list(map(lambda x, y: abs(abs(x) - abs(y)), a1, a2))
        counter = 0
        fDEV.write(f'RESULTS OF DEVIATION BETWEEN CDMK DATA AND DATA FROM {USER_name} GROUP DEVICE \n' + '\n')
        for item in var_list:
            fDEV.write('        ' + str(item) + '        ')
        fDEV.write('\n')
        for item in result:
            counter += 1
            fDEV.write(str(item) + ' ')
            if counter % 9 == 0:
                fDEV.write('\n')
        numOfCalc = counter / 9
        print(numOfCalc)
        for i in range(int(numOfCalc)):
            deviation_list[0] += result[9*i]
            deviation_list[1] += result[9*i+1]
            deviation_list[2] += result[9*i+2]
            deviation_list[3] += result[9*i+3]
            deviation_list[4] += result[9*i+4]
            deviation_list[5] += result[9*i+5]
            deviation_list[6] += result[9*i+6]
            deviation_list[7] += result[9*i+7]
            deviation_list[8] += result[9*i+8]
        print('\nDeviation between received data')
        print(deviation_list)
        deviation_list_res = [x / numOfCalc for x in deviation_list]
        deviation_list = [0] * 9
        fDEV.write('\n' + 'AVERAGE DEVIATION FOR COLUMNS RESULTS \n' + '\n')
        for item in var_list:
            fDEV.write('        ' + str(item) + '        ')
        fDEV.write('\n')
        for elem in deviation_list_res:
            fDEV.write(str(elem) + ' ')

        fDEV.write('\n \nAVERAGE DEVIATION FOR ALL RESULTS \n' + '\n')
        summ = 0
        for elem in deviation_list_res:
            summ += elem
        fDEV.write(str(summ/9))

    os.chdir(main_dir)

