from llm_sdk import Small_LLM_Model
import numpy as np
import json
from tkinter import *
import threading

response_lock = threading.Lock()
response = ""

model = Small_LLM_Model()

stop = False
lock = threading.Lock()

vocab_path = model.get_path_to_vocab_file()


with open(vocab_path, "r", encoding="utf-8") as file:
    vocab_dict = json.loads(file.read())

id_to_token = {}
for key, value in vocab_dict.items():
    id_to_token[value] = key

def split(prompt):
    tokens = []
    word = ""
    for i, ch in enumerate(prompt):
        if ch == " ":
            if word != "":
                tokens.append(word)
                word = " "
        else:
            word += ch
        if i == len(prompt) - 1 and word != "":
            tokens.append(word)
    for i in range(len(tokens)):
        word = list(tokens[i])
        for x in range(len(word)):
            if word[x] == " ":
                word[x] = "Ġ"
        tokens[i] = "".join(word)
    return tokens


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

def encode_word(word):
    tokens = []
    start = 0

    while start < len(word):
        found = False
        for end in range(len(word), start, -1):
            piece = word[start:end]
            token_id = vocab_dict.get(piece)
            if token_id is not None:
                tokens.append(token_id)
                start = end
                found = True
                break
        if not found:
            start += 1
    return tokens

def encode(prompt) -> list[int]:
    global vocab_dict

    words = split(prompt)

    tokens: list[int] = []

    for word in words:
        to = encode_word(word)
        for i in to:
            tokens.append(i)
    return tokens


def decode(token_id):
    if token_id == 5267:
        return "?\n"
    word = id_to_token.get(token_id, "")

    word = word.replace("Ġ", " ")

    return word

# print ("'\\n' --> " + str(model.encode("\n")))
# print ("' Hi' --> " + str(vocab_dict.get("ĠHi", -1)))
# print ("'?Ċ' --> '" + str(model.decode(5267))+"'")

def ask(quastion):
    global stop, history, response
    response = ""
    prompt = f"{history}\nUser: {quastion} \nAssistant: "
    stop = False
    state = {"user": "", "the_user_says": ""}
    counter = 1
    break_in_dot = False

    while True:
        # tokens = model.encode(prompt)
        # tokens_array = tokens[0].tolist()

        tokens_array = encode(prompt)

        predictions = model.get_logits_from_input_ids(tokens_array)

        # next_token = np.argmax(predictions)

        next_token = np.argpartition(predictions, -2)
        print(next_token[-1])
        # word = model.decode(next_token[-1])
        word = decode(next_token[-1])
        # print(f"code: {next_token[-1]} value: {word}")
        # if prompt.endswith("\n\n") or prompt.endswith("\n \n"):
        #     break

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

    # print(prompt)

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