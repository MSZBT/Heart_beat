import json
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

current_order = {} #порядок спортсменов

@app.route("/")
def init():
    return render_template("index.html")

@app.route("/manage")
def manager():
    return render_template("manager_page.html")

@app.route('/update_order', methods=['POST'])
def update_order():
    global current_order
    current_order = request.json
    return jsonify({"status": "success"})

@app.route('/get_order')
def get_order():
    print(current_order)
    return jsonify(current_order)

@app.route("/get_heart_rate")  
def get_heart_rate():
    data = get_data()
    return jsonify(data)  

def get_data():
    try:
        with open("TRANSMIT.json", "r") as f:
            data = json.load(f)
            print("Current heart rates:", data)
            return data
    except FileNotFoundError:
        print("Data file not found yet")
        return {"error": "Data not available"}

if __name__ == "__main__":
    app.run(host="192.168.10.34", port="8080")