import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time

def create_mcp() :
    spi=busio.SPI(clock=board.SCK,MISO=board.MISO,MOSI=board.MOSI)
    cs=digitalio.DigitalInOut(board.D5)
    mcp=MCP.MCP3008(spi,cs)
    channel=AnalogIn(mcp,MCP.P0)
    return channel

my_mcp=create_mcp()

while True :
    value=(my_mcp.value/65472)*100
    print(value)
    time.sleep(0.1)