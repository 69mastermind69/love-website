from flask import Flask, render_template, request, redirect, url_for
import os
import psycopg

app = Flask(__name__)


# --------------------------------
# Database connection
# --------------------------------

def get_database_url():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set."
        )

    # Some PostgreSQL URLs may use postgres://
    # psycopg expects postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    return database_url


def get_connection():
    return psycopg.connect(get_database_url())


# --------------------------------
# Create database table
# --------------------------------

def init_database():

    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    birthday TEXT,
                    favorite_color TEXT,
                    love_answer TEXT,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

        conn.commit()


# --------------------------------
# Home page
# --------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------
# Submit response
# --------------------------------

@app.route("/submit", methods=["POST"])
def submit():

    name = request.form.get(
        "name",
        ""
    ).strip()

    birthday = request.form.get(
        "birthday",
        ""
    ).strip()

    favorite_color = request.form.get(
        "favorite_color",
        ""
    ).strip()

    # Supports either name for your existing form
    love_answer = request.form.get(
        "love_answer",
        ""
    ).strip()

    if not love_answer:
        love_answer = request.form.get(
            "love",
            ""
        ).strip()

    message = request.form.get(
        "message",
        ""
    ).strip()


    # Name is required
    if not name:

        return "Name is required.", 400


    # Save to PostgreSQL
    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO responses
                (
                    name,
                    birthday,
                    favorite_color,
                    love_answer,
                    message
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    name,
                    birthday,
                    favorite_color,
                    love_answer,
                    message
                )
            )

        conn.commit()


    return redirect(
        url_for("thank_you")
    )


# --------------------------------
# Thank you page
# --------------------------------

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


# --------------------------------
# Responses page
# --------------------------------

@app.route("/responses")
def responses_page():

    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    id,
                    name,
                    birthday,
                    favorite_color,
                    love_answer,
                    message,
                    created_at
                FROM responses
                ORDER BY id DESC
            """)

            responses = cur.fetchall()


    return render_template(
        "responses.html",
        responses=responses
    )


# --------------------------------
# Start app
# --------------------------------

if __name__ == "__main__":

    # Create table when running locally
    init_database()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
