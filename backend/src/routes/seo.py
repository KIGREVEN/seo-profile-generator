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
        
        # Remove only script and style elements (keep footer for opening hours!)
        for script in soup(["script", "style"]):
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
        
        # Extract footer content separately (important for opening hours!)
        footer_content = ""
        footer_elements = soup.find_all(['footer', '.footer', '#footer', '.site-footer'])
        for footer in footer_elements:
            footer_text = footer.get_text(separator=' ', strip=True)
            if len(footer_text) > 20:  # Only substantial footer content
                footer_content += footer_text + "\n\n"
        
        # Combine main content with footer
        full_content = main_content
        if footer_content:
            full_content += "\n\n=== FOOTER-INFORMATIONEN ===\n" + footer_content
        
        # Clean up text
        full_content = re.sub(r'\s+', ' ', full_content).strip()
        
        # Limit content length to avoid token limits
        if len(full_content) > 4000:
            full_content = full_content[:4000] + "..."
        
        # Extract contact information and opening hours
        contact_info = extract_contact_info(soup)
        opening_hours = extract_opening_hours(soup)
        
        return {
            'url': url,
            'title': title_text,
            'meta_description': meta_description,
            'content': full_content,
            'contact_info': contact_info,
            'opening_hours': opening_hours,
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

def extract_opening_hours(soup):
    """Extract opening hours from website with comprehensive patterns"""
    opening_hours = {}
    
    # Get all text from the page
    full_text = soup.get_text()
    
    # Debug: Print relevant sections
    print("=== OPENING HOURS DEBUG ===")
    print(f"Full text length: {len(full_text)}")
    
    # Look for opening hours keywords in full text
    opening_keywords = [
        'öffnungszeiten', 'opening hours', 'geschäftszeiten', 'servicezeiten',
        'sprechzeiten', 'bürozeiten', 'arbeitszeiten', 'zeiten'
    ]
    
    # Find lines containing opening hours
    lines = full_text.split('\n')
    relevant_lines = []
    
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if any(keyword in line_lower for keyword in opening_keywords):
            # Include surrounding lines for context
            start = max(0, i - 3)
            end = min(len(lines), i + 5)
            context_lines = lines[start:end]
            relevant_lines.extend(context_lines)
            print(f"Found opening hours context around line {i}:")
            for j, context_line in enumerate(context_lines):
                print(f"  {start + j}: {context_line.strip()}")
            break
    
    # Also check footer specifically
    footer_elements = soup.find_all(['footer', '.footer', '#footer', '.contact', '.kontakt'])
    for footer in footer_elements:
        footer_text = footer.get_text()
        print(f"Footer content: {footer_text}")
        relevant_lines.extend(footer_text.split('\n'))
    
    # Look for the specific pattern from screenshot: "Mo - Fr: 10:00 - 13:00 Uhr & 14:00 - 18:00 Uhr"
    full_text_lower = full_text.lower()
    
    # Multiple patterns to try
    patterns_to_test = [
        # Original patterns for & separator
        r'mo[\s\-]+fr[\s:]*(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})\s*uhr\s*[&]+\s*(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})\s*uhr',
        r'mo[\s\-]+fr[\s:]*(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})\s*[&]+\s*(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})',
        r'(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})\s*uhr\s*[&]+\s*(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})\s*uhr',
        r'(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})\s*[&]+\s*(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})',
        # New patterns for 'bis' separator - "Mo. bis Sa.: 8:00 bis 18:00 Uhr"
        r'mo\.?\s*bis\s*sa\.?[\s:]*(\d{1,2}):(\d{2})\s*bis\s*(\d{1,2}):(\d{2})\s*uhr',
        r'mo\.?\s*bis\s*sa\.?[\s:]*(\d{1,2}):(\d{2})\s*bis\s*(\d{1,2}):(\d{2})',
        # General day range patterns
        r'(mo|montag)\.?\s*bis\s*(sa|samstag)\.?[\s:]*(\d{1,2}):(\d{2})\s*bis\s*(\d{1,2}):(\d{2})\s*uhr',
        r'(mo|montag)\.?\s*bis\s*(sa|samstag)\.?[\s:]*(\d{1,2}):(\d{2})\s*bis\s*(\d{1,2}):(\d{2})',
    ]
    
    print("Testing patterns on full text...")
    for i, pattern in enumerate(patterns_to_test):
        matches = re.findall(pattern, full_text_lower)
        print(f"Pattern {i+1}: {pattern}")
        print(f"Matches: {matches}")
        
        if matches:
            match = matches[0]
            
            # Handle different match group lengths
            if len(match) >= 8:  # Double time range (&)
                time_str = f"{match[0]}:{match[1]} - {match[2]}:{match[3]} & {match[4]}:{match[5]} - {match[6]}:{match[7]}"
                print(f"SUCCESS: Found double time range: {time_str}")
                for day in ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag']:
                    opening_hours[day] = time_str
                print("=== END DEBUG ===")
                return opening_hours
            elif len(match) >= 6:  # Day range with bis (Mo bis Sa)
                # Extract time from the match
                if match[0] in ['mo', 'montag'] and match[1] in ['sa', 'samstag']:
                    # Mo bis Sa pattern
                    start_hour = match[2] if len(match) > 2 else match[-4]
                    start_min = match[3] if len(match) > 3 else match[-3]
                    end_hour = match[4] if len(match) > 4 else match[-2]
                    end_min = match[5] if len(match) > 5 else match[-1]
                    time_str = f"{start_hour}:{start_min} - {end_hour}:{end_min}"
                    print(f"SUCCESS: Found Mo bis Sa range: {time_str}")
                    # Apply to all days Monday to Saturday
                    for day in ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag', 'samstag']:
                        opening_hours[day] = time_str
                    print("=== END DEBUG ===")
                    return opening_hours
            elif len(match) >= 4:  # Simple time range
                start_hour = match[-4] if len(match) >= 4 else match[0]
                start_min = match[-3] if len(match) >= 4 else match[1]
                end_hour = match[-2] if len(match) >= 4 else match[2]
                end_min = match[-1] if len(match) >= 4 else match[3]
                time_str = f"{start_hour}:{start_min} - {end_hour}:{end_min}"
                print(f"SUCCESS: Found simple time range: {time_str}")
                # Check if this is a Mo bis Sa pattern by looking at the original text
                if 'mo' in full_text_lower and 'bis' in full_text_lower and 'sa' in full_text_lower:
                    for day in ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag', 'samstag']:
                        opening_hours[day] = time_str
                else:
                    for day in ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag']:
                        opening_hours[day] = time_str
                print("=== END DEBUG ===")
                return opening_hours
    
    # Fallback to original logic if patterns don't work
    print("No double patterns matched, falling back to original logic...")
    print("=== END DEBUG ===")
    
    # German day names and their variations
    day_patterns = {
        'montag': ['montag', 'mo', 'mon'],
        'dienstag': ['dienstag', 'di', 'die', 'tue'],
        'mittwoch': ['mittwoch', 'mi', 'mit', 'wed'],
        'donnerstag': ['donnerstag', 'do', 'don', 'thu'],
        'freitag': ['freitag', 'fr', 'fre', 'fri'],
        'samstag': ['samstag', 'sa', 'sam', 'sat'],
        'sonntag': ['sonntag', 'so', 'son', 'sun']
    }
    
    # Time patterns - enhanced for more formats
    time_patterns = [
        # Standard formats
        r'(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})',  # 09:00 - 18:00
        r'(\d{1,2})\.(\d{2})\s*-\s*(\d{1,2})\.(\d{2})',  # 09.00 - 18.00
        r'(\d{1,2})\s*-\s*(\d{1,2})\s*Uhr',  # 9 - 18 Uhr
        r'(\d{1,2}):(\d{2})\s*bis\s*(\d{1,2}):(\d{2})',  # 09:00 bis 18:00
        r'(\d{1,2})\s*bis\s*(\d{1,2})\s*Uhr',  # 9 bis 18 Uhr
        # Multiple time ranges with & or und
        r'(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*(?:Uhr\s*)?[&und]+\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*Uhr?',  # 10:00 - 13:00 Uhr & 14:00 - 18:00 Uhr
        # NEW: Formats with "Uhr" and em-dash (–)
        r'(\d{1,2}):(\d{2})\s*Uhr\s*[–-]\s*(\d{1,2}):(\d{2})\s*Uhr',  # 8:00 Uhr – 16:00 Uhr
        r'(\d{1,2}):(\d{2})\s*[–-]\s*(\d{1,2}):(\d{2})\s*Uhr',  # 8:00 – 16:00 Uhr
    ]
    
    # Look for opening hours keywords
    opening_keywords = [
        'öffnungszeiten', 'opening hours', 'geschäftszeiten', 'servicezeiten',
        'sprechzeiten', 'bürozeiten', 'arbeitszeiten', 'zeiten'
    ]
    
    # Split text into lines for better parsing
    lines = full_text.lower().split('\n')
    
    # Find sections that might contain opening hours
    relevant_sections = []
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in opening_keywords):
            # Include surrounding lines
            start = max(0, i - 2)
            end = min(len(lines), i + 10)
            relevant_sections.extend(lines[start:end])
    
    # If no specific sections found, search in footer and contact areas
    if not relevant_sections:
        footer_elements = soup.find_all(['footer', '.footer', '#footer', '.contact', '.kontakt'])
        for element in footer_elements:
            relevant_sections.extend(element.get_text().lower().split('\n'))
    
    # Parse opening hours from relevant sections
    for line in relevant_sections:
        line = line.strip()
        if len(line) < 5:  # Skip very short lines
            continue
        
        # NEW: Handle complex day patterns like "Montag, Mittwoch, Donnerstag:" and "Dienstag und Freitag:"
        # Pattern for multiple days with comma: "Montag, Mittwoch, Donnerstag: 8:00 Uhr – 16:00 Uhr"
        complex_day_pattern = r'((?:montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag)(?:\s*,\s*(?:montag|dienstag|mittwoch|donnerstag|freitag|samstag|sonntag))*)\s*:\s*(.+)'
        complex_match = re.search(complex_day_pattern, line.lower())
        if complex_match:
            days_str = complex_match.group(1)
            time_str = complex_match.group(2)
            
            # Extract individual days
            days = [day.strip() for day in days_str.replace(' und ', ', ').split(',')]
            
            # Extract time from the time string
            for pattern in time_patterns:
                time_matches = re.findall(pattern, time_str)
                if time_matches:
                    match = time_matches[0]
                    if len(match) == 4:  # Full time format
                        formatted_time = f"{match[0]}:{match[1]} - {match[2]}:{match[3]}"
                    elif len(match) == 2:  # Simple hour format
                        formatted_time = f"{match[0]}:00 - {match[1]}:00"
                    else:
                        formatted_time = time_str.strip()
                    
                    # Apply to all mentioned days
                    for day in days:
                        day = day.strip()
                        if day in day_patterns:
                            opening_hours[day] = formatted_time
                            print(f"Found complex pattern for {day}: {formatted_time}")
                    break
            continue
            
        # Check each day
        for day_name, variations in day_patterns.items():
            for variation in variations:
                if variation in line:
                    # Look for time patterns in this line
                    for pattern in time_patterns:
                        matches = re.findall(pattern, line)
                        if matches:
                            # Format the time nicely
                            match = matches[0]
                            if len(match) == 8:  # Multiple time ranges (10:00-13:00 & 14:00-18:00)
                                time_str = f"{match[0]}:{match[1]} - {match[2]}:{match[3]} & {match[4]}:{match[5]} - {match[6]}:{match[7]}"
                            elif len(match) == 4:  # Full time format
                                time_str = f"{match[0]}:{match[1]} - {match[2]}:{match[3]}"
                            elif len(match) == 2:  # Simple hour format
                                time_str = f"{match[0]}:00 - {match[1]}:00"
                            else:
                                time_str = line.strip()
                            
                            opening_hours[day_name] = time_str
                            break
                    
                    # Also check for "geschlossen" or "closed"
                    if any(word in line for word in ['geschlossen', 'closed', 'zu']):
                        opening_hours[day_name] = 'Geschlossen'
    
    # Look for common patterns like "Mo-Fr: 9-18" and "Mo - Fr: 9:00 - 17:00"
    range_patterns = [
        # Mo - Fr: 9:00 - 17:00
        r'(mo|montag)[\s\-]+(fr|freitag)[\s:]*(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})',
        # Mo-Fr: 9-18
        r'(mo|montag)[\s\-]+(fr|freitag)[\s:]*(\d{1,2})[\s\-]+(\d{1,2})',
        # Sa - So: Geschlossen
        r'(sa|samstag)[\s\-]+(so|sonntag)[\s:]*geschlossen',
        # Mo - Fr 9:00 - 17:00 (without colon)
        r'(mo|montag)[\s\-]+(fr|freitag)\s+(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})',
    ]
    
    for line in relevant_sections:
        # Check for weekday ranges
        for pattern in range_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                if 'geschlossen' in line.lower():
                    # Weekend closed
                    for day in ['samstag', 'sonntag']:
                        if day not in opening_hours:
                            opening_hours[day] = 'Geschlossen'
                else:
                    # Weekday hours
                    groups = match.groups()
                    if len(groups) >= 6:  # Full time format with minutes
                        start_hour = groups[2]
                        start_min = groups[3]
                        end_hour = groups[4]
                        end_min = groups[5]
                        time_str = f"{start_hour}:{start_min} - {end_hour}:{end_min}"
                    elif len(groups) >= 4:  # Simple hour format
                        start_hour = groups[2]
                        end_hour = groups[3]
                        time_str = f"{start_hour}:00 - {end_hour}:00"
                    else:
                        continue
                    
                    # Apply to weekdays
                    for day in ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag']:
                        if day not in opening_hours:
                            opening_hours[day] = time_str
    
    # Additional specific patterns for the format seen in the screenshot
    # Look for "Mo - Fr" followed by time, and "Sa - So" followed by "Geschlossen"
    mo_fr_pattern = r'mo[\s\-]+fr[\s:]*(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})'
    sa_so_pattern = r'sa[\s\-]+so[\s:]*geschlossen'
    
    # Pattern for multiple time ranges like "Mo - Fr: 10:00 - 13:00 Uhr & 14:00 - 18:00 Uhr"
    mo_fr_double_pattern = r'mo[\s\-]+fr[\s:]*(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})\s*(?:uhr\s*)?[&und]+\s*(\d{1,2}):(\d{2})[\s\-]+(\d{1,2}):(\d{2})\s*uhr?'
    
    full_text_lower = full_text.lower()
    
    # Check for Mo - Fr pattern with double time ranges first
    mo_fr_double_match = re.search(mo_fr_double_pattern, full_text_lower)
    if mo_fr_double_match:
        start_hour1 = mo_fr_double_match.group(1)
        start_min1 = mo_fr_double_match.group(2)
        end_hour1 = mo_fr_double_match.group(3)
        end_min1 = mo_fr_double_match.group(4)
        start_hour2 = mo_fr_double_match.group(5)
        start_min2 = mo_fr_double_match.group(6)
        end_hour2 = mo_fr_double_match.group(7)
        end_min2 = mo_fr_double_match.group(8)
        time_str = f"{start_hour1}:{start_min1} - {end_hour1}:{end_min1} & {start_hour2}:{start_min2} - {end_hour2}:{end_min2}"
        
        for day in ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag']:
            if day not in opening_hours:
                opening_hours[day] = time_str
    
    # Check for simple Mo - Fr pattern (fallback)
    elif not opening_hours:  # Only if no hours found yet
        mo_fr_match = re.search(mo_fr_pattern, full_text_lower)
        if mo_fr_match:
            start_hour = mo_fr_match.group(1)
            start_min = mo_fr_match.group(2)
            end_hour = mo_fr_match.group(3)
            end_min = mo_fr_match.group(4)
            time_str = f"{start_hour}:{start_min} - {end_hour}:{end_min}"
            
            for day in ['montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag']:
                if day not in opening_hours:
                    opening_hours[day] = time_str
    
    # Check for Sa - So pattern
    if re.search(sa_so_pattern, full_text_lower):
        for day in ['samstag', 'sonntag']:
            if day not in opening_hours:
                opening_hours[day] = 'Geschlossen'
    
    return opening_hours

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
        print("=== PARSING DEBUG ===")
        print(f"Response text length: {len(response_text)}")
        print(f"First 500 chars: {response_text[:500]}")
        
        # Extract sections using regex patterns for the new format
        sections = {
            # New format patterns without markdown
            'short_description': r'Kurzbeschreibung\s*\([^)]*\)\s*\n(.*?)(?=\n\n|\nLangbeschreibung)',
            'long_description': r'Langbeschreibung\s*\([^)]*\)\s*\n(.*?)(?=\n\n|\nLeistungen:|\nKeywords)',
            'keywords': r'Keywords\s*\n(.*?)(?=\n\n|\nÖffnungszeiten)',
            'opening_hours': r'Öffnungszeiten\s*\n(.*?)(?=\n\n|\nImpressum)',
            'company_info': r'Impressum\s*\n(.*?)(?=\n\n|$)',
            
            # Fallback patterns for old format (with markdown)
            'short_description_old': r'1\.\s*\*\*Kurzbeschreibung\*\*.*?\n(.*?)(?=\n\n|\n2\.)',
            'long_description_old': r'2\.\s*\*\*Langbeschreibung\*\*.*?\n(.*?)(?=\n\n|\n3\.)',
            'keywords_old': r'3\.\s*\*\*Keywords\*\*.*?\n(.*?)(?=\n\n|\n4\.)',
            'opening_hours_old': r'4\.\s*\*\*Öffnungszeiten\*\*.*?\n(.*?)(?=\n\n|\n5\.)',
            'company_info_old': r'5\.\s*\*\*Impressum\*\*.*?\n(.*?)(?=\n\n|$)'
        }
        
        # Try new format first, then fallback to old format
        for key in ['short_description', 'long_description', 'keywords', 'opening_hours', 'company_info']:
            # Try new format
            pattern = sections[key]
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                result[key] = match.group(1).strip()
                print(f"Found {key} (new format): {result[key][:100]}...")
            else:
                # Try old format
                old_pattern = sections[f'{key}_old']
                match = re.search(old_pattern, response_text, re.DOTALL | re.IGNORECASE)
                if match:
                    result[key] = match.group(1).strip()
                    print(f"Found {key} (old format): {result[key][:100]}...")
                else:
                    print(f"No match found for {key}")
        
        # Additional parsing for Leistungen (services) if present
        services_pattern = r'Leistungen:\s*\n((?:–[^\n]+\n?)+)'
        services_match = re.search(services_pattern, response_text, re.DOTALL | re.IGNORECASE)
        if services_match:
            services = services_match.group(1).strip()
            # Append services to long description if found
            if result['long_description']:
                result['long_description'] += f"\n\nLeistungen:\n{services}"
            print(f"Found services: {services[:100]}...")
        
        print("=== END PARSING DEBUG ===")
    
    except Exception as e:
        print(f"Error parsing SEO response: {e}")
        import traceback
        traceback.print_exc()
    
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
    prompt = f"""ROLLE
Du bist ein erfahrener SEO-Texter und Experte für Google-Unternehmensprofile.

ZIEL
Erstelle eine prägnante, suchmaschinenoptimierte und zugleich kundenfreundliche Unternehmensbeschreibung für ein Google-Unternehmensprofil. Keine Quellenverweise. Es soll ein überzeugender Werbetext sein, wie von einem SEO-Profi geschrieben – mit authentischem, professionellem Ton.

ARBEITSABLAUF — SCHRITT FÜR SCHRITT

Website analysieren
Prüfe und notiere:
• Dienstleistungen / Produkte
• Alleinstellungsmerkmale (USPs)
• Zielgruppe
• Standort(e)
• Öffnungszeiten
• Impressumsangaben (Firmenname, Adresse, Geschäftsführer, E-Mail, Telefonnummer, Handelsregister, USt-ID)

WEBSITE-INFORMATIONEN:
URL: {crawl_result['url']}
Titel: {crawl_result['title']}
Meta-Beschreibung: {crawl_result['meta_description']}

WEBSITE-INHALT:
{crawl_result['content']}

KONTAKT-INFORMATIONEN:
{json.dumps(crawl_result['contact_info'], indent=2)}

GEFUNDENE ÖFFNUNGSZEITEN:
{json.dumps(crawl_result['opening_hours'], indent=2)}

Inhalte aufbereiten
– Aktive, klare Sprache. Keine Füllwörter.
– Unternehmensbeschreibung immer aus Sicht des Unternehmens formulieren (z. B. „Wir sind…", „Wir bieten…").
– Kundennutzen und Mehrwert deutlich herausstellen.
– Zehn relevante SEO-Keywords natürlich einbauen (kein Keyword-Stuffing). Fehlende Infos mit „[Angabe fehlt]" kennzeichnen.
– Bei mehreren Standorten jeden Standort separat mit vollständigen Daten aufführen.

AUSGABESTRUKTUR
(Rein als Klartext, keine Markdown-Syntax verwenden)

Kurzbeschreibung (max. 150 Zeichen)
<Knackige Zusammenfassung des Angebots aus Sicht des Unternehmens – SEO-relevant und aufmerksamkeitsstark>

Langbeschreibung (ca. 750 Zeichen)
<Ausführliche, suchmaschinenoptimierte Beschreibung, aus Sicht des Unternehmens formuliert („Wir sind…", „Wir helfen…", etc.). Fokus auf USPs, Keywords und Kundennutzen. Keine Quellenverweise. Ziel: präzise erklären, wer das Unternehmen ist und was es bietet. Direkt unter die Beschreibung folgt eine strukturierte Auflistung der Leistungen.>

Leistungen:
– Leistung 1
– Leistung 2
– Leistung 3
– usw.

Keywords
– Keyword 1, Keyword 2, … Keyword 10

Öffnungszeiten
– Montag–Freitag: <Zeiten>
– Samstag: <Zeiten>
– Sonntag: <Zeiten>

Impressum
Unternehmen: <Firmenname>
Adresse: <Straße, PLZ, Stadt>
Geschäftsführer: <Name>
Kontakt: <Telefon, E-Mail>

HINWEISE
Keine Quellenangaben, Fußnoten, URLs oder sonstige Verweise im Text.

Zeichenlimits strikt einhalten.

Klare, informative und überzeugende Formulierungen. Qualität vor Quantität.

Unternehmenssprache beibehalten: „Wir" statt dritte Person."""

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

