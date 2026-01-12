import time
import hashlib
import logging
from functools import wraps
from flask import request, jsonify
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiting middleware to prevent API abuse
    """
    
    def __init__(self, requests_per_minute=60, requests_per_hour=1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_buckets = defaultdict(list)
        self.hour_buckets = defaultdict(list)
    
    def is_allowed(self, identifier):
        """Check if request is allowed based on rate limits"""
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_entries(identifier, current_time)
        
        # Check minute limit
        minute_requests = len(self.minute_buckets[identifier])
        if minute_requests >= self.requests_per_minute:
            return False, 'rate_limit_minute_exceeded'
        
        # Check hour limit
        hour_requests = len(self.hour_buckets[identifier])
        if hour_requests >= self.requests_per_hour:
            return False, 'rate_limit_hour_exceeded'
        
        # Add current request
        self.minute_buckets[identifier].append(current_time)
        self.hour_buckets[identifier].append(current_time)
        
        return True, None
    
    def _cleanup_old_entries(self, identifier, current_time):
        """Remove entries older than time windows"""
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        self.minute_buckets[identifier] = [
            t for t in self.minute_buckets[identifier] if t > minute_ago
        ]
        self.hour_buckets[identifier] = [
            t for t in self.hour_buckets[identifier] if t > hour_ago
        ]

class RequestValidator:
    """
    Validates incoming requests for required fields and data types
    """
    
    @staticmethod
    def validate_search_request(data):
        """Validate dataset search request"""
        if not data:
            return False, 'request_body_required'
        
        if 'query' not in data:
            return False, 'query_field_required'
        
        if not isinstance(data['query'], str):
            return False, 'query_must_be_string'
        
        if len(data['query']) > 500:
            return False, 'query_too_long'
        
        if 'filters' in data and not isinstance(data['filters'], dict):
            return False, 'filters_must_be_object'
        
        return True, None
    
    @staticmethod
    def validate_purchase_request(data):
        """Validate dataset purchase request"""
        if not data:
            return False, 'request_body_required'
        
        required_fields = ['buyer_id', 'dataset_id', 'price']
        for field in required_fields:
            if field not in data:
                return False, f'{field}_required'
        
        if not isinstance(data['buyer_id'], str):
            return False, 'buyer_id_must_be_string'
        
        if not isinstance(data['dataset_id'], str):
            return False, 'dataset_id_must_be_string'
        
        if not isinstance(data['price'], (int, float)):
            return False, 'price_must_be_number'
        
        if data['price'] <= 0:
            return False, 'price_must_be_positive'
        
        return True, None
    
    @staticmethod
    def validate_agent_registration(data):
        """Validate agent registration request"""
        if not data:
            return False, 'request_body_required'
        
        required_fields = ['agent_id', 'name', 'endpoint']
        for field in required_fields:
            if field not in data:
                return False, f'{field}_required'
        
        if not isinstance(data['agent_id'], str):
            return False, 'agent_id_must_be_string'
        
        if not isinstance(data['name'], str):
            return False, 'name_must_be_string'
        
        if not isinstance(data['endpoint'], str):
            return False, 'endpoint_must_be_string'
        
        if not data['endpoint'].startswith('http'):
            return False, 'endpoint_must_be_valid_url'
        
        return True, None

class AuthenticationMiddleware:
    """
    Handles API authentication and authorization
    """
    
    def __init__(self):
        self.api_keys = {}
        self.sessions = {}
    
    def generate_api_key(self, user_id):
        """Generate API key for user"""
        timestamp = str(time.time())
        key_data = f"{user_id}:{timestamp}"
        api_key = hashlib.sha256(key_data.encode()).hexdigest()
        
        self.api_keys[api_key] = {
            'user_id': user_id,
            'created_at': time.time(),
            'last_used': time.time()
        }
        
        return api_key
    
    def validate_api_key(self, api_key):
        """Validate API key"""
        if not api_key:
            return False, None
        
        if api_key not in self.api_keys:
            return False, None
        
        key_info = self.api_keys[api_key]
        key_info['last_used'] = time.time()
        
        return True, key_info['user_id']
    
    def create_session(self, user_id, duration_hours=24):
        """Create user session"""
        session_id = hashlib.sha256(f"{user_id}:{time.time()}".encode()).hexdigest()
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': time.time(),
            'expires_at': time.time() + (duration_hours * 3600)
        }
        
        return session_id
    
    def validate_session(self, session_id):
        """Validate session"""
        if not session_id:
            return False, None
        
        if session_id not in self.sessions:
            return False, None
        
        session = self.sessions[session_id]
        
        if time.time() > session['expires_at']:
            del self.sessions[session_id]
            return False, None
        
        return True, session['user_id']

class RequestLogger:
    """
    Logs API requests for monitoring and debugging
    """
    
    def __init__(self):
        self.request_log = []
        self.max_log_size = 10000
    
    def log_request(self, request_data):
        """Log incoming request"""
        log_entry = {
            'timestamp': time.time(),
            'method': request_data.get('method'),
            'path': request_data.get('path'),
            'ip': request_data.get('ip'),
            'user_agent': request_data.get('user_agent'),
            'status_code': request_data.get('status_code'),
            'response_time': request_data.get('response_time')
        }
        
        self.request_log.append(log_entry)
        
        # Cleanup old logs
        if len(self.request_log) > self.max_log_size:
            self.request_log = self.request_log[-self.max_log_size:]
        
        logger.info(f"Request: {log_entry['method']} {log_entry['path']} - {log_entry['status_code']}")
    
    def get_recent_logs(self, limit=100):
        """Get recent request logs"""
        return self.request_log[-limit:]
    
    def get_request_statistics(self):
        """Get request statistics"""
        if not self.request_log:
            return {}
        
        total_requests = len(self.request_log)
        successful_requests = sum(1 for log in self.request_log 
                                 if log.get('status_code', 0) < 400)
        
        method_counts = defaultdict(int)
        path_counts = defaultdict(int)
        
        for log in self.request_log:
            method_counts[log.get('method', 'unknown')] += 1
            path_counts[log.get('path', 'unknown')] += 1
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
            'method_distribution': dict(method_counts),
            'endpoint_distribution': dict(path_counts)
        }

# Initialize middleware instances
rate_limiter = RateLimiter()
request_validator = RequestValidator()
auth_middleware = AuthenticationMiddleware()
request_logger = RequestLogger()

# Decorator functions
def require_rate_limit(f):
    """Decorator to enforce rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        identifier = request.remote_addr
        
        allowed, error = rate_limiter.is_allowed(identifier)
        if not allowed:
            return jsonify({'error': error}), 429
        
        return f(*args, **kwargs)
    return decorated_function

