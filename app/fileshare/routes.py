from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.models import File, User
import uuid
import os

fileshare_bp = Blueprint('fileshare', __name__)

@fileshare_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_files():
    """
    GET /files/
    Return all files for authenticated user
    """
    current_user = get_jwt_identity()
    
    # Get user's files from database
    files = File.query.filter_by(user_id=current_user['user_id'])\
        .order_by(File.created_at.desc())\
        .all()
    
    # Format response
    files_list = []
    for file in files:
        files_list.append({
            'id': file.id,
            'unique_id': f"{file.unique_id}.{file.suffix}",
            'file_name': file.file_name,
            'suffix': file.suffix,
            'aws_url': file.aws_url,
            'created_at': file.created_at.isoformat(),
            'direct_url': f"/files/{file.unique_id}.{file.suffix}"
        })
    
    return jsonify({
        'success': True,
        'files': files_list,
        'count': len(files_list)
    })

@fileshare_bp.route('/<path:file_path>', methods=['GET'])
@jwt_required()
def get_file(file_path):
    """
    GET /files/{unique_id}.{suffix}
    Redirect to AWS URL after authorization check
    """
    current_user = get_jwt_identity()
    
    try:
        # Extract unique_id and suffix from path
        filename = os.path.basename(file_path)
        name_parts = filename.rsplit('.', 1)
        
        if len(name_parts) != 2:
            return jsonify({'error': 'Invalid file path'}), 400
        
        unique_id, suffix = name_parts
        
        # Find file in database
        file = File.query.filter_by(
            unique_id=unique_id, 
            suffix=suffix
        ).first()
        
        if not file:
            return jsonify({'error': 'File not found'}), 404
        
        # Check authorization
        if file.user_id != current_user['user_id']:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Redirect to AWS URL
        return redirect(file.aws_url)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fileshare_bp.route('/upload', methods=['POST'])
@jwt_required()
def create_file_record():
    """
    Create file metadata record when file is uploaded to AWS
    Frontend should first upload to AWS S3, then call this endpoint
    """
    current_user = get_jwt_identity()
    
    data = request.get_json()
    
    # Validate input
    required_fields = ['file_name', 'suffix', 'aws_url']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400
    
    # Generate unique ID
    unique_id = str(uuid.uuid4().hex)[:20]
    
    # Create file record
    file = File(
        unique_id=unique_id,
        file_name=data['file_name'],
        suffix=data['suffix'],
        aws_url=data['aws_url'],
        user_id=current_user['user_id']
    )
    
    db.session.add(file)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'file': {
            'id': file.id,
            'unique_id': f"{file.unique_id}.{file.suffix}",
            'file_name': file.file_name,
            'direct_url': f"/files/{file.unique_id}.{file.suffix}"
        }
    })

@fileshare_bp.route('/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """
    Delete file record (Note: doesn't delete from AWS, just metadata)
    """
    current_user = get_jwt_identity()
    
    file = File.query.get(file_id)
    
    if not file:
        return jsonify({'error': 'File not found'}), 404
    
    # Check authorization
    if file.user_id != current_user['user_id']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(file)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'File deleted'})