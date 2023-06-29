'''
    BLE Monitor.
'''

##t
import subprocess, device_registry, parameters, ble_scanner, time, datetime, network_data
import socket, fcntl, struct, log_error
import sys, os 
from threading import Thread
import board
import adafruit_dht
import time
import sys, json
import serial
import psutil
# for error logging 
logger = log_error.logger

# frequency seconds 
frequency_to_update_list = parameters.get_freq_update_list()  # 5 mins
frequency_to_send_to_cloud = parameters.get_freq_send_to_cloud()   # 2 min 
frequency_to_environment_to_send_to_cloud = parameters.get_freq_temp_send_to_cloud()   # 2 min 
frequency_config_reset = parameters.get_config_set_frequency()   # 2 min 
refresh_interval = 300  # 2 min 
scan_frequency = parameters.get_freq_scan()   # 2 min 
dht_pin = 4
send_now = False
frequency_reset_ble_attempts = parameters.get_freq_reset_ble_attempts() 
ble_limit_failures = parameters.get_freq_reset_ble_limit_failures()
adapter_type = "lan"


def app_init():
    json_file_path = []
    proceed = False
    global adapter_type
    global frequency_to_update_list
    global frequency_to_send_to_cloud
    global frequency_to_environment_to_send_to_cloud
    global frequency_config_reset
    global refresh_interval
    global scan_frequency
    global dht_pin
    global send_now
    global frequency_reset_ble_attempts
    global ble_limit_failures
    global adapter_type
    try :
        pi_mac = network_data.read_mac_address_lan()
        # set the file path
        logger.debug("getting config list on lan {}".format(pi_mac))
        dev_list = device_registry.config_list(pi_mac)
        if dev_list.status_code == 200:
            logger.debug("updating ip lan")
            device_registry.update_ip(pi_mac, "lan")
            dev_list = dev_list.json()
            frequency_to_send_to_cloud = dev_list['movementFrequency']
            frequency_to_environment_to_send_to_cloud = dev_list['tempHumidityFrequency']
            frequency_to_update_list = dev_list['hubWorkPointListUpdate']
            frequency_config_reset = dev_list['configResetFrequency']
            scan_frequency = dev_list['hubScanFrequency']
            frequency_reset_ble_attempts = dev_list['hubResetAttempts']
            ble_limit_failures = dev_list['hubFailureLimitFailures']
            refresh_interval = dev_list['refreshInterval']
            adapter_type = "lan"
            logger.debug("adapter: {}".format(adapter_type))
            proceed = True

    except Exception as e:
        try:
            # define function to run with Thread 
            def error_api():
                log_error.pub_error(mac_dev, ip_dev, e)

            # instance thread class and call it 
            t = Thread(target=error_api)
            t.start()
            logger.error(e)
            logger.error("not able to load device list, check network configuration")
            # log_error.pub_error(mac_dev, ip_dev, e)
        except Exception as e:
            logger.error(e)
            logger.error("not able to send error message to the API")
            logger.error("not able to load device list, check network configuration")
        return []
    if proceed == False:
        try :
            pi_mac = network_data.read_mac_address_wifi()
            # set the file path
            logger.debug("getting config list on wifi {}".format(pi_mac))
            dev_list = device_registry.config_list(pi_mac)
            if dev_list.status_code == 200:
                logger.debug("updating ip wifi")
                device_registry.update_ip(pi_mac, "wifi")
                dev_list = dev_list.json()
                frequency_to_send_to_cloud = dev_list['movementFrequency']
                frequency_to_environment_to_send_to_cloud = dev_list['tempHumidityFrequency']
                frequency_to_update_list = dev_list['hubWorkPointListUpdate']
                frequency_config_reset = dev_list['configResetFrequency']
                scan_frequency = dev_list['hubScanFrequency']
                frequency_reset_ble_attempts = dev_list['hubResetAttempts']
                ble_limit_failures = dev_list['hubFailureLimitFailures']
                refresh_interval = dev_list['refreshInterval']
                adapter_type = "wifi"
                logger.debug("adapter: {}".format(adapter_type))
                proceed = True

        except Exception as e:
            try:
                # define function to run with Thread 
                def error_api():
                    log_error.pub_error(mac_dev, ip_dev, e)

                # instance thread class and call it 
                t = Thread(target=error_api)
                t.start()
                logger.error(e)
                logger.error("not able to load device list, check network configuration")
                # log_error.pub_error(mac_dev, ip_dev, e)
            except Exception as e:
                logger.error(e)
                logger.error("not able to send error message to the API")
                logger.error("not able to load device list, check network configuration")
            return []

    if proceed == True:
        return True
    return False

# main process 
def main():
    global adapter_type
    global frequency_to_update_list
    global frequency_to_send_to_cloud
    global frequency_to_environment_to_send_to_cloud
    global frequency_config_reset
    global refresh_interval
    global scan_frequency
    global dht_pin
    global send_now
    global frequency_reset_ble_attempts
    global ble_limit_failures
    global adapter_type
    try:
        
        # counter for ble exceptions
        ble_attempts = 0
        ble_last_check = time.time() 
        config_last_check = time.time() 

        # starting application with a debug message
        logger.debug("app initializing")

        # get ip address 
        proceed = app_init()

        if proceed == True:
            logger.debug("hello, starting application with adapter: {}".format(adapter_type))
            logger.debug("scan frequency: {}".format(scan_frequency))
            logger.debug("cloud sending frequency: {}".format(frequency_to_send_to_cloud))
            ip_list = network_data.get_ip_address()
            if adapter_type == "wifi":
                ip_list = network_data.get_wifi_ip_address() 
            logger.debug("ip is: {}".format(ip_list))
            
            pi_mac = network_data.read_mac_address_lan()

            if adapter_type == "wifi":
                pi_mac = network_data.read_mac_address_wifi() 
            # get the mac address from the pi
            logger.debug("the mac address is: -> {}".format(pi_mac))
        # read and save current time to measure frequency to update device list 
            past_check_update_list = time.time()

            # read current time to measure frequency to send data to the API 
            past_send_cloud = time.time()
            past_temp_send_cloud = time.time()

            # load json file 
            json_file_data = device_registry.load_list()

            for x in json_file_data:
                x['date'] = time.time()
                logger.debug("MAC: {}, Name: {}, Date: {}".format(x.get("mac"), x.get("name"), x.get("date")))
                
            # print("json file loaded: {}".format(json_file_data))
            # declare list to send over POST
            device_to_api = []
            near_devices = []
            not_detected = []
            detected = []
    
            while True:
                try:
                    if time.time() - config_last_check > frequency_config_reset:
                        config_last_check = time.time()
                        app_init()

                    if time.time() - ble_last_check > frequency_reset_ble_attempts:
                        # if ble module has failed enough 
                        if ble_attempts >= ble_limit_failures:
                                        
                            # create simple function to reboot 
                            def sleep_and_reboot():
                                time.sleep(2)
                                os.system("sudo reboot")

                            try:
                                # try send notification to server
                                message = "Device has failed too many times, rebooting now"
                                log_error.pub_error(pi_mac, ip_list, message)
                                logger.error("not able to scan devices, resetting ble modules")
                                            
                                # instance thread class and call it 
                                t = Thread(target=sleep_and_reboot)
                                t.start()
                            except Exception as e:
                                # log error in case that device has failed to send notification to error 
                                logger.error(e)
                                logger.error("Device has failed too many times, rebooting now")
                                logger.error("unable to publish this message to API")
                                            
                                # instance thread class and call it 
                                t = Thread(target=sleep_and_reboot)
                                t.start()
                                            
                        ble_last_check = time.time()


                    # function to measure time to publish data 
                    if (time.time() - past_send_cloud > frequency_to_send_to_cloud or send_now == True):
                        past_send_cloud = time.time()
                        if len(device_to_api) > 0:
                            if(send_now == True):
                                logger.debug("Sending Event Immediately:")
                                for x in device_to_api:
                                    logger.debug("MAC: {}, Battery: {}, Date: {}".format(x.get("MAC"), x.get("BatteryLife"), x.get("DateCreated")))
                            else:
                                logger.debug("Sending Event:")
                                for x in device_to_api:
                                    logger.debug("MAC: {}, Battery: {}, Date: {}".format(x.get("MAC"), x.get("BatteryLife"), x.get("DateCreated")))
                            # define function to run with Thread 
                            def data_to_api_thread(dev):
                                ble_scanner.register_event(dev, adapter_type)

                            # instance thread class and call it 
                            t = Thread(target=data_to_api_thread(device_to_api))
                            t.start()

                            # clear device lists
                            del device_to_api[:]
                            send_now = False

                        if len(detected) > 0:
                            logger.debug("Sending Undetected device:")
                            for x in not_detected:
                                logger.debug("Not detected MAC: {}".format(x))
                            for x in detected:
                                logger.debug("Detected MAC: {}".format(x))

                            def undected_to_api_thread(dev):
                                ble_scanner.log_undected_event(dev, adapter_type)
                            t = Thread(target=undected_to_api_thread({"MAC": not_detected, "DetectedMAC": detected}))
                            t.start()
                            # clear device lists
                            del device_to_api[:]

                    # function to measure temperature and humidity
                    if (time.time() - past_temp_send_cloud > frequency_to_environment_to_send_to_cloud):
                        past_temp_send_cloud = time.time()
                        success = False
                        temperature = 0
                        humidity = 0
                        iaq = 0
                        pressure = 0
                        gasResistance = 0
                        while success is False:
                            try:
                                message = ""
                                #uart = serial.Serial('/dev/tty.usbmodem14101', 115200, timeout=11) # (MacOS)
                                uart = serial.Serial('/dev/ttyACM0', 115200, timeout=11) # Linux
                                uart.write(b'J\n')
                                message = uart.readline()
                                uart.flushInput()
                                data_dict = json.loads(message.decode())
                                temperature = 0
                                humidity = 0
                                iaq = 0
                                pressure = 0
                                gasResistance = 0
                                for measurement, value in data_dict.items():
                                    logger.debug("sensor thing value: {} measurement: {}".format(measurement, value))
                                    if (measurement ==  'temperature'):
                                        temperature = float(value)
                                    if (measurement ==  'humidity'):
                                        humidity = float(value)
                                    if (measurement ==  'IAQ'):
                                        iaq = float(value)
                                    if (measurement ==  'pressure'):
                                        pressure = float(value)
                                    if (measurement ==  'gasResistance'):
                                        gasResistance = float(value)
                                temperatureMessage = {"temperature" : temperature, "humidity" : humidity, "iaq" : iaq, "pressure": pressure, "gasResistance": gasResistance}
                                logger.debug("sending event: {}".format(temperatureMessage))
                                def temp_to_api_thread(temp):
                                    ble_scanner.register_aq_event(temp, adapter_type)
                                t = Thread(target=temp_to_api_thread(temperatureMessage))
                                t.start()
                                success = True
                            except ValueError:
                                print("Value Error on received or parsing data!")
                            except IndexError:
                                print("Index Error on received or parsing data!")
                            except:
                                print("Error opening uart")
                                success = True

                        try:
                            dhtDevice = adafruit_dht.DHT22(board.D4, use_pulseio=False)
                            temperature = dhtDevice.temperature
                            humidity = dhtDevice.humidity
                            logger.debug("starting environment")
                            if humidity is not None and temperature is not None:
                                temperatureMessage = {"temperature" : temperature, "humidity" : humidity, "iaq" : iaq, "pressure": pressure, "gasResistance": gasResistance}
                                logger.debug("sending event: {}".format(temperatureMessage))
                                def temp_to_api_thread(temp):
                                    ble_scanner.register_aq_event(temp, adapter_type)
                                t = Thread(target=temp_to_api_thread(temperatureMessage))
                                t.start()
                        except RuntimeError as error:
                            # Errors happen fairly often, DHT's are hard to read, just keep going
                            print(error.args[0])
                        except Exception as error:
                            dhtDevice.exit()
                            print("Value Error on received or parsing data!")
                    # function to check and update device list 
                    if (time.time() - past_check_update_list > frequency_to_update_list or len(json_file_data) == 0):
                                    
                        # read device list
                        logger.debug("getting device list")
                        dev_list = device_registry.devices_list(pi_mac)
                        logger.debug("the list of devices is:")

                        

                        # save the list into a json file
                        device_registry.save_list(dev_list)

                        # load json file 
                        json_file_data = device_registry.load_list()
                        for x in json_file_data:
                            x['date'] = time.time()
                            logger.debug("MAC: {}, Name: {}, Date: {}".format(x.get("mac"), x.get("name"), x.get("date")))
                        # print("json file loaded: {}".format(type(json_file_data)))

                        # read last time 
                        past_check_update_list = time.time()

                                
                    # check if device list is empty
                    if len(json_file_data) > 0:
                        # # get near devices scanned for bluetooth 
                        logger.debug("scanning for near devices... ")

                        try: 
                            # getting callback from ble scanner 
                            scan_data = ble_scanner.parse_data(ble_scanner.scan(scan_frequency), json_file_data, refresh_interval)
                            not_detected = scan_data['not_detected']
                            near_devices = scan_data['near_devices']
                            detected = scan_data['detected']
                            json_file_data = scan_data['new_json_file']
                            for x in near_devices:
                                logger.debug("MAC: {}, Battery: {}, Date: {}".format(x.get("MAC"), x.get("BatteryLife"), x.get("DateCreated")))
                            for x in not_detected:
                                logger.debug("Not detected MAC: {}".format(x))
                            for x in detected:
                                logger.debug("Detected MAC: {}".format(x))
                            send_now = scan_data['send_now']
                            logger.debug("Send Now!: {}".format(send_now))
                            ble_attempts = 0

                        except AttributeError as e:
                            logger.error(e)
                            logger.error("not able to get device data")
                        except Exception as e:
                            near_devices = []
                            ble_attempts += 1
                            try:

                                # define function to run with Thread 
                                def error_api():
                                    log_error.pub_error(pi_mac, ip_list, e)

                                # instance thread class and call it 
                                t = Thread(target=error_api)
                                t.start()
                                logger.error("not able to scan devices, resetting ble module")
                                ble_scanner.reset_ble()
                            except Exception as e:
                                logger.error("not able to scan devices, resetting ble module")
                                logger.error("unable to publish this message to API")
                                ble_scanner.reset_ble()

                            
                        if len(near_devices) > 0:

                            # if list is empty 
                            if len(device_to_api) == 0:
                                            
                                for i in near_devices:
                                    device_to_api.append(i)

                            # if data is already listed/registered 
                            else:

                                # check mac address in list 
                                for i in near_devices:
                                                
                                    # if mac address is not registered in buffer to send to API
                                    if not any(d.get('MAC') == i["MAC"] for d in device_to_api):
                                        device_to_api.append(i)
                    
                    else:
                        time.sleep(1)
                        try:
                            # define function to run with Thread
                            e = "registered devices list is empty"
                            def error_api():
                                log_error.pub_error(pi_mac, ip_list, e)

                            # instance thread class and call it 
                            t = Thread(target=error_api)
                            t.start()
                            # log_error.pub_error(pi_mac, ip_list, e)
                            logger.warning("registered devices list is empty")
                        except Exception:
                            logger.error("not able to publish error message to API")
                            logger.warning("registered devices list is empty")

                except Exception as e:
                    try:
                        # define function to run with Thread 
                        def error_api():
                            log_error.pub_error(pi_mac, ip_list, e)

                            # instance thread class and call it 
                            t = Thread(target=error_api)
                            t.start()
                            # log_error.pub_error(pi_mac, ip_list, e)
                            logger.error(e)
                    except Exception as e:
                        logger.error("not able to send error message to API")
                        logger.error(e)
        else:
            logger.error("device not registered")
    except Exception as e:
        try:

            # define function to run with Thread 
            def error_api():
                log_error.pub_error(pi_mac, ip_list, e)

            # instance thread class and call it 
            t = Thread(target=error_api)
            t.start()
            logger.error(e)
        except Exception as e:
            logger.error(e)
            logger.error("device was not able to publish error message")
            logger.error("please check your network configuration")


# calling main application
main()
