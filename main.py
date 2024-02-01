# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,invalid-name,consider-using-f-string,line-too-long,redefined-outer-name,global-statement,eval-used

# created by shaples for the Bambu Lab X1 Carbon.
# -----------------------------------------------
# Licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International.
# https://creativecommons.org/licenses/by-nc-sa/4.0/
# -----------------------------------------------

import ssl
import random
import json
import time

import tkinter as tk
import tkinter.font as tkFont
import paho.mqtt.client as mqtt

light_state = bool

class MQTTClient:
    def __init__(self, broker_address, port, client_id, username, password, topic):
        self.client = mqtt.Client(client_id)
        self.client.username_pw_set(username, password)
        self.client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.client.on_connect = self.on_connect
        self.topic = topic
        self.client.connect(broker_address, port, 60)

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")

    def publish_message(self, message):
        result = self.client.publish(self.topic, message)
        status = result[0]
        if status == 0:
            print(f"Sent message to topic `{self.topic}`:\n\t{str(message)}\n")
        else:
            print(f"Failed to send message to topic `{self.topic}`")

    def start_loop(self):
        self.client.loop_start()

    def stop_loop(self):
        self.client.loop_stop()

    class commands:
        def arbitrary_gcode(self, gcode):
            return json.dumps({"print": {"command": "gcode_line", "param": (gcode + " \n"), "sequence_id": "0"}})

        toolhead_logo_on = json.dumps({"print": {"command": "gcode_line", "param": "M960 S5 P1 \n", "sequence_id": "0"}})
        toolhead_logo_off = json.dumps({"print": {"command": "gcode_line", "param": "M960 S5 P0 \n", "sequence_id": "0"}})

        chamber_light_on = json.dumps({"system": {"sequence_id": "0", "command": "ledctrl", "led_node": "chamber_light", "led_mode": "on", "led_on_time": 500, "led_off_time": 500, "loop_times": 0, "interval_time": 0}})
        chamber_light_off = json.dumps({"system": {"sequence_id": "0", "command": "ledctrl", "led_node": "chamber_light", "led_mode": "off", "led_on_time": 500, "led_off_time": 500, "loop_times": 0, "interval_time": 0}})

        scanner_light_on = json.dumps({"print": {"command": "gcode_line", "param": "M960 S0 P1 \n", "sequence_id": "0"}})
        scanner_light_off = json.dumps({"print": {"command": "gcode_line", "param": "M960 S0 P0 \n", "sequence_id": "0"}})


