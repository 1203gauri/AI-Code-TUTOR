# from manim import *
# from moviepy.editor import VideoFileClip, AudioFileClip
# from gtts import gTTS
# import tempfile
# import os


# # Simple Manim scene that shows a title, then iterates through scene lines.
# class TutorScene(Scene):
#     def __init__(self, title: str, scenes: list[str], **kwargs):
#         self._title = title
#         self._scenes = scenes or [
#             "Explain the core idea",
#             "Show inputs",
#             "Walk through steps",
#             "Show result"
#         ]
#         super().__init__(**kwargs)

#     def construct(self):
#         # Show title
#         title = Text(self._title).scale(1.0)
#         self.play(Write(title))
#         self.wait(1)
#         self.play(FadeOut(title))

#         # Show each step as a bullet
#         for idx, line in enumerate(self._scenes, start=1):
#             bullet = Text(f"Step {idx}: {line}").scale(0.6)
#             self.play(Write(bullet))
#             self.wait(1.5)
#             self.play(FadeOut(bullet))


# def generate_animated_video(
#     title: str,
#     narration: str,
#     scenes: list[str],
#     output_path: str = "animated_explanation.mp4"
# ) -> str:
#     # 1) Make TTS audio
#     with tempfile.TemporaryDirectory() as tmp:
#         audio_path = os.path.join(tmp, "narration.mp3")
#         gTTS(narration).save(audio_path)

#         # 2) Render Manim scene to video
#         from manim import config, tempconfig
#         video_path = os.path.join(tmp, "manim.mp4")
#         with tempconfig({"output_file": video_path, "format": "mp4", "fps": 30}):
#             TutorScene(title=title, scenes=scenes).render()

#         # 3) Combine video + audio using MoviePy
#         clip = VideoFileClip(video_path)
#         audio = AudioFileClip(audio_path)
#         final = clip.set_audio(audio)
#         final.write_videofile(output_path, codec="libx264", audio_codec="aac")

#     return output_path






# src/video_generator.py
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tempfile
import os
from typing import Dict, Any, List
import json
import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip, ColorClip
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import io
import base64

