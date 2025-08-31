







# import streamlit as st
# import json
# import hashlib
# import time
# from src.gemini_api import stream_markdown_answer, get_video_script
# from src.video_generator import generate_animated_video

# st.set_page_config(page_title="CodeExplainer AI", page_icon="💡", layout="wide")

# MAX_HISTORY = 20

# # ---------------- Session Init ----------------
# def initialize_session_state():
#     defaults = {
#         'authenticated': False,
#         'user_email': '',
#         'user_id': '',
#         'user_name': '',
#         'settings': {
#             'language': 'Python',
#             'level': 'Beginner',
#             'explain_lines': False,
#             'model': 'gemini-pro'
#         }
#     }
#     for key, value in defaults.items():
#         if key not in st.session_state:
#             st.session_state[key] = value
#     if "conversations" not in st.session_state:
#         st.session_state.conversations = {"Chat 1": []}
#     if "active_chat" not in st.session_state:
#         st.session_state.active_chat = "Chat 1"

# initialize_session_state()

# def get_active_messages():
#     return st.session_state.conversations[st.session_state.active_chat]

# def set_active_messages(msgs):
#     st.session_state.conversations[st.session_state.active_chat] = msgs

# def trim_history():
#     msgs = get_active_messages()
#     if len(msgs) > MAX_HISTORY:
#         set_active_messages(msgs[-MAX_HISTORY:])

# # ---------------- Auth Functions ----------------
# def hash_password(password: str) -> str:
#     return hashlib.sha256(password.encode()).hexdigest()

# def verify_password(password: str, hashed: str) -> bool:
#     return hashlib.sha256(password.encode()).hexdigest() == hashed

# def get_users_db():
#     try:
#         users_json = st.secrets.get("users", "{}")
#         if isinstance(users_json, str):
#             return json.loads(users_json)
#         return users_json
#     except:
#         return {}

# def authenticate_user(email: str, password: str) -> tuple[bool, str]:
#     users_db = get_users_db()
#     if email in users_db and verify_password(password, users_db[email]['password']):
#         return True, users_db[email]['name']
#     if email and password:
#         return True, email.split('@')[0].title()
#     return False, "Invalid credentials"

# def register_user(email: str, password: str, name: str) -> tuple[bool, str]:
#     users_db = get_users_db()
#     if email in users_db:
#         return False, "User already exists"
#     return True, "Account created successfully"

# # ---------------- Custom CSS ----------------
# def load_chatgpt_css():
#     st.markdown("""
#     <style>
#     body {background: #212121; color: white; font-family: 'Inter', sans-serif;}
#     .sidebar .sidebar-content {
#         background: #1e1e1e;
#         color: white;
#         padding: 1rem;
#     }
#     .chat-container {max-width: 768px; margin: 0 auto; padding: 2rem 1rem; min-height: calc(100vh - 140px);}
#     .message {margin: 1rem 0; display: flex; gap: 1rem;}
#     .message.user {flex-direction: row-reverse;}
#     .message-avatar {width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;}
#     .user .message-avatar {background: #10a37f; color: white;}
#     .assistant .message-avatar {background: #6366f1; color: white;}
#     .message-content {background: #2f2f2f; padding: 1rem 1.5rem; border-radius: 12px; border: 1px solid #424242; max-width: 70%;}
#     .user .message-content {background: #10a37f; color: white; border: 1px solid #10a37f;}
#     .input-container {position: fixed; bottom: 0; left: 300px; right: 0; background: #2f2f2f; border-top: 1px solid #424242; padding: 1rem;}
#     textarea {border-radius: 8px; border: 1px solid #444; background: #1e1e1e; color: white;}
#     </style>
#     """, unsafe_allow_html=True)

# # ---------------- Login Page ----------------
# def show_login_page():
#     load_chatgpt_css()
#     st.markdown("<h1 style='text-align:center;color:#10a37f'>💡 CodeExplainer</h1>", unsafe_allow_html=True)
#     tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
#     with tab1:
#         with st.form("login_form"):
#             email = st.text_input("Email")
#             password = st.text_input("Password", type="password")
#             login_clicked = st.form_submit_button("Sign In")
#             if login_clicked and email and password:
#                 success, message = authenticate_user(email, password)
#                 if success:
#                     st.session_state.authenticated = True
#                     st.session_state.user_email = email
#                     st.session_state.user_name = message
#                     st.rerun()
#                 else:
#                     st.error(message)
#     with tab2:
#         with st.form("register_form"):
#             name = st.text_input("Full Name")
#             email = st.text_input("Email")
#             password = st.text_input("Password", type="password")
#             confirm_password = st.text_input("Confirm Password", type="password")
#             register_clicked = st.form_submit_button("Create Account")
#             if register_clicked:
#                 if password == confirm_password:
#                     success, message = register_user(email, password, name)
#                     if success:
#                         st.session_state.authenticated = True
#                         st.session_state.user_email = email
#                         st.session_state.user_name = name
#                         st.success("Account created!")
#                         time.sleep(1)
#                         st.rerun()
#                     else:
#                         st.error(message)
#                 else:
#                     st.error("Passwords don't match")

# # ---------------- Sidebar ----------------
# def show_sidebar():
#     with st.sidebar:
#         st.markdown("## 💬 Chats")
#         if st.button("➕ New Chat", use_container_width=True):
#             new_chat_name = f"Chat {len(st.session_state.conversations)+1}"
#             st.session_state.conversations[new_chat_name] = []
#             st.session_state.active_chat = new_chat_name
#             st.rerun()

#         chat_choice = st.radio("Select Chat", list(st.session_state.conversations.keys()), index=list(st.session_state.conversations.keys()).index(st.session_state.active_chat))
#         if chat_choice != st.session_state.active_chat:
#             st.session_state.active_chat = chat_choice
#             st.rerun()

#         if st.button("Reset Current Chat", use_container_width=True):
#             set_active_messages([])
#             st.rerun()

#         st.divider()
#         st.markdown("## ⚙️ Settings")
#         st.session_state.settings['language'] = st.selectbox("Language", ["Python","Java","C++","JavaScript","Go","Rust"], index=["Python","Java","C++","JavaScript","Go","Rust"].index(st.session_state.settings['language']))
#         st.session_state.settings['level'] = st.selectbox("Level", ["Beginner","Intermediate","Advanced"], index=["Beginner","Intermediate","Advanced"].index(st.session_state.settings['level']))
#         st.session_state.settings['explain_lines'] = st.checkbox("Line by line", value=st.session_state.settings['explain_lines'])
#         st.session_state.settings['model'] = st.selectbox("Model", ["gemini-pro","gpt-4"], index=["gemini-pro","gpt-4"].index(st.session_state.settings['model']))

#         st.divider()
#         if st.button("🚪 Logout", use_container_width=True):
#             st.session_state.clear()
#             st.rerun()

# # ---------------- Chat Interface ----------------
# def show_chat_interface():
#     load_chatgpt_css()
#     show_sidebar()

#     st.markdown('<div class="chat-container">', unsafe_allow_html=True)
#     messages = get_active_messages()
#     if not messages:
        
#         st.image("assets\Gemini_Generated_Image_f34thmf34thmf34t.png", width=120)
#         st.markdown("<h2 style='color:white;text-align:center;'>Your AI-powered coding tutor.Ask me to explain, debug, or generate code.</h2>", unsafe_allow_html=True)
    
       

#     col1, col2, col3 = st.columns(3)

#     with col1:
#         st.markdown("### Examples")
#         if st.button(" Explain recursion with a simple example", use_container_width=True):
#             generate_text_response("Explain recursion with a simple example")
#             trim_history()
#             st.rerun()
#         if st.button(" Write Python code for bubble sort", use_container_width=True):
#             generate_text_response("Write Python code for bubble sort")
#             trim_history()
#             st.rerun()
#         if st.button(" Debug my JavaScript function", use_container_width=True):
#             generate_text_response("Debug my JavaScript function")
#             trim_history()
#             st.rerun()

#     with col2:
#         st.markdown("### Capabilities")
#         st.markdown("✅ Supports Python, Java, C++, JS")
#         st.markdown("✅ Line-by-line explanations")
#         st.markdown("✅ Generates animated tutorials")

#     with col3:
#         st.markdown("### Tips")
#         st.markdown("📝 The more details you give, the better")
#         st.markdown("🔍 Ask follow-ups to dive deeper")
#         st.markdown("🎯 Use settings to personalize results")

#     for msg in messages:
#         role = msg["role"]
#         avatar = "👤" if role == "user" else "🤖"
#         st.markdown(f"""
#         <div class="message {role}">
#             <div class="message-avatar">{avatar}</div>
#             <div class="message-content">{msg["content"]}</div>
#         </div>
#         """, unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)

#     with st.form("chat_form", clear_on_submit=True):
#         col1, col2 = st.columns([8,1])
#         with col1:
#             user_input = st.text_area("Message", placeholder="Ask me anything...", height=60, label_visibility="collapsed")
#         with col2:
#             send_clicked = st.form_submit_button("Send")
#         if send_clicked and user_input.strip():
#             generate_text_response(user_input)
#             trim_history()
#             st.rerun()

# # ---------------- AI Response Functions ----------------
# def generate_text_response(user_input):
#     msgs = get_active_messages()
#     msgs.append({"role": "user", "content": user_input})
#     msgs.append({"role": "assistant", "content": ""})
#     full_response = ""
#     settings = st.session_state.settings
#     for chunk in stream_markdown_answer(
#         msgs,
#         settings['language'],
#         settings['level'],
#         settings['explain_lines']
#     ):
#         full_response += chunk
#         msgs[-1]["content"] = full_response
#     set_active_messages(msgs)

# # ---------------- Main ----------------
# def main():
#     if not st.session_state.authenticated:
#         show_login_page()
#     else:
#         show_chat_interface()

# if __name__ == "__main__":
#     main()










import streamlit as st
import json
import hashlib
import time
from PIL import Image
import base64
import io

# Import functions with error handling
try:
    from src.gemini_api import stream_markdown_answer
    BASIC_FEATURES_AVAILABLE = True
except ImportError:
    BASIC_FEATURES_AVAILABLE = False
    def stream_markdown_answer(messages, language, level, explain_lines):
        yield "⚠️ Basic functionality requires src/gemini_api.py"

try:
    from src.gemini_api import get_video_script, analyze_image_question
    from src.video_generator import generate_animated_video
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    ENHANCED_FEATURES_AVAILABLE = False
    
    def get_video_script(explanation_text, style, duration):
        return {"content": explanation_text, "style": style}
    
    def analyze_image_question(img_base64, settings):
        return "📸 Image analysis requires enhanced setup. Please check your dependencies."
    
    def generate_animated_video(script, style, duration, language):
        return None

st.set_page_config(page_title="CodeExplainer AI", page_icon="💡", layout="wide")

MAX_HISTORY = 20

# ---------------- Session Init ----------------
def initialize_session_state():
    defaults = {
        'authenticated': False,
        'user_email': '',
        'user_id': '',
        'user_name': '',
        'settings': {
            'language': 'Python',
            'level': 'Beginner',
            'explain_lines': False,
            'model': 'gemini-pro'
        },
        'show_video_generator': False,
        'current_explanation': '',
        'video_generation_status': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "conversations" not in st.session_state:
        st.session_state.conversations = {"Chat 1": []}
    if "active_chat" not in st.session_state:
        st.session_state.active_chat = "Chat 1"

initialize_session_state()

def get_active_messages():
    return st.session_state.conversations[st.session_state.active_chat]

def set_active_messages(msgs):
    st.session_state.conversations[st.session_state.active_chat] = msgs

def trim_history():
    msgs = get_active_messages()
    if len(msgs) > MAX_HISTORY:
        set_active_messages(msgs[-MAX_HISTORY:])

# ---------------- Auth Functions ----------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == hashed

def get_users_db():
    try:
        users_json = st.secrets.get("users", "{}")
        if isinstance(users_json, str):
            return json.loads(users_json)
        return users_json
    except:
        return {}

def authenticate_user(email: str, password: str) -> tuple[bool, str]:
    users_db = get_users_db()
    if email in users_db and verify_password(password, users_db[email]['password']):
        return True, users_db[email]['name']
    if email and password:
        return True, email.split('@')[0].title()
    return False, "Invalid credentials"

def register_user(email: str, password: str, name: str) -> tuple[bool, str]:
    users_db = get_users_db()
    if email in users_db:
        return False, "User already exists"
    return True, "Account created successfully"

# ---------------- Image Processing Functions ----------------
def process_uploaded_image(image_file):
    """Process uploaded image and convert to base64 for API"""
    try:
        image = Image.open(image_file)
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize if too large (max 1024x1024 for better API performance)
        max_size = 1024
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convert to base64
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return img_base64, image
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None, None

def camera_input_component():
    """Custom camera input component"""
    st.markdown("### 📸 Upload Question Photo")
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["📷 Camera", "📁 File Upload"])
    
    with tab1:
        camera_photo = st.camera_input("Take a photo of your code question")
        if camera_photo is not None:
            return camera_photo
    
    with tab2:
        uploaded_file = st.file_uploader(
            "Upload an image", 
            type=['png', 'jpg', 'jpeg'],
            help="Upload a photo of code, whiteboard, or handwritten question"
        )
        if uploaded_file is not None:
            return uploaded_file
    
    return None

# ---------------- Video Generation Functions ----------------
def show_video_generator_interface():
    """Show video generation interface"""
    st.markdown("### 🎬 Generate AI Explanation Video")
    
    if st.session_state.current_explanation:
        st.markdown("**Current Explanation:**")
        with st.expander("View explanation", expanded=False):
            st.markdown(st.session_state.current_explanation[:500] + "..." if len(st.session_state.current_explanation) > 500 else st.session_state.current_explanation)
        
        col1, col2 = st.columns(2)
        with col1:
            video_style = st.selectbox(
                "Video Style",
                ["Animated Tutorial", "Code Walkthrough", "Interactive Demo", "Whiteboard Style"]
            )
        with col2:
            video_duration = st.slider("Duration (minutes)", 1, 5, 2)
        
        if st.button("🎬 Generate Explanation Video", use_container_width=True):
            generate_explanation_video(st.session_state.current_explanation, video_style, video_duration)
    else:
        st.info("💡 Ask a coding question first, then generate an animated video explanation!")

def generate_explanation_video(explanation_text, style, duration):
    """Generate animated explanation video"""
    try:
        with st.spinner("🎬 Creating your animated explanation video..."):
            # Update status
            st.session_state.video_generation_status = "generating"
            
            # Get video script from AI
            script = get_video_script(explanation_text, style, duration)
            
            # Generate animated video
            video_path = generate_animated_video(
                script=script,
                style=style,
                duration=duration,
                language=st.session_state.settings['language']
            )
            
            if video_path:
                st.session_state.video_generation_status = "complete"
                st.success("✅ Video generated successfully!")
                
                # Display video
                st.video(video_path)
                
                # Add download button
                with open(video_path, "rb") as video_file:
                    st.download_button(
                        label="📥 Download Video",
                        data=video_file.read(),
                        file_name=f"code_explanation_{int(time.time())}.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
                
                # Add video to chat history
                msgs = get_active_messages()
                msgs.append({
                    "role": "assistant", 
                    "content": f"🎬 **Generated Explanation Video**\n\nStyle: {style}\nDuration: {duration} minutes\n\n[Video successfully generated and ready for download]",
                    "type": "video",
                    "video_path": video_path
                })
                set_active_messages(msgs)
                
            else:
                st.session_state.video_generation_status = "error"
                st.error("❌ Failed to generate video. Please try again.")
                
    except Exception as e:
        st.session_state.video_generation_status = "error"
        st.error(f"❌ Error generating video: {str(e)}")

# ---------------- Custom CSS ----------------
def load_chatgpt_css():
    st.markdown("""
    <style>
    body {background: #212121; color: white; font-family: 'Inter', sans-serif;}
    .sidebar .sidebar-content {
        background: #1e1e1e;
        color: white;
        padding: 1rem;
    }
    .chat-container {max-width: 768px; margin: 0 auto; padding: 2rem 1rem; min-height: calc(100vh - 140px);}
    .message {margin: 1rem 0; display: flex; gap: 1rem;}
    .message.user {flex-direction: row-reverse;}
    .message-avatar {width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;}
    .user .message-avatar {background: #10a37f; color: white;}
    .assistant .message-avatar {background: #6366f1; color: white;}
    .message-content {background: #2f2f2f; padding: 1rem 1.5rem; border-radius: 12px; border: 1px solid #424242; max-width: 70%;}
    .user .message-content {background: #10a37f; color: white; border: 1px solid #10a37f;}
    .input-container {position: fixed; bottom: 0; left: 300px; right: 0; background: #2f2f2f; border-top: 1px solid #424242; padding: 1rem;}
    textarea {border-radius: 8px; border: 1px solid #444; background: #1e1e1e; color: white;}
    
    /* New styles for enhanced features */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        color: white;
        text-align: center;
    }
    
    .photo-upload-area {
        border: 2px dashed #10a37f;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        background: #1a1a1a;
        margin: 1rem 0;
    }
    
    .video-generation-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .status-generating {
        background: linear-gradient(45deg, #ff9a9e, #fecfef);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        color: #333;
        font-weight: bold;
    }
    
    .status-complete {
        background: linear-gradient(45deg, #a8edea, #fed6e3);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        color: #333;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------- Login Page ----------------
def show_login_page():
    load_chatgpt_css()
    st.markdown("<h1 style='text-align:center;color:#10a37f'>💡 CodeExplainer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#888'>Now with 📸 Photo Upload & 🎬 AI Video Generation!</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_clicked = st.form_submit_button("Sign In")
            if login_clicked and email and password:
                success, message = authenticate_user(email, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.user_name = message
                    st.rerun()
                else:
                    st.error(message)
    with tab2:
        with st.form("register_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_clicked = st.form_submit_button("Create Account")
            if register_clicked:
                if password == confirm_password:
                    success, message = register_user(email, password, name)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_name = name
                        st.success("Account created!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Passwords don't match")

# ---------------- Sidebar ----------------
def show_sidebar():
    with st.sidebar:
        st.markdown("## 💬 Chats")
        if st.button("➕ New Chat", use_container_width=True):
            new_chat_name = f"Chat {len(st.session_state.conversations)+1}"
            st.session_state.conversations[new_chat_name] = []
            st.session_state.active_chat = new_chat_name
            st.rerun()

        chat_choice = st.radio("Select Chat", list(st.session_state.conversations.keys()), index=list(st.session_state.conversations.keys()).index(st.session_state.active_chat))
        if chat_choice != st.session_state.active_chat:
            st.session_state.active_chat = chat_choice
            st.rerun()

        if st.button("Reset Current Chat", use_container_width=True):
            set_active_messages([])
            st.session_state.current_explanation = ''
            st.session_state.show_video_generator = False
            st.rerun()

        st.divider()
        st.markdown("## ⚙️ Settings")
        st.session_state.settings['language'] = st.selectbox("Language", ["Python","Java","C++","JavaScript","Go","Rust"], index=["Python","Java","C++","JavaScript","Go","Rust"].index(st.session_state.settings['language']))
        st.session_state.settings['level'] = st.selectbox("Level", ["Beginner","Intermediate","Advanced"], index=["Beginner","Intermediate","Advanced"].index(st.session_state.settings['level']))
        st.session_state.settings['explain_lines'] = st.checkbox("Line by line", value=st.session_state.settings['explain_lines'])
        st.session_state.settings['model'] = st.selectbox("Model", ["gemini-pro","gpt-4"], index=["gemini-pro","gpt-4"].index(st.session_state.settings['model']))

        st.divider()
        
        # New Features Section
        st.markdown("## 🚀 New Features")
        
        if not ENHANCED_FEATURES_AVAILABLE:
            st.warning("⚠️ Enhanced features require additional setup")
        
        # Video Generator Toggle
        if st.session_state.current_explanation and ENHANCED_FEATURES_AVAILABLE:
            if st.button("🎬 Generate Video", use_container_width=True):
                st.session_state.show_video_generator = not st.session_state.show_video_generator
                st.rerun()
        else:
            disabled_reason = "Ask a question first" if not st.session_state.current_explanation else "Setup required"
            st.button("🎬 Generate Video", disabled=True, use_container_width=True, help=disabled_reason)
        
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ---------------- Chat Interface ----------------
def show_chat_interface():
    load_chatgpt_css()
    show_sidebar()

    # Main content area
    if st.session_state.show_video_generator:
        main_col, video_col = st.columns([2, 1])
    else:
        main_col = st.container()
    
    with main_col:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        messages = get_active_messages()
        
        if not messages:
            st.image("assets/Gemini_Generated_Image_f34thmf34thmf34t.png", width=120)
            st.markdown("<h2 style='color:white;text-align:center;'>Your AI-powered coding tutor. Ask me to explain, debug, or generate code.</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center;color:#10a37f;'>✨ New: Upload photos & generate AI videos!</p>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("### Examples")
                if st.button("🔄 Explain recursion with a simple example", use_container_width=True):
                    generate_text_response("Explain recursion with a simple example")
                    trim_history()
                    st.rerun()
                if st.button("💻 Write Python code for bubble sort", use_container_width=True):
                    generate_text_response("Write Python code for bubble sort")
                    trim_history()
                    st.rerun()
                if st.button("🐛 Debug my JavaScript function", use_container_width=True):
                    generate_text_response("Debug my JavaScript function")
                    trim_history()
                    st.rerun()

            with col2:
                st.markdown("### Capabilities")
                st.markdown("✅ Supports Python, Java, C++, JS")
                st.markdown("✅ Line-by-line explanations")
                st.markdown("📸 **NEW: Photo question upload**")
                st.markdown("🎬 **NEW: AI explanation videos**")

            with col3:
                st.markdown("### Tips")
                st.markdown("📝 The more details you give, the better")
                st.markdown("🔍 Ask follow-ups to dive deeper")
                st.markdown("🎯 Use settings to personalize results")
                st.markdown("📸 **Upload photos of code/questions**")

        # Display chat messages
        for i, msg in enumerate(messages):
            role = msg["role"]
            avatar = "👤" if role == "user" else "🤖"
            
            # Handle different message types
            if msg.get("type") == "image_question":
                st.markdown(f"""
                <div class="message {role}">
                    <div class="message-avatar">{avatar}</div>
                    <div class="message-content">
                        📸 <strong>Uploaded Image Question</strong><br>
                        {msg["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if "image" in msg:
                    st.image(msg["image"], width=300)
            elif msg.get("type") == "video":
                st.markdown(f"""
                <div class="message {role}">
                    <div class="message-avatar">{avatar}</div>
                    <div class="message-content">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
                if "video_path" in msg and msg["video_path"]:
                    st.video(msg["video_path"])
            else:
                st.markdown(f"""
                <div class="message {role}">
                    <div class="message-avatar">{avatar}</div>
                    <div class="message-content">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add video generation button after assistant responses
                if (role == "assistant" and 
                    i == len(messages) - 1 and  # Last message
                    len(msg["content"]) > 100 and  # Substantial content
                    ENHANCED_FEATURES_AVAILABLE and
                    not st.session_state.show_video_generator):
                    
                    if st.button("🎬 Generate Video Explanation", key=f"video_btn_{i}"):
                        st.session_state.show_video_generator = True
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Enhanced input section with photo upload
        st.markdown("---")
        
        # Photo upload section (only show if enhanced features available)
        if ENHANCED_FEATURES_AVAILABLE:
            uploaded_image = camera_input_component()
            
            if uploaded_image is not None:
                st.success("📸 Image uploaded successfully!")
                
                # Process and display image
                img_base64, processed_image = process_uploaded_image(uploaded_image)
                
                if img_base64 and processed_image:
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(processed_image, caption="Uploaded Image", width=200)
                    with col2:
                        st.markdown("**Image processed successfully!**")
                        if st.button("🔍 Analyze This Image", use_container_width=True):
                            analyze_uploaded_image(img_base64, processed_image)
                            st.rerun()
        else:
            st.info("📸 Photo upload feature requires enhanced setup. Run setup.py to enable.")

        # Text input form (existing functionality)
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([8,1])
            with col1:
                user_input = st.text_area("Message", placeholder="Ask me anything about code...", height=60, label_visibility="collapsed")
            with col2:
                send_clicked = st.form_submit_button("Send")
            if send_clicked and user_input.strip():
                generate_text_response(user_input)
                trim_history()
                st.rerun()
   
    
    # Handle + button (photo upload options)
    # The following block referenced 'plus_clicked', which was not defined.
    # If you want to add a "+" button for photo upload, define it like:
    # plus_clicked = st.button("➕ Upload/Scan Photo")
    # and then use the block below.
    # For now, this block is removed to avoid the undefined variable error.

    # Video generation panel (if enabled)
    if st.session_state.show_video_generator:
        with video_col:
            st.markdown('<div class="video-generation-card">', unsafe_allow_html=True)
            show_video_generator_interface()
            st.markdown('</div>', unsafe_allow_html=True)

# ---------------- AI Response Functions ----------------
def generate_text_response(user_input):
    """Generate text response (existing functionality)"""
    msgs = get_active_messages()
    msgs.append({"role": "user", "content": user_input})
    msgs.append({"role": "assistant", "content": ""})
    full_response = ""
    settings = st.session_state.settings
    
    for chunk in stream_markdown_answer(
        msgs,
        settings['language'],
        settings['level'],
        settings['explain_lines']
    ):
        full_response += chunk
        msgs[-1]["content"] = full_response
    
    # Store current explanation for video generation
    st.session_state.current_explanation = full_response
    set_active_messages(msgs)

def analyze_uploaded_image(img_base64, processed_image):
    """Analyze uploaded image and generate response"""
    try:
        with st.spinner("🔍 Analyzing your image..."):
            # Import the analysis function
            from src.gemini_api import analyze_image_question
            
            # Get AI analysis of the image
            analysis_result = analyze_image_question(img_base64, st.session_state.settings)
            
            if analysis_result:
                msgs = get_active_messages()
                
                # Add user message with image
                msgs.append({
                    "role": "user", 
                    "content": "📸 Uploaded an image with a coding question",
                    "type": "image_question",
                    "image": processed_image
                })
                
                # Add AI response
                msgs.append({
                    "role": "assistant", 
                    "content": analysis_result
                })
                
                # Store current explanation for video generation
                st.session_state.current_explanation = analysis_result
                set_active_messages(msgs)
                
                st.success("✅ Image analyzed successfully!")
                    
            else:
                st.error("❌ Failed to analyze image. Please try again.")
                
    except Exception as e:
        st.error(f"❌ Error analyzing image: {str(e)}")

# ---------------- Main ----------------
def main():
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_chat_interface()

if __name__ == "__main__":
    main()