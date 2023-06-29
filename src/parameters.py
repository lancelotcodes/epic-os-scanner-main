import json


def get_device_json_list():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'
    json_file_data = ""

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

        for p in data['device_parameters']:
            json_file_data = p['device_list_path']
    
    return json_file_data

def get_url():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'
    url = ""

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

        for p in data['device_parameters']:
            url = p['url']
    
    return url

def get_key():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'
    key = ""

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

        for p in data['device_parameters']:
            key = p['key']
    
    return key

def get_freq_update_list():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

    return data['frequency']['update_list']

def get_freq_scan():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

    return data['frequency']['scan_frequency']

def get_freq_send_to_cloud():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

    return data['frequency']['send_to_cloud']


def get_freq_temp_send_to_cloud():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

    return data['frequency']['temp_send_to_cloud']

def get_config_set_frequency():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

    return data['frequency']['config_set_frequency']
    
def get_freq_reset_ble_attempts():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

    return data['frequency']['reset_ble_attempts']

def get_freq_reset_ble_limit_failures():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

    return data['frequency']['ble_limit_failures']

def get_adapter_type():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

    return data['frequency']['adapter_type']

def get_save_path():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'
    save_list_path = ""

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

        for p in data['device_parameters']:
            save_list_path = p['save_list_path']
    
    return save_list_path

def get_log_path():
    path = '/home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/config/appconfig.json'
    save_list_path = ""

    with open(path, 'r', encoding='utf-8') as json_f:
        data = json.load(json_f)

        for p in data['device_parameters']:
            save_list_path = p['log_file_path']
            
    return save_list_path