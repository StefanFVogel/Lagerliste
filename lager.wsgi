#!/usr/bin/python
import sys, os
# Pfad zur Anwendung hinzufügen
sys.path.insert(0, '/var/www/vhosts/final-aerotec.de/lager.final-aerotec.de')

# Fügen Sie den site-packages Pfad der virtuellen Umgebung hinzu.
# Passen Sie 'python3.x' an Ihre Python-Version an (z.B. python3.9)
sys.path.insert(0, '/var/www/vhosts/final-aerotec.de/lager.final-aerotec.de/venv/lib/python3.x/site-packages')

# Setze ggf. notwendige Umgebungsvariablen
os.environ['FLASK_APP'] = 'app.py'  # Passe 'app.py' an, falls der Name der Hauptdatei anders lautet

# Importiere die Flask-Anwendung
from app import app as application  # Ersetze 'app' ggf. mit dem Modulnamen deiner Anwendung
