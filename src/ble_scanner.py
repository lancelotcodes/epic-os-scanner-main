import  requests, datetime, parameters, json, os, time, log_error, network_data
from operator import itemgetter
from bluepy.btle import Scanner, DefaultDelegate, Peripheral
from threading import Thread

logger = log_error.logger 
ip_dev = network_data.get_ip_address()
mac_dev = network_data.read_mac_address_lan()

bit_movement_detected = 1
bit_low_battery = 2
manufacturer_data = "Manufacturer"
service_data = "16b Service Data"

def get_bit(byteval,idx):
    return ((byteval & (1 << idx)) != 0)


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self) 

    def handleDiscovery(self,dev,isNewDev,isNewData):
        pass 

def reset_ble():
    # set the required commands to run bluetooth scan
    down_ble_service = "sudo hciconfig hci0 down"
    up_ble_service = "sudo hciconfig hci0 up"

    os.system(down_ble_service)
    time.sleep(2.5)
    os.system(up_ble_service)
    time.sleep(2.5)



# function to scan for ble PIR sensors 
def scan(scan_frequency):

    # scan for devices 
    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(scan_frequency) # scan for devices at specific frequency

    return devices


def define_adapter_ip(adapter_type):
    ip_address = network_data.get_ip_address()
    if adapter_type == "wifi":
        ip_address = network_data.get_wifi_ip_address()
    return ip_address

def define_adapter_mac(adapter_type):
    mac_address = network_data.read_mac_address_lan()
    if adapter_type == "wifi":
        mac_address = network_data.read_mac_address_wifi()
    return mac_address

def register_event(dev_publish, adapter_type):
    ip_add = define_adapter_ip(adapter_type)
    mac_add = define_adapter_mac(adapter_type)
    try: 
        # set url 
        url = parameters.get_url() + '/api/telemery/upload-logs' + '/' + mac_add + '/' + ip_add

        # set the content-type
        header = {"Content-type": "application/json", "ApiKey": parameters.get_key()}

        request = requests.post(url, json=dev_publish, headers=header)

        # # print status code and result
        # print(request)
        # print(request.text)
        logger.debug(request)
        
    except Exception as e:
        try:
            # log_error.pub_error(mac_dev, ip_dev, e)
            # define function to run with Thread 
            def error_api():
                log_error.pub_error(mac_add, ip_add, e)

            # instance thread class and call it 
            t = Thread(target=error_api)
            t.start()
            logger.error("not able to register event, check your network configuration")
        except Exception as e:
            logger.error("not able to send message to the api")

def log_undected_event(dev_publish, adapter_type):
    mac_add = define_adapter_mac(adapter_type)
    try: 
        # set url 
        url = parameters.get_url() + '/api/telemery/missing-workpoints' + '/' + mac_add

        # set the content-type
        header = {"Content-type": "application/json", "ApiKey": parameters.get_key()}

        request = requests.put(url, json=dev_publish, headers=header)

        # # print status code and result
        # print(request)
        # print(request.text)
        logger.debug(request)
        
    except Exception as e:
        try:
            # log_error.pub_error(mac_dev, ip_dev, e)
            # define function to run with Thread 
            def error_api():
                log_error.pub_error(mac_add, ip_add, e)

            # instance thread class and call it 
            t = Thread(target=error_api)
            t.start()
            logger.error("not able to register event, check your network configuration")
        except Exception as e:
            logger.error("not able to send message to the api")

def register_newmac_event(dev_publish, adapter_type):
    mac_add = define_adapter_mac(adapter_type)
    try: 
        # set url 
        url = parameters.get_url() + '/api/telemery/register-by-mac' + '/' + mac_add
        # set the content-type
        header = {"Content-type": "application/json", "ApiKey": parameters.get_key()}

        publish = {"WorkPointMAC": dev_publish}

        request = requests.post(url, json=publish, headers=header)

        # # print status code and result
        # print(request)
        # print(request.text)
        logger.debug(request)
        
    except Exception as e:
        try:
            # log_error.pub_error(mac_dev, ip_dev, e)
            # define function to run with Thread 
            def error_api():
                log_error.pub_error(mac_add, ip_add, e)

            # instance thread class and call it 
            t = Thread(target=error_api)
            t.start()
            logger.error("not able to register event, check your network configuration")
        except Exception as e:
            logger.error("not able to send message to the api")


            

def register_temp_event(dev_publish):
    try: 
        # set url 
        url = parameters.get_url() + '/api/temperature-humidity-hub/create-logs'

        # set the content-type
        header = {"Content-type": "application/json", "ApiKey": parameters.get_key()}

        print("publish this: {}".format(dev_publish))

        request = requests.post(url, json=dev_publish, headers=header)

        # # print status code and result
        # print(request)
        # print(request.text)
        logger.debug(request)
        logger.debug(request.text)
        
    except Exception as e:
        try:
            # log_error.pub_error(mac_dev, ip_dev, e)
            # define function to run with Thread 
            def error_api():
                log_error.pub_error(mac_add, ip_add, e)

            # instance thread class and call it 
            t = Thread(target=error_api)
            t.start()
            logger.error("not able to register event, check your network configuration")
        except Exception as e:
            logger.error("not able to send message to the api")

def register_aq_event(dev_publish, adapter_type):
    mac_add = define_adapter_mac(adapter_type)
    try: 
        # set url 
        url = parameters.get_url() + '/api/air-quality-hub/create-logs'+ '/' + mac_add 

        # set the content-type
        header = {"Content-type": "application/json", "ApiKey": parameters.get_key()}

        print("publish this: {}".format(dev_publish))

        request = requests.post(url, json=dev_publish, headers=header)

        # # print status code and result
        # print(request)
        # print(request.text)
        logger.debug(request)
        logger.debug(request.text)
        
    except Exception as e:
        try:
            # log_error.pub_error(mac_dev, ip_dev, e)
            # define function to run with Thread 
            def error_api():
                log_error.pub_error(mac_add, ip_add, e)

            # instance thread class and call it 
            t = Thread(target=error_api)
            t.start()
            logger.error("not able to register event, check your network configuration")
        except Exception as e:
            logger.error("not able to send message to the api")


def parse_data(devices, dev_list, interval):
    data = []
    unique_mac_list = []
    device_on_area = []
    not_detected = []
    detected = []
    dev_dict = {}
    returnData = {}
    send_now = False

    for dev in devices:
        data.append(dev.addr)
        dev_addr = dev.addr.upper()

        for (adtype, desc, value) in dev.getScanData():
            if desc == service_data:
                device_on_area.append(dev_addr)

        if any(d.get('mac') == dev_addr for d in dev_list):
            # set address to uppercase
            dev_addr = dev.addr.upper()
            # check mac address in list 

            # get manufacturer data
            for (adtype, desc, value) in dev.getScanData():
                if desc == service_data:
                    hex_str = hex(int(value[20:22]))
                    bat_str = value[18:20]
                    bat_str1 = value[16:18]
                    joint = bat_str + bat_str1
                    bat_life = int(joint, 16)
                    logger.debug("bat value: {}".format(int(joint, 16)))
                    dec_val = int(hex_str, 16)     
                    logger.debug("dec val is: {}".format(dec_val))  

                    if dec_val == 1:  
                        logger.debug("movement detected!")      
                        print("add {} to unique list".format(dev_addr))    
                        logger.debug("add {} to unique list".format(dev_addr))
                        now = datetime.datetime.now()
                        dev_dict["MAC"] = dev_addr
                        dev_dict["Battery"] = False
                        dev_dict["BatteryLife"] = bat_life
                        if bat_life <= 2000:
                            dev_dict["Battery"] = True
                        date = now.strftime("%Y-%m-%dT%H:%M:%S")
                        dev_dict["DateCreated"] = date
                        unique_mac_list.append(dev_dict)

                        for x in dev_list:
                            if x.get('mac') == dev_addr:
                                logger.debug(x.get('date') == None)  
                                if x.get('date') != None:
                                    logger.debug("current time: {}".format(time.time()))  
                                    logger.debug("last time: {}".format(x.get('date')))  
                                    logger.debug("difference: {}".format(time.time() - x.get('date')))  
                                    logger.debug("interval: {}".format(interval))  
                                    if ((time.time() - x.get('date')) > interval):
                                        send_now = True
                                        logger.debug("send now: {}".format(send_now))  
                                    x['date'] = time.time()
                                else:            
                                    now = datetime.datetime.now()
                                    x['date'] = time.time()


                # if desc == manufacturer_data:
                #     # save data byte to evaluate sensor status
                #     hex_str = hex(int(value[10:12]))
                #     dec_val = int(hex_str, 16)

                #     # check if movement was detected
                #     if get_bit(dec_val, bit_movement_detected) == True:
                #         # print("movement detected!")
                #         logger.debug("movement detected!")
                #         # if device is not in the unique_mac_list, add it
                #         print("add {} to unique list".format(dev_addr))
                #         now = datetime.datetime.now()

                #         if get_bit(dec_val, bit_low_battery) == True:
                #             dev_dict["MAC"] = dev_addr
                #             dev_dict["Battery"] = True
                #             date = now.strftime("%Y-%m-%dT%H:%M:%S")
                #             dev_dict["DateCreated"] = date
                #             unique_mac_list.append(dev_dict)
                #         else:
                #             dev_dict["MAC"] = dev_addr
                #             dev_dict["Battery"] = False
                #             date = now.strftime("%Y-%m-%dT%H:%M:%S")
                #             dev_dict["DateCreated"] = date
                #             unique_mac_list.append(dev_dict)

                #         for x in dev_list:
                #             if x.get('mac') == dev_addr:
                #                 if x.get('date') != None:
                #                     logger.debug("current time: {}".format(time.time()))  
                #                     logger.debug("last time: {}".format(x.get('date')))  
                #                     logger.debug("difference: {}".format(time.time() - x.get('date')))  
                #                     logger.debug("interval: {}".format(interval))  
                #                     if ((time.time() - x.get('date')) > interval):
                #                         send_now = True
                #                         logger.debug("send now: {}".format(send_now))  
                #                     x['date'] = time.time()
                #                 else:            
                #                     now = datetime.datetime.now()
                #                     x['date'] = time.time()


    for dev in dev_list:
        if any(d == dev.get('mac') for d in device_on_area):
            detected.append(dev.get('mac'))
        else:
            not_detected.append(dev.get('mac'))

    returnData['near_devices'] = unique_mac_list
    returnData['not_detected'] = not_detected
    returnData['detected'] = detected
    returnData['new_json_file'] = dev_list
    returnData['send_now'] = send_now
    return returnData


def parseall_data(devices, dev_list):
    data = []
    unique_mac_list = []
    dev_dict = {}

    # p = Peripheral("D9:52:E0:4D:C0:29", "random")
    # # for service in services:
    # #     logger.debug("service! {}".format(service))
    # s = p.getServiceByUUID("d35b1000-e01c-9fac-ba8d-7ce20bdba0c6")
    # chars = s.getCharacteristics("d35b1003-e01c-9fac-ba8d-7ce20bdba0c6")
    # for char in chars:
    #     # read = char.getHandle()
    #     # readChar = char.read()
    #     char.write(bytes([7]))
    #     # response = char.writeCharacteristic(char.getHandle(), bytes([7]) , True)
    #     # logger.debug("response! {}".format(response))
    # # read = chars.readCharacteristic()
    # # logger.debug("service! {}".format(read))
    # p.disconnect()


    for dev in devices:
        data.append(dev.addr)
        dev_addr = dev.addr.upper()
        logger.debug("mac: {}".format(dev_addr)) 
        # set address to uppercase 
        # get manufacturer data
        if any(d.get('mac') == dev_addr for d in dev_list):
            logger.debug("sensor on list!")  
        else:
            for (adtype, desc, value) in dev.getScanData():
                if desc == service_data:
                    unique_mac_list.append(dev_addr)
                    

    return unique_mac_list
        # if any(d.get('mac') == dev_addr for d in dev_list):
