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

def send_email(mail_config, mail_dest, text):
    # creates SMTP session
    s = smtplib.SMTP(mail_config.get('mail_smtp_server'), mail_config.get("mail_smtp_port"))
    s.starttls()                        # start TLS for security
    s.login(mail_config.get('mail_user'), mail_config.get('mail_pwd'))        # Authentication
    msg = MIMEMultipart("alternative")  # Instance of MIMEMultipart
    msg["Subject"] = "LIVOX Alert"    # Write the subject
    msg["From"] = mail_config.get('mail_user')
    msg["To"] = mail_dest
    # Attach the Plain body with the msg instance
    msg.attach(MIMEText(text, "plain"))
    # Sending the mail
    s.sendmail(mail_config.get('mail_user'), mail_dest, msg.as_string())
    s.quit()

def alert_mail(mail_config, mail_dest):
    host_machine = os.uname()[1]
    t1 = 'WARNING: Livox lidar on {} not running.\n\n'.format(host_machine)
    t2 = '--- Email automatically sent ---'
    send_email(mail_config, mail_dest, t1+t2)
    print('---> Mail sent')


if __name__ == "__main__":
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

        # 1. test if file is missing
        # 2. try rebooting lidar and apply delay
        # 3. check if lidar is now working

        # 4. if not, send email
        alert_mail(mail_config, mail_dest)
    else:


