from flask import Flask, render_template, request, redirect, url_for
import os
import psycopg

app = Flask(__name__)


# =========================================================
# DATABASE URL
# =========================================================

def get_database_url():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not set."
        )

    # Convert old postgres:// format if necessary
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    return database_url


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    return psycopg.connect(
        get_database_url()
    )


# =========================================================
# CREATE TABLE
# =========================================================

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

                    created_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                )
            """)

        conn.commit()


# =========================================================
# INITIALIZE DATABASE
# =========================================================

# Render uses:
# gunicorn app:app
#
# Therefore __main__ is not executed.
# So we initialize the database when this module loads.

try:

    init_database()

    print("Database initialized successfully.")

except Exception as e:

    print(
        "Database initialization failed:",
        e
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# SUBMIT RESPONSE
# =========================================================

@app.route(
    "/submit",
    methods=["POST"]
)
def submit():

    # -------------------------
    # Get form data
    # -------------------------

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

    love_answer = request.form.get(
        "love_answer",
        ""
    ).strip()

    # Support old form field name too

    if not love_answer:

        love_answer = request.form.get(
            "love",
            ""
        ).strip()

    message = request.form.get(
        "message",
        ""
    ).strip()


    # -------------------------
    # Validate name
    # -------------------------

    if not name:

        return (
            "Name is required.",
            400
        )


    # -------------------------
    # Save to PostgreSQL
    # -------------------------

    try:

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
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
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


    except Exception as e:

        print(
            "Error saving response:",
            e
        )

        return (
            "Sorry, there was a problem saving your response.",
            500
        )


    # -------------------------
    # Success
    # -------------------------

    return redirect(
        url_for("thank_you")
    )


# =========================================================
# THANK YOU PAGE
# =========================================================

@app.route("/thank-you")
def thank_you():

    return """
<!DOCTYPE html>

<html>

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>Thank You 💗</title>


    <style>

        * {
            box-sizing: border-box;
        }

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

            line-height: 1.5;
        }


        .heart {

            font-size: 70px;
        }


        .powered {

            position: fixed;

            bottom: 10px;

            left: 0;

            width: 100%;

            text-align: center;

            font-size: 12px;

            color: #999;
        }

    </style>

</head>


<body>


    <div class="box">

        <div class="heart">
            💗
        </div>


        <h1>
            Thank You!
        </h1>


        <p>
            Your response has been saved. 🥰
        </p>

    </div>


    <div class="powered">
        Powered by Do_x_Die
    </div>


</body>

</html>
"""


# =========================================================
# RESPONSES
# =========================================================

@app.route("/responses")
def responses_page():

    try:

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


    except Exception as e:

        print(
            "Error loading responses:",
            e
        )

        return (
            "Could not load responses. "
            "Please check the database connection.",
            500
        )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    try:

        with get_connection() as conn:

            with conn.cursor() as cur:

                cur.execute(
                    "SELECT 1"
                )

                cur.fetchone()


        return "OK", 200


    except Exception as e:

        print(
            "Health check database error:",
            e
        )

        return "Database error", 500


# =========================================================
# LOCAL DEVELOPMENT
# =========================================================

if __name__ == "__main__":

    try:

        init_database()

        print(
            "Database initialized successfully."
        )

    except Exception as e:

        print(
            "Database initialization failed:",
            e
        )


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
