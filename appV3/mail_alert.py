'''
Script to check the lidar is running, if not working after reboot, then send email
S.Filhol and L. Girdo November 2021

Logic to follow
1. check date of last file acquired from lidar
2. If date is more than max(sampling period or 1h) then try reboot the lidar
3. If after reboot + 1smapling period still no new file then send email alert


'''


import smtplib,  time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import glob, os, subprocess
import configparser, argparse
import datetime

def ping_ip(current_ip_address):
        try:
            command = ['ping', '-c', '1', current_ip_address]
            output = subprocess.call(command)
            if output == 0:
                return True
            else:
                return False
        except Exception:
            print('ERROR: Ping function not working')
            return False


def condition_alert():
    # check if Lidar has brought a new file
    return

def compose_email(from_email, to_email, subject, text):
    msg = MIMEMultipart("alternative")  # Instance of MIMEMultipart
    msg["Subject"] = subject    # Write the subject
    msg["From"] = from_email
    msg["To"] = to_email
    # Attach the Plain body with the msg instance
    msg.attach(MIMEText(text, "plain"))
    return msg

def send_email(mail_config, mail_dest, msg):
    # creates SMTP session
    server = smtplib.SMTP_SSL(mail_config.get('mail_smtp'), mail_config.get("mail_smtp_port"))
    time.sleep(2)
    server.login(mail_config.get('mail_user'), mail_config.get('mail_pwd'))
    time.sleep(2)
    # Sending the mail
    server.sendmail(mail_config.get('mail_user'), mail_dest, msg.as_string())
    server.quit()

def alert_mail(mail_config, mail_dest):
    host_machine = os.uname()[1]
    t1 = f'WARNING: Livox lidar on {host_machine} not running.\n\n'
    t2 = '--- Email automatically sent ---'
    send_email(mail_config, mail_dest, t1+t2)
    print('---> Mail sent')


if __name__ == "__main__":
    '''
    TODO: Rewrite code that the following triggers email alert:
        1. disk sapce is becoming too low
        2. last file on disk is X old
    - remove config file system
    - 
    '''



    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', '-cf', help='Path to config file', default='/home/config.ini')
    args = parser.parse_args()

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(args.config_file)

    mail_dest = config.get('acquisition', 'mail_dest')
    mail_smtp_server = config.get('acquisition', "mail_smtp_server")
    mail_smtp_port = config.getint('acquisition', "mail_smtp_port")
    mail_config = {'mail_smtp': mail_smtp_server,
                   'mail_smtp_port': mail_smtp_port,
                   'mail_user': os.getenv('MAIL_USER_LIVOX'),
                   'mail_pwd': os.getenv('MAIL_PWD_LIVOX')}

    if not ping_ip(config.get('acquisition', 'scanner_IP')):
        if not ping_ip(config.get('acquisition', 'scanner_IP')):
            txt = 'WARNING: Lidar from {} is not pinging, even after reboot attempt!'.format(os.uname()[1])
            msg = compose_email(mail_config.get('mail_user'), mail_dest, 'Livox lidar WARNING', txt)
            send_email(mail_config, mail_dest, msg)

    # 1. test if file is missing
    flist = glob.glob(config.get('acquisition', 'data_folder') + 'archive/*.bin')
    flist.sort()
    last_file = datetime.datetime.strptime(flist[-1][:-4], "%Y.%m.%dT%H-%M-%S")
    now = datetime.datetime.now()

    if (now - last_file).seconds > config.getint('acquisition', 'scanning_interval')*5:
        # 2. try rebooting lidar and apply delay
        reboot_lidar(config)

            # How to check if Lidar is working????





            # 3. check if lidar is now working

        # 4. if not, send email
        txt = ''
        msg = compose_email(mail_config.get('mail_user'), mail_dest, 'Livox lidar WARNING', txt)
        send_email(mail_config, mail_dest, msg)
    else:


