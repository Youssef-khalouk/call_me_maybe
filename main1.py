from llm_sdk import Small_LLM_Model
import numpy as np
import json
from tkinter import *
import threading
from call_me_maybe.my_model import My_Model


response_lock = threading.Lock()
response = ""

model = Small_LLM_Model()

stop = False
lock = threading.Lock()

def Check_for_stop_and_add_word(word, state) -> bool:
    global response
    with response_lock:
        # ===== Detect "User:" =====
        if word.strip() == "User:":
            return True
        if word.strip() == "User":
            state["user"] = "User"
            return False

        if word.strip() == ":":
            if state["user"] == "User":
                state["user"] = ""
                return True
        
        # ===== Detect "The user says" =====
        if word.strip() == "The":
            state["the_user_says"] = "The"
            return False

        if word.strip() == "user":
            if state["the_user_says"] == "The":
                state["the_user_says"] = "The user"
                return False
            else:
                response += "user"
                return False

        if word.strip() == "says":
            if state["the_user_says"] == "The user":
                state["the_user_says"] = ""
                return True
            else:
                response += "says"
                return False

        if state["user"] != "":
            response ++ state["user"]
            state["user"] = ""

        if state["the_user_says"] != "":
            response += state["the_user_says"]
            state["the_user_says"] = ""
        response += word
    return False

history = ""
model = My_Model()

def ask(quastion):
    global stop, history, response
    response = ""
    prompt = f"{history}\nUser: {quastion} \nAssistant: "
    stop = False
    state = {"user": "", "the_user_says": ""}
    counter = 1
    break_in_dot = False
        

    while True:
        
        word = model.get_next_token(prompt)

        if Check_for_stop_and_add_word(word, state):
            break

        prompt += word

        if word == ".":
            response += "\n"
        if ".\n" in prompt[-4:]:
            break
        if '.' in word and break_in_dot:
            break
        counter+=1
        if counter == 100:
            break_in_dot = True
        with lock:
            if stop:
                break
    if not history.endswith("\n"):
        history += "\n"
    history += f"User: {quastion} \nAssistant: {response} "

    print(history, end="")

root = Tk()

root.geometry("500x500+300+200")

entry = Entry()
entry.pack(padx=40, pady=40, fill='x')

label = Label(root)
label.pack(padx=40, pady=40)

def update_label():
    global response_lock
    with response_lock:
        label.config(text=response)
    root.after(100, update_label)
update_label()



def start_ask():
    label.config(text="")
    t = threading.Thread(target=lambda: ask(entry.get()))
    t.start()

b_ask = Button(root, text="ask", command= start_ask, justify="center", width=10)
b_ask.pack(padx=40, pady=40, side="left")



def clean_history():
    global history, response, response_lock
    history = ""
    with response_lock:
        response = ""
        label.config(text=response)
    entry.config(text="")


clean = Button(root, text="clean history", command=clean_history, justify="center", width=10)
clean.pack(padx=40, pady=40, side="left")

def st():
    global stop
    with lock:
        stop = True

finish = Button(root, text="stop", command=st, justify="center", width=10)
finish.pack(padx=40, pady=40, side="left")

def on_close():
    global stop
    with lock:
        stop = True
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()