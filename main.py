from flask import Flask, render_template, request, session, redirect, jsonify
import secrets
import random
import re

def has_link(text):
    return len(re.findall(r'\b(?:https?|ftp):\/\/[-A-Z0-9+&@#/%?=~_|!:,.;]*[-A-Z0-9+&@#/%=~_|]', text, re.IGNORECASE)) > 0

def htmlspecialchars(text):
    return (
        text.replace("&", "&amp;").
        replace('"', "&quot;").
        replace("<", "&lt;").
        replace(">", "&gt;")
    )

class MarkovChain:
    def __init__(self, order=1):
        self.order = order
        self.prefix_dict = {}

    def add(self, text):
        words = list(text)
        for n in range(1, self.order+1):
            for i in range(len(words) - n):
                prefix = tuple(words[i:i+n])
                suffix = words[i+n]
                if prefix in self.prefix_dict:
                    self.prefix_dict[prefix].append(suffix)
                else:
                    self.prefix_dict[prefix] = [suffix]

    def generate(self, prompt, chars_to_generate, include_prompt):
        prompt_trimmed = prompt

        while len(prompt_trimmed) > 0:
            result = self.generate_raw(prompt_trimmed, chars_to_generate)
            if result != "":
                if include_prompt:
                    return prompt + result
                else:
                    return result
            prompt_trimmed = prompt_trimmed[1:]
        return prompt

    def generate_raw(self, prompt, chars_to_generate):
        if prompt is None:
            prefix = random.choice(list(self.prefix_dict.keys()))
        else:
            prefix = tuple(prompt)
        words = list(prefix)
        new_words = []
        while len(words) < chars_to_generate + len(prompt):
            if prefix not in self.prefix_dict:
                break
            suffix = random.choice(self.prefix_dict[prefix])
            words.append(suffix)
            new_words.append(suffix)
            prefix = tuple(words[-self.order:])
        return ''.join(new_words)


chain = MarkovChain(order=14)

app = Flask(__name__, template_folder="templates", static_folder="static")

with open("corpus.txt", "r", encoding="utf-8") as file:
    preloaded_corpus = file.read()
    for line in file.readlines():
        chain.add(preloaded_corpus)

session_training_data = {

}

# CHANGE THIS WHEN DEPLOYING
app.secret_key = ""

@app.route("/", methods=["GET"])
def main():
    if "agreedToTerms" in session:
        if session["agreedToTerms"]:
            return render_template("index.html")
        else:
            return render_template("terms.html")
    else:
        return render_template("terms.html")

@app.route("/autopilot", methods=["GET"])
def autopilot():
    if "agreedToTerms" in session:
        if session["agreedToTerms"]:
            return render_template("autopilot.html")
        else:
            return render_template("terms.html")
    else:
        return render_template("terms.html")

@app.route("/main", methods=["GET"])
def main_redirect():
    return redirect("/")

@app.route("/agree", methods=["GET"])
def agree():
    session["agreedToTerms"] = True
    return redirect("/")

@app.route("/send-message", methods=["POST"])
def send_message():
    payload = request.get_json()

    if "message" not in payload or "trainModel" not in payload:
        return jsonify({
            "message" : "",
            "reply" : "",
            "success" : False
        })

    if len(payload["message"]) <= 0 or len(payload["message"]) > 100 or has_link(payload["message"]):
        return jsonify({
            "message" : htmlspecialchars(payload["message"]),
            "reply" : "",
            "success" : False
        })
    else:
        if "uniqueConversationID" in session and payload["trainModel"]:
            if session["uniqueConversationID"] in session_training_data:
                prompt = session_training_data[session["uniqueConversationID"]][-20:]
            else:
                prompt = ""
        else:
            prompt = ""
        prompt += payload["message"].replace("§", "").replace("\n", "").strip() + "§"
    message = chain.generate(prompt, 1, False)
    while message[-1:] != "§":
        message = chain.generate(message, 1, True)
    
    if message.replace(".", "").lstrip().rstrip().replace("§", "") == "":
        message = "I don't understand.§"
    
    if payload["trainModel"]:
        if "uniqueConversationID" in session:
            if session["uniqueConversationID"] in session_training_data:
                session_training_data[session["uniqueConversationID"]] += payload["message"].replace("§", "") + "§" + message
            else:
                id = str(random.randint(100000, 999999))
                session["uniqueConversationID"] = id
                session_training_data[id] = "§" + payload["message"].replace("§", "") + "§" + message
        else:
            id = str(random.randint(100000, 999999))
            session["uniqueConversationID"] = id
            session_training_data[id] = "§" + payload["message"].replace("§", "") + "§" + message

        chain.prefix_dict.clear()

        chain.add(preloaded_corpus)

        corpus_to_save = preloaded_corpus

        for key in session_training_data.keys():
        #     if len(key) > 4000:
        #         while len(key) > 4000 or key[0] != "§":
        #             key = key[1:]
            chain.add(session_training_data[key])
            corpus_to_save += "\n" + session_training_data[key]

        with open("corpus.txt", "w", encoding="utf-8") as file:
            file.write(corpus_to_save)
    
    result = {
        "message" : htmlspecialchars(payload["message"]),
        "reply" : htmlspecialchars(message[:-1]),
        "success" : True
    }

    return jsonify(result)

if __name__ == "__main__":
    app.run()
