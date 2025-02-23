print("Hello World")

values=[0]*41

BOARD="GPIO.BOARD"
BCM="GPIO.BCM"
RISING="GPIO.RISING"
IN='GPIO.IN'
OUT="GPIO.OUT"
PUD_DOWN="GPIO.PUD_DOWN"
debug_mode=False

def add_event_detect(arg1=None,arg2=None,arg3=None,arg4=None,arg5=None,debug=debug_mode) :
    None
    if debug_mode :
        print(f"Function GPIO.add_event_detect called with arguments :")
        print(f"arg1 : {arg1}")
        print(f"arg2 : {arg2}")
        print(f"arg3 : {arg3}")
        print(f"arg4 : {arg4}")
        print(f"arg5 : {arg5}")

def set_value(num,value) :
    values[num]=value

def setmode(arg1=None,debug=debug_mode) :
    None
    if debug_mode :
        print(f"Function GPIO.setmode called with arguments :")
        print(f"arg1 : {arg1}")

def setup(arg1=None,arg2=None,arg3=None,arg4=None,arg5=None,debug=debug_mode) :
    None
    if debug_mode :
        print(f"Function GPIO.setup called with arguments :")
        print(f"arg1 : {arg1}")
        print(f"arg2 : {arg2}")
        print(f"arg3 : {arg3}")
        print(f"arg4 : {arg4}")
        print(f"arg5 : {arg5}")

def output(arg1=None,arg2=None,arg3=None,arg4=None,arg5=None,debug=debug_mode) :
    None
    if debug_mode :
        print(f"Function GPIO.output called with arguments :")
        print(f"arg1 : {arg1}")
        print(f"arg2 : {arg2}")
        print(f"arg3 : {arg3}")
        print(f"arg4 : {arg4}")
        print(f"arg5 : {arg5}")

def input(arg1,arg2=None,arg3=None,arg4=None,arg5=None,debug=debug_mode,values=values) :
    None
    if debug_mode :
        print(f"Function GPIO.input called with arguments :")
        print(f"arg1 : {arg1}")
        print(f"arg2 : {arg2}")
        print(f"arg3 : {arg3}")
        print(f"arg4 : {arg4}")
        print(f"arg5 : {arg5}")
    return values[arg1]
