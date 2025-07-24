# Deployment Guide - Render.com

Diese Anleitung führt Sie durch den Deployment-Prozess der SEO Profile Generator Anwendung auf Render.com.

## 📋 Voraussetzungen

1. **GitHub Account** mit dem Repository
2. **Render.com Account** (kostenlos verfügbar)
3. **OpenAI API Key** (von OpenAI Platform)

## 🚀 Schritt-für-Schritt Deployment

### 1. Repository vorbereiten

Stellen Sie sicher, dass Ihr Repository alle notwendigen Dateien enthält:
- `render.yaml` (Deployment-Konfiguration)
- `backend/requirements.txt` (Python-Abhängigkeiten)
- `frontend/package.json` (Node.js-Abhängigkeiten)
- Alle Quellcode-Dateien

### 2. Render.com Account einrichten

1. Besuchen Sie [render.com](https://render.com)
2. Registrieren Sie sich oder melden Sie sich an
3. Verbinden Sie Ihr GitHub-Konto

### 3. Web Service erstellen

1. **Dashboard öffnen**: Klicken Sie auf "New +"
2. **Web Service auswählen**: Wählen Sie "Web Service"
3. **Repository verbinden**: 
   - Wählen Sie Ihr GitHub Repository
   - Klicken Sie "Connect"

### 4. Service konfigurieren

#### Grundeinstellungen
- **Name**: `seo-profile-generator`
- **Region**: `Frankfurt` (oder gewünschte Region)
- **Branch**: `main` (oder Ihr Hauptbranch)
- **Runtime**: `Python 3`

#### Build & Deploy Einstellungen
- **Build Command**:
  ```bash
  cd backend && pip install -r requirements.txt && cd ../frontend && npm install && npm run build && cp -r dist/* ../backend/src/static/
  ```
- **Start Command**:
  ```bash
  cd backend && python src/main.py
  ```

#### Plan auswählen
- **Free Plan**: Für Entwicklung und Tests
- **Starter Plan**: Für Produktionsumgebungen

### 5. Umgebungsvariablen konfigurieren

Fügen Sie folgende Umgebungsvariablen hinzu:

#### Erforderliche Variablen
```
OPENAI_API_KEY = [Ihr OpenAI API Key]
```

#### Automatisch generierte Variablen
Render.com generiert automatisch:
- `JWT_SECRET_KEY`
- `SECRET_KEY`

#### Optionale Variablen
```
FLASK_ENV = production
```

### 6. Deployment starten

1. Klicken Sie "Create Web Service"
2. Render.com startet automatisch den Build-Prozess
3. Überwachen Sie die Logs im Dashboard

### 7. Deployment verifizieren

Nach erfolgreichem Deployment:

1. **URL öffnen**: Klicken Sie auf die bereitgestellte URL
2. **Login testen**: Verwenden Sie admin/admin123
3. **Funktionalität prüfen**: Testen Sie die Domain-Analyse

## 🔧 Automatisches Deployment mit render.yaml

Wenn Sie `render.yaml` verwenden:

1. **Datei committen**: Stellen Sie sicher, dass `render.yaml` im Repository-Root liegt
2. **Blueprint verwenden**: 
   - Gehen Sie zu "Blueprints" im Render Dashboard
   - Klicken Sie "New Blueprint Instance"
   - Wählen Sie Ihr Repository
3. **Umgebungsvariablen setzen**: Nur `OPENAI_API_KEY` manuell hinzufügen

## 📊 Monitoring und Wartung

### Logs überwachen
- **Build Logs**: Zeigen den Build-Prozess
- **Deploy Logs**: Zeigen Deployment-Status
- **Service Logs**: Zeigen Anwendungslogs

### Automatische Deployments
- **Auto-Deploy**: Aktiviert für automatische Deployments bei Git-Push
- **Manual Deploy**: Über "Manual Deploy" Button

### Gesundheitsprüfung
- **Health Check**: Automatisch auf `/` konfiguriert
- **Uptime Monitoring**: Verfügbar im Dashboard

## 🔐 Sicherheit und Best Practices

### Umgebungsvariablen
- **Niemals** API-Keys in den Code committen
- Verwenden Sie Render's Environment Variables
- Rotieren Sie Secrets regelmäßig

### Domain und SSL
- **Custom Domain**: Konfigurierbar in den Service-Einstellungen
- **SSL**: Automatisch bereitgestellt
- **HTTPS**: Standardmäßig aktiviert

### Backup und Recovery
- **Database**: SQLite-Datei wird mit dem Service gespeichert
- **Code**: Über Git-Repository gesichert
- **Environment**: Dokumentieren Sie alle Umgebungsvariablen

## 🐛 Troubleshooting

### Häufige Build-Fehler

#### Python-Abhängigkeiten
```bash
# Fehler: Package nicht gefunden
# Lösung: requirements.txt aktualisieren
pip freeze > backend/requirements.txt
```

#### Node.js Build-Fehler
```bash
# Fehler: npm install fehlgeschlagen
# Lösung: package-lock.json löschen und neu generieren
rm frontend/package-lock.json
npm install
```

#### Frontend-Build-Fehler
```bash
# Fehler: Build-Verzeichnis nicht gefunden
# Lösung: Build-Command überprüfen
cd frontend && npm run build && ls -la dist/
```

### Häufige Runtime-Fehler

#### Port-Konfiguration
```python
# Render.com stellt PORT-Umgebungsvariable bereit
import os
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

#### Database-Pfad
```python
# Absoluter Pfad für SQLite
import os
db_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
```

### Performance-Optimierung

#### Free Plan Limitierungen
- **Sleep nach Inaktivität**: Service schläft nach 15 Minuten
- **Cold Start**: Erste Anfrage nach Sleep dauert länger
- **Bandbreite**: 100GB/Monat

#### Optimierungen
- **Static Files**: Über CDN bereitstellen
- **Database**: Für Produktion PostgreSQL verwenden
- **Caching**: Redis für Session-Management

## 📞 Support und Hilfe

### Render.com Support
- **Dokumentation**: [render.com/docs](https://render.com/docs)
- **Community**: [community.render.com](https://community.render.com)
- **Status**: [status.render.com](https://status.render.com)

### Anwendungs-Support
- **Repository Issues**: Für Code-bezogene Probleme
- **Logs**: Immer zuerst die Service-Logs prüfen
- **Environment**: Umgebungsvariablen verifizieren

## 🔄 Updates und Wartung

### Code-Updates
1. **Lokale Änderungen** committen und pushen
2. **Auto-Deploy** wartet auf Git-Push
3. **Manual Deploy** für sofortige Updates

### Dependency-Updates
```bash
# Backend
cd backend && pip list --outdated
pip install --upgrade package_name
pip freeze > requirements.txt

# Frontend
cd frontend && npm outdated
npm update
```

### Monitoring
- **Uptime**: Render Dashboard
- **Performance**: Service Metrics
- **Errors**: Application Logs

---

**Erfolgreiches Deployment! 🎉**

Ihre SEO Profile Generator Anwendung ist jetzt live und bereit für die Nutzung.

