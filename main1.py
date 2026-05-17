from llm_sdk import Small_LLM_Model
import numpy as np
import json
from tkinter import *
import threading
import re

response_lock = threading.Lock()
response = ""

model = Small_LLM_Model()

stop = False
lock = threading.Lock()

vocab_path = model.get_path_to_vocab_file()
tokenizer_path = model.get_path_to_tokenizer_file()


with open(vocab_path, "r", encoding="utf-8") as file:
    vocab_dict = json.loads(file.read())


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

def remove_spaces(word):
    for i, ch in enumerate(word):
        if ch != " ":
            return (word[i:])
    return word


def splite_one_word(word):
    array = []
    buffer = ""
    for ch in word:
        if ch.isalpha() or ch == ' ' or ch == '\n':
            buffer += ch
        else:
            if buffer != "":
                array.append(buffer)
                buffer = ""
            array.append(ch)
    if buffer != "":
        array.append(buffer)
        buffer = ""
    return array


def encode(prompt) -> list[int]:
    global vocab_dict
    # words = prompt.split()
    words = re.findall(r'\s*\S+', prompt)

    tokens: list[int] = []

    for word in words:
        token_id = vocab_dict.get(word, -1)
        if token_id == -1:
            subwords = splite_one_word(word)
            for subword in subwords:
                subword = remove_spaces(subword)
                if subword.startswith("\n"):
                    tokens.append(715)
                sub_token_id = vocab_dict.get(subword.strip(), -1)
                if sub_token_id == -1:
                    # print(f"cant find this -> '{subword}'")
                    for i in subword:
                        ww = vocab_dict.get(i, -1)
                        if ww != -1:
                            tokens.append(ww)
                else:
                    tokens.append(sub_token_id)
        else:
            tokens.append(token_id)
    return tokens

def ask(quastion):
    global stop, history, response
    response = ""
    prompt = f"History: {history}\nUser:{quastion} \nAssistant: "
    stop = False
    state = {"user": "", "the_user_says": ""}
    counter = 1
    break_in_dot = False

    while True:
        tokens = model.encode(prompt)
        tokens_array = tokens[0].tolist()
        # print("the package encode ->> " + str(tokens_array))

        tokens = encode(prompt);
        tokens_array = tokens

        # print("my function encode ->> " + str(tokens_array))

        predictions = model.get_logits_from_input_ids(tokens_array)

        # next_token = np.argmax(predictions)

        next_token = np.argpartition(predictions, -2)

        word = model.decode(next_token[-1])
        # print(f"the word is -> '{word}'")
        # print(next_token[-1])
        # word1 = model.decode(next_token[-2])

        # word = word.strip()

        if (response and response[-1] !=" " and response[-1] != "\n") and word.strip() not in ["\n", ",", "!", "?", "."]:
            response += " "

        if response and (response[-1] == "\n" or response.endswith("\n ")) and word.strip() == "\n":
            break
        if prompt.endswith("\n\n") or prompt.endswith("\n \n"):
            break

        if Check_for_stop_and_add_word(word, state):
            break
        
        if (prompt[-1] !=" " and prompt[-1] != "\n") and word not in ["\n", ",", "!", "?", "."]:
            prompt += " "
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