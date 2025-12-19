import json
import requests
from flask import current_app
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

class GoogleOAuth:
    @staticmethod
    def get_oauth_url():
        """Generate Google OAuth URL for frontend"""
        config = current_app.config
        
        # Scopes needed
        scopes = [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'openid'
        ]
        
        # Build the authorization URL
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={config['GOOGLE_CLIENT_ID']}&"
            f"redirect_uri={config['BACKEND_URL']}/auth/callback&"
            f"response_type=code&"
            f"scope={' '.join(scopes)}&"
            f"access_type=offline&"
            f"prompt=consent"
        )
        
        return auth_url
    
    @staticmethod
    def exchange_code_for_token(code):
        """Exchange authorization code for access token"""
        config = current_app.config
        
        token_url = "https://oauth2.googleapis.com/token"
        
        payload = {
            'client_id': config['GOOGLE_CLIENT_ID'],
            'client_secret': config['GOOGLE_CLIENT_SECRET'],
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': f"{config['BACKEND_URL']}/auth/callback"
        }
        
        response = requests.post(token_url, data=payload)
        token_data = response.json()
        
        if 'id_token' not in token_data:
            raise Exception("No ID token in response")
        
        return token_data
    
    @staticmethod
    def verify_id_token(id_token_str):
        """Verify Google ID token and return user info"""
        config = current_app.config
        
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                config['GOOGLE_CLIENT_ID']
            )
            
            # Get user info
            user_info = {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', '')
            }
            
            return user_info
            
        except ValueError as e:
            raise Exception(f"Invalid token: {str(e)}")
    
    @staticmethod
    def get_user_info(access_token):
        """Get user info from Google API using access token"""
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(userinfo_url, headers=headers)
        user_info = response.json()
        
        return {
            'google_id': user_info['id'],
            'email': user_info['email'],
            'name': user_info.get('name', ''),
            'picture': user_info.get('picture', '')
        }