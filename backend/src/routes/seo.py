from flask import Blueprint, jsonify, request, session
from src.models.user import User, SEOResult, db
import openai
import json
import re
from urllib.parse import urlparse

seo_bp = Blueprint('seo', __name__)

def require_admin():
    """Helper function to check if current user is admin"""
    if 'user_id' not in session:
        return False
    current_user = User.query.get(session['user_id'])
    return current_user and current_user.role == 'admin'

def get_current_user():
    """Helper function to get current user from session"""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

def normalize_domain(domain):
    """Normalize domain input to ensure consistent format"""
    if not domain.startswith(('http://', 'https://')):
        domain = 'https://' + domain
    
    parsed = urlparse(domain)
    return parsed.netloc.lower()

def parse_seo_response(response_text):
    """Parse the structured SEO response from GPT"""
    result = {
        'short_description': '',
        'long_description': '',
        'keywords': '',
        'opening_hours': '',
        'company_info': ''
    }
    
    try:
        # Extract sections using regex patterns
        sections = {
            'short_description': r'1\.\s*\*\*Kurzbeschreibung\*\*.*?\n(.*?)(?=\n\n|\n2\.)',
            'long_description': r'2\.\s*\*\*Langbeschreibung\*\*.*?\n(.*?)(?=\n\n|\n3\.)',
            'keywords': r'3\.\s*\*\*Keywords\*\*.*?\n(.*?)(?=\n\n|\n4\.)',
            'opening_hours': r'4\.\s*\*\*Öffnungszeiten\*\*.*?\n(.*?)(?=\n\n|\n5\.)',
            'company_info': r'5\.\s*\*\*Impressum\*\*.*?\n(.*?)(?=\n\n|$)'
        }
        
        for key, pattern in sections.items():
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                result[key] = match.group(1).strip()
    
    except Exception as e:
        print(f"Error parsing SEO response: {e}")
    
    return result

