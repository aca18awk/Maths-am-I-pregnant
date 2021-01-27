import csv
import os
import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

def get_contraceptions():
  with open('app/static/contraception.csv') as csv_file:
    data = csv.reader(csv_file, delimiter=',')
    first_line = True
    contraceptions = []
    for row in data:
      if not first_line:
        contraceptions.append({
          "id": str(row[0]).replace(" ", ""),
          "name": row[0],
          "likelihood": row[1]
        })
      else:
        first_line = False
  return contraceptions

def get_days():
  with open('app/static/date.csv') as csv_file:
    data = csv.reader(csv_file, delimiter=',')
    first_line = True
    days = []
    for row in data:
      if not first_line:
        days.append({
          "day": row[0],
          "likelihood": row[1]
        })
      else:
        first_line = False
  return days

@app.route("/")
def index():
  contraceptions = get_contraceptions()
  return render_template("index.html", contraceptions=contraceptions, response='')

@app.route("/submit", methods=["GET", "POST"])
# def submit():
#   contraceptions = get_contraceptions()
#   return render_template("index.html", contraceptions=contraceptions, response='', description='')
def submit():
  contraceptions = get_contraceptions()

  if request.method == "GET":
    return render_template("index.html", contraceptions=contraceptions, response='')

  elif request.method == "POST":
    if_had_sex = request.form.get('if-had-sex')
    when_had_sex = request.form.get('when-had-sex')
    last_period = request.form.get('last-period')
    menstrual_cycle = request.form.get('menstrual-cycle')
    ovulation_given = request.form.get('ovulation-day')

    if if_had_sex == "yes":
      beginning = datetime.datetime.strptime(last_period, "%Y-%m-%d")
      if ovulation_given == "":
        ovulation = beginning + datetime.timedelta(days=int(menstrual_cycle) - 14 - 1)
      else:
        ovulation = datetime.datetime.strptime(ovulation_given, "%Y-%m-%d")
      coitous = datetime.datetime.strptime(when_had_sex, "%Y-%m-%d")
      difference = (coitous - ovulation).days
      
      days = [-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2]
      younger = [0.0042, 0.0119, 0.0308, 0.0820, 0.2565, 0.2971, 0.5336, 0.3221, 0.1010, 0.0232, 0.0210]
      older   = [0.0039, 0.0108, 0.0265, 0.0658, 0.1728, 0.1951, 0.2901, 0.2029, 0.0798, 0.0205, 0.0187]

      if request.form.get('age') == "younger":
        probability = 0.0042
        age_response = "(19-26)"
        for (index,day) in enumerate(days):
          if difference == day:
            probability = younger[index]
            break 
      else:
        probability = 0.0039
        age_response = "(35-39)"
        for (index,day) in enumerate(days):
          if difference == day:
            probability = older[index]
            break         

      if difference < 0:
        date_response = str(difference*(-1)) + " days before the ovulation is: " + str(round(probability*100,2)) + "%."
      elif difference == 0:
        date_response = "in the day of the ovulation is: "+ str(round(probability*100,2)) + "%."
      else:   
        date_response = str(difference) + " days after the ovulation is: " + str(round(probability*100,2)) + "%."
      
      contraception_response = ""
      for contraception in contraceptions:
        if request.form.get(contraception["id"]) == contraception["id"] and contraception["id"] != "None":
          probability *= float(contraception["likelihood"])
          if contraception_response != "":
            contraception_response += ", "
          contraception_response+= contraception["name"] + ": " + str(100 - round(float(contraception["likelihood"]) * 100,2)) + "%"
      
   
    ovulation_date = ovulation.strftime("%d") + " " +ovulation.strftime("%b") + " " + ovulation.strftime("%Y")
    response = {
      "probability": round(probability*100,2),
      "ovulation": ovulation_date,
      "age": age_response,
      "date": date_response,
      "contraception": contraception_response
    }    
    return render_template("response.html", contraceptions=contraceptions, response=response)

