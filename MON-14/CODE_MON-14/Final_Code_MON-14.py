import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
import time
import math

ssid = 'pbchandra mobile'
password = 'Pullabhotla'

# MCP3208 Configuration
spi = machine.SPI(0, sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))
cs_pin = machine.Pin(5, machine.Pin.OUT)
# Function to read analog values from MCP3208
def read_adc(channel):
    cs_pin.value(0)
    spi.write(bytearray([0x06 | ((channel & 0x07) >> 1), ((channel & 0x07) << 7), 0x00]))
    response = spi.read(3)
    cs_pin.value(1)
    value = ((response[0] & 0x0F) << 8) | response[1]
    return value

# Function to convert digital value to voltage
def convert_to_volts(value):
    print((((value* 4.89) / 4096.0)))
    return (((value* 4.89) / 4096.0)-1.89)

# Function to calculate RMS of analog values in volts
def calculate_rms_volts(values):
    sum_of_squares = sum([x*x for x in values])
    rms = math.sqrt(sum_of_squares/len(values))
    return rms

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(r1,r2,r3,r4):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            
            
            <p>ch1: {r1}</p>
            <p>ch2: {r2}</p>
            <p>ch3: {r3}</p>
            <p>ch4: {r4}</p>
            
            </body>
            </html>
            """
    return str(html)
def serve(connection):
    #Start a web server
    state1 ='on'
    state = 'OFF'
    pico_led.off()
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        a = [0 for x in range(4)]
    # Read analog values from MCP3208 channels
        analog_values = [read_adc(0), read_adc(1), read_adc(2), read_adc(3)]
    
    # Convert analog values to voltage
        voltage_values = [convert_to_volts(x) for x in analog_values]
    
    # Calculate RMS of each channel in volts
        for i in range(len(voltage_values)):
            a[i] = calculate_rms_volts([voltage_values[i]])
            #print(a[i])
        r1=str(a[0])
        r2=str(a[1])
        r3=str(a[2])
        r4=str(a[3])
        
        # Print RMS value of each channel in volts
        #print("RMS Value of Channel {} in Volts: {:.2f}".format(i, rms_value))
    
        time.sleep(1)

        
        html = webpage(r1,r2,r3,r4)
        client.send(html)
        client.close()
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