class App:
    def __init__(self, root):
        root.title(" BambuControl")
        width=269
        height=217
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        # arbitrary gcode execution
        arb_gcode_entry=tk.Entry(root)
        self.arb_gcode_entry_text = tk.StringVar()
        arb_gcode_entry["borderwidth"] = "1px"
        arb_gcode_entry["cursor"] = "arrow"
        ft = tkFont.Font(family='Times',size=10)
        arb_gcode_entry["font"] = ft
        arb_gcode_entry["fg"] = "#333333"
        arb_gcode_entry["justify"] = "left"
        arb_gcode_entry["text"] = "Enter GCODE command..."
        arb_gcode_entry.place(x=20,y=170,width=135,height=30)
        arb_gcode_entry["textvariable"] = self.arb_gcode_entry_text

        arb_gcode_send_button=tk.Button(root)
        arb_gcode_send_button["bg"] = "#f0f0f0"
        arb_gcode_send_button["cursor"] = "arrow"
        ft = tkFont.Font(family='Times',size=10)
        arb_gcode_send_button["font"] = ft
        arb_gcode_send_button["fg"] = "#000000"
        arb_gcode_send_button["justify"] = "center"
        arb_gcode_send_button["text"] = "Send"
        arb_gcode_send_button.place(x=170,y=170,width=70,height=30)
        arb_gcode_send_button["command"] = self.arb_gcode_send_button_command

        toolhead_logo_light_on_button=tk.Button(root)
        toolhead_logo_light_on_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        toolhead_logo_light_on_button["font"] = ft
        toolhead_logo_light_on_button["fg"] = "#000000"
        toolhead_logo_light_on_button["justify"] = "center"
        toolhead_logo_light_on_button["text"] = "On"
        toolhead_logo_light_on_button.place(x=160,y=50,width=30,height=30)
        toolhead_logo_light_on_button["command"] = self.toolhead_logo_light_on_button_command

        toolhead_logo_light_label=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        toolhead_logo_light_label["font"] = ft
        toolhead_logo_light_label["fg"] = "#333333"
        toolhead_logo_light_label["justify"] = "right"
        toolhead_logo_light_label["text"] = "Toolhead Logo Light"
        toolhead_logo_light_label.place(x=10,y=50,width=124,height=31)

        toolhead_logo_light_off_button=tk.Button(root)
        toolhead_logo_light_off_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        toolhead_logo_light_off_button["font"] = ft
        toolhead_logo_light_off_button["fg"] = "#000000"
        toolhead_logo_light_off_button["justify"] = "center"
        toolhead_logo_light_off_button["text"] = "Off"
        toolhead_logo_light_off_button.place(x=210,y=50,width=30,height=30)
        toolhead_logo_light_off_button["command"] = self.toolhead_logo_light_off_button_command

        chamber_light_label=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        chamber_light_label["font"] = ft
        chamber_light_label["fg"] = "#333333"
        chamber_light_label["justify"] = "right"
        chamber_light_label["text"] = "Chamber Light"
        chamber_light_label.place(x=40,y=10,width=93,height=30)

        chamber_light_on_button=tk.Button(root)
        chamber_light_on_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        chamber_light_on_button["font"] = ft
        chamber_light_on_button["fg"] = "#000000"
        chamber_light_on_button["justify"] = "center"
        chamber_light_on_button["text"] = "On"
        chamber_light_on_button.place(x=160,y=10,width=30,height=30)
        chamber_light_on_button["command"] = self.chamber_light_on_button_command

        chamber_light_off_button=tk.Button(root)
        chamber_light_off_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        chamber_light_off_button["font"] = ft
        chamber_light_off_button["fg"] = "#000000"
        chamber_light_off_button["justify"] = "center"
        chamber_light_off_button["text"] = "Off"
        chamber_light_off_button.place(x=210,y=10,width=30,height=30)
        chamber_light_off_button["command"] = self.chamber_light_off_button_command

        scanner_light_label=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        scanner_light_label["font"] = ft
        scanner_light_label["fg"] = "#333333"
        scanner_light_label["justify"] = "right"
        scanner_light_label["text"] = "Scanner LED (X1)"
        scanner_light_label.place(x=30,y=90,width=104,height=30)

        scanner_light_on_button=tk.Button(root)
        scanner_light_on_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        scanner_light_on_button["font"] = ft
        scanner_light_on_button["fg"] = "#000000"
        scanner_light_on_button["justify"] = "center"
        scanner_light_on_button["text"] = "On"
        scanner_light_on_button.place(x=160,y=90,width=30,height=30)
        scanner_light_on_button["command"] = self.scanner_light_on_button_command

        scanner_light_off_button=tk.Button(root)
        scanner_light_off_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        scanner_light_off_button["font"] = ft
        scanner_light_off_button["fg"] = "#000000"
        scanner_light_off_button["justify"] = "center"
        scanner_light_off_button["text"] = "Off"
        scanner_light_off_button.place(x=210,y=90,width=30,height=30)
        scanner_light_off_button["command"] = self.scanner_light_off_button_command
        
        all_lights_on_button=tk.Button(root)
        all_lights_on_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        all_lights_on_button["font"] = ft
        all_lights_on_button["fg"] = "#000000"
        all_lights_on_button["justify"] = "center"
        all_lights_on_button["text"] = "All On"
        all_lights_on_button.place(x=50,y=130,width=70,height=25)
        all_lights_on_button["command"] = self.all_lights_on_button_command

        all_lights_off_button=tk.Button(root)
        all_lights_off_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        all_lights_off_button["font"] = ft
        all_lights_off_button["fg"] = "#000000"
        all_lights_off_button["justify"] = "center"
        all_lights_off_button["text"] = "All Off"
        all_lights_off_button.place(x=160,y=130,width=70,height=25)
        all_lights_off_button["command"] = self.all_lights_off_button_command

        self.mqtt_client = MQTTClient(
                    broker_address='PUT_PRINTER_IP_HERE',
                    port=8883,
                    client_id=f'python-mqtt-{random.randint(0, 1000)}',
                    username='bblp',
                    password='PUT_LAN_ACCESS_CODE_HERE',
                    topic='device/PUT_PRINTER_SERIAL_HERE/request'
                )
        self.mqtt_client.start_loop()

    def arb_gcode_send_button_command(self):
        entered_text = self.arb_gcode_entry_text.get()
        print('\nsending arbitrary gcode:\n\t' + entered_text)
        self.mqtt_client.publish_message(MQTTClient.commands.arbitrary_gcode(MQTTClient, entered_text))

    def toolhead_logo_light_on_button_command(self):
        print('\nturning on toolhead logo light')
        self.mqtt_client.publish_message(MQTTClient.commands.toolhead_logo_on)

    def toolhead_logo_light_off_button_command(self):
        print('\nturning off toolhead logo light')
        self.mqtt_client.publish_message(MQTTClient.commands.toolhead_logo_off)

    def chamber_light_on_button_command(self):
        print('\nturning on chamber light')
        self.mqtt_client.publish_message(MQTTClient.commands.chamber_light_on)

    def chamber_light_off_button_command(self):
        print('\nturning off chamber light')
        self.mqtt_client.publish_message(MQTTClient.commands.chamber_light_off)

    def scanner_light_on_button_command(self):
        print('\nturning on scanner light')
        self.mqtt_client.publish_message(MQTTClient.commands.scanner_light_on)

    def scanner_light_off_button_command(self):
        print('\nturning off scanner light')
        self.mqtt_client.publish_message(MQTTClient.commands.scanner_light_off)

    def all_lights_on_button_command(self):
        for command in dir(MQTTClient.commands):
            if command.endswith('_on'):
                self.mqtt_client.publish_message(eval('MQTTClient.commands.' + command))
                time.sleep(0.05)

    def all_lights_off_button_command(self):
        for command in dir(MQTTClient.commands):
            if command.endswith('_off'):
                self.mqtt_client.publish_message(eval('MQTTClient.commands.' + command))
                time.sleep(0.005)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    print('exiting...')
            
