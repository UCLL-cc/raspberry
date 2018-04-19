import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)

TRIG = 16
ECHO = 18

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

print("Create connection")
client = mqtt.Client("Crowd control sensor 1")
client.username_pw_set("bjprbmwc", password="BjEbmRkVwazu")
client.connect("m23.cloudmqtt.com", port=17184, keepalive=600)
print("Connection created")

def on_disconnect(client, userdata, rc):
    time.sleep(2)
    client.reconnect()
client.on_disconnect = on_disconnect

GPIO.output(TRIG, False)
print("Waiting for sensor to settle")
time.sleep(2)
print("Started")


#Settings
activate_trigger = 0.8
deactivate_trigger = 0.9
trigger_buffer = 3
trigger_buffer_cutoff = 1       
wait = 0.05      
maxi_buffer = 20
#########


def avg(array):
    return sum(array) / len(array)


hit = False;
last_distances = [400] * maxi_buffer
def check(distance):
    global hit
    global last_distances
    
    last_distances = last_distances[1:] + [distance]

    average = avg(sorted(last_distances[-trigger_buffer:])[trigger_buffer_cutoff:-trigger_buffer_cutoff])
    maxi = max(last_distances)
    
    if not(hit) and average < activate_trigger * maxi:
        hit = True
        return True
    elif hit and average > deactivate_trigger * maxi:
        hit = False

    return False


def pulse():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)


people = 0
try:
    while True:
        pulse()
        
        start = time.time()
        while GPIO.input(ECHO) == 0:
            start = time.time()

        end = time.time()
        while GPIO.input(ECHO) == 1:
            end = time.time()

        pulse_duration = end - start

        distance = pulse_duration * 17150
        
        #print(round(distance, 2))

        if check(distance):
            people = people + 1
            print("% Someone passed by: #", people)
            client.publish("trigger", "")

        time.sleep(wait)  
except Exception as e:
    print(e)
    print("DONE")
    GPIO.cleanup()
except KeyboardInterrupt:
    print("DONE")
    GPIO.cleanup()
