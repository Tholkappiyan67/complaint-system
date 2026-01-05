from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash



app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE CONNECTION ----------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="thols",   # <-- change this
        database="complaint_system"
    )

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username=%s",
            (username,)
        )
        user = cur.fetchone()
        db.close()

        if user and check_password_hash(user[2], password):
            if user[3] == "admin":
                error = "Admin must login from Admin Login page"
            else:
                session["username"] = username
                session["role"] = "user"
                return redirect(url_for("complaint"))
        else:
            error = "Invalid username or password"

    # ✅ THIS RETURN WAS MISSING (MAIN FIX)
    return render_template("login.html", error=error)





# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)


        db = get_db()
        cur = db.cursor()

        # check if user already exists
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            error = "Username already exists"
            db.close()
        else:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            db.commit()
            db.close()
            return redirect(url_for("login"))

    return render_template("register.html", error=error)

# ---------------- SUBMIT COMPLAINT ----------------
@app.route("/complaint", methods=["GET", "POST"])
def complaint():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        text = request.form["complaint"]

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO complaints (username, complaint, status) VALUES (%s, %s, %s)",
            (session["username"], text, "Pending")
        )
        db.commit()
        db.close()

        return redirect(url_for("status"))

    return render_template("complaint.html")


# ---------------- VIEW STATUS ----------------
@app.route("/status")
def status():
    if "username" not in session:
        return redirect(url_for("login"))

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM complaints WHERE username=%s",
        (session["username"],)
    )
    data = cur.fetchall()
    db.close()

    return render_template("status.html", data=data)
# ---------------- ADMIN PANEL ----------------
@app.route("/admin")
def admin():
    if "username" not in session or session.get("role") != "admin":
        return redirect(url_for("admin_login"))

    db = get_db()
    cur = db.cursor()

    # fetch all complaints
    cur.execute("SELECT * FROM complaints")
    complaints = cur.fetchall()

    # dashboard counts
    cur.execute("SELECT COUNT(*) FROM complaints")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'")
    pending = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM complaints WHERE status='In Progress'")
    in_progress = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'")
    resolved = cur.fetchone()[0]

    db.close()

    return render_template(
        "admin.html",
        complaints=complaints,
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved
    )




# ---------------- UPDATE STATUS ----------------
@app.route("/update_status/<int:complaint_id>", methods=["POST"])
def update_status(complaint_id):
    if "username" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))

    new_status = request.form["status"]

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE complaints SET status=%s WHERE id=%s",
        (new_status, complaint_id)
    )
    db.commit()
    db.close()

    return redirect(url_for("admin"))


# ---------------- ADMIN LOGIN ----------------
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username=%s AND role='admin'",
            (username,)
        )
        admin = cur.fetchone()
        db.close()

        if admin and check_password_hash(admin[2], password):
            session["username"] = username
            session["role"] = "admin"
            return redirect(url_for("admin"))
        else:
            error = "Invalid admin credentials"

    return render_template("admin_login.html", error=error)




# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run()
