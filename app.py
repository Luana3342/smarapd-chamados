import csv
import io
import os
import sqlite3
from datetime import date
from functools import wraps

from flask import (Flask, Response, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave")
DB_PATH = os.environ.get("DB_PATH", "chamados.db")
APP_USER = os.environ.get("APP_USER", "admin")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "smarapd123")
STATUS = ["Aberto", "Em andamento", "Concluído"]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute(
            """CREATE TABLE IF NOT EXISTS chamados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                titulo TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Aberto',
                data_conclusao TEXT)"""
        )
    return g.db


@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("logado"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def data_para_status(status, data_informada):
    """Concluído sem data -> hoje. Outros status -> sem data."""
    if status != "Concluído":
        return None
    return data_informada or date.today().isoformat()


@app.route("/health")
def health():
    """Endpoint usado pelo monitoramento da nuvem."""
    try:
        get_db().execute("SELECT 1")
        return jsonify(status="ok"), 200
    except Exception:
        return jsonify(status="erro"), 500


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (request.form.get("usuario") == APP_USER
                and request.form.get("senha") == APP_PASSWORD):
            session["logado"] = True
            return redirect(url_for("index"))
        flash("Usuário ou senha inválidos.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    filtro = request.args.get("status", "")
    db = get_db()
    if filtro in STATUS:
        rows = db.execute("SELECT * FROM chamados WHERE status=? ORDER BY id DESC", (filtro,)).fetchall()
    else:
        rows = db.execute("SELECT * FROM chamados ORDER BY id DESC").fetchall()
    return render_template("index.html", chamados=rows, status=STATUS, filtro=filtro)


@app.route("/add", methods=["POST"])
@login_required
def add():
    numero = request.form.get("numero", "").strip()
    titulo = request.form.get("titulo", "").strip()
    status = request.form.get("status", "Aberto")
    if not numero or not titulo or status not in STATUS:
        flash("Preencha número e título.")
        return redirect(url_for("index"))
    data = data_para_status(status, request.form.get("data_conclusao"))
    try:
        db = get_db()
        db.execute("INSERT INTO chamados (numero, titulo, status, data_conclusao) VALUES (?,?,?,?)",
                   (numero, titulo, status, data))
        db.commit()
    except sqlite3.IntegrityError:
        flash(f"O chamado {numero} já existe.")
    return redirect(url_for("index"))


@app.route("/update/<int:cid>", methods=["POST"])
@login_required
def update(cid):
    status = request.form.get("status", "Aberto")
    if status not in STATUS:
        return redirect(url_for("index"))
    data = data_para_status(status, request.form.get("data_conclusao"))
    db = get_db()
    db.execute("UPDATE chamados SET status=?, data_conclusao=? WHERE id=?", (status, data, cid))
    db.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:cid>", methods=["POST"])
@login_required
def delete(cid):
    db = get_db()
    db.execute("DELETE FROM chamados WHERE id=?", (cid,))
    db.commit()
    return redirect(url_for("index"))


@app.route("/export.csv")
@login_required
def export():
    rows = get_db().execute("SELECT numero, titulo, status, data_conclusao FROM chamados ORDER BY id").fetchall()
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(["Número", "Título", "Status", "Data de conclusão"])
    for r in rows:
        w.writerow([r["numero"], r["titulo"], r["status"], r["data_conclusao"] or ""])
    return Response("\ufeff" + buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=chamados.csv"})


if __name__ == "__main__":
    app.run(debug=True)
