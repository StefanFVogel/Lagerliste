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
    artikelname = db.Column(db.String(250), nullable=True)
    hersteller = db.Column(db.String(100), nullable=False)
    rechnungsnummer_hersteller = db.Column(db.String(100), nullable=False)
    continer = db.Column(db.String(100), nullable=False)
    container_ankuftsdatum = db.Column(db.String(20), nullable=True)
    kunde = db.Column(db.String(100), nullable=True)
    rechnungsnummer_kunde = db.Column(db.String(100), nullable=False)
    verkauft = db.Column(db.Date, nullable=True)
    anzahlung = db.Column(db.Float, default=0.0)
    gesamtpreis = db.Column(db.Float, nullable=False)
    standort = db.Column(db.String(100), nullable=False, default='Weeze')
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
    return render_template('index.html', lager=lager)

@app.route('/new', methods=['GET', 'POST'])
def new():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        artikelnummer = request.form['artikelnummer']
        artikelname = request.form.get('artikelname')
        hersteller = request.form['hersteller']
        rechnungsnummer_hersteller = request.form['rechnungsnummer_hersteller']
        continer = request.form['continer']
        container_ankuftsdatum = request.form.get('container_ankuftsdatum')
        kunde = request.form.get('kunde')
        rechnungsnummer_kunde = request.form['rechnungsnummer_kunde']
        verkauft_input = request.form.get('verkauft')
        verkauft_date = datetime.strptime(verkauft_input, '%Y-%m-%d').date() if verkauft_input else None
        anzahlung = float(request.form['anzahlung']) if request.form.get('anzahlung') else 0.0
        gesamtpreis = float(request.form['gesamtpreis'])
        standort = request.form['standort']
        anmerkungen = request.form.get('anmerkungen')

        neuer_eintrag = Lagerliste(
            artikelnummer=artikelnummer,
            artikelname=artikelname,
            hersteller=hersteller,
            rechnungsnummer_hersteller=rechnungsnummer_hersteller,
            continer=continer,
            container_ankuftsdatum=container_ankuftsdatum,
            kunde=kunde,
            rechnungsnummer_kunde=rechnungsnummer_kunde,
            verkauft=verkauft_date,
            anzahlung=anzahlung,
            gesamtpreis=gesamtpreis,
            standort=standort,
            anmerkungen=anmerkungen
        )
        db.session.add(neuer_eintrag)
        db.session.commit()
        return redirect(url_for('index'))
    # Bei GET wird dasselbe Template wie für das Bearbeiten verwendet, jedoch ohne vorhandenes item
    return render_template('edit.html', item=None)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    item = Lagerliste.query.get(id)
    if request.method == 'POST':
        item.artikelnummer = request.form['artikelnummer']
        item.artikelname = request.form.get('artikelname')
        item.hersteller = request.form['hersteller']
        item.rechnungsnummer_hersteller = request.form['rechnungsnummer_hersteller']
        item.continer = request.form['continer']
        item.container_ankuftsdatum = request.form.get('container_ankuftsdatum')
        item.kunde = request.form.get('kunde')
        item.rechnungsnummer_kunde = request.form['rechnungsnummer_kunde']
        verkauft_input = request.form.get('verkauft')
        item.verkauft = datetime.strptime(verkauft_input, '%Y-%m-%d').date() if verkauft_input else None
        item.anzahlung = float(request.form['anzahlung']) if request.form.get('anzahlung') else 0.0
        item.gesamtpreis = float(request.form['gesamtpreis'])
        item.standort = request.form['standort']
        item.anmerkungen = request.form.get('anmerkungen')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', item=item)

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
