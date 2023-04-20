import cv2
import datetime
import argparse, os
import configparser

def filename_builder():
    today = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{today}_gruve_cam.jpg'
    return filename

def snap_picture(fname, cam_param, path='./'):

    url = f"rtsp://{cam_param['cam_user']}:{cam_param['cam_pwd']}@{cam_param['cam_IP']}:{cam_param['cam_port']}/test.mjpg"
    print(url)
    cap = cv2.VideoCapture(url)
    cv2.imwrite(f'{path}{fname}', cap.read()[1])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', '-cf', help='Path to config file', default='/home/config.ini')
    args = parser.parse_args()

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(args.config_file)

    #try:
    fname = filename_builder()
    cam_param = {'cam_user':config.get('webcam', 'cam_user'),
                 'cam_pwd':config.get('webcam', 'cam_pwd'),
                 'cam_IP':config.get('webcam', 'cam_IP'),
                 'cam_port':config.get('webcam', 'cam_port')}

    snap_picture(fname, cam_param, path=config.get('webcam', 'dir_to_images'))
    #except:
    #    print('ERROR: problem with webcam')

