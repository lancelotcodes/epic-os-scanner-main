import requests, json, network_data, log_error
from ast import literal_eval
import parameters
from threading import Thread

logger = log_error.logger 
ip_dev = network_data.get_ip_address()
wifi_ip_dev = network_data.get_wifi_ip_address()
mac_dev = network_data.read_mac_address_wifi()


def devices_list(mac):
    try: 
        # set the content-type
        header = {"Content-type": "application/json", "ApiKey": parameters.get_key()}

        # set the url address to send the http post
        url = parameters.get_url() + '/api/telemery/workpoint-by-hub/'+mac

        # send the http post request 
        request = requests.get(url, json = {}, headers = header)
        
        return request.text
        
    except Exception as e:
        try:
            # log_error.pub_error(mac_dev, ip_dev, e)
            # define function to run with Thread 
            def error_api():
                log_error.pub_error(mac_dev, ip_dev, e)

            # instance thread class and call it 
            t = Thread(target=error_api)
            t.start()
            logger.error(e)
            logger.error("not able to get device list")
        except Exception as e:
            logger.error(e)
            logger.error("not able to send error message to the API")
            logger.error("not able to get device list")

def config_list(mac):

    try: 
        # set the content-type
        header = {"Content-type": "application/json", "ApiKey": parameters.get_key()}

        # set the url address to send the http post
        url = parameters.get_url() + '/api/hub-config/'+mac

        # send the http post request 
        request = requests.get(url, json = {}, headers = header)
        
        return request
        
    except Exception as e:
        try:
            # log_error.pub_error(mac_dev, ip_dev, e)
            # define function to run with Thread 
            def error_api():
                log_error.pub_error(mac_dev, ip_dev, e)

            # instance thread class and call it 
            t = Thread(target=error_api)
            t.start()
            logger.error(e)
            logger.error("not able to get config list")
        except Exception as e:
            logger.error(e)
            logger.error("not able to send error message to the API")
            logger.error("not able to get config list")

def update_ip(mac, network_type):
    ip_add = network_data.get_ip_address()
    if network_type == "wifi":
        ip_add = network_data.get_wifi_ip_address()

    try: 
        # set the content-type
        header = {"Content-type": "application/json", "ApiKey": parameters.get_key()}

        # set the url address to send the http post
        url = parameters.get_url() + '/api/hub-config/register-ip/'+mac+'/'+ip_add

        # send the http post request 
        request = requests.get(url, json = {}, headers = header)
        
        return request.json()
        
    except Exception as e:
        try:
            # log_error.pub_error(mac_dev, ip_dev, e)
            # define function to run with Thread 
            def error_api():
                log_error.pub_error(mac_dev, ip_dev, e)

            # instance thread class and call it 
            t = Thread(target=error_api)
            t.start()
            logger.error(e)
            logger.error("not able to get config list")
        except Exception as e:
            logger.error(e)
            logger.error("not able to send error message to the API")
            logger.error("not able to get config list")

def save_list(device_list):

    try: 
        # set the file path
        json_file_path = parameters.get_save_path()

        # save the json file 
        with open(json_file_path, 'w') as outfile:
            json.dump(device_list, outfile)

    except Exception as e:
        try:
            # log_error.pub_error(mac_dev, ip_dev, e)
            # define function to run with Thread 
            def error_api():
                log_error.pub_error(mac_dev, ip_dev, e)

            # instance thread class and call it 
            t = Thread(target=error_api)
            t.start()
            logger.error(e)
            logger.error("not able to save list")
        except Exception as e:
            logger.error(e)
            logger.error("not able to send error message to the API")
            logger.error("not able to save device list")


def load_list():
    json_file_path = []
    try :
        # set the file path
        json_file_path = parameters.get_device_json_list()

        # load json object and return it 
        with open(json_file_path) as json_file:
            data = json.load(json_file)
            python_dict = literal_eval(data)
        
        return python_dict 
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

