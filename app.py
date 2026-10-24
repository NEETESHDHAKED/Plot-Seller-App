from flask import Flask, render_template, request, redirect
import json, os
from datetime import date
import urllib.parse

app = Flask(__name__)
FILE = "plot.json"

def load():
    if os.path.exists(FILE):
        try:
            with open(FILE) as f:
                data = json.load(f)
                for i, p in enumerate(data):
                    p["id"] = i
                    if "payments" not in p: p["payments"] = []
                    if "paid" not in p: p["paid"] = 0
                    if "baki" not in p: p["baki"] = int(p["price"])
                return data
        except: return []
    return []

def save(d):
    for p in d:
        if "id" in p: del p["id"]
    with open(FILE,"w") as f:
        json.dump(d,f)

@app.route("/")
def home():
    plots = load()
    q = request.args.get("q","")
    search_result = []
    if q:
        search_result = [p for p in plots if q.lower() in p['plot_no'].lower() or q.lower() in p.get('customer','').lower() or q.lower() in p['location'].lower()]
    total_plots = len(plots)
    sold = len([p for p in plots if p['status']=="SOLD"])
    khali = len([p for p in plots if p['status']=="KHAAALI"])
    total_value = sum(int(p['price']) for p in plots)
    total_collected = sum(int(p['paid']) for p in plots)
    total_baki = sum(int(p['baki']) for p in plots)
    return render_template("plot.html", plots=plots, search_result=search_result, q=q, total_plots=total_plots, sold=sold, khali=khali, total_value=total_value, total_collected=total_collected, total_baki=total_baki)

@app.route("/add", methods=["POST"])
def add():
    p = load()
    price = int(request.form["price"])
    p.append({
        "plot_no": request.form["plot_no"],
        "size": request.form["size"],
        "location": request.form["location"],
        "price": price,
        "customer": "",
        "phone": "",
        "status": "KHAAALI",
        "paid": 0,
        "baki": price,
        "payments": []
    })
    save(p)
    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    p = load()
    if id < len(p): p.pop(id); save(p)
    return redirect("/")

@app.route("/plot/<int:id>")
def plot(id):
    all_p = load()
    if id >= len(all_p): return redirect("/")
    p = all_p[id]
    msg = f"Namaste {p['customer']} ji 🙏 Plot No {p['plot_no']} - {p['location']} ka ₹{p['baki']} baki hai. Kripya kist jama kar de. - Ramesh Property"
    wa_link = "https://wa.me/91" + p['phone'] + "?text=" + urllib.parse.quote(msg) if p['phone'] else "#"
    return render_template("customer.html", p=p, id=id, wa_link=wa_link)

@app.route("/sell/<int:id>", methods=["POST"])
def sell(id):
    p = load()
    advance = int(request.form["advance"])
    p[id]["customer"] = request.form["customer"]
    p[id]["phone"] = request.form["phone"]
    p[id]["status"] = "SOLD"
    p[id]["paid"] = advance
    p[id]["baki"] = int(p[id]["price"]) - advance
    p[id]["payments"].append({"date": str(date.today()), "amount": advance, "note": "Advance / Booking"})
    save(p)
    return redirect(f"/plot/{id}")

@app.route("/kist/<int:id>", methods=["POST"])
def kist(id):
    p = load()
    amt = int(request.form["amount"])
    p[id]["payments"].append({"date": str(date.today()), "amount": amt, "note": request.form.get("note","Kist")})
    p[id]["paid"] = int(p[id]["paid"]) + amt
    p[id]["baki"] = int(p[id]["baki"]) - amt
    save(p)
    return redirect(f"/plot/{id}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