class AnimatedVideoGenerator:
    def __init__(self, width=1280, height=720, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.temp_dir = tempfile.mkdtemp()
        
    def create_code_animation(self, code_lines: List[str], highlight_sequence: List[int], style: str):
        """Create animated code walkthrough"""
        try:
            fig, ax = plt.subplots(figsize=(16, 9), facecolor='#1e1e1e')
            ax.set_facecolor('#2d2d2d')
            ax.set_xlim(0, 10)
            ax.set_ylim(0, len(code_lines) + 2)
            ax.axis('off')
            
            frames = []
            
            for frame_idx in range(len(highlight_sequence) * 30):  # 30 frames per highlight
                ax.clear()
                ax.set_facecolor('#2d2d2d')
                ax.set_xlim(0, 10)
                ax.set_ylim(0, len(code_lines) + 2)
                ax.axis('off')
                
                current_highlight = highlight_sequence[frame_idx // 30] if frame_idx // 30 < len(highlight_sequence) else -1
                
                # Draw code lines
                for i, line in enumerate(code_lines):
                    y_pos = len(code_lines) - i
                    color = '#00ff00' if i == current_highlight else '#ffffff'
                    weight = 'bold' if i == current_highlight else 'normal'
                    
                    ax.text(0.5, y_pos, f"{i+1:2d}: {line}", 
                           fontsize=12, color=color, weight=weight,
                           fontfamily='monospace', ha='left')
                
                # Add title
                ax.text(5, len(code_lines) + 1, f"Code Walkthrough - {style}", 
                       fontsize=16, color='#00ccff', weight='bold', ha='center')
                
                # Save frame
                frame_path = os.path.join(self.temp_dir, f"frame_{frame_idx:04d}.png")
                plt.savefig(frame_path, facecolor='#1e1e1e', dpi=100, bbox_inches='tight')
                frames.append(frame_path)
            
            plt.close()
            return frames
            
        except Exception as e:
            st.error(f"Error creating code animation: {str(e)}")
            return []

    def create_concept_visualization(self, concept: str, steps: List[str], style: str):
        """Create animated concept visualization"""
        try:
            fig, ax = plt.subplots(figsize=(16, 9), facecolor='#1e1e1e')
            frames = []
            
            for step_idx, step in enumerate(steps):
                ax.clear()
                ax.set_facecolor('#2d2d2d')
                ax.set_xlim(0, 10)
                ax.set_ylim(0, 10)
                ax.axis('off')
                
                # Title
                ax.text(5, 9, concept, fontsize=20, color='#00ccff', 
                       weight='bold', ha='center')
                
                # Current step
                ax.text(5, 7, f"Step {step_idx + 1}: {step}", 
                       fontsize=14, color='#ffffff', ha='center', wrap=True)
                
                # Progress bar
                progress = (step_idx + 1) / len(steps)
                bar_width = 6
                ax.add_patch(patches.Rectangle((2, 1), bar_width, 0.5, 
                                             facecolor='#444444', alpha=0.5))
                ax.add_patch(patches.Rectangle((2, 1), bar_width * progress, 0.5, 
                                             facecolor='#00ff00', alpha=0.8))
                
                # Save frames (multiple frames per step for smooth animation)
                for frame in range(30):  # 1 second per step at 30fps
                    frame_path = os.path.join(self.temp_dir, f"concept_frame_{step_idx*30 + frame:04d}.png")
                    plt.savefig(frame_path, facecolor='#1e1e1e', dpi=100, bbox_inches='tight')
                    frames.append(frame_path)
            
            plt.close()
            return frames
            
        except Exception as e:
            st.error(f"Error creating concept visualization: {str(e)}")
            return []

    def create_algorithm_animation(self, algorithm_steps: List[Dict], style: str):
        """Create step-by-step algorithm animation"""
        try:
            fig, ax = plt.subplots(figsize=(16, 9), facecolor='#1e1e1e')
            frames = []
            
            for step_data in algorithm_steps:
                for frame_num in range(60):  # 2 seconds per step
                    ax.clear()
                    ax.set_facecolor('#2d2d2d')
                    ax.set_xlim(0, 10)
                    ax.set_ylim(0, 10)
                    ax.axis('off')
                    
                    # Algorithm title
                    ax.text(5, 9, step_data.get('title', 'Algorithm Step'), 
                           fontsize=18, color='#00ccff', weight='bold', ha='center')
                    
                    # Step description
                    ax.text(5, 7, step_data.get('description', ''), 
                           fontsize=12, color='#ffffff', ha='center')
                    
                    # Code snippet if available
                    if 'code' in step_data:
                        ax.text(5, 5, step_data['code'], 
                               fontsize=10, color='#00ff00', ha='center', 
                               fontfamily='monospace')
                    
                    # Visual elements
                    if 'visual_elements' in step_data:
                        for elem in step_data['visual_elements']:
                            if elem['type'] == 'arrow':
                                ax.arrow(elem['start'][0], elem['start'][1], 
                                        elem['end'][0] - elem['start'][0], 
                                        elem['end'][1] - elem['start'][1],
                                        head_width=0.1, head_length=0.1, 
                                        fc='#ffff00', ec='#ffff00')
                    
                    frame_path = os.path.join(self.temp_dir, f"algo_frame_{len(frames):04d}.png")
                    plt.savefig(frame_path, facecolor='#1e1e1e', dpi=100, bbox_inches='tight')
                    frames.append(frame_path)
            
            plt.close()
            return frames
            
        except Exception as e:
            st.error(f"Error creating algorithm animation: {str(e)}")
            return []

    def frames_to_video(self, frames: List[str], output_path: str, audio_path: str = None):
        """Convert frames to video with optional audio"""
        try:
            if not frames:
                return False
                
            # Read first frame to get dimensions
            first_frame = cv2.imread(frames[0])
            height, width, layers = first_frame.shape
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))
            
            # Write frames
            for frame_path in frames:
                frame = cv2.imread(frame_path)
                if frame is not None:
                    video_writer.write(frame)
            
            video_writer.release()
            
            # Add audio if provided
            if audio_path and os.path.exists(audio_path):
                try:
                    video_clip = VideoFileClip(output_path)
                    audio_clip = AudioFileClip(audio_path)
                    
                    # Adjust audio duration to match video
                    if audio_clip.duration > video_clip.duration:
                        audio_clip = audio_clip.subclip(0, video_clip.duration)
                    elif audio_clip.duration < video_clip.duration:
                        # Loop audio to match video duration
                        loops_needed = int(video_clip.duration / audio_clip.duration) + 1
                        audio_clip = audio_clip.loop(loops_needed).subclip(0, video_clip.duration)
                    
                    final_video = video_clip.set_audio(audio_clip)
                    final_output = output_path.replace('.mp4', '_with_audio.mp4')
                    final_video.write_videofile(final_output, codec='libx264', audio_codec='aac')
                    
                    # Cleanup
                    video_clip.close()
                    audio_clip.close()
                    final_video.close()
                    
                    return final_output
                except Exception as e:
                    st.warning(f"Could not add audio: {str(e)}")
                    return output_path
            
            return output_path
            
        except Exception as e:
            st.error(f"Error creating video: {str(e)}")
            return None

def generate_animated_video(script: Dict[str, Any], style: str, duration: int, language: str) -> str:
    """
    Main function to generate animated explanation video
    """
    try:
        generator = AnimatedVideoGenerator()
        
        # Create output path
        output_filename = f"explanation_video_{int(time.time())}.mp4"
        output_path = os.path.join(generator.temp_dir, output_filename)
        
        # Generate frames based on script content
        frames = []
        
        if isinstance(script, dict) and 'scenes' in script:
            # Handle structured script
            for scene in script['scenes']:
                if 'code' in scene:
                    code_lines = scene['code'].split('\n')
                    highlight_seq = list(range(len(code_lines)))
                    scene_frames = generator.create_code_animation(code_lines, highlight_seq, style)
                    frames.extend(scene_frames)
                else:
                    # Create concept visualization
                    steps = [scene.get('narration', 'Explaining concept...')]
                    concept_frames = generator.create_concept_visualization(
                        scene.get('title', 'Concept'), steps, style
                    )
                    frames.extend(concept_frames)
        else:
            # Handle simple script - create basic visualization
            content = script.get('content', 'No content available')
            
            # Extract code blocks if present
            import re
            code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
            
            if code_blocks:
                for code_block in code_blocks:
                    code_lines = [line.strip() for line in code_block.split('\n') if line.strip()]
                    highlight_seq = list(range(len(code_lines)))
                    code_frames = generator.create_code_animation(code_lines, highlight_seq, style)
                    frames.extend(code_frames)
            else:
                # Create concept-based animation
                concepts = content.split('\n\n')[:5]  # Take first 5 paragraphs
                concept_frames = generator.create_concept_visualization(
                    f"{language} Explanation", concepts, style
                )
                frames.extend(concept_frames)
        
        if frames:
            # Convert frames to video
            video_path = generator.frames_to_video(frames, output_path)
            
            if video_path and os.path.exists(video_path):
                # Move to accessible location
                final_path = f"generated_videos/{output_filename}"
                os.makedirs(os.path.dirname(final_path), exist_ok=True)
                
                # Copy to final location
                import shutil
                shutil.copy2(video_path, final_path)
                
                return final_path
            else:
                return None
        else:
            st.error("No frames generated for video")
            return None
            
    except Exception as e:
        st.error(f"Error in video generation: {str(e)}")
        return None

def generate_narration_audio(script_text: str, voice_style: str = "neutral") -> str:
    """
    Generate narration audio using text-to-speech
    Note: This would require a TTS service like Google Cloud TTS, Azure Speech, or AWS Polly
    """
    try:
        # Placeholder for TTS implementation
        # You would integrate with your preferred TTS service here
        
        # For now, return None to indicate no audio
        # In a real implementation, you would:
        # 1. Call TTS API with script_text
        # 2. Save audio file
        # 3. Return path to audio file
        
        return None
        
    except Exception as e:
        st.error(f"Error generating narration: {str(e)}")
        return None

def create_thumbnail(video_path: str) -> str:
    """Create thumbnail for generated video"""
    try:
        # Extract first frame as thumbnail
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            thumbnail_path = video_path.replace('.mp4', '_thumbnail.jpg')
            cv2.imwrite(thumbnail_path, frame)
            return thumbnail_path
        
        return None
        
    except Exception as e:
        st.error(f"Error creating thumbnail: {str(e)}")
        return None

def get_video_metadata(video_path: str) -> Dict[str, Any]:
    """Get metadata for generated video"""
    try:
        cap = cv2.VideoCapture(video_path)
        
        # Get video properties
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        cap.release()
        
        # Get file size
        file_size = os.path.getsize(video_path)
        
        return {
            "duration": round(duration, 2),
            "fps": fps,
            "resolution": f"{width}x{height}",
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "frame_count": frame_count
        }
        
    except Exception as e:
        return {"error": f"Could not get metadata: {str(e)}"}

# Additional utility functions for enhanced video features

def create_interactive_elements(explanation_data: Dict[str, Any]) -> List[Dict]:
    """Create interactive elements for video"""
    interactive_elements = []
    
    # Quiz questions
    if 'quiz_questions' in explanation_data:
        for i, question in enumerate(explanation_data['quiz_questions']):
            interactive_elements.append({
                "type": "quiz",
                "timestamp": i * 30,  # Every 30 seconds
                "data": question
            })
    
    # Code highlights
    if 'code_highlights' in explanation_data:
        for highlight in explanation_data['code_highlights']:
            interactive_elements.append({
                "type": "highlight",
                "timestamp": highlight.get('time', 0),
                "data": highlight
            })
    
    return interactive_elements

def enhance_video_with_effects(video_path: str, effects: List[str]) -> str:
    """Add visual effects to enhance the video"""
    try:
        from moviepy.editor import VideoFileClip, CompositeVideoClip
        
        clip = VideoFileClip(video_path)
        enhanced_clips = [clip]
        
        # Add effects based on style
        if "glow" in effects:
            # Add glow effect (simplified)
            pass
        
        if "transitions" in effects:
            # Add transition effects
            pass
        
        # Composite all clips
        final_clip = CompositeVideoClip(enhanced_clips)
        enhanced_path = video_path.replace('.mp4', '_enhanced.mp4')
        final_clip.write_videofile(enhanced_path, codec='libx264')
        
        # Cleanup
        clip.close()
        final_clip.close()
        
        return enhanced_path
        
    except Exception as e:
        st.warning(f"Could not enhance video: {str(e)}")
        return video_path

# Main function that's called from the app
def generate_animated_video(script: Dict[str, Any], style: str, duration: int, language: str) -> str:
    """
    Main entry point for video generation
    """
    try:
        # Ensure output directory exists
        os.makedirs("generated_videos", exist_ok=True)
        
        # Initialize generator
        generator = AnimatedVideoGenerator()
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🎬 Initializing video generation...")
        progress_bar.progress(10)
        
        # Parse script and create animations
        status_text.text("🎨 Creating animations...")
        progress_bar.progress(30)
        
        # Generate video based on style
        if style == "Code Walkthrough":
            # Extract code from script
            content = script.get('content', '')
            import re
            code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
            
            if code_blocks:
                code_lines = code_blocks[0].split('\n')
                highlight_seq = list(range(len(code_lines)))
                frames = generator.create_code_animation(code_lines, highlight_seq, style)
            else:
                frames = []
        
        elif style == "Animated Tutorial":
            # Create concept-based animation
            content = script.get('content', '')
            concepts = [p.strip() for p in content.split('\n\n') if p.strip()][:5]
            frames = generator.create_concept_visualization(f"{language} Tutorial", concepts, style)
        
        elif style == "Interactive Demo":
            # Create algorithm animation
            algorithm_steps = [
                {"title": "Step 1", "description": "Initialize variables"},
                {"title": "Step 2", "description": "Process data"},
                {"title": "Step 3", "description": "Return result"}
            ]
            frames = generator.create_algorithm_animation(algorithm_steps, style)
        
        else:  # Whiteboard Style
            content = script.get('content', '')
            concepts = [p.strip() for p in content.split('\n\n') if p.strip()][:3]
            frames = generator.create_concept_visualization("Whiteboard Explanation", concepts, style)
        
        status_text.text("🎞️ Rendering video...")
        progress_bar.progress(70)
        
        if frames:
            # Create output path
            output_filename = f"{style.lower().replace(' ', '_')}_{int(time.time())}.mp4"
            output_path = os.path.join("generated_videos", output_filename)
            
            # Generate video
            video_path = generator.frames_to_video(frames, output_path)
            
            status_text.text("✅ Video generation complete!")
            progress_bar.progress(100)
            
            # Clean up temporary files
            try:
                import shutil
                shutil.rmtree(generator.temp_dir)
            except:
                pass
            
            return video_path
        else:
            status_text.text("❌ No frames generated")
            return None
            
    except Exception as e:
        st.error(f"Error generating animated video: {str(e)}")
        return None

# Utility functions for video management
def list_generated_videos() -> List[Dict[str, Any]]:
    """List all generated videos with metadata"""
    videos = []
    video_dir = "generated_videos"
    
    if os.path.exists(video_dir):
        for filename in os.listdir(video_dir):
            if filename.endswith('.mp4'):
                video_path = os.path.join(video_dir, filename)
                metadata = get_video_metadata(video_path)
                metadata['filename'] = filename
                metadata['path'] = video_path
                videos.append(metadata)
    
    return videos

def cleanup_old_videos(max_videos: int = 10):
    """Clean up old videos to save space"""
    try:
        videos = list_generated_videos()
        if len(videos) > max_videos:
            # Sort by creation time and remove oldest
            videos.sort(key=lambda x: os.path.getctime(x['path']))
            
            for video in videos[:-max_videos]:
                try:
                    os.remove(video['path'])
                    # Remove thumbnail if exists
                    thumbnail_path = video['path'].replace('.mp4', '_thumbnail.jpg')
                    if os.path.exists(thumbnail_path):
                        os.remove(thumbnail_path)
                except:
                    pass
                    
    except Exception as e:
        st.warning(f"Could not cleanup old videos: {str(e)}")

# Initialize video directory
os.makedirs("generated_videos", exist_ok=True)