# SEO Profile Generator

Ein vollständiges Web-Tool zur automatischen Generierung von SEO-optimierten Unternehmensbeschreibungen für Google-Unternehmensprofile mittels ChatGPT-4.

## 🎯 Funktionen

- **Domain-Analyse**: Eingabe einer Domain zur automatischen SEO-Analyse
- **ChatGPT-4 Integration**: Strukturierte Prompts für professionelle SEO-Texte
- **Benutzerrollen**: Admin- und Benutzer-Rollen mit entsprechenden Berechtigungen
- **Suchfunktion**: Durchsuchbare Ergebnisse mit Filterung nach Domain-Namen
- **Kopier-Funktionalität**: Einfaches Kopieren aller generierten Inhalte
- **Responsive Design**: Optimiert für Desktop und Mobile

## 🏗️ Technologie-Stack

### Backend
- **Framework**: Flask (Python)
- **Datenbank**: SQLite
- **Authentifizierung**: JWT (JSON Web Tokens)
- **API**: OpenAI GPT-4
- **CORS**: Flask-CORS für Frontend-Backend-Kommunikation

### Frontend
- **Framework**: React mit Vite
- **UI-Bibliothek**: shadcn/ui + Tailwind CSS
- **Icons**: Lucide React
- **State Management**: React Context API

## 📋 Voraussetzungen

- Python 3.11+
- Node.js 20+
- OpenAI API Key
- Git

## 🚀 Lokale Installation

### 1. Repository klonen
```bash
git clone <repository-url>
cd seo-profile-generator
```

### 2. Backend einrichten
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
```

### 3. Frontend einrichten
```bash
cd ../frontend
npm install
```

### 4. Umgebungsvariablen konfigurieren
Erstellen Sie eine `.env` Datei im Backend-Verzeichnis:
```env
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
SECRET_KEY=your_flask_secret_key_here
```

### 5. Anwendung starten

#### Entwicklungsmodus
```bash
# Terminal 1: Backend starten
cd backend
source venv/bin/activate
python src/main.py

# Terminal 2: Frontend starten
cd frontend
npm run dev
```

#### Produktionsmodus
```bash
# Frontend bauen
cd frontend
npm run build
cp -r dist/* ../backend/src/static/

# Backend starten
cd ../backend
source venv/bin/activate
python src/main.py
```

Die Anwendung ist dann unter `http://localhost:5000` erreichbar.

## 👤 Standard-Anmeldedaten

- **Benutzername**: admin
- **Passwort**: admin123
- **Rolle**: Administrator

## 📁 Projektstruktur

```
seo-profile-generator/
├── backend/                 # Flask Backend
│   ├── src/
│   │   ├── models/         # Datenbankmodelle
│   │   ├── routes/         # API-Routen
│   │   ├── static/         # Frontend-Build-Dateien
│   │   ├── database/       # SQLite-Datenbank
│   │   └── main.py         # Hauptanwendung
│   ├── venv/               # Python Virtual Environment
│   └── requirements.txt    # Python-Abhängigkeiten
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # React-Komponenten
│   │   ├── context/        # React Context
│   │   └── ...
│   ├── dist/               # Build-Ausgabe
│   └── package.json        # Node.js-Abhängigkeiten
├── render.yaml             # Render.com Deployment-Konfiguration
└── README.md               # Diese Datei
```

## 🔧 API-Endpunkte

### Authentifizierung
- `POST /api/auth/login` - Benutzer-Anmeldung
- `GET /api/auth/verify` - Token-Verifizierung
- `GET /api/auth/me` - Aktuelle Benutzerinformationen

### Benutzerverwaltung (Admin)
- `GET /api/users` - Alle Benutzer abrufen
- `POST /api/users` - Neuen Benutzer erstellen
- `PUT /api/users/{id}` - Benutzer aktualisieren
- `DELETE /api/users/{id}` - Benutzer löschen

### SEO-Analyse
- `POST /api/seo/analyze` - Domain analysieren
- `GET /api/seo/results` - Ergebnisse abrufen (mit Suche/Filterung)
- `GET /api/seo/results/{id}` - Spezifisches Ergebnis abrufen
- `DELETE /api/seo/results/{id}` - Ergebnis löschen (Admin)
- `GET /api/seo/domains/autocomplete` - Domain-Vorschläge

## 🌐 Deployment auf Render.com

### Automatisches Deployment

1. **Repository zu GitHub pushen**
2. **Render.com Account erstellen**
3. **Neuen Web Service erstellen**
4. **Repository verbinden**
5. **Umgebungsvariablen setzen**:
   - `OPENAI_API_KEY`: Ihr OpenAI API-Schlüssel
   - Andere Variablen werden automatisch generiert

### Manuelle Deployment-Schritte

1. **Render.com Dashboard öffnen**
2. **"New Web Service" klicken**
3. **GitHub Repository auswählen**
4. **Konfiguration**:
   - **Name**: seo-profile-generator
   - **Environment**: Python
   - **Build Command**: 
     ```bash
     cd backend && pip install -r requirements.txt && cd ../frontend && npm install && npm run build && cp -r dist/* ../backend/src/static/
     ```
   - **Start Command**: 
     ```bash
     cd backend && python src/main.py
     ```
5. **Umgebungsvariablen hinzufügen**
6. **Deploy klicken**

## 🔐 Sicherheitshinweise

- Ändern Sie die Standard-Admin-Anmeldedaten nach der ersten Anmeldung
- Verwenden Sie starke, einzigartige Passwörter für Produktionsumgebungen
- Halten Sie Ihren OpenAI API-Schlüssel geheim
- Aktualisieren Sie regelmäßig die Abhängigkeiten

## 🐛 Fehlerbehebung

### Häufige Probleme

1. **Authentifizierungsfehler (422)**
   - Überprüfen Sie die JWT-Token-Konfiguration
   - Stellen Sie sicher, dass CORS korrekt konfiguriert ist

2. **OpenAI API-Fehler**
   - Überprüfen Sie Ihren API-Schlüssel
   - Stellen Sie sicher, dass Sie ausreichend Credits haben

3. **Datenbankfehler**
   - Löschen Sie `backend/src/database/app.db` für einen Neustart
   - Die Datenbank wird automatisch neu erstellt

### Logs überprüfen

```bash
# Backend-Logs
cd backend
source venv/bin/activate
python src/main.py

# Frontend-Logs (Entwicklung)
cd frontend
npm run dev
```

## 📝 Lizenz

Dieses Projekt ist für den internen Gebrauch bestimmt. Alle Rechte vorbehalten.

## 🤝 Beitragen

1. Fork des Repositories erstellen
2. Feature-Branch erstellen (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen

## 📞 Support

Bei Fragen oder Problemen erstellen Sie bitte ein Issue im Repository oder kontaktieren Sie das Entwicklungsteam.

---

**Entwickelt mit ❤️ für effiziente SEO-Optimierung**

