# -*- coding: utf-8 -*-
import sys
import time
import base64
import json
import urllib2

sys.path.insert(0, r'C:\Path\To\pythonSDK\lib')

from naoqi import ALProxy

NAO_IP = "YOUR_NAO_IP"  
NAO_PORT   = 9559
SERVER_URL = "http://YOUR_SERVER_IP:5000/frame"

def disable_auto_reactions():
    try:
        autonomous_life = ALProxy("ALAutonomousLife", NAO_IP, NAO_PORT)
        print("Current AutonomousLife state:", autonomous_life.getState())
        autonomous_life.setState("disabled")
        print("AutonomousLife disabled.")
    except Exception as e:
        print("AutonomousLife warning:", e)

    try:
        basic_awareness = ALProxy("ALBasicAwareness", NAO_IP, NAO_PORT)
        basic_awareness.stopAwareness()
        print("BasicAwareness stopped.")
    except Exception as e:
        print("BasicAwareness warning:", e)

    try:
        listening_movement = ALProxy("ALListeningMovement", NAO_IP, NAO_PORT)
        listening_movement.setEnabled(False)
        print("ListeningMovement disabled.")
    except Exception as e:
        print("ListeningMovement warning:", e)

def freeze_head():
    try:
        motion = ALProxy("ALMotion", NAO_IP, NAO_PORT)
        motion.setStiffnesses("Head", 1.0)
        motion.angleInterpolation(
            ["HeadYaw", "HeadPitch"],
            [0.0, 0.0],
            [0.5, 0.5],
            True
        )
        print("Head centered and fixed.")
    except Exception as e:
        print("Head freeze warning:", e)

def enable_auto_reactions():
    try:
        autonomous_life = ALProxy("ALAutonomousLife", NAO_IP, NAO_PORT)
        autonomous_life.setState("solitary")
        print("AutonomousLife restored.")
    except Exception as e:
        print("AutonomousLife restore warning:", e)

    try:
        basic_awareness = ALProxy("ALBasicAwareness", NAO_IP, NAO_PORT)
        basic_awareness.startAwareness()
        print("BasicAwareness restored.")
    except Exception as e:
        print("BasicAwareness restore warning:", e)

    try:
        listening_movement = ALProxy("ALListeningMovement", NAO_IP, NAO_PORT)
        listening_movement.setEnabled(True)
        print("ListeningMovement restored.")
    except Exception as e:
        print("ListeningMovement restore warning:", e)

CAM_INDEX      = 1  
#CAM_RESOLUTION = 0   # kQQVGA = 160x120 
CAM_RESOLUTION = 1   # kQVGA = 320x240
CAM_COLORSPACE = 11  # kRGBColorSpace
CAM_FPS        = 30

def send_frame(img_b64, width, height):
    payload = json.dumps({
        "image": img_b64,
        "width": width,
        "height": height
    })
    req = urllib2.Request(
        SERVER_URL,
        payload.encode("utf-8"),
        {"Content-Type": "application/json"}
    )
    try:
        response = urllib2.urlopen(req, timeout=5)
        print("Server response:", response.getcode(), response.read())
    except urllib2.HTTPError as e:
        print("HTTP error code:", e.code)
        try:
            print("HTTP error body:", e.read())
        except:
            pass
    except Exception as e:
        print("Send error:", repr(e))

def main():
    disable_auto_reactions()
    freeze_head()

    video = ALProxy("ALVideoDevice", NAO_IP, NAO_PORT)

    sub_id = video.subscribeCamera(
        "nao_stream",
        CAM_INDEX,
        CAM_RESOLUTION,
        CAM_COLORSPACE,
        CAM_FPS
    )

    print("Streaming camera to", SERVER_URL)
    print("Press Ctrl+C to stop.")

    try:
        while True:
            img_data = video.getImageRemote(sub_id)
            if img_data is None:
                print("No image received from camera.")
                time.sleep(0.1)
                continue

            width = img_data[0]
            height = img_data[1]
            raw = bytes(bytearray(img_data[6]))
            img_b64 = base64.b64encode(raw).decode("ascii")

            send_frame(img_b64, width, height)
            print("Frame sent: %dx%d" % (width, height))

            time.sleep(1.0 / CAM_FPS)

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        try:
            video.unsubscribe(sub_id)
        except Exception:
            pass

        try:
            enable_auto_reactions()
        except Exception as e:
            print("Restore warning:", e)

        print("Done.")

if __name__ == "__main__":
    main()
