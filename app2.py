import socket
import cv2, numpy, threading

ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # server socket for sending
cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # client socket for recieving

ss.bind(("192.168.43.145", 3033))
ss.listen(5)

cs.connect(("192.168.43.2", 2022))  # send request to server2 for connection

c_s, addr = ss.accept()  # accept connection request to server socket
print("Connected to - ", addr)
cs.settimeout(1)
flag = -1

cap = cv2.VideoCapture(0)  # start capture video form external camera


def send():
    global cap
    while True:
        if flag == 0:
            break
        try:
            ret, photo = cap.read()  # read images
            b_img = cv2.imencode(".jpg", photo)[1].tobytes()  # first encode and then convert to bytes
            c_s.sendall(b_img)  # send images
        except:
            continue
    cap.release()  # release camera after the function is done sending
    ss.close()  # close the server (sending ) socket


def receive():
    global flag,cap
    while True:
        try:
            mess = cs.recv(100000)  # recieve 1 lack bytes of data
            if mess:
                nparr = numpy.frombuffer(mess, numpy.uint8)  # retreive the array form bytes
                img1 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # create image from array

                # adding the image image being sent in top left corner
                ret, photo1 = cap.read()
                resized = cv2.resize(photo1, (150, 150), interpolation=cv2.INTER_AREA)
                img1[10:160, 10:160] = resized
                img1 = cv2.rectangle(img1, (0, 0), (170, 170), (0, 0, 250), 3)

                # showing the final images
                cv2.imshow("From server1.ipynb", img1)
                if cv2.waitKey(10) == 13:  # if user press enter break the loop
                    break
        except:
            continue
    flag = 0
    cv2.destroyAllWindows()  # destroy the image window
    cs.close()  # close client (reciever) socket


# Putting the send and recieve functions in different thread so they can run in parallel
t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=send)
t1.start()
t2.start()  #