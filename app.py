from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-production"
DB_PATH = Path(__file__).with_name("gym.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            gender TEXT,
            join_date TEXT NOT NULL,
            plan_id INTEGER,
            status TEXT NOT NULL DEFAULT 'Active',
            notes TEXT,
            FOREIGN KEY(plan_id) REFERENCES plans(id)
        );
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            duration_months INTEGER NOT NULL,
            price REAL NOT NULL,
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            method TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER NOT NULL,
            checkin_date TEXT NOT NULL,
            checkin_time TEXT NOT NULL,
            FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS trainers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            specialty TEXT,
            salary REAL DEFAULT 0,
            status TEXT DEFAULT 'Active'
        );
        """)
        if db.execute("SELECT COUNT(*) FROM plans").fetchone()[0] == 0:
            db.executemany("INSERT INTO plans(name,duration_months,price,description) VALUES(?,?,?,?)", [
                ("Monthly", 1, 1200, "One month gym access"),
                ("Quarterly", 3, 3200, "Three months gym access"),
                ("Half Yearly", 6, 5800, "Six months gym access"),
                ("Yearly", 12, 10000, "Twelve months gym access")
            ])
        if db.execute("SELECT COUNT(*) FROM members").fetchone()[0] == 0:
            today = date.today().isoformat()
            db.execute("INSERT INTO members(name,phone,email,gender,join_date,plan_id,status) VALUES(?,?,?,?,?,?,?)",
                       ("Aarav Sharma", "9876543210", "aarav@example.com", "Male", today, 2, "Active"))
            mid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            db.execute("INSERT INTO payments(member_id,amount,payment_date,method,notes) VALUES(?,?,?,?,?)",
                       (mid, 3200, today, "UPI", "Sample payment"))
            db.execute("INSERT INTO trainers(name,phone,specialty,salary) VALUES(?,?,?,?)",
                       ("Rahul Verma", "9876501234", "Strength Training", 25000))

@app.template_filter("money")
def money(value):
    return "₹{:,.0f}".format(value or 0)

@app.context_processor
def inject_globals():
    return {"today": date.today().isoformat()}

@app.route("/")
def dashboard():
    with get_db() as db:
        stats = {
            "members": db.execute("SELECT COUNT(*) FROM members").fetchone()[0],
            "active": db.execute("SELECT COUNT(*) FROM members WHERE status='Active'").fetchone()[0],
            "revenue": db.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE strftime('%Y-%m',payment_date)=?", (date.today().strftime("%Y-%m"),)).fetchone()[0],
            "trainers": db.execute("SELECT COUNT(*) FROM trainers WHERE status='Active'").fetchone()[0],
            "today_attendance": db.execute("SELECT COUNT(*) FROM attendance WHERE checkin_date=?", (today_iso(),)).fetchone()[0]
        }
        recent = db.execute("""SELECT p.*,m.name AS member_name FROM payments p JOIN members m ON m.id=p.member_id
                               ORDER BY p.payment_date DESC,p.id DESC LIMIT 6""").fetchall()
        attendance = db.execute("""SELECT a.*,m.name AS member_name FROM attendance a JOIN members m ON m.id=a.member_id
                                   WHERE a.checkin_date=? ORDER BY a.id DESC LIMIT 6""", (today_iso(),)).fetchall()
    return render_template("dashboard.html", stats=stats, recent=recent, attendance=attendance)

def today_iso():
    return date.today().isoformat()

@app.route("/members")
def members():
    q = request.args.get("q", "").strip()
    with get_db() as db:
        rows = db.execute("""SELECT m.*,p.name AS plan_name FROM members m LEFT JOIN plans p ON p.id=m.plan_id
                             WHERE m.name LIKE ? OR m.phone LIKE ? ORDER BY m.id DESC""", (f"%{q}%", f"%{q}%")).fetchall()
    return render_template("members.html", members=rows, q=q)

@app.route("/members/add", methods=["GET", "POST"])
def add_member():
    with get_db() as db:
        plans = db.execute("SELECT * FROM plans ORDER BY price").fetchall()
        if request.method == "POST":
            data = request.form
            if not data.get("name", "").strip() or not data.get("phone", "").strip():
                flash("Name and phone are required.", "error")
                return render_template("member_form.html", plans=plans, member=None)
            db.execute("""INSERT INTO members(name,phone,email,gender,join_date,plan_id,status,notes)
                          VALUES(?,?,?,?,?,?,?,?)""",
                       (data["name"].strip(), data["phone"].strip(), data.get("email"), data.get("gender"),
                        data.get("join_date") or today_iso(), data.get("plan_id") or None,
                        data.get("status") or "Active", data.get("notes")))
            flash("Member added successfully.", "success")
            return redirect(url_for("members"))
    return render_template("member_form.html", plans=plans, member=None)

@app.route("/members/<int:member_id>/edit", methods=["GET", "POST"])
def edit_member(member_id):
    with get_db() as db:
        member = db.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
        if not member:
            flash("Member not found.", "error")
            return redirect(url_for("members"))
        plans = db.execute("SELECT * FROM plans ORDER BY price").fetchall()
        if request.method == "POST":
            d = request.form
            db.execute("""UPDATE members SET name=?,phone=?,email=?,gender=?,join_date=?,plan_id=?,status=?,notes=? WHERE id=?""",
                       (d["name"].strip(), d["phone"].strip(), d.get("email"), d.get("gender"), d.get("join_date"),
                        d.get("plan_id") or None, d.get("status"), d.get("notes"), member_id))
            flash("Member updated.", "success")
            return redirect(url_for("members"))
    return render_template("member_form.html", plans=plans, member=member)

@app.post("/members/<int:member_id>/delete")
def delete_member(member_id):
    with get_db() as db:
        db.execute("DELETE FROM members WHERE id=?", (member_id,))
    flash("Member deleted.", "success")
    return redirect(url_for("members"))

@app.route("/plans", methods=["GET", "POST"])
def plans():
    with get_db() as db:
        if request.method == "POST":
            d = request.form
            try:
                db.execute("INSERT INTO plans(name,duration_months,price,description) VALUES(?,?,?,?)",
                           (d["name"].strip(), int(d["duration_months"]), float(d["price"]), d.get("description")))
                flash("Plan created.", "success")
            except sqlite3.IntegrityError:
                flash("A plan with that name already exists.", "error")
            return redirect(url_for("plans"))
        rows = db.execute("SELECT p.*,COUNT(m.id) AS member_count FROM plans p LEFT JOIN members m ON m.plan_id=p.id GROUP BY p.id ORDER BY p.price").fetchall()
    return render_template("plans.html", plans=rows)

@app.post("/plans/<int:plan_id>/delete")
def delete_plan(plan_id):
    with get_db() as db:
        db.execute("UPDATE members SET plan_id=NULL WHERE plan_id=?", (plan_id,))
        db.execute("DELETE FROM plans WHERE id=?", (plan_id,))
    flash("Plan deleted.", "success")
    return redirect(url_for("plans"))

@app.route("/payments", methods=["GET", "POST"])
def payments():
    with get_db() as db:
        if request.method == "POST":
            d = request.form
            try:
                db.execute("INSERT INTO payments(member_id,amount,payment_date,method,notes) VALUES(?,?,?,?,?)",
                           (int(d["member_id"]), float(d["amount"]), d.get("payment_date") or today_iso(), d["method"], d.get("notes")))
                flash("Payment recorded.", "success")
            except (ValueError, sqlite3.IntegrityError):
                flash("Please enter valid payment details.", "error")
            return redirect(url_for("payments"))
        rows = db.execute("""SELECT p.*,m.name AS member_name FROM payments p JOIN members m ON m.id=p.member_id
                             ORDER BY p.payment_date DESC,p.id DESC""").fetchall()
        member_rows = db.execute("SELECT id,name FROM members ORDER BY name").fetchall()
    return render_template("payments.html", payments=rows, members=member_rows)

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    with get_db() as db:
        if request.method == "POST":
            member_id = request.form.get("member_id")
            try:
                db.execute("INSERT INTO attendance(member_id,checkin_date,checkin_time) VALUES(?,?,?)",
                           (int(member_id), today_iso(), datetime.now().strftime("%H:%M")))
                flash("Attendance marked.", "success")
            except (ValueError, sqlite3.IntegrityError):
                flash("Select a valid member.", "error")
            return redirect(url_for("attendance"))
        rows = db.execute("""SELECT a.*,m.name AS member_name,m.phone FROM attendance a JOIN members m ON m.id=a.member_id
                             ORDER BY a.checkin_date DESC,a.id DESC LIMIT 100""").fetchall()
        member_rows = db.execute("SELECT id,name FROM members WHERE status='Active' ORDER BY name").fetchall()
    return render_template("attendance.html", attendance=rows, members=member_rows)

@app.route("/trainers", methods=["GET", "POST"])
def trainers():
    with get_db() as db:
        if request.method == "POST":
            d = request.form
            db.execute("INSERT INTO trainers(name,phone,specialty,salary,status) VALUES(?,?,?,?,?)",
                       (d["name"].strip(), d.get("phone"), d.get("specialty"), float(d.get("salary") or 0), d.get("status") or "Active"))
            flash("Trainer added.", "success")
            return redirect(url_for("trainers"))
        rows = db.execute("SELECT * FROM trainers ORDER BY id DESC").fetchall()
    return render_template("trainers.html", trainers=rows)

@app.post("/trainers/<int:trainer_id>/delete")
def delete_trainer(trainer_id):
    with get_db() as db:
        db.execute("DELETE FROM trainers WHERE id=?", (trainer_id,))
    flash("Trainer deleted.", "success")
    return redirect(url_for("trainers"))

@app.route("/reports")
def reports():
    with get_db() as db:
        revenue = db.execute("""SELECT strftime('%Y-%m',payment_date) AS month,SUM(amount) AS total
                                FROM payments GROUP BY month ORDER BY month DESC LIMIT 6""").fetchall()
        total = db.execute("SELECT COALESCE(SUM(amount),0) FROM payments").fetchone()[0]
        methods = db.execute("SELECT method,COUNT(*) AS count,SUM(amount) AS total FROM payments GROUP BY method").fetchall()
    return render_template("reports.html", revenue=revenue, total=total, methods=methods)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
