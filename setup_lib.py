import os


def install_prereqs():
    os.system('sudo apt-get update')
    os.system("sudo pip3 install pexpect")
    os.system("sudo timedatectl set-timezone Asia/Singapore")
    os.system('sudo apt-get install python3-pip libglib2.0-dev')
    os.system('sudo pip3 install bluepy')
    os.system('sudo pip3 install adafruit-circuitpython-dht')
    os.system('sudo apt install libgpiod2')
    os.system('sudo pip install pyserial')
    os.system('sudo pip install --upgrade psutil')
    os.system("sudo pip3 install python-crontab")

def copy_crontab():
    from crontab import CronTab
    os.system('sudo chmod 755 /home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner')
    cron = CronTab(user='pi')
    cron.remove_all()
    job = cron.new(command='sleep 60 && sh /home/pi/actions-runner/_work/epic-os-scanner/epic-os-scanner/launcher/launcher.sh >> /dev/null 2>&1')
    job.every_reboot()
    cron.write()