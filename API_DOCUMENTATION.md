# API Documentation - SEO Profile Generator

Diese Dokumentation beschreibt alle verfügbaren API-Endpunkte der SEO Profile Generator Anwendung.

## 🔗 Base URL

```
Lokal: http://localhost:5000/api
Produktion: https://your-app.onrender.com/api
```

## 🔐 Authentifizierung

Die API verwendet JWT (JSON Web Tokens) für die Authentifizierung. Nach erfolgreicher Anmeldung erhalten Sie einen Token, der bei allen geschützten Endpunkten im Authorization-Header gesendet werden muss.

### Header Format
```
Authorization: Bearer <your_jwt_token>
```

## 📋 Endpunkt-Übersicht

### Authentifizierung
- `POST /auth/login` - Benutzer-Anmeldung
- `GET /auth/verify` - Token-Verifizierung
- `GET /auth/me` - Aktuelle Benutzerinformationen
- `POST /auth/register` - Neuen Benutzer registrieren (Admin)

### Benutzerverwaltung
- `GET /users` - Alle Benutzer abrufen (Admin)
- `POST /users` - Neuen Benutzer erstellen (Admin)
- `GET /users/{id}` - Spezifischen Benutzer abrufen (Admin)
- `PUT /users/{id}` - Benutzer aktualisieren (Admin)
- `DELETE /users/{id}` - Benutzer löschen (Admin)

### SEO-Analyse
- `POST /seo/analyze` - Domain analysieren
- `GET /seo/results` - Ergebnisse abrufen
- `GET /seo/results/{id}` - Spezifisches Ergebnis abrufen
- `DELETE /seo/results/{id}` - Ergebnis löschen (Admin)
- `GET /seo/domains/autocomplete` - Domain-Vorschläge

---

## 🔐 Authentifizierung Endpunkte

### POST /auth/login
Benutzer-Anmeldung mit Benutzername und Passwort.

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "created_at": "2025-07-24T08:00:00"
  }
}
```

**Response (401):**
```json
{
  "error": "Invalid credentials"
}
```

### GET /auth/verify
Token-Verifizierung für automatische Anmeldung.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "valid": true,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "created_at": "2025-07-24T08:00:00"
  }
}
```

**Response (401):**
```json
{
  "error": "Invalid token"
}
```

### GET /auth/me
Aktuelle Benutzerinformationen abrufen.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "created_at": "2025-07-24T08:00:00"
}
```

### POST /auth/register
Neuen Benutzer registrieren (nur für Admins).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepassword",
  "role": "user"
}
```

**Response (201):**
```json
{
  "id": 2,
  "username": "newuser",
  "email": "newuser@example.com",
  "role": "user",
  "created_at": "2025-07-24T08:30:00"
}
```

---

## 👥 Benutzerverwaltung Endpunkte

### GET /users
Alle Benutzer abrufen (nur für Admins).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "created_at": "2025-07-24T08:00:00"
  },
  {
    "id": 2,
    "username": "user1",
    "email": "user1@example.com",
    "role": "user",
    "created_at": "2025-07-24T08:30:00"
  }
]
```

### POST /users
Neuen Benutzer erstellen (nur für Admins).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepassword",
  "role": "user"
}
```

**Response (201):**
```json
{
  "id": 3,
  "username": "newuser",
  "email": "newuser@example.com",
  "role": "user",
  "created_at": "2025-07-24T09:00:00"
}
```

### GET /users/{id}
Spezifischen Benutzer abrufen (nur für Admins).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (200):**
```json
{
  "id": 2,
  "username": "user1",
  "email": "user1@example.com",
  "role": "user",
  "created_at": "2025-07-24T08:30:00"
}
```

### PUT /users/{id}
Benutzer aktualisieren (nur für Admins).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request:**
```json
{
  "username": "updateduser",
  "email": "updated@example.com",
  "role": "admin",
  "password": "newpassword"
}
```

**Response (200):**
```json
{
  "id": 2,
  "username": "updateduser",
  "email": "updated@example.com",
  "role": "admin",
  "created_at": "2025-07-24T08:30:00"
}
```

### DELETE /users/{id}
Benutzer löschen (nur für Admins).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (204):**
```
No Content
```

---

## 🔍 SEO-Analyse Endpunkte

### POST /seo/analyze
Domain analysieren und SEO-Beschreibung generieren.

**Headers:**
```
Authorization: Bearer <token>
```

**Request:**
```json
{
  "domain": "example.com"
}
```

**Response (201):**
```json
{
  "message": "Domain analysis completed successfully",
  "result": {
    "id": 1,
    "domain": "example.com",
    "short_description": "Innovative Lösungen für moderne Unternehmen...",
    "long_description": "Unser Unternehmen bietet innovative Lösungen...",
    "keywords": "Keyword 1, Keyword 2, Keyword 3...",
    "opening_hours": "Montag–Freitag: 9:00–18:00...",
    "company_info": "Unternehmen: Example GmbH...",
    "raw_response": "**BILDER:** [Bild 1] [Bild 2]...",
    "created_at": "2025-07-24T09:15:00",
    "user_id": 1,
    "username": "admin"
  }
}
```

**Response (200) - Bereits analysiert:**
```json
{
  "message": "Analysis already exists for this domain",
  "result": {
    "id": 1,
    "domain": "example.com",
    // ... gleiche Struktur wie oben
  }
}
```

**Response (500):**
```json
{
  "error": "Analysis failed: OpenAI API error"
}
```

### GET /seo/results
Ergebnisse abrufen mit optionaler Suche und Paginierung.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `search` (optional): Suchbegriff für Domain-Namen
- `page` (optional): Seitennummer (Standard: 1)
- `per_page` (optional): Ergebnisse pro Seite (Standard: 10)

**Beispiel:**
```
GET /seo/results?search=example&page=1&per_page=5
```

**Response (200):**
```json
{
  "results": [
    {
      "id": 1,
      "domain": "example.com",
      "short_description": "Innovative Lösungen...",
      "long_description": "Unser Unternehmen...",
      "keywords": "Keyword 1, Keyword 2...",
      "opening_hours": "Montag–Freitag: 9:00–18:00...",
      "company_info": "Unternehmen: Example GmbH...",
      "raw_response": "**BILDER:** [Bild 1]...",
      "created_at": "2025-07-24T09:15:00",
      "user_id": 1,
      "username": "admin"
    }
  ],
  "total": 1,
  "pages": 1,
  "current_page": 1,
  "per_page": 10
}
```

### GET /seo/results/{id}
Spezifisches Ergebnis abrufen.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "domain": "example.com",
  "short_description": "Innovative Lösungen...",
  "long_description": "Unser Unternehmen...",
  "keywords": "Keyword 1, Keyword 2...",
  "opening_hours": "Montag–Freitag: 9:00–18:00...",
  "company_info": "Unternehmen: Example GmbH...",
  "raw_response": "**BILDER:** [Bild 1]...",
  "created_at": "2025-07-24T09:15:00",
  "user_id": 1,
  "username": "admin"
}
```

**Response (403) - Zugriff verweigert:**
```json
{
  "error": "Access denied"
}
```

### DELETE /seo/results/{id}
Ergebnis löschen (nur für Admins).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Response (204):**
```
No Content
```

### GET /seo/domains/autocomplete
Domain-Vorschläge für Autocomplete-Funktionalität.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `q`: Suchbegriff

**Beispiel:**
```
GET /seo/domains/autocomplete?q=exam
```

**Response (200):**
```json
[
  "example.com",
  "example.org",
  "example-shop.de"
]
```

---

## 🚨 Fehler-Codes

### HTTP Status Codes

| Code | Bedeutung | Beschreibung |
|------|-----------|--------------|
| 200 | OK | Anfrage erfolgreich |
| 201 | Created | Ressource erfolgreich erstellt |
| 204 | No Content | Erfolgreich, keine Antwort |
| 400 | Bad Request | Ungültige Anfrage |
| 401 | Unauthorized | Authentifizierung erforderlich |
| 403 | Forbidden | Zugriff verweigert |
| 404 | Not Found | Ressource nicht gefunden |
| 422 | Unprocessable Entity | Validierungsfehler |
| 500 | Internal Server Error | Serverfehler |

### Fehler-Response Format

```json
{
  "error": "Beschreibung des Fehlers"
}
```

### Häufige Fehler

#### Authentifizierung
```json
{
  "error": "Invalid credentials"
}
```

#### Autorisierung
```json
{
  "error": "Admin access required"
}
```

#### Validierung
```json
{
  "error": "Username and password required"
}
```

#### OpenAI API
```json
{
  "error": "Analysis failed: OpenAI API error"
}
```

---

## 📝 Beispiel-Workflows

### Vollständiger Anmelde-Workflow

1. **Anmelden:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

2. **Token verwenden:**
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer <your_token>"
```

### Domain-Analyse-Workflow

1. **Domain analysieren:**
```bash
curl -X POST http://localhost:5000/api/seo/analyze \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

2. **Ergebnisse abrufen:**
```bash
curl -X GET http://localhost:5000/api/seo/results \
  -H "Authorization: Bearer <your_token>"
```

### Benutzerverwaltung-Workflow (Admin)

1. **Alle Benutzer anzeigen:**
```bash
curl -X GET http://localhost:5000/api/users \
  -H "Authorization: Bearer <admin_token>"
```

2. **Neuen Benutzer erstellen:**
```bash
curl -X POST http://localhost:5000/api/users \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "new@example.com", "password": "password123", "role": "user"}'
```

---

## 🔧 Rate Limiting

Aktuell sind keine Rate Limits implementiert. Für Produktionsumgebungen wird empfohlen:

- **Authentifizierung**: 5 Versuche pro Minute
- **Domain-Analyse**: 10 Anfragen pro Stunde (OpenAI API Limits)
- **Allgemeine API**: 100 Anfragen pro Minute

## 📊 Monitoring

### Health Check
```bash
curl -X GET http://localhost:5000/
```

### API Status
```bash
curl -X GET http://localhost:5000/api/auth/verify \
  -H "Authorization: Bearer <token>"
```

---

**API Version: 1.0**  
**Letzte Aktualisierung: Juli 2025**

