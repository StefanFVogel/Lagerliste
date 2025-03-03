#!/usr/bin/python
import sys, os
# Pfad zur Anwendung hinzufügen
sys.path.insert(0, '/var/www/lagerliste')

# Falls du eine virtuelle Umgebung verwendest:
# os.environ['PATH'] = '/var/www/lagerliste/venv/bin:' + os.environ['PATH']

# Setze ggf. notwendige Umgebungsvariablen
os.environ['FLASK_APP'] = 'app.py'  # Passe 'app.py' an den Namen der Hauptdatei an

# Importiere die Flask-Anwendung
from app import app as application  # Ersetze 'app' mit dem Modulnamen deiner Anwendung