@seo_bp.route('/analyze', methods=['POST'])
def analyze_domain():
    """Analyze a domain using OpenAI GPT-4"""
    # Check authentication
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    current_user = User.query.get(session['user_id'])
    if not current_user:
        session.clear()
        return jsonify({'error': 'User not found'}), 404
    
    data = request.json
    if not data or not data.get('domain'):
        return jsonify({'error': 'Domain is required'}), 400
    
    domain = normalize_domain(data['domain'])
    
    # Check if analysis already exists for this domain
    existing_result = SEOResult.query.filter_by(domain=domain).first()
    if existing_result:
        return jsonify({
            'message': 'Analysis already exists for this domain',
            'result': existing_result.to_dict()
        }), 200
    
    # Prepare the GPT prompt
    prompt = f"""[**ROLLE** Du bist ein erfahrener SEO-Texter und Experte für Google-Unternehmensprofile. **ZIEL** Erstelle eine prägnante, suchmaschinenoptimierte und zugleich kundenfreundliche Unternehmensbeschreibung für ein Google-Unternehmensprofil. Keine Quellenverweise. Es soll ein guter Werbetext sein wie von einem SEO Profi geschrieben.

--- ### ARBEITSABLAUF — SCHRITT FÜR SCHRITT
1. **Website-URL anfordern**
Bitte fordere zunächst die URL der Unternehmenswebsite an, um die benötigten Informationen zu extrahieren.
2. **Website analysieren**
Prüfe und notiere:
• Dienstleistungen / Produkte
• Alleinstellungsmerkmale (USPs)
• Zielgruppe
• Standort
• Öffnungszeiten
• Impressumsangaben (Firmenname, Adresse, Geschäftsführer, E-Mail, Telefonnummer, Kontakt, Handelsregister, USt-ID)
3. **Inhalte aufbereiten**
– Aktive, klare Sprache; keine Füllwörter.
– Kundennutzen und Mehrwert deutlich herausstellen.
– Zehn relevante SEO-Keywords natürlich einbauen (kein Keyword-Stuffing); fehlende Infos mit „[Angabe fehlt]" kennzeichnen.
– Bei mehreren Standorten jeden Standort separat mit vollständigen Daten aufführen.
4. **Bilder einbinden**
– Wähle 1 – 3 aussagekräftige, lizenzfreie Screenshots oder Fotos von der Website (Hero-Bereich, Produkt, Team o. Ä.).
– Zeige die Bilder direkt im Chat, bevor du die Textabschnitte ausgibst.
– Verwende ausschließlich eigene Screenshots oder frei nutzbare Bilder.

--- ### AUSGABESTRUKTUR *(Rein als Klartext, keine Markdown-Syntax verwenden)*
**BILDER:** [Bild 1] [Bild 2] [Bild 3]

1. **Kurzbeschreibung** (max. 150 Zeichen)
<Knackige Zusammenfassung des Angebots>

2. **Langbeschreibung** (ca. 750 Zeichen)
<Ausführliche, SEO-optimierte Beschreibung mit USPs, Keywords und Kundennutzen>

3. **Keywords**
– Keyword 1, Keyword 2, … Keyword 10

4. **Öffnungszeiten**
– Montag–Freitag: <Zeiten>
– Samstag: <Zeiten>
– Sonntag: <Zeiten>

5. **Impressum**
Unternehmen: <Firmenname>
Adresse: <Straße, PLZ, Stadt>
Geschäftsführer: <n>
Kontakt: <Telefon, E-Mail>

--- ### HINWEISE
* Keine Quellenangaben, Fußnoten, URLs oder sonstige Verweise im Text.
* Zeichenlimits strikt einhalten.
* Qualität vor Quantität: klare, informative und überzeugende Formulierungen.

Bitte analysiere die Website: {domain}"""

    try:
        # Call OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du bist ein erfahrener SEO-Experte und Texter für Google-Unternehmensprofile."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        raw_response = response.choices[0].message.content
        
        # Parse the structured response
        parsed_data = parse_seo_response(raw_response)
        
        # Save to database
        seo_result = SEOResult(
            domain=domain,
            short_description=parsed_data['short_description'],
            long_description=parsed_data['long_description'],
            keywords=parsed_data['keywords'],
            opening_hours=parsed_data['opening_hours'],
            company_info=parsed_data['company_info'],
            raw_response=raw_response,
            user_id=current_user_id
        )
        
        db.session.add(seo_result)
        db.session.commit()
        
        return jsonify({
            'message': 'Domain analysis completed successfully',
            'result': seo_result.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@seo_bp.route('/results', methods=['GET'])
def get_results():
    """Get SEO results with optional search and filtering"""
    # Check authentication
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    current_user = User.query.get(session['user_id'])
    if not current_user:
        session.clear()  # Clear invalid session
        return jsonify({'error': 'User not found'}), 401
    
    # Get query parameters
    search = request.args.get('search', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Build query
    query = SEOResult.query
    
    # If not admin, only show user's own results
    if current_user.role != 'admin':
        query = query.filter_by(user_id=current_user.id)
    
    # Apply search filter
    if search:
        query = query.filter(SEOResult.domain.contains(search))
    
    # Order by creation date (newest first)
    query = query.order_by(SEOResult.created_at.desc())
    
    # Paginate results
    results = query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'results': [result.to_dict() for result in results.items],
        'total': results.total,
        'pages': results.pages,
        'current_page': page,
        'per_page': per_page
    }), 200

@seo_bp.route('/results/<int:result_id>', methods=['GET'])
def get_result(result_id):
    """Get specific SEO result"""
    # Check authentication
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    current_user = User.query.get(session['user_id'])
    if not current_user:
        session.clear()
        return jsonify({'error': 'User not found'}), 404
    
    result = SEOResult.query.get_or_404(result_id)
    
    # Check access permissions
    if current_user.role != 'admin' and result.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(result.to_dict()), 200

@seo_bp.route('/results/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    """Delete SEO result (admin only)"""
    if not require_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    result = SEOResult.query.get_or_404(result_id)
    db.session.delete(result)
    db.session.commit()
    
    return '', 204

@seo_bp.route('/domains/autocomplete', methods=['GET'])
def autocomplete_domains():
    """Get domain suggestions for autocomplete"""
    # Check authentication
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    current_user = User.query.get(session['user_id'])
    if not current_user:
        session.clear()
        return jsonify({'error': 'User not found'}), 404
    
    search = request.args.get('q', '').strip()
    
    if not search:
        return jsonify([]), 200
    
    # Build query
    query = SEOResult.query
    
    # If not admin, only show user's own results
    if current_user.role != 'admin':
        query = query.filter_by(user_id=current_user_id)
    
    # Filter by domain containing search term
    domains = query.filter(SEOResult.domain.contains(search)).with_entities(SEOResult.domain).distinct().limit(10).all()
    
    return jsonify([domain[0] for domain in domains]), 200

