from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Vendor table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vendor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT
    )
    """)

    # Requisition table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS requisition (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT,
        quantity INTEGER
    )
    """)
    # Purchase Order table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS purchase_order (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER,
        requisition_id INTEGER,
        status TEXT
    )
    """)
    # Goods Receipt table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS goods_receipt (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        po_id INTEGER,
        received_qty INTEGER
    )
    """)
    # Invoice table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoice (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        po_id INTEGER,
        amount REAL
    )
    """)
    # Payment table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- VENDOR ----------------
@app.route("/add_vendor", methods=["GET", "POST"])
def add_vendor():
    if request.method == "POST":
        name = request.form["name"]
        contact = request.form["contact"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO vendor (name, contact) VALUES (?, ?)", (name, contact))
        conn.commit()
        conn.close()

        return redirect("/vendors")

    return render_template("add_vendor.html")


@app.route("/vendors")
def vendors():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM vendor")
    data = cur.fetchall()
    conn.close()

    return render_template("vendors.html", vendors=data)


# ---------------- REQUISITION ----------------
@app.route("/add_requisition", methods=["GET", "POST"])
def add_requisition():
    if request.method == "POST":
        item = request.form["item"]
        qty = request.form["quantity"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO requisition (item_name, quantity) VALUES (?, ?)", (item, qty))
        conn.commit()
        conn.close()

        return redirect("/requisitions")

    return render_template("add_requisition.html")


@app.route("/requisitions")
def requisitions():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM requisition")
    data = cur.fetchall()
    conn.close()

    return render_template("requisitions.html", requisitions=data)

# Add Purchase Order
@app.route("/add_po", methods=["GET", "POST"])
def add_po():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Fetch vendors and requisitions for dropdown
    cur.execute("SELECT * FROM vendor")
    vendors = cur.fetchall()

    cur.execute("SELECT * FROM requisition")
    requisitions = cur.fetchall()

    if request.method == "POST":
        vendor_id = request.form["vendor_id"]
        req_id = request.form["req_id"]

        cur.execute("""
        INSERT INTO purchase_order (vendor_id, requisition_id, status)
        VALUES (?, ?, ?)
        """, (vendor_id, req_id, "Created"))

        conn.commit()
        conn.close()

        return redirect("/pos")

    conn.close()
    return render_template("add_po.html", vendors=vendors, requisitions=requisitions)


# View Purchase Orders
@app.route("/pos")
def pos():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT po.id, v.name, r.item_name, r.quantity, po.status
    FROM purchase_order po
    JOIN vendor v ON po.vendor_id = v.id
    JOIN requisition r ON po.requisition_id = r.id
    """)

    data = cur.fetchall()
    conn.close()

    return render_template("pos.html", pos=data) 

# Add Goods Receipt
@app.route("/add_gr", methods=["GET", "POST"])
def add_gr():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM purchase_order")
    pos = cur.fetchall()

    if request.method == "POST":
        po_id = request.form["po_id"]
        qty = request.form["qty"]

        cur.execute("""
        INSERT INTO goods_receipt (po_id, received_qty)
        VALUES (?, ?)
        """, (po_id, qty))

        # Update PO status
        cur.execute("UPDATE purchase_order SET status='Received' WHERE id=?", (po_id,))

        conn.commit()
        conn.close()

        return redirect("/grs")

    conn.close()
    return render_template("add_gr.html", pos=pos)


# View Goods Receipts
@app.route("/grs")
def grs():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT gr.id, po.id, gr.received_qty
    FROM goods_receipt gr
    JOIN purchase_order po ON gr.po_id = po.id
    """)

    data = cur.fetchall()
    conn.close()

    return render_template("grs.html", grs=data) 

# Add Invoice
@app.route("/add_invoice", methods=["GET", "POST"])
def add_invoice():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM purchase_order")
    pos = cur.fetchall()

    if request.method == "POST":
        po_id = request.form["po_id"]
        amount = request.form["amount"]

        cur.execute("""
        INSERT INTO invoice (po_id, amount)
        VALUES (?, ?)
        """, (po_id, amount))

        conn.commit()
        conn.close()

        return redirect("/invoices")

    conn.close()
    return render_template("add_invoice.html", pos=pos)


# View Invoice
@app.route("/invoices")
def invoices():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT i.id, po.id, i.amount
    FROM invoice i
    JOIN purchase_order po ON i.po_id = po.id
    """)

    data = cur.fetchall()
    conn.close()

    return render_template("invoices.html", invoices=data) 

# Add Payment
@app.route("/add_payment", methods=["GET", "POST"])
def add_payment():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM invoice")
    invoices = cur.fetchall()

    if request.method == "POST":
        invoice_id = request.form["invoice_id"]

        cur.execute("""
        INSERT INTO payment (invoice_id, status)
        VALUES (?, ?)
        """, (invoice_id, "Paid"))

        conn.commit()
        conn.close()

        return redirect("/payments")

    conn.close()
    return render_template("add_payment.html", invoices=invoices)


# View Payments
@app.route("/payments")
def payments():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT p.id, i.id, p.status
    FROM payment p
    JOIN invoice i ON p.invoice_id = i.id
    """)

    data = cur.fetchall()
    conn.close()

    return render_template("payments.html", payments=data) 

# ---------------- RUN ----------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)

