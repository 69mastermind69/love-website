from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

# Responses এই file-এ save হবে
DATA_FILE = "responses.json"


def load_responses():
    """Saved responses load করে।"""

    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_responses(responses):
    """Responses JSON file-এ save করে।"""

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            responses,
            file,
            ensure_ascii=False,
            indent=4
        )


# -------------------------
# Main Website
# -------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -------------------------
# Submit Response
# -------------------------

@app.route("/submit", methods=["POST"])
def submit():

    name = request.form.get("name", "").strip()
    birthday = request.form.get("birthday", "").strip()
    favorite_color = request.form.get(
        "favorite_color",
        ""
    ).strip()
    message = request.form.get("message", "").strip()

    # Name required
    if not name:
        return "Name is required.", 400

    # Response তৈরি
    response = {
        "name": name,
        "birthday": birthday,
        "favorite_color": favorite_color,
        "message": message
    }

    # পুরোনো responses load
    responses = load_responses()

    # নতুন response যোগ
    responses.append(response)

    # Save
    save_responses(responses)

    # Thank-you page
    return redirect(url_for("thank_you"))


# -------------------------
# Thank You Page
# -------------------------

@app.route("/thank-you")
def thank_you():

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <meta charset="UTF-8">

        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">

        <title>Thank You 💗</title>

        <style>

            body {
                margin: 0;

                min-height: 100vh;

                display: flex;

                justify-content: center;

                align-items: center;

                text-align: center;

                font-family: Arial, sans-serif;

                background: #fff0f6;
            }

            .box {
                width: 350px;

                max-width: 85%;

                background: white;

                padding: 40px;

                border-radius: 25px;

                box-shadow:
                    0 10px 30px
                    rgba(0, 0, 0, 0.12);
            }

            h1 {
                color: #ff4f87;
            }

            p {
                color: #666;

                font-size: 18px;
            }

        </style>

    </head>


    <body>

        <div class="box">

            <div style="font-size:70px;">
                💗
            </div>

            <h1>
                Thank You!
            </h1>

            <p>
                Your response has been saved. 🥰
            </p>

        </div>

    </body>

    </html>
    """


# -------------------------
# Private Responses Page
# -------------------------

@app.route("/responses")
def responses_page():

    responses = load_responses()

    return render_template(
        "responses.html",
        responses=responses
    )


# -------------------------
# Run Locally
# -------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )