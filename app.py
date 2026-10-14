
import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# Change this before deploying the website publicly.
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "anvaya-development-key-change-before-deployment"
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "anvaya.db")

# Demo admin login
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "AnvayaDemo123!")


# --------------------------------------------------
# DATABASE CONNECTION AND INITIALIZATION
# --------------------------------------------------

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                donor_name TEXT NOT NULL,
                donor_type TEXT NOT NULL,
                food_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                safe_until TEXT NOT NULL,
                pickup_location TEXT NOT NULL,
                contact TEXT NOT NULL,
                notes TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Pending',
                pickup_status TEXT NOT NULL DEFAULT 'Available',
                ngo_name TEXT DEFAULT '',
                ngo_contact TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        db.commit()


# --------------------------------------------------
# TEMPLATE CONTEXT
# --------------------------------------------------

@app.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}


# --------------------------------------------------
# COMMON HELPERS
# --------------------------------------------------

def admin_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Please log in as an administrator first.", "error")
            return redirect(url_for("admin_login"))
        return view_function(*args, **kwargs)
    return wrapped_view


def get_impact():
    with get_db() as db:
        approved = db.execute("""
            SELECT COUNT(*) AS total,
                   COALESCE(SUM(quantity), 0) AS kg
            FROM donations
            WHERE status = 'Approved'
        """).fetchone()

        collected = db.execute("""
            SELECT COALESCE(SUM(quantity), 0) AS kg
            FROM donations
            WHERE status = 'Approved'
              AND pickup_status = 'Collected'
        """).fetchone()

    return {
        "approved_donations": approved["total"],
        "approved_kg": round(approved["kg"], 2),
        "collected_kg": round(collected["kg"], 2),
    }


def get_admin_stats():
    with get_db() as db:
        total = db.execute(
            "SELECT COUNT(*) FROM donations"
        ).fetchone()[0]

        pending = db.execute("""
            SELECT COUNT(*) FROM donations
            WHERE status = 'Pending'
        """).fetchone()[0]

        approved = db.execute("""
            SELECT COUNT(*) FROM donations
            WHERE status = 'Approved'
        """).fetchone()[0]

        picked = db.execute("""
            SELECT COUNT(*) FROM donations
            WHERE pickup_status = 'Collected'
              AND status = 'Approved'
        """).fetchone()[0]

    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "picked": picked,
    }


# --------------------------------------------------
# HOME / DONOR PORTAL
# --------------------------------------------------

@app.route("/")
def home():
    return render_template(
        "index.html",
        impact=get_impact(),
        donation_error=None
    )


