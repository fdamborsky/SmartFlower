import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import spidev as SPI
from lib import LCD_1inch8
from PIL import Image, ImageDraw, ImageFont

i2c = busio.I2C(scl=3, sda=2)
ads = ADS.ADS1115(i2c)
ads.gain = 1 

lm35 = AnalogIn(ads, ADS.P0)
moisture = AnalogIn(ads, ADS.P1)
ldr = AnalogIn(ads, ADS.P2)

RST = 27
DC = 25
BL = 18
bus = 0
device = 0

disp = LCD_1inch8.LCD_1inch8(spi=SPI.SpiDev(bus, device), spi_freq=4000000, rst=RST, dc=DC, bl=BL)
disp.Init()
disp.clear()

font = ImageFont.load_default()

def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def read_sensors():
    lm35_val = lm35.value + 1500
    temp_c = (lm35_val * 0.00005) * 100 
    
    ldr_val = ldr.value
    ldr_percent = _map(ldr_val, 15000, 100, 0, 100)
    
    moisture_val = moisture.value
    moisture_percent = _map(moisture_val, 27500, 0, 100, 0)
    
    print(f"Teplota: {temp_c:.2f}°C")
    print(f"Světlo: {ldr_percent}%")
    print(f"Vlhkost: {moisture_percent}%")
    
    return temp_c, moisture_percent, ldr_percent

def update_display(temp, moisture, ldr):
    image = Image.new("RGB", (disp.width, disp.height), "BLACK")
    draw = ImageDraw.Draw(image)

    draw.text((10, 10), f"Teplota: {temp:.1f}°C", font=font, fill="WHITE")
    draw.text((10, 30), f"Vlhkost: {moisture}%", font=font, fill="WHITE")
    draw.text((10, 50), f"Svetlo: {ldr}%", font=font, fill="WHITE")

    image = image.rotate(180)
    disp.ShowImage(image)

def main():
    while True:
        temp, moisture, ldr = read_sensors()
        update_display(temp, moisture, ldr)
        time.sleep(3)

try:
    main()
except KeyboardInterrupt:
    disp.module_exit()
    print("Program ukončen.")