def require_authentication(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'authorization_required'}), 401
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            valid, user_id = auth_middleware.validate_api_key(token)
            
            if not valid:
                return jsonify({'error': 'invalid_token'}), 401
            
            request.user_id = user_id
        else:
            return jsonify({'error': 'invalid_authorization_format'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def validate_request(validator_method):
    """Decorator to validate request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            
            valid, error = validator_method(data)
            if not valid:
                return jsonify({'error': error}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_request_middleware(f):
    """Decorator to log requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            response = f(*args, **kwargs)
            status_code = response[1] if isinstance(response, tuple) else 200
        except Exception as e:
            status_code = 500
            raise e
        finally:
            end_time = time.time()
            
            request_logger.log_request({
                'method': request.method,
                'path': request.path,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'status_code': status_code,
                'response_time': end_time - start_time
            })
        
        return response
    return decorated_function

def cors_middleware(f):
    """Decorator to handle CORS"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        if isinstance(response, tuple):
            response_data, status_code = response
        else:
            response_data = response
            status_code = 200
        
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        
        return response_data, status_code, headers
    return decorated_function

def sanitize_input(data):
    """Sanitize input data to prevent injection attacks"""
    if isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        # Remove potential script tags and SQL injection attempts
        dangerous_patterns = ['<script>', '</script>', 'DROP TABLE', 'DELETE FROM', '--', ';']
        sanitized = data
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern, '')
        return sanitized
    else:
        return data

def check_content_type(f):
    """Decorator to check content type"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.headers.get('Content-Type', '')
            
            if 'application/json' not in content_type:
                return jsonify({'error': 'content_type_must_be_json'}), 415
        
        return f(*args, **kwargs)
    return decorated_function