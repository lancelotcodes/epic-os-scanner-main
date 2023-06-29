import socket, fcntl, struct, log_error, subprocess

logger = log_error.logger

# get ip addresses related to pi 
def get_ip_address():
    # ifname = ['lo', "eth0", "wlan0"]
    ifname = "eth0"
    # ip_list = []
    # for i in range(0, 3):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return (socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode())
        )[20:24]))

    except Exception as e:
        logger.error(e)
        logger.error("not able to get ip addresss.")
        return None

        # logger.error(ifname[i])
        # ip_list.append(None)

def get_wifi_ip_address():
    # ifname = ['lo', "eth0", "wlan0"]
    ifname = "wlan0"
    # ip_list = []
    # for i in range(0, 3):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return (socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode())
        )[20:24]))

    except Exception as e:
        logger.error(e)
        logger.error("not able to get ip addresss.")
        return None

        # logger.error(ifname[i])
        # ip_list.append(None)
    


# looks for the MAC address for wlan0 (wifi module)
def read_mac_address_wifi():
    mac = subprocess.check_output("sudo ifconfig wlan0 | grep -Eo ..\(\:..\){5}", shell = True)	# outputs the mac address
    mac = mac.decode("utf-8")
    mac_to_post = ""
    i = 0

    # extract the \n from the string 
    while i < len(mac):
        if (mac[i] != '\n'):
            mac_to_post += mac[i]
        i = i + 1

    # reset iterator 
    i = 0

    # return the corrected mac address to uppercase
    mac_converted = ""
    while (i < len(mac_to_post)):
        mac_converted += mac_to_post[i].upper()
        i = i + 1

    return mac_converted

def read_mac_address_lan():
    mac = subprocess.check_output("sudo ifconfig eth0 | grep -Eo ..\(\:..\){5}", shell = True)	# outputs the mac address
    mac = mac.decode("utf-8")
    mac_to_post = ""
    i = 0

    # extract the \n from the string 
    while i < len(mac):
        if (mac[i] != '\n'):
            mac_to_post += mac[i]
        i = i + 1

    # reset iterator 
    i = 0

    # return the corrected mac address to uppercase
    mac_converted = ""
    while (i < len(mac_to_post)):
        mac_converted += mac_to_post[i].upper()
        i = i + 1

    return mac_converted
