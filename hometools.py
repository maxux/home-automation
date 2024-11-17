import serial
import time
import sys
import traceback
from readserial import ReadLine
from flask import Flask, request, abort, render_template, jsonify

class HomeTools:
    def __init__(self):
        self.app = Flask(__name__, static_url_path='/static')

        self.board = serial.Serial("/dev/ttyACM0", 9600)
        self.reader = ReadLine(self.board)

    def hardread(self):
        try:
            line = self.reader.readline()
            data = line.decode('utf-8').strip()

            print(f"[<] {data}")

            return data

        except Exception:
            traceback.print_exc()
            return

    def hardwait(self):
        print("[+] waiting for arduino ready state")

        while True:
            data = self.hardread()

            if data == "core: waiting for user input":
                print("[+] arduno ready, starting up web server")
                break

    def routes(self):
        @self.app.route('/trigger/<id>', methods=['GET'])
        def hardware_trigger_id(id):
            value = int(id)
            if value < 0 or value > 6:
                abort(401)

            self.board.write(f"{value}".encode("utf-8"))
            data = self.hardread()

            return jsonify({"status": data})

        @self.app.route('/', methods=['GET'])
        def index():
            return render_template("index.html")

    def listen(self):
        print("[+] listening")
        self.app.run(host="0.0.0.0", port=80, debug=True, use_reloader=False, threaded=True)

if __name__ == "__main__":
    home = HomeTools()
    home.hardwait()
    home.routes()
    home.listen()
