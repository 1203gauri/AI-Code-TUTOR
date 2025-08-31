# firebase_config.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

class FirebaseManager:
    """Centralized Firebase management with robust error handling"""
    
    def __init__(self):
        self.db = None
        self.init_firebase()
    
    @st.cache_resource
    def init_firebase(_self):
        """Initialize Firebase with multiple configuration options"""
        try:
            # Check if already initialized
            if firebase_admin._apps:
                _self.db = firestore.client()
                return _self.db
            
            cred = None
            cred_source = None
            
            # Option 1: Streamlit secrets (primary method)
            if hasattr(st, 'secrets') and st.secrets:
                try:
                    # Check for firebase section in secrets
                    if 'firebase' in st.secrets:
                        firebase_config = dict(st.secrets['firebase'])
                        
                        # Create proper credentials dictionary
                        firebase_credentials = {
                            "type": firebase_config.get('type', 'service_account'),
                            "project_id": firebase_config.get('project_id'),
                            "private_key_id": firebase_config.get('private_key_id'),
                            "private_key": firebase_config.get('private_key', '').replace('\\n', '\n'),
                            "client_email": firebase_config.get('client_email'),
                            "client_id": firebase_config.get('client_id'),
                            "auth_uri": firebase_config.get('auth_uri', 'https://accounts.google.com/o/oauth2/auth'),
                            "token_uri": firebase_config.get('token_uri', 'https://oauth2.googleapis.com/token'),
                            "auth_provider_x509_cert_url": firebase_config.get('auth_provider_x509_cert_url', 'https://www.googleapis.com/oauth2/v1/certs'),
                            "client_x509_cert_url": firebase_config.get('client_x509_cert_url')
                        }
                        
                        # Validate required fields
                        required_fields = ['project_id', 'private_key', 'client_email']
                        if all(field in firebase_credentials and firebase_credentials[field] for field in required_fields):
                            cred = credentials.Certificate(firebase_credentials)
                            cred_source = "Streamlit secrets"
                        else:
                            st.warning("⚠️ Incomplete Firebase credentials in secrets")
                    
                except Exception as e:
                    st.warning(f"⚠️ Error parsing Streamlit secrets: {str(e)}")
            
            # Option 2: Direct service account file (for local development)
            if cred is None:
                service_account_paths = [
                    "firebase-service-account.json",
                    "./firebase-service-account.json",
                    os.path.join(os.path.dirname(__file__), "firebase-service-account.json")
                ]
                
                for path in service_account_paths:
                    if os.path.exists(path):
                        try:
                            cred = credentials.Certificate(path)
                            cred_source = f"file: {path}"
                            break
                        except Exception as e:
                            st.warning(f"⚠️ Failed to load service account from {path}: {e}")
                            continue
            
            # If no credentials found, run in demo mode
            if cred is None:
                st.info("🔧 Running in demo mode - data persists during session only")
                st.info("💡 To enable Firebase, add credentials to .streamlit/secrets.toml")
                return None
            
            # Initialize Firebase
            firebase_admin.initialize_app(cred)
            _self.db = firestore.client()
            st.success(f"🚀 Firebase initialized from {cred_source}!")
            return _self.db
            
        except Exception as e:
            st.warning(f"⚠️ Firebase initialization failed: {str(e)}")
            st.info("🔧 Running in demo mode - data persists during session only")
            return None
    
    def is_connected(self):
        """Check if Firebase is properly connected"""
        return self.db is not None
    
    def create_user_profile(self, user_id, email, display_name):
        """Create user profile in Firestore"""
        if not self.is_connected():
            # Demo mode - store in session state
            if 'demo_users' not in st.session_state:
                st.session_state.demo_users = {}
            st.session_state.demo_users[user_id] = {
                'email': email,
                'display_name': display_name,
                'created_at': datetime.now(),
                'total_searches': 0,
                'video_generations': 0,
                'favorite_language': 'Python'
            }
            return True
        
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_ref.set({
                'email': email,
                'display_name': display_name,
                'created_at': firestore.SERVER_TIMESTAMP,
                'total_searches': 0,
                'video_generations': 0,
                'favorite_language': 'Python'
            }, merge=True)
            return True
        except Exception as e:
            st.error(f"Failed to create user profile: {e}")
            return False
    
    def save_search(self, user_id, search_data):
        """Save search to user's history"""
        if not self.is_connected():
            # Demo mode - store in session state
            if 'demo_history' not in st.session_state:
                st.session_state.demo_history = {}
            if user_id not in st.session_state.demo_history:
                st.session_state.demo_history[user_id] = []
            
            st.session_state.demo_history[user_id].append({
                **search_data,
                'timestamp': datetime.now(),
                'id': f"demo_{len(st.session_state.demo_history[user_id])}"
            })
            return True
        
        try:
            history_ref = self.db.collection('users').document(user_id).collection('history')
            history_ref.add({
                **search_data,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'total_searches': firestore.Increment(1),
                'last_active': firestore.SERVER_TIMESTAMP
            })
            
            if search_data.get('response_type') == 'video':
                user_ref.update({'video_generations': firestore.Increment(1)})
            
            return True
            
        except Exception as e:
            st.error(f"Failed to save search: {e}")
            return False
    
    def get_user_history(self, user_id, limit=50, filters=None):
        """Get user's search history"""
        if not self.is_connected():
            if 'demo_history' in st.session_state and user_id in st.session_state.demo_history:
                history = st.session_state.demo_history[user_id]
                if filters:
                    if filters.get('language') and filters['language'] != 'All':
                        history = [item for item in history if item.get('language') == filters['language']]
                    if filters.get('response_type') and filters['response_type'] != 'All':
                        history = [item for item in history if item.get('response_type') == filters['response_type']]
                return history[-limit:]
            return []
        
        try:
            query = self.db.collection('users').document(user_id).collection('history')
            
            if filters:
                if filters.get('language') and filters['language'] != 'All':
                    query = query.where('language', '==', filters['language'])
                if filters.get('response_type') and filters['response_type'] != 'All':
                    query = query.where('response_type', '==', filters['response_type'])
            
            docs = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit).stream()
            
            history = []
            for doc in docs:
                data = doc.to_dict()
                history.append({
                    'id': doc.id,
                    **data
                })
            
            return history
            
        except Exception as e:
            st.error(f"Failed to load history: {e}")
            return []
    
    def delete_history_item(self, user_id, item_id):
        """Delete a specific history item"""
        if not self.is_connected():
            if 'demo_history' in st.session_state and user_id in st.session_state.demo_history:
                st.session_state.demo_history[user_id] = [
                    item for item in st.session_state.demo_history[user_id] 
                    if item['id'] != item_id
                ]
            return True
        
        try:
            self.db.collection('users').document(user_id).collection('history').document(item_id).delete()
            return True
        except Exception as e:
            st.error(f"Failed to delete item: {e}")
            return False
    
    def clear_all_history(self, user_id):
        """Clear all user history"""
        if not self.is_connected():
            if 'demo_history' in st.session_state and user_id in st.session_state.demo_history:
                st.session_state.demo_history[user_id] = []
            return True
        
        try:
            docs = self.db.collection('users').document(user_id).collection('history').stream()
            for doc in docs:
                doc.reference.delete()
            
            user_ref = self.db.collection('users').document(user_id)
            user_ref.update({
                'total_searches': 0,
                'video_generations': 0
            })
            
            return True
            
        except Exception as e:
            st.error(f"Failed to clear history: {e}")
            return False
    
    def get_user_stats(self, user_id):
        """Get comprehensive user statistics"""
        if not self.is_connected():
            if 'demo_history' in st.session_state and user_id in st.session_state.demo_history:
                history = st.session_state.demo_history[user_id]
                languages = {}
                for item in history:
                    lang = item.get('language', 'Python')
                    languages[lang] = languages.get(lang, 0) + 1
                
                favorite_language = max(languages.items(), key=lambda x: x[1])[0] if languages else 'Python'
                
                return {
                    'total_searches': len(history),
                    'video_generations': sum(1 for item in history if item.get('response_type') == 'video'),
                    'favorite_language': favorite_language,
                    'streak_days': min(len(history), 7),
                    'languages_used': list(languages.keys())
                }
            
            return {
                'total_searches': 0,
                'video_generations': 0,
                'favorite_language': 'Python',
                'streak_days': 0,
                'languages_used': []
            }
        
        try:
            user_doc = self.db.collection('users').document(user_id).get()
            user_data = user_doc.to_dict() if user_doc.exists else {}
            
            history_docs = self.db.collection('users').document(user_id).collection('history')\
                          .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                          .limit(100).stream()
            
            languages = {}
            dates = set()
            
            for doc in history_docs:
                data = doc.to_dict()
                lang = data.get('language', 'Python')
                languages[lang] = languages.get(lang, 0) + 1
                
                if 'timestamp' in data and data['timestamp']:
                    date_str = data['timestamp'].strftime('%Y-%m-%d')
                    dates.add(date_str)
            
            favorite_language = max(languages.items(), key=lambda x: x[1])[0] if languages else 'Python'
            
            return {
                'total_searches': user_data.get('total_searches', 0),
                'video_generations': user_data.get('video_generations', 0),
                'favorite_language': favorite_language,
                'streak_days': len(dates),
                'languages_used': list(languages.keys())
            }
            
        except Exception as e:
            st.error(f"Failed to get stats: {e}")
            return {
                'total_searches': 0,
                'video_generations': 0,
                'favorite_language': 'Python',
                'streak_days': 0,
                'languages_used': []
            }

# Authentication utilities
class AuthManager:
    """Handle authentication logic"""
    
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email/password"""
        try:
            if not email or not password:
                return {'success': False, 'error': 'Email and password are required'}
            
            if len(password) < 6:
                return {'success': False, 'error': 'Password must be at least 6 characters'}
            
            if '@' not in email:
                return {'success': False, 'error': 'Please enter a valid email'}
            
            user_id = email.split('@')[0].replace('.', '_')
            
            firebase_manager = FirebaseManager()
            if firebase_manager.create_user_profile(user_id, email, user_id.title()):
                return {
                    'success': True,
                    'user_id': user_id,
                    'email': email,
                    'display_name': user_id.title()
                }
            else:
                return {'success': False, 'error': 'Failed to create user profile'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def create_account(email, password, display_name):
        """Create new user account"""
        try:
            if not email or not password or not display_name:
                return {'success': False, 'error': 'All fields are required'}
            
            if len(password) < 6:
                return {'success': False, 'error': 'Password must be at least 6 characters'}
            
            if '@' not in email:
                return {'success': False, 'error': 'Please enter a valid email'}
            
            user_id = email.split('@')[0].replace('.', '_')
            
            firebase_manager = FirebaseManager()
            if firebase_manager.create_user_profile(user_id, email, display_name):
                return {
                    'success': True,
                    'user_id': user_id,
                    'email': email,
                    'display_name': display_name
                }
            else:
                return {'success': False, 'error': 'Failed to create user profile'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

# UI Components
def render_user_avatar(user_name, user_email):
    """Render user avatar component"""
    initials = ''.join([name[0].upper() for name in user_name.split()[:2]])
    
    return f"""
    <div style="display: flex; align-items: center; gap: 0.75rem;">
        <div style="
            width: 40px; height: 40px; 
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 50%; 
            display: flex; align-items: center; justify-content: center;
            color: white; font-weight: 600; font-size: 14px;
        ">
            {initials}
        </div>
        <div>
            <div style="font-weight: 600; font-size: 14px;">{user_name}</div>
            <div style="color: #6b7280; font-size: 12px;">{user_email}</div>
        </div>
    </div>
    """

def render_feature_card(icon, title, description, highlight=False):
    """Render feature highlight card"""
    bg_color = "linear-gradient(135deg, #667eea, #764ba2)" if highlight else "#f8fafc"
    text_color = "white" if highlight else "#374151"
    
    return f"""
    <div style="
        background: {bg_color};
        color: {text_color};
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    " onmouseover="this.style.transform='translateY(-5px)'" 
       onmouseout="this.style.transform='translateY(0)'">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-weight: 600; margin-bottom: 0.5rem;">{title}</div>
        <div style="font-size: 0.9rem; opacity: 0.9;">{description}</div>
    </div>
    """

# Session state helpers
def login_user(user_data):
    """Set session state for logged in user"""
    st.session_state.authenticated = True
    st.session_state.user_id = user_data['user_id']
    st.session_state.user_email = user_data['email']
    st.session_state.user_name = user_data['display_name']

def logout_user():
    """Clear session state for logout"""
    keys_to_clear = ['authenticated', 'user_id', 'user_email', 'user_name', 'page', 'prefill']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

# Analytics helpers
def track_user_activity(user_id, activity_type, metadata=None):
    """Track user activity for analytics"""
    firebase_manager = FirebaseManager()
    
    if firebase_manager.is_connected():
        try:
            firebase_manager.db.collection('analytics').add({
                'user_id': user_id,
                'activity_type': activity_type,
                'metadata': metadata or {},
                'timestamp': firestore.SERVER_TIMESTAMP
            })
        except Exception:
            pass