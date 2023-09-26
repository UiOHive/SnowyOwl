import cv2
import datetime
import argparse, os
import subprocess, logging

def ping(host):
    command = ['ping', '-c', '1', host]
    return subprocess.call(command) == 0

def filename_builder():
    today = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{today}_gruve_cam.jpg'
    return filename

def snap_picture(fname, cam_param, path='./'):

    if ping(cam_param['cam_IP']):
        url = f"rtsp://{cam_param['cam_user']}:{cam_param['cam_pwd']}@{cam_param['cam_IP']}:{cam_param['cam_port']}/test.mjpg"
        print(url)
        cap = cv2.VideoCapture(url)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)

        fout = f'{path}{fname}'
        cv2.imwrite(fout, cap.read()[1])
        print(f'---> Image {fname} stored as {fout}')
        cap.release()
    else:
        print(f"IP {cam_param['cam_IP']} does not ping")
        logging.error(f"IP {cam_param['cam_IP']} does not ping")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--IP_address', '-ip', help='IP of webcam', default='192.168.1.120')
    parser.add_argument('--port', '-p', help='Port of webcam', default='554')
    parser.add_argument('--user', '-u', help='User of webcam', default='admin')
    parser.add_argument('--password', '-pwd', help='Password of webcam', default='*******')
    parser.add_argument('--output_dir', '-o', help='directory for output image', default='./myfolder/')
    args = parser.parse_args()

    logging.basicConfig(filename=args.output_dir + 'webcam.log',
                        level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s : %(message)s')

    fname = filename_builder()
    cam_param = {'cam_user':args.user,
                 'cam_pwd':args.password,
                 'cam_IP':args.IP_address,
                 'cam_port':args.port}

    snap_picture(fname, cam_param, path=args.output_dir)
    #except:
    #    print('ERROR: problem with webcam')

