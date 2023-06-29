'''
    BLE Monitor
'''
import subprocess, device_registry, parameters, ble_scanner, time, datetime, network_data
import socket, fcntl, struct, log_error
import sys, os 
from threading import Thread
import time
import sys, json
import serial
import psutil
# for error logging 
logger = log_error.logger

# frequency seconds 
FREQUENCY_TO_UPDATE_LIST = parameters.get_freq_update_list()  # 5 mins
FREQUENCY_TO_SEND_CLOUD = parameters.get_freq_send_to_cloud()   # 2 min 
FREQUENCY_TO_TEMPERATURE_SEND_CLOUD = parameters.get_freq_temp_send_to_cloud()   # 2 min 
FREQUENCY_CONFIG_RESET = parameters.get_config_set_frequency()   # 2 min 
REFRESH_INTERVAL = 300  # 2 min 
SCAN_FREQUENCY = parameters.get_freq_scan()   # 2 min 
SEND_NOW = False


FREQUENCY_RESET_BLE_ATTEMPTS = parameters.get_freq_reset_ble_attempts() 
BLE_LIMIT_FAILURES = parameters.get_freq_reset_ble_limit_failures()

appended_data = {'cpuTemperature': 'value'}
json_message = [{
    "measurement": "humidity",
    "fields": {
        "value": 12.34
    }
}]


def load_config():
    json_file_path = []
    try :
        pi_mac = network_data.read_mac_address_wifi()
        # set the file path
        logger.debug("getting config list")
        dev_list = device_registry.config_list(pi_mac)
        device_registry.update_ip(pi_mac)
        FREQUENCY_TO_SEND_CLOUD = dev_list['movementFrequency']
        FREQUENCY_TO_TEMPERATURE_SEND_CLOUD = dev_list['tempHumidityFrequency']
        FREQUENCY_TO_UPDATE_LIST = dev_list['hubWorkPointListUpdate']
        FREQUENCY_CONFIG_RESET = dev_list['configResetFrequency']
        SCAN_FREQUENCY = dev_list['hubScanFrequency']
        FREQUENCY_RESET_BLE_ATTEMPTS = dev_list['hubResetAttempts']
        BLE_LIMIT_FAILURES = dev_list['hubFailureLimitFailures']
        REFRESH_INTERVAL = dev_list['refreshInterval']

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

# main process 
def main():
    try:
        # counter for ble exceptions
        ble_attempts = 0
        ble_last_check = time.time() 
        config_last_check = time.time() 

        # starting application with a debug message
        logger.debug("hello, starting application")

        # get ip address 
        ip_list = network_data.get_ip_address()
        logger.debug("ip is: {}".format(ip_list))
        
        # get the mac address from the pi
        pi_mac = network_data.read_mac_address_wifi()
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
        unregistered_mac_to_api = []
        near_devices = []
        load_config()
        while True:
            try:
                if time.time() - config_last_check > FREQUENCY_CONFIG_RESET:
                    config_last_check = time.time()
                    load_config()

                if time.time() - ble_last_check > FREQUENCY_RESET_BLE_ATTEMPTS:
                                
                    # if ble module has failed enough 
                    if ble_attempts >= BLE_LIMIT_FAILURES:
                                    
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
                if (time.time() - past_send_cloud > FREQUENCY_TO_SEND_CLOUD or SEND_NOW == True):
                    past_send_cloud = time.time()

                    if len(unregistered_mac_to_api) > 0:
                        logger.debug("Sending Unregistered MAC:")
                        for x in unregistered_mac_to_api:
                            logger.debug("MAC: {}".format(x))
                        def unregistered_mac_to_api_thread(dev):
                            ble_scanner.register_newmac_event(dev)

                        # instance thread class and call it 
                        t = Thread(target=unregistered_mac_to_api_thread(unregistered_mac_to_api))
                        t.start()
                        
                # function to measure temperature and humidity
                # function to check and update device list 
                if (time.time() - past_check_update_list > FREQUENCY_TO_UPDATE_LIST or len(json_file_data) == 0):
                                
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
                # # get near devices scanned for bluetooth 
                logger.debug("scanning for near devices... ")

                try: 
                    # getting callback from ble scanner 
                    unregistered_mac = ble_scanner.parseall_data(ble_scanner.scan(SCAN_FREQUENCY), json_file_data)
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

                if len(unregistered_mac) > 0:
                    for i in unregistered_mac:
                        unregistered_mac_to_api.append(i)
            

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
