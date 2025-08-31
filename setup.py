# setup.py - Run this to set up enhanced features
import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    
    requirements = [
        "streamlit>=1.28.0",
        "google-generativeai>=0.3.0", 
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "moviepy>=1.0.3",
        "matplotlib>=3.7.0",
        "numpy>=1.24.0"
    ]
    
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✅ Installed {req}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {req}")

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "src",
        "assets", 
        "generated_videos",
        ".streamlit"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_config_files():
    """Create configuration files"""
    print("⚙️ Creating configuration files...")
    
    # Create secrets template
    secrets_content = """# .streamlit/secrets.toml
GEMINI_API_KEY = "your_gemini_api_key_here"

# Optional: User database
[users]
# Example: "user@example.com" = {"password": "hashed_password", "name": "User Name"}
"""
    
    secrets_path = ".streamlit/secrets.toml"
    if not os.path.exists(secrets_path):
        with open(secrets_path, "w") as f:
            f.write(secrets_content)
        print(f"✅ Created {secrets_path}")
        print("⚠️  Please update your Gemini API key in .streamlit/secrets.toml")
    else:
        print(f"ℹ️  {secrets_path} already exists")

def create_placeholder_image():
    """Create placeholder image if not exists"""
    from PIL import Image, ImageDraw, ImageFont
    
    image_path = "assets/Gemini_Generated_Image_f34thmf34t.png"
    
    if not os.path.exists(image_path):
        print("🎨 Creating placeholder image...")
        
        # Create a simple placeholder image
        img = Image.new('RGB', (400, 300), color='#2d2d2d')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        text = "CodeExplainer AI\n💡🤖"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = ((400 - text_width) // 2, (300 - text_height) // 2)
        draw.text(position, text, fill='#00ccff', font=font, align='center')
        
        img.save(image_path)
        print(f"✅ Created placeholder image: {image_path}")

def main():
    """Main setup function"""
    print("🚀 Setting up Enhanced CodeExplainer...")
    print("=" * 50)
    
    # Step 1: Install requirements
    install_requirements()
    print()
    
    # Step 2: Create directories
    create_directories()
    print()
    
    # Step 3: Create config files
    create_config_files()
    print()
    
    # Step 4: Create placeholder image
    create_placeholder_image()
    print()
    
    print("✅ Setup complete!")
    print("\n📋 Next Steps:")
    print("1. Add your Gemini API key to .streamlit/secrets.toml")
    print("2. Run: streamlit run app.py")
    print("3. Test photo upload and video generation features")
    print("\n🆕 New Features:")
    print("📸 Camera/file upload for coding questions")
    print("🎬 AI-generated animated explanation videos")
    print("🎯 Enhanced code analysis and visualization")

if __name__ == "__main__":
    main()