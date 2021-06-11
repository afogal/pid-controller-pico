from mqtt_client import MQTTClient
import json, sys, time
import datetime as dt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QPlainTextEdit
from PyQt5 import QtWidgets, QtCore, QtGui
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # main window
        self.setWindowTitle("PID Command")
        self.setGeometry(100,100,1300,850)
        color = self.palette().color(QtGui.QPalette.Window)  # Get the default window background,
        styles = {"color": "#000", "font-size": "20px"}

        # create, move, show graphs
        self.therm_graph = pg.PlotWidget(parent=self,axisItems = {'bottom': pg.DateAxisItem()})
        self.therm_graph.move(20,20)
        self.therm_graph.resize(600,400)
        self.therm_graph.show()
        self.therm_graph.setBackground(color)
        self.therm_graph.setTitle("Measured Temperature", color="k", size="20pt")
        self.therm_graph.setLabel("left", "Temperature (°C)", **styles)
        self.therm_graph.setLabel("bottom", "Time", **styles)
        self.therm_graph.addLegend()
        self.therm_graph.showGrid(x=True, y=True)

        self.curr_graph = pg.PlotWidget(parent=self,axisItems = {'bottom': pg.DateAxisItem()})
        self.curr_graph.move(650,20)
        self.curr_graph.resize(600,400)
        self.curr_graph.show()
        self.curr_graph.setBackground(color)
        self.curr_graph.setTitle("Output Current", color="k", size="20pt")
        self.curr_graph.setLabel("left", "Current (A)", **styles)
        self.curr_graph.setLabel("bottom", "Time", **styles)
        self.curr_graph.addLegend()
        self.curr_graph.showGrid(x=True, y=True)

        self.mqtt_label = QLabel('MQTT:', parent=self)
        self.mqtt_label.move(650, 450)
        self.mqtt_label.resize(200,50)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.mqtt_label.setFont(font)
        self.mqtt_label.show()

        self.text = QPlainTextEdit(parent=self)
        self.text.move(650, 520)
        self.text.resize(600,300)
        self.text.show()
        self.text.setReadOnly(True)

        self.temp_send = QLineEdit(parent=self)
        self.temp_send.move(20, 520)
        self.temp_send.resize(60, 30)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.temp_send.setFont(font)
        self.temp_send.show()

        self.curr_send = QLineEdit(parent=self)
        self.curr_send.move(20, 570)
        self.curr_send.resize(60, 30)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.curr_send.setFont(font)
        self.curr_send.show()

        self.command_label = QLabel('Commands:', parent=self)
        self.command_label.move(20, 450)
        self.command_label.resize(200,50)
        font = QtGui.QFont()
        font.setPointSize(24)
        self.command_label.setFont(font)
        self.command_label.show()

        self.temp_send_btn = QPushButton("Set Temp", parent=self)
        self.temp_send_btn.move(90, 520)
        self.temp_send_btn.resize(80, 30)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.temp_send_btn.setFont(font)
        self.temp_send_btn.show()
        self.temp_send_btn.clicked.connect(self.settemp)

        self.curr_send_btn = QPushButton("Set Curr", parent=self)
        self.curr_send_btn.move(90, 570)
        self.curr_send_btn.resize(80, 30)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.curr_send_btn.setFont(font)
        self.curr_send_btn.show()
        self.curr_send_btn.clicked.connect(self.setcurr)

        self.toggle_btn = QPushButton("Toggle Output", parent=self)
        self.toggle_btn.move(60, 620)
        self.toggle_btn.resize(110, 30)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.toggle_btn.setFont(font)
        self.toggle_btn.show()
        self.toggle_btn.clicked.connect(self.toggle)

        self.ack_led = QLabel("",parent=self)
        self.ack_led.move(20, 670)
        self.ack_led.resize(30,30)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.ack_led.setFont(font)
        self.ack_led.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.ack_led.setText("")
        self.ack_led.setPixmap(QtGui.QPixmap("icons/green-led-on.png"))
        self.ack_led.setScaledContents(True)
        self.ack_led.show()

        self.ack_label = QLabel('Command Acked', parent=self)
        self.ack_label.move(60, 660)
        self.ack_label.resize(200, 50)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.ack_label.setFont(font)
        self.ack_label.show()

        self.toggle_led = QLabel("",parent=self)
        self.toggle_led.move(20, 620)
        self.toggle_led.resize(30,30)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.toggle_led.setFont(font)
        self.toggle_led.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.toggle_led.setText("")
        self.toggle_led.setPixmap(QtGui.QPixmap("icons/green-led-on.png"))
        self.toggle_led.setScaledContents(True)
        self.toggle_led.show()

        # init mqtt
        self.acked = True
        self.ack_time = time.time()
        #self.init_mqtt()

        self.therm_data = []
        self.therm_set_data = []
        self.curr_data =[]
        self.curr_set_data = []
        self.time = []

        # plot empty data
        self.therm = self.plot(self.therm_graph, self.time, self.therm_data, "pico", "r")
        self.therm_set = self.plot(self.therm_graph, self.time, self.therm_set_data, "set", "k")

        self.curr = self.plot(self.curr_graph, self.time, self.curr_data, "pico", "r")
        self.curr_set = self.plot(self.curr_graph, self.time, self.curr_set_data, "set", "k")

    def plot(self, graph, x, y, name, color):
        if name == "set":
            pen = pg.mkPen(color=color, width=4, style=QtCore.Qt.DashLine)
        else:
            pen = pg.mkPen(color=color, width=4)

        return graph.plot(x, y, name=name, pen=pen)

    def init_mqtt(self):
        self.client = MQTTClient("server", "password", service_host="192.168.0.103", secure=False, port=5005)
        self.client.on_message = self.recv
        try:
            self.client.connect()
        except:
            self.conn = False
            return -1

        time.sleep(0.5)
        self.client.subscribe("state", feed_user='pico')
        self.client.subscribe("warnings", feed_user='pico')
        self.client.subscribe("ack", feed_user='pico')
        time.sleep(0.5)

        self.client.loop_background()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.poll)
        self.timer.start()

    def recv(self, client, feed_id, payload):
        self.append_line(f"Got message from {feed_id}")

        if feed_id == "ack" and payload == "ACK":
            self.acked = True
            self.ack_time = time.time()
        elif feed_id == "state":
            state = json.dumps(payload)
            self.therm_data.append(state['temp'])
            self.curr_data.append(state['curr'])
            self.therm_set_data.append(state['state']['setTemp'])
            self.curr_set_data.append(state['state']['setCurrent'])
            self.time.append(time.time())

            self.outputToggle = state['state']['outputToggle']
            self.constCurr = state['state']['constCurr']

            # log these probably here

            self.therm.setData(self.time, self.therm_data)
            self.therm_set.setData(self.time, self.therm_set_data)
            self.curr.setData(self.time, self.curr_data)
            self.curr_set.setData(self.time, self.curr_set_data)
            t = self.time[-1]
            self.therm_graph.setXRange(t-600, t+1, padding=0) # display 10mins of data
            self.curr_graph.setXRange(t-600, t+1, padding=0)

    def append_line(self, line):
        new = '\n' + line
        self.text.insertPlainText(new)

    def poll(self):
        # this function is run on a timer
        # originally i had this checking for new messages
        # but there was actually a better function that handles background threads
        # seems a little smarter that way
        #self.client.loop(timeout_sec=0.1)

        # check that commands are acknowledged
        td = time.time() - self.ack_time
        if not self.acked and td >= 20:
            self.append_line(f"No ack for {td} seconds!!")
            self.ack_time = time.time()

        # indicator if command has been acknowledged
        if self.acked:
            self.ack_led.setPixmap(QtGui.QPixmap("icons/green-led-on.png"))
        else:
            self.ack_led.setPixmap(QtGui.QPixmap("icons/red-led-on.png"))

        # output toggle led
        if self.outputToggle:
            self.toggle_led.setPixmap(QtGui.QPixmap("icons/green-led-on.png"))
        else:
            self.toggle_led.setPixmap(QtGui.QPixmap("icons/red-led-on.png"))

    def settemp(self):
        try:
            temp = float(self.temp_send.text())

            command = {"command": "settemp", "temp": temp}
            self.client.publish("commands", json.dumps(command))
            self.acked = False
            self.ack_time = time.time()
        except ValueError:
            self.append_line("Cannot set temp: couldnt convert string to float")

    def setcurr(self):
        try:
            curr = float(self.curr_send.text())

            command = {"command": "setcurr", "curr": curr}
            self.client.publish("commands", json.dumps(command))
            self.acked = False
            self.ack_time = time.time()
        except ValueError:
            self.append_line("Cannot set curr: couldnt convert string to float")

    def toggle(self):
        command = {"command": "toggleOutput", "toggle" : self.outputToggle}
        self.client.publish("commands", json.dumps(command))
        self.acked = False
        self.ack_time = time.time()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())