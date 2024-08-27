import serial
import argparse

def send_and_recv(port, baudrate, command_list):
    # Configure the serial port
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.5
    )

    # Open the serial port
    if ser.isOpen():
        print(f"Serial port {ser.port} opened successfully")

    for command in command_list:
        # Send the text
        command = command + '\r'
        ser.write(command.encode('utf-8'))
        print(f"Sent: {command}")

        # Wait for a response
        response = ser.read(100)  # Reads up to 100 bytes or until timeout
        while response:
            resTxt = response.decode('utf-8')
            resCTxt = resTxt.replace('\r', '\n')
            print(resCTxt)
            response = ser.read(100)  # Reads up to 100 bytes or until timeout

    # Close the serial port
    ser.close()
    print("Serial port closed")

def get_filt_val(filt):
    # NR Band filters according to SC2430 Configuration and Control API
    # SCT-SW0A21vc
    filter_values = {
            'n39':0x0,
            'n34':0x1,
            'n40':0x2,
            'n41':0x3,
            'n38':0x4,
            'n78':0x5,
            'n48':0x6,
            'n77':0x7,
            'n79':0x8,
            'n46':0x9,
            'n47':0x9,
            'n96':0xa,
            'bypass':0xb
            }
    filt_key = 'n' + str(filt)
    # LSB 4 bits are used to select sub bands but it is set to 0 now
    u_filter_hex = filter_values[filt_key]
    filter_hex = hex(u_filter_hex << 4)
    print(filter_hex)
    return filter_hex

def configure_device(args):
    cmd_list = ['HW:SW 0 RX 3 0']
    cmd_list += ['HW:SW 0 TX 3 0']
    cmd_list += ['HW:SW 0 RX 0x1 0x01']
    cmd_list += [f'HW:GAIN 0 RX 0 {args.rxgain}']
    cmd_list += [f'HW:GAIN 0 TX 0 {args.txgain}']
    filthex = get_filt_val(args.band)
    cmd_list += [f'HW:FLT 0 RX 0x1 {filthex}']
    cmd_list += [f'HW:FLT 0 TX 0x2 {filthex}']
    print(cmd_list)

    send_and_recv(args.port, args.baudrate, cmd_list)

def read_configuration(args):
    cmd_list = ['HW:SW? 0 RX 0x1','HW:SW? 0 RX 0x3','HW:SW? 0 TX 0x3']
    cmd_list += ['HW:GAIN? 0 RX 0','HW:GAIN? 0 TX 0']
    cmd_list += ['HW:FLT? 0 RX 0x1','HW:FLT? 0 TX 0x2']
    print(cmd_list)
    send_and_recv(args.port, args.baudrate, cmd_list)

def gain_in_range(value):
    ivalue = int(value)
    if ivalue < -128 or ivalue > 127:
        raise argparse.ArgumentTypeError(f"{value} is out of range. Must be between -128 and 127.")
    return ivalue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parameters configure SC2430')
    parser.add_argument('-p', '--port', required=True, type=str)
    parser.add_argument('-b', '--baudrate', default=115200, type=int)
    parser.add_argument('-n', '--band', default=41, type=int, help='NR Band')
    parser.add_argument('-t', '--txgain', default=0, type=gain_in_range, help='Tx gain')
    parser.add_argument('-r', '--rxgain', default=0, type=gain_in_range, help='Rx gain')
    parser.add_argument('-m', '--readback', default=False, action='store_true')
    args = parser.parse_args()
    if args.readback:
        read_configuration(args)
    else:
        configure_device(args)