@app.route("/donate", methods=["POST"])
def submit_donation():
    donor_name = request.form.get("donor_name", "").strip()
    donor_type = request.form.get("donor_type", "").strip()
    food_name = request.form.get("food_name", "").strip()
    quantity_text = request.form.get("quantity", "").strip()
    safe_until = request.form.get("safe_until", "").strip()
    pickup_location = request.form.get("pickup_location", "").strip()
    contact = request.form.get("contact", "").strip()
    notes = request.form.get("notes", "").strip()

    # Validate required fields
    if not all([
        donor_name,
        donor_type,
        food_name,
        quantity_text,
        safe_until,
        pickup_location,
        contact
    ]):
        flash("Please fill in all required donation fields.", "error")
        return redirect(url_for("home") + "#donate")

    try:
        quantity = float(quantity_text)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        flash("Enter a valid food quantity greater than zero.", "error")
        return redirect(url_for("home") + "#donate")

    try:
        safe_date = datetime.strptime(safe_until, "%Y-%m-%d")
        if safe_date.date() < datetime.now().date():
            flash("Please enter a valid future or current safe-until date.", "error")
            return redirect(url_for("home") + "#donate")
    except ValueError:
        flash("Please enter a valid safe-until date.", "error")
        return redirect(url_for("home") + "#donate")

    with get_db() as db:
        db.execute("""
            INSERT INTO donations (
                donor_name, donor_type, food_name, quantity,
                safe_until, pickup_location, contact, notes,
                status, pickup_status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 'Available', ?)
        """, (
            donor_name,
            donor_type,
            food_name,
            quantity,
            safe_until,
            pickup_location,
            contact,
            notes,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        db.commit()

    flash(
        "Thank you! Your donation has been submitted for admin approval.",
        "success"
    )
    return redirect(url_for("home") + "#donate")


# --------------------------------------------------
# ADMIN LOGIN AND LOGOUT
# --------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear()
            session["is_admin"] = True
            flash("Welcome to the Anvaya admin portal.", "success")
            return redirect(url_for("admin_dashboard"))

        error = "Invalid username or password."

    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

@app.route("/admin")
@admin_required
def admin_dashboard():
    with get_db() as db:
        donations = db.execute("""
            SELECT *
            FROM donations
            ORDER BY
                CASE status
                    WHEN 'Pending' THEN 0
                    ELSE 1
                END,
                id DESC
        """).fetchall()

    return render_template(
        "admin_dashboard.html",
        donations=donations,
        stats=get_admin_stats()
    )


# Approve or reject a donation
@app.route("/admin/donation/<int:donation_id>/status", methods=["POST"])
@admin_required
def admin_update_donation(donation_id):
    new_status = request.form.get("status", "").strip()

    if new_status not in ("Approved", "Rejected"):
        flash("Invalid donation status.", "error")
        return redirect(url_for("admin_dashboard"))

    with get_db() as db:
        donation = db.execute(
            "SELECT * FROM donations WHERE id = ?",
            (donation_id,)
        ).fetchone()

        if donation is None:
            abort(404)

        if donation["status"] == "Rejected" and new_status == "Approved":
            db.execute("""
                UPDATE donations
                SET status = ?, pickup_status = 'Available',
                    ngo_name = '', ngo_contact = ''
                WHERE id = ?
            """, (new_status, donation_id))
        elif new_status == "Rejected":
            db.execute("""
                UPDATE donations
                SET status = ?, pickup_status = 'Available',
                    ngo_name = '', ngo_contact = ''
                WHERE id = ?
            """, (new_status, donation_id))
        else:
            db.execute("""
                UPDATE donations
                SET status = ?
                WHERE id = ?
            """, (new_status, donation_id))

        db.commit()

    flash(f"Donation #{donation_id} marked as {new_status}.", "success")
    return redirect(url_for("admin_dashboard"))


# Mark an approved donation as collected
@app.route("/admin/donation/<int:donation_id>/pickup", methods=["POST"])
@admin_required
def admin_update_pickup(donation_id):
    with get_db() as db:
        donation = db.execute(
            "SELECT * FROM donations WHERE id = ?",
            (donation_id,)
        ).fetchone()

        if donation is None:
            abort(404)

        if donation["status"] != "Approved":
            flash("Only approved donations can be marked as collected.", "error")
            return redirect(url_for("admin_dashboard"))

        if not donation["ngo_name"]:
            flash("An NGO must request the donation before collection.", "error")
            return redirect(url_for("admin_dashboard"))

        db.execute("""
            UPDATE donations
            SET pickup_status = 'Collected'
            WHERE id = ?
        """, (donation_id,))
        db.commit()

    flash(f"Donation #{donation_id} marked as collected.", "success")
    return redirect(url_for("admin_dashboard"))


# --------------------------------------------------
# NGO PORTAL
# --------------------------------------------------

@app.route("/ngo")
def ngo_dashboard():
    with get_db() as db:
        donations = db.execute("""
            SELECT *
            FROM donations
            WHERE status = 'Approved'
              AND pickup_status != 'Collected'
            ORDER BY safe_until ASC, id DESC
        """).fetchall()

    return render_template(
        "ngo_dashboard.html",
        donations=donations
    )


# NGO requests an approved donation
@app.route("/ngo/request/<int:donation_id>", methods=["POST"])
def ngo_request_pickup(donation_id):
    ngo_name = request.form.get("ngo_name", "").strip()
    ngo_contact = request.form.get("ngo_contact", "").strip()

    if not ngo_name or not ngo_contact:
        flash("Please enter your NGO name and contact details.", "error")
        return redirect(url_for("ngo_dashboard"))

    with get_db() as db:
        donation = db.execute(
            "SELECT * FROM donations WHERE id = ?",
            (donation_id,)
        ).fetchone()

        if donation is None:
            abort(404)

        if donation["status"] != "Approved":
            flash("This donation is not available for pickup.", "error")
            return redirect(url_for("ngo_dashboard"))

        if donation["pickup_status"] == "Collected":
            flash("This donation has already been collected.", "error")
            return redirect(url_for("ngo_dashboard"))

        if donation["ngo_name"]:
            flash("This donation has already been requested by an NGO.", "error")
            return redirect(url_for("ngo_dashboard"))

        db.execute("""
            UPDATE donations
            SET ngo_name = ?, ngo_contact = ?,
                pickup_status = 'Requested'
            WHERE id = ?
        """, (ngo_name, ngo_contact, donation_id))
        db.commit()

    flash(
        "Pickup request submitted! The admin can now see your request.",
        "success"
    )
    return redirect(url_for("ngo_dashboard"))


# --------------------------------------------------
# ERROR PAGES
# --------------------------------------------------

@app.errorhandler(404)
def not_found(error):
    return (
        "<h1>404 - Page not found</h1>"
        "<p>The requested page or donation could not be found.</p>"
        '<p><a href="/">Return to Anvaya home</a></p>',
        404
    )


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

init_db()

if __name__ == "__main__":
    app.run(debug=True)
