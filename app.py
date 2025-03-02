from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lagerliste.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Sicherstellen, dass das Templates-Verzeichnis existiert
if not os.path.exists('templates'):
    os.makedirs('templates')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Lagerliste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artikelnummer = db.Column(db.String(100), nullable=False)
    artikelbezeichnung = db.Column(db.String(100), nullable=True)
    maßstab = db.Column(db.String(50), nullable=True)
    hersteller = db.Column(db.String(100), nullable=False)
    kunde = db.Column(db.String(100), nullable=True)
    verkauft = db.Column(db.String(10), nullable=False, default='Nein')
    anzahlung = db.Column(db.Float, default=0.0)
    gesamtpreis = db.Column(db.Float, nullable=False)
    offene_summe = db.Column(db.Float, nullable=False)
    lagerbestand = db.Column(db.Integer, nullable=False, default=1)
    standort = db.Column(db.String(100), nullable=False, default='Weeze')
    eingangsdatum = db.Column(db.String(20), nullable=True)
    anmerkungen = db.Column(db.Text, nullable=True)

@app.template_filter('date_de')
def date_de_filter(value):
    if value:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%d.%m.%Y")
    return ""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    lager = Lagerliste.query.all()
    return render_template('index.html', lager=lager, title='Lagerliste Final AeroTec GmbH')

@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    artikelnummer = request.form['artikelnummer']
    artikelbezeichnung = request.form['artikelbezeichnung']
    maßstab = request.form['maßstab']
    hersteller = request.form['hersteller']
    kunde = request.form['kunde']
    verkauft = request.form['verkauft']
    anzahlung = float(request.form['anzahlung'])
    gesamtpreis = float(request.form['gesamtpreis'])
    offene_summe = gesamtpreis - anzahlung
    lagerbestand = int(request.form['lagerbestand'])
    standort = request.form['standort']
    eingangsdatum = request.form['eingangsdatum']
    anmerkungen = request.form['anmerkungen']

    neues_modell = Lagerliste(
        artikelnummer=artikelnummer, artikelbezeichnung=artikelbezeichnung, maßstab=maßstab,
        hersteller=hersteller, kunde=kunde, verkauft=verkauft,
        anzahlung=anzahlung, gesamtpreis=gesamtpreis,
        offene_summe=offene_summe, lagerbestand=lagerbestand,
        standort=standort, eingangsdatum=eingangsdatum,
        anmerkungen=anmerkungen)

    db.session.add(neues_modell)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    item = Lagerliste.query.get(id)
    if request.method == 'POST':
        item.artikelnummer = request.form['artikelnummer']
        item.artikelbezeichnung = request.form['artikelbezeichnung']
        item.maßstab = request.form['maßstab']
        item.hersteller = request.form['hersteller']
        item.kunde = request.form['kunde']
        item.verkauft = request.form['verkauft']
        item.anzahlung = float(request.form['anzahlung'])
        item.gesamtpreis = float(request.form['gesamtpreis'])
        item.offene_summe = item.gesamtpreis - item.anzahlung
        item.lagerbestand = int(request.form['lagerbestand'])
        item.standort = request.form['standort']
        item.eingangsdatum = request.form['eingangsdatum']
        item.anmerkungen = request.form['anmerkungen']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', item=item, standorte=['Weeze', 'Niedenstein'])

@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    eintrag = Lagerliste.query.get(id)
    db.session.delete(eintrag)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
