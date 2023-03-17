
from flask import Flask, render_template, request
import pandas as pd
import re

app = Flask(__name__)
app.static_folder = 'static'

df = pd.read_sas("adsl.xpt", encoding="utf-8")
df.columns = [x.lower() for x in df.columns]
columns = list(df.columns)

def preprocess_input(s):
  # Split user input into conditions
  split_input = s.split("and")

  s1, s2 = "", ""
  if len(split_input) > 1:
    s1 = split_input[0]
    s2 = split_input[1]
  else:
    s1 = split_input[0]
  
  return s1, s2

def prompt1(s1, s2, data = "adsl"):
  col1, col2 = "", ""

  # String 1
  for w in s1.split(" "):
    if w.lower() in columns:
      col1 = w.lower()
      break
  
  # Find a number in string
  temp = re.findall(r'\d+', s1)
  res = list(map(int, temp))

  # String 2
  for w in s2.split(" "):
    if w.lower() == "treatment":
      if data == "adsl":
        col2 = "trt01a"
      elif data == "adlbc":
        col2 = "trta"
      break
    elif w.lower() in columns:
      col2 = w.lower()
      break

  print(col1, col2)
  if ("greater" in s1) and ("equal" in s1) :
    return len((df.loc[(df[col1] >= res[0]) & (df[col2] == s2.split(" ")[-1])]))
  elif ("lesser" in s1) and ("equal" in s1):
    return len(df.loc[(df[col1] <= res[0]) & (df[col2] == s2.split(" ")[-1])])
  elif "greater" in s1:
    return len(df.loc[(df[col1] > res[0]) & (df[col2] == s2.split(" ")[-1])])
  elif "lesser" in s1:
    return len((df.loc[(df[col1] < res[0]) & (df[col2] == s2.split(" ")[-1])]))
  elif "equal" in s1:
    return len((df.loc[(df[col1] == res[0]) & (df[col2] == s2.split(" ")[-1])]))
  
def prompt2(s, data = "adsl"):
  cols = []

  for w in s.split(" "):
    if w.lower() == "treatment" and data == "adlbc":
      cols.append("trta")
      break
    elif w.lower() == "treatment" and data == "adsl":
      cols.append("trt01a")
      break
    elif w.lower() in columns:
      cols.append(w.lower())
  
  print(cols)

  if "mean" in s and "median" in s and "mode" in s:
    return {
        "Mean": df[df[cols[-1]] == s.split(" ")[-1]][cols[0]].mean(),
        "Median": df[df[cols[-1]] == s.split(" ")[-1]][cols[0]].median(),
        "Mode": df[df[cols[-1]] == s.split(" ")[-1]][cols[0]].mode()[0]
    }
  elif "mean" in s and "median" in s:

    return {
        "Mean": df[df[cols[-1]] == s.split(" ")[-1]][cols[0]].mean(),
        "Median": df[df[cols[-1]] == s.split(" ")[-1]][cols[0]].median(),
    }
  elif "mean" in s and "mode" in s:
    return {
        "Mean": df[df[cols[-1]] == s.split(" ")[-1]][cols[0]].mean(),
        "Mode": df[df[cols[-1]] == s.split(" ")[-1]][cols[0]].mode()[0]
    }
  elif "median" in s and "mode" in s:
    return {
        "Median": df[df[cols[-1]] == s.split(" ")[-1]][cols[0]].median(),
        "Mode": df[df[cols[-1]] == s.split(" ")[-1]][cols[0]].mode()[0]
    }
  elif "mean" in s:
    return {
        "Mean": df[df[cols[-1]] == s.split(" ")[-1]][cols[0]].mean()
    }
  elif "median" in s:
    return {
        "Median": df[df[cols[-1]] == s.split(" ")[-1]][cols[0]].median(),
    }
  elif "mode" in s:
    return {
        "Mode": df[df[cols[-1]] == s.split(" ")[-1]][cols[0]].mode()[0],
    }

def prompt3():
  pass


@app.route("/")
def home():
    return render_template("index.html")
@app.route("/get")
def get_bot_response():

    user_input = request.args.get('msg')
    sen1, sen2 = preprocess_input(user_input)
    print(sen1, sen2)

    if any(word in sen1.lower() for word in ["hello", "hi", "hey"]):
      return "Hi, I'm good. How can I help you ?"
    elif "addverse" in sen1.lower():
      pass
    elif "lab" in sen1.lower():
      pass
    else:
        if any(word in sen1 for word in ["greater", "lesser", "equal"]):
            res = prompt1(sen1, sen2, "adsl")
            print("Chatbot: ", res)
            return str(res)
        elif any(word in user_input for word in ["mean", "median", "mode"]):
            res = prompt2(user_input, "adsl")
            print("Chatbot", res)
            return str(res)

    return "I didn't understood your question, please ask me that in which I'm expert to answer ?"
if __name__ == "__main__":
    app.run(debug=True)