import logging, requests, datetime, parameters, sys, os, json


# setup logging 
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(filename)s:%(message)s')

# log_file_path = '/home/pi/projects/ble_pir_scanner/logs/sample.log'
log_file_path = parameters.get_log_path()
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

# function to send error message to the API
def pub_error(mac, ip, msg):
    msg = str(msg)
    logger.debug("message is: {}".format(msg))
    logger.debug("message type: {}".format(type(msg)))
    # get url to request 
    url = parameters.get_url() + '/api/telemery/hub-logs'

    # set the content-type
    header = {"Content-type": "application/json", "ApiKey": parameters.get_key()}

    error_list = []
    error_dict = {}
    error_dict["MAC"] = mac
    error_dict["IPaddress"] = ip

    # get current time and date 
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%dT%H:%M:%S")
    error_dict["DateCreated"] = date 
    
    error_dict["Message"] = msg

    error_list.append(error_dict)

    logger.debug("public error: {}".format(error_list))

    request = requests.post(url, json=error_list, headers=header)

    # print status code and result
    logger.debug(request)
    logger.debug(request.text)
    
