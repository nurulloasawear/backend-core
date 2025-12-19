from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, set_access_cookies
from app import db
from app.models.models import User
from app.auth.google_oauth import GoogleOAuth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Frontend POST qilganda Google OAuth URL qaytaradi
    Frontend bu URLni ochib, foydalanuvchini Google'ga yo'naltiradi
    """
    try:
        # Generate Google OAuth URL
        auth_url = GoogleOAuth.get_oauth_url()
        
        return jsonify({
            'success': True,
            'auth_url': auth_url
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/callback', methods=['GET'])
def callback():
    """
    Google OAuth callback endpoint
    Frontend bu URLga redirect qilinadi
    """
    try:
        # Get authorization code from query parameters
        code = request.args.get('code')
        
        if not code:
            return jsonify({'error': 'No code provided'}), 400
        
        # Exchange code for tokens
        token_data = GoogleOAuth.exchange_code_for_token(code)
        
        # Verify ID token and get user info
        user_info = GoogleOAuth.verify_id_token(token_data['id_token'])
        
        # Find or create user
        user = User.query.filter_by(google_id=user_info['google_id']).first()
        
        if not user:
            user = User(
                google_id=user_info['google_id'],
                email=user_info['email'],
                name=user_info['name'],
                picture=user_info['picture']
            )
            db.session.add(user)
            db.session.commit()
        
        # Create JWT token
        access_token = create_access_token(identity={
            'user_id': user.id,
            'email': user.email
        })
        
        # Create response
        response = make_response(jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'picture': user.picture
            }
        }))
        
        # Set JWT in cookie
        set_access_cookies(response, access_token)
        
        # Redirect to frontend with token in cookie
        from flask import redirect, current_app
        frontend_url = current_app.config['FRONTEND_URL']
        
        # Redirect to frontend dashboard
        return redirect(f"{frontend_url}/dashboard?auth_success=true")
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Logout endpoint - clear JWT cookie
    """
    response = jsonify({'success': True, 'message': 'Logged out'})
    
    # Clear JWT cookie
    from flask_jwt_extended import unset_jwt_cookies
    unset_jwt_cookies(response)
    
    return response

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get current user info from JWT
    """
    from flask_jwt_extended import jwt_required, get_jwt_identity
    
    @jwt_required()
    def protected():
        current_user = get_jwt_identity()
        
        user = User.query.get(current_user['user_id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'picture': user.picture
        })
    
    return protected()