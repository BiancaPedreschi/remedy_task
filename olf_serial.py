# -*- coding: utf-8 -*-

# Importing Libraries
import serial
import threading

ser = None


def _reader():
    try:
        while True:
            try:
                data = ser.readline()
                msg = str(data, "utf-8").strip()

                # questo è un esempio della tipologia dei messaggi che puou ricevere
                if msg == "Lost connection":
                    break
                else:
                    if msg.find("ERROR") != -1:
                        print(msg)
                    elif msg.find("WARM") != -1:
                        print(msg)
                    else:
                        print(msg)

            except Exception as en:
                print(en)
                pass

    except Exception as e:
        print(e)
        print("Lost connection!")


def write(data):
    if ser:
        return 0

    try:
        if isinstance(data, str):
            data = bytes(data, "utf-8")
        ser.write(data)
        return 1
    except Exception as e:
        print(e)
        return 0



# if __name__ == '__main__':
try:
    #ser = serial.Serial(port="tty.usbmodem20220051", baudrate=115200)#(port="COM6", baudrate=115200)
    ser = serial.Serial('/dev/ttyACM0', 9600) #ultima versione


    if ser.isOpen():
        print("Opened Serial Port")
        thw = threading.Thread(None, target=_reader)
        thw.start()

    else:
        pass

# except print('Error')
except serial.SerialException as se:
    print("Monitor: Disconnected (Serial exception)")
except IOError:
    print("Monitor: Disconnected (I/O Error)")
except ValueError as ve:
    print(ve)

write('C M;;;;;;;')  # Setting olfactometer configuration to manual - 1/0 only is proof?
write('E 1')
write ('S 1')