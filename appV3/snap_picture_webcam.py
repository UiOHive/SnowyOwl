import datetime
import argparse, os
import subprocess, logging
import datetime

def ping(host):
    command = ['ping', '-c', '1', host]
    return subprocess.call(command) == 0

def filename_builder():
    today = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{today}_gruve_cam.jpg'
    return filename

def snap_picture(fname, cam_param, path='./'):

    if ping(cam_param['cam_IP']):
        fname = f"{datetime.datetime.now().strftime("%Y%m%d%H%M")}_cam.png."
        cmd = f"ffmpeg -rtsp_transport tcp -i rtsp://{cam_param['cam_user']}:{cam_param['cam_pwd']}@{cam_param['cam_IP']}/stream1 -frames:v 1 -y {path}{fname}"
        #url = f"rtsp://{cam_param['cam_user']}:{cam_param['cam_pwd']}@{cam_param['cam_IP']}:{cam_param['cam_port']}/test.mjpg"
        print(cmd)
        os.system(cmd)

        fout = f'{path}{fname}'
        
        print(f'---> Image {fname} stored as {fout}')
        
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

