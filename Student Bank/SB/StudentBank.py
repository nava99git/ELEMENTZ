from flask import Flask, render_template, request
from flask_table import Table, Col
import datetime
import sqlite3

app = Flask(__name__)
@app.route("/")
def hello():
   return render_template('index.html')

@app.route("/LoginCred", methods=['POST'])
def login():
   StudentID = int(request.form['Student_ID'])
   Pin = int(request.form['Pin'])
   LogSt = 0
   conn = sqlite3.connect('StudentBankDB.db')
   cur = conn.cursor()
   try:
      cur.execute("SELECT PIN FROM Students WHERE ID='%d'" % (StudentID))
      PIN_DB = int(cur.fetchone()[0])
      cur.execute("SELECT NoofTry FROM Students WHERE ID='%d'" % (StudentID))
      NoofTry = int(cur.fetchone()[0])
      print(NoofTry)
      if Pin == PIN_DB and NoofTry <= 3:
         print("Succesful Login")
         LogSt = 1
      else:
         print("Invalid Pin")
         LogSt = -1
   except:
      print("Invalid Student ID")
 
   if LogSt == 1 and NoofTry != -1:
      conn.close()
      templateData = {'ID': StudentID}
      return render_template('dashboard.html', **templateData)

   elif LogSt == 1 and NoofTry == -1:
      conn.close()
      templateData = {'ID': StudentID}
      return render_template('ChangePin.html', **templateData)

   elif LogSt == -1:
      conn.close()
      return render_template('index.html')

   else:
      cur.execute("UPDATE Students set NoofTry = NoofTry + 1 WHERE ID='%d'" % (StudentID))
      conn.commit()
      conn.close()
      templateData = {'LoginError': 'Invalid ID/PIN'}
      return render_template('index.html', **templateData)

@app.route("/ChangePin", methods=['POST'])
def changepin():
   ID = int(request.form['StudentID'])
   NewPin = int(request.form['NewPin'])
   ConfirmPin = int(request.form['ConfirmPin'])
   if NewPin == ConfirmPin:
      conn = sqlite3.connect('StudentBankDB.db')
      cur = conn.cursor()
      try:
         cur.execute("SELECT PIN FROM Students WHERE ID='%d'" % (ID))
         PIN_DB = int(cur.fetchone()[0])
         if NewPin == PIN_DB:
            print("Same as previous password")
            templateData = {'Error':"Same as previous password"}
            conn.close()
            return render_template('ChangePin.html', **templateData)
         else:
            cur.execute("UPDATE Students set PIN = %d WHERE ID='%d'" % (NewPin, ID))
            cur.execute("UPDATE Students set NoofTry = 0 WHERE ID='%d'" % (ID))
            conn.commit()
            conn.commit()
            conn.close()
            print("Pin Changed Succesfully")
            templateData = {'ID': ID}
            return render_template('dashboard.html', **templateData)
      
      except:
         print("Invalid ID")
         templateData = {'LoginError': 'ID was changed'}
         return render_template('index.html', **templateData)
   else:
      print("Pins do not match")
      templateData = {'Error':"Pins do not match", 'ID': ID }
      return render_template('ChangePin.html', **templateData)

@app.route("/Transactions", methods=['POST'])
def Transactions():
   class ItemTable(Table):
      name = Col('Name')
      description = Col('Description')
   items = [Item('Name1', 'Description1'),
         Item('Name2', 'Description2'),
         Item('Name3', 'Description3')]
   table = ItemTable(items)
   templateData = {'ID': ID, 'Table': table}
   return render_template('dashboard.html', **templateData)

# @app.route("/<deviceName>/<action>")
# def action(deviceName, action):
#    if action == "on":
#       print("Button ON")
#    if action == "off":
#       print("Button OFF")
#    now = datetime.datetime.now()
#    timeString = now.strftime("%Y-%m-%d %H:%M")
#    templateData = {
#       'title' : 'HELLO!',
#       'time': timeString
#       }
#    return render_template('index.html', **templateData)

if __name__ == "__main__":
   app.run(host='192.168.43.86', port=80, debug=True)
