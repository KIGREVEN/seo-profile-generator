from flask import Blueprint, jsonify, request, session
from src.models.user import User, SEOResult, db
import openai
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time

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

def crawl_website(url):
    """Crawl website and extract relevant content"""
    try:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else ""
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc.get('content', '').strip() if meta_desc else ""
        
        # Extract main content
        # Try to find main content areas
        main_content = ""
        
        # Look for main content containers
        content_selectors = [
            'main', '[role="main"]', '.main-content', '#main-content',
            '.content', '#content', '.page-content', '.entry-content',
            'article', '.article', 'section', '.section'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements[:3]:  # Take first 3 matches
                    text = element.get_text(separator=' ', strip=True)
                    if len(text) > 100:  # Only include substantial content
                        main_content += text + "\n\n"
                break
        
        # If no main content found, extract from body
        if not main_content:
            body = soup.find('body')
            if body:
                main_content = body.get_text(separator=' ', strip=True)
        
        # Clean up text
        main_content = re.sub(r'\s+', ' ', main_content).strip()
        
        # Limit content length to avoid token limits
        if len(main_content) > 3000:
            main_content = main_content[:3000] + "..."
        
        # Extract contact information
        contact_info = extract_contact_info(soup)
        
        return {
            'url': url,
            'title': title_text,
            'meta_description': meta_description,
            'content': main_content,
            'contact_info': contact_info,
            'success': True
        }
        
    except requests.RequestException as e:
        return {
            'url': url,
            'error': f'Failed to fetch website: {str(e)}',
            'success': False
        }
    except Exception as e:
        return {
            'url': url,
            'error': f'Failed to parse website: {str(e)}',
            'success': False
        }

def extract_contact_info(soup):
    """Extract contact information from website"""
    contact_info = {}
    
    # Look for phone numbers
    phone_pattern = r'(\+49|0)[0-9\s\-/()]{8,}'
    text = soup.get_text()
    phones = re.findall(phone_pattern, text)
    if phones:
        contact_info['phone'] = phones[0]
    
    # Look for email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        contact_info['email'] = emails[0]
    
    # Look for addresses (German format)
    address_pattern = r'\d{5}\s+[A-Za-zäöüß\s]+'
    addresses = re.findall(address_pattern, text)
    if addresses:
        contact_info['address'] = addresses[0]
    
    return contact_info

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
    
    # Crawl the website first
    print(f"Crawling website: {domain}")
    crawl_result = crawl_website(domain)
    
    if not crawl_result['success']:
        return jsonify({
            'error': f'Failed to crawl website: {crawl_result["error"]}'
        }), 400
    
    # Prepare the GPT prompt with real website content
    prompt = f"""**ROLLE:** Du bist ein erfahrener SEO-Texter und Experte für Google-Unternehmensprofile.

**AUFGABE:** Erstelle eine prägnante, suchmaschinenoptimierte Unternehmensbeschreibung für ein Google-Unternehmensprofil basierend auf den ECHTEN Website-Inhalten.

**WEBSITE-INFORMATIONEN:**
URL: {crawl_result['url']}
Titel: {crawl_result['title']}
Meta-Beschreibung: {crawl_result['meta_description']}

**WEBSITE-INHALT:**
{crawl_result['content']}

**KONTAKT-INFORMATIONEN:**
{json.dumps(crawl_result['contact_info'], indent=2)}

**ANWEISUNGEN:**
1. Analysiere NUR die bereitgestellten Website-Inhalte
2. Erfinde KEINE Informationen, die nicht auf der Website stehen
3. Erstelle eine professionelle SEO-optimierte Beschreibung
4. Verwende natürliche Keywords aus dem Website-Inhalt
5. Halte die Zeichenlimits ein

**AUSGABEFORMAT:**
1. **Kurzbeschreibung** (max. 150 Zeichen)
[Prägnante Zusammenfassung basierend auf echten Website-Inhalten]

2. **Langbeschreibung** (ca. 750 Zeichen)
[Ausführliche Beschreibung mit echten USPs und Services von der Website]

3. **Keywords** (10 relevante Keywords aus dem Website-Inhalt)
[Keyword 1, Keyword 2, ...]

4. **Öffnungszeiten**
[Falls auf der Website gefunden, sonst: "Nicht auf Website angegeben"]

5. **Kontaktinformationen**
[Echte Kontaktdaten von der Website oder "Nicht verfügbar"]

**WICHTIG:** Verwende ausschließlich Informationen, die tatsächlich auf der Website stehen!"""

    try:
        # Call OpenAI API
        import os
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        client = openai.OpenAI(api_key=api_key)
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
            user_id=current_user.id
        )
        
        db.session.add(seo_result)
        db.session.commit()
        
        return jsonify({
            'message': 'Domain analysis completed successfully',
            'result': seo_result.to_dict()
        }), 201
        
    except Exception as e:
        print(f"SEO Analysis Error: {str(e)}")
        import traceback
        traceback.print_exc()
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

