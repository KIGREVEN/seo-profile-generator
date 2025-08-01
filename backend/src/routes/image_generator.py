import os
import base64
import uuid
import openai
from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from src.models.image import GeneratedImage

image_bp = Blueprint('image', __name__)

# OpenAI API configuration
openai.api_key = os.environ.get('OPENAI_API_KEY')

def save_base64_image(b64_string, image_type):
    """Convert base64 string to image file and return file path"""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.getcwd(), 'static', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        filename = f"{image_type}_{uuid.uuid4().hex}.png"
        file_path = os.path.join(upload_dir, filename)
        
        # Decode base64 and save to file
        image_data = base64.b64decode(b64_string)
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        # Return relative URL for database storage
        return f"/static/uploads/{filename}"
        
    except Exception as e:
        print(f"Error saving base64 image: {str(e)}")
        return None

def get_current_user():
    """Get current user from session"""
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

def build_prompt(user_input, image_type):
    """Build the professional prompt for image generation"""
    
    # Base prompt template
    base_prompt = "professional photography, ultra-realistic, 4K UHD resolution, shallow depth of field, soft natural lighting, high dynamic range, sharp focus, bokeh background, cinematic composition, wide aspect ratio"
    
    # Format-specific settings for gpt-image-1 model
    # Supported sizes: '1024x1024', '1024x1536', '1536x1024', and 'auto'
    if image_type == 'header':
        format_ratio = "(16:9)"
        format_text = "web header format"
        size = "1536x1024"  # gpt-image-1 supported size for header
    elif image_type == 'kachel':
        format_ratio = "(4:3)"
        format_text = "editorial layout"
        size = "1024x1024"  # gpt-image-1 supported size closest to 4:3
    else:
        # Fallback
        format_ratio = "(16:9)"
        format_text = "web header format"
        size = "1536x1024"  # gpt-image-1 supported size
    
    # Build complete prompt
    complete_prompt = f"{base_prompt} {format_ratio}, {format_text}, color graded like editorial magazine, taken with DSLR or mirrorless camera (Canon EOS R5 / Sony A7R IV), {user_input}"
    
    return complete_prompt, size

@image_bp.route('/generate', methods=['POST'])
def generate_image():
    """Generate an image using OpenAI DALL-E"""
    
    # Check authentication
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_input = data.get('user_input', '').strip()
        image_type = data.get('image_type', 'header')
        
        if not user_input:
            return jsonify({'error': 'User input is required'}), 400
        
        if image_type not in ['header', 'kachel']:
            return jsonify({'error': 'Invalid image type. Must be "header" or "kachel"'}), 400
        
        # Check if OpenAI API key is available
        if not openai.api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Build prompt and get size
        prompt, size = build_prompt(user_input, image_type)
        
        print(f"=== IMAGE GENERATION DEBUG ===")
        print(f"User input: {user_input}")
        print(f"Image type: {image_type}")
        print(f"Size: {size}")
        print(f"Prompt: {prompt}")
        print(f"=== END DEBUG ===")
        
        # Generate image using OpenAI gpt-image-1
        try:
            client = openai.OpenAI(api_key=openai.api_key)
            
            response = client.images.generate(
                model="gpt-image-1",  # Back to gpt-image-1 as requested
                prompt=prompt,
                size=size,
                quality="high",  # gpt-image-1 supports quality parameter
                n=1
                # Note: response_format is not supported by gpt-image-1
            )
            
            print(f"OpenAI API Response: {response}")
            print(f"Response type: {type(response)}")
            print(f"Response data: {response.data if hasattr(response, 'data') else 'No data attribute'}")
            
            # Process the base64 image response
            if response and hasattr(response, 'data') and response.data and len(response.data) > 0:
                first_item = response.data[0]
                print(f"First data item: {first_item}")
                print(f"First item type: {type(first_item)}")
                print(f"First item attributes: {[attr for attr in dir(first_item) if not attr.startswith('_')]}")
                
                # Handle base64 response from gpt-image-1
                if hasattr(first_item, 'b64_json') and first_item.b64_json:
                    print("Processing base64 image from gpt-image-1")
                    image_url = save_base64_image(first_item.b64_json, image_type)
                    if not image_url:
                        return jsonify({'error': 'Failed to save base64 image'}), 500
                    print(f"Base64 image saved to: {image_url}")
                elif hasattr(first_item, 'url') and first_item.url:
                    # Fallback for URL response (shouldn't happen with b64_json format)
                    image_url = first_item.url
                    print(f"Found URL (unexpected): {image_url}")
                else:
                    print(f"No usable image data found. Available attributes: {[attr for attr in dir(first_item) if not attr.startswith('_')]}")
                    return jsonify({'error': 'Image generation failed: No usable image data returned'}), 500
                
            else:
                print("ERROR: Invalid response structure from OpenAI API")
                print(f"Response has data: {hasattr(response, 'data')}")
                if hasattr(response, 'data'):
                    print(f"Data length: {len(response.data) if response.data else 'Data is None'}")
                return jsonify({'error': 'Image generation failed: Invalid API response'}), 500
            
        except Exception as openai_error:
            print(f"OpenAI API error: {str(openai_error)}")
            return jsonify({'error': f'Image generation failed: {str(openai_error)}'}), 500
        
        # Save to database
        try:
            generated_image = GeneratedImage(
                user_id=current_user.id,
                user_input=user_input,
                image_type=image_type,
                image_url=image_url,
                prompt_used=prompt,
                image_size=size
            )
            
            db.session.add(generated_image)
            db.session.commit()
            
            print(f"Image saved to database with ID: {generated_image.id}")
            
            return jsonify({
                'success': True,
                'image': generated_image.to_dict()
            }), 200
            
        except Exception as db_error:
            db.session.rollback()
            print(f"Database error: {str(db_error)}")
            return jsonify({'error': f'Failed to save image: {str(db_error)}'}), 500
        
    except Exception as e:
        print(f"General error in generate_image: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@image_bp.route('/history', methods=['GET'])
def get_image_history():
    """Get user's image generation history"""
    
    # Check authentication
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Query user's images
        images_query = GeneratedImage.query.filter_by(user_id=current_user.id).order_by(GeneratedImage.created_at.desc())
        
        # Paginate
        images_paginated = images_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'images': [image.to_dict() for image in images_paginated.items],
            'total': images_paginated.total,
            'pages': images_paginated.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        print(f"Error in get_image_history: {str(e)}")
        return jsonify({'error': f'Failed to get image history: {str(e)}'}), 500

@image_bp.route('/delete/<int:image_id>', methods=['DELETE'])
def delete_image(image_id):
    """Delete a generated image"""
    
    # Check authentication
    current_user = get_current_user()
    if not current_user:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Find the image
        image = GeneratedImage.query.filter_by(id=image_id, user_id=current_user.id).first()
        
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Delete from database
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Image deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_image: {str(e)}")
        return jsonify({'error': f'Failed to delete image: {str(e)}'}), 500

