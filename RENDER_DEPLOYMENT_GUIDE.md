# Render.com Deployment Guide - SEO Profile Generator

## 🚀 Schnell-Deployment für Ihr GitHub Repository

**Repository URL:** https://github.com/KIGREVEN/seo-profile-generator

### Schritt 1: Render.com Account
1. Besuchen Sie [render.com](https://render.com)
2. Registrieren Sie sich mit Ihrem GitHub-Account
3. Autorisieren Sie Render.com für GitHub-Zugriff

### Schritt 2: Web Service erstellen
1. **Dashboard öffnen** → Klicken Sie "New +"
2. **Web Service auswählen** → "Web Service"
3. **Repository verbinden:**
   - Suchen Sie "seo-profile-generator"
   - Klicken Sie "Connect"

### Schritt 3: Service konfigurieren

#### Grundeinstellungen:
- **Name:** `seo-profile-generator`
- **Region:** `Frankfurt` (oder gewünschte Region)
- **Branch:** `main`
- **Runtime:** `Python 3`

#### Build & Deploy (wird automatisch erkannt):
- **Build Command:** 
  ```bash
  cd backend && pip install -r requirements.txt && cd ../frontend && npm install && npm run build && cp -r dist/* ../backend/src/static/
  ```
- **Start Command:** 
  ```bash
  cd backend && python src/main.py
  ```

### Schritt 4: Umgebungsvariablen hinzufügen

**Erforderlich:**
```
OPENAI_API_KEY = [Ihr OpenAI API Key]
```

**Automatisch generiert (von Render.com):**
- `JWT_SECRET_KEY`
- `SECRET_KEY`

### Schritt 5: Deployment starten
1. Klicken Sie "Create Web Service"
2. Warten Sie auf Build-Completion (ca. 3-5 Minuten)
3. Ihre App ist live unter der bereitgestellten URL!

## 🔧 Standard-Anmeldedaten

Nach erfolgreichem Deployment:
- **Benutzername:** admin
- **Passwort:** admin123

⚠️ **Wichtig:** Ändern Sie diese Anmeldedaten nach der ersten Anmeldung!

## 📊 Monitoring

- **Build Logs:** Überwachen Sie den Build-Prozess
- **Service Logs:** Verfolgen Sie Anwendungslogs
- **Health Check:** Automatisch auf `/` konfiguriert

## 🐛 Troubleshooting

### Build-Fehler:
- Überprüfen Sie die Build-Logs
- Stellen Sie sicher, dass alle Abhängigkeiten korrekt sind

### Runtime-Fehler:
- Überprüfen Sie die Service-Logs
- Verifizieren Sie Umgebungsvariablen

### OpenAI API-Fehler:
- Überprüfen Sie Ihren API-Key
- Stellen Sie sicher, dass Sie Credits haben

## 🎯 Nach dem Deployment

1. **Testen Sie die Anwendung** mit den Standard-Anmeldedaten
2. **Erstellen Sie neue Benutzer** über die Admin-Oberfläche
3. **Testen Sie die Domain-Analyse** mit einer echten Domain
4. **Konfigurieren Sie Custom Domain** (optional)

---

**Ihr SEO Profile Generator ist jetzt live! 🎉**

