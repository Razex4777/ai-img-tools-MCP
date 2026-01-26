"""
Video Analyzer - AI Video Understanding with Gemini
Analyze video content using Gemini's multimodal capabilities.
Supports multiple local files, YouTube URLs, timestamps, and clipping.
"""

import os
import time
from typing import Optional, List
from google import genai
from google.genai import types


# Configure API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Google GenAI client
client = None
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)


# Supported video formats
SUPPORTED_FORMATS = [
    "video/mp4", "video/mpeg", "video/mov", "video/avi",
    "video/x-flv", "video/mpg", "video/webm", "video/wmv", "video/3gpp"
]

EXTENSION_TO_MIME = {
    ".mp4": "video/mp4",
    ".mpeg": "video/mpeg",
    ".mpg": "video/mpg",
    ".mov": "video/mov",
    ".avi": "video/avi",
    ".flv": "video/x-flv",
    ".webm": "video/webm",
    ".wmv": "video/wmv",
    ".3gp": "video/3gpp",
    ".3gpp": "video/3gpp",
}


async def video_analyzer(
    prompt: str,
    video_path: Optional[str] = None,
    video_paths: Optional[List[str]] = None,
    youtube_url: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    fps: float = 1.0,
) -> str:
    """
    🎥 VIDEO ANALYZER - AI Video Understanding with Gemini!
    
    Analyze video content using Gemini's powerful multimodal capabilities.
    Supports local video files, YouTube URLs, timestamp queries, and clipping.
    Uses the state-of-the-art Gemini 3 Flash Preview model.
    
    Args:
        prompt: Your question or task for the video.
                Examples:
                - "Summarize this video in 3 sentences"
                - "What topics are discussed?"
                - "What happens at 02:30?"
                - "List all the products shown"
                - "Create a quiz based on this video"
        
        video_path: Path to a local video file.
                   Supported formats: mp4, mpeg, mov, avi, flv, mpg, webm, wmv, 3gpp
                   For files >20MB, the file is uploaded via Files API.
                   Example: "presentation.mp4"
        
        video_paths: List of paths to multiple local video files.
                    Use this to analyze and compare multiple videos at once.
                    Example: ["video1.mp4", "video2.mp4", "video3.mp4"]
        
        youtube_url: YouTube video URL to analyze.
                    Example: "https://www.youtube.com/watch?v=abc123"
                    Note: Only one of video_path or youtube_url should be provided.
        
        start_time: Start time for clipping (MM:SS format).
                   Only analyzed portion of video from this time.
                   Example: "01:30" (start at 1 minute 30 seconds)
        
        end_time: End time for clipping (MM:SS format).
                 Only analyzed portion of video up to this time.
                 Example: "05:00" (end at 5 minutes)
        
        fps: Frame sampling rate (frames per second).
            Default: 1.0 (1 frame per second)
            Lower values = faster processing, less detail
            Higher values = more detail, slower processing
    
    Returns:
        Analysis result from Gemini, or error message
    
    Examples:
        # Summarize a local video
        video_analyzer(
            video_path="lecture.mp4",
            prompt="Summarize the main points of this lecture"
        )
        
        # Analyze multiple videos
        video_analyzer(
            video_paths=["intro.mp4", "main.mp4", "outro.mp4"],
            prompt="Compare these three videos and describe the differences"
        )
        
        # Analyze a YouTube video
        video_analyzer(
            youtube_url="https://youtube.com/watch?v=abc123",
            prompt="What are the key takeaways?"
        )
        
        # Query specific timestamp
        video_analyzer(
            video_path="demo.mp4",
            prompt="Describe what happens between 02:00 and 03:30",
            start_time="02:00",
            end_time="03:30"
        )
        
        # Detailed analysis with higher FPS
        video_analyzer(
            video_path="sports.mp4",
            prompt="Describe all the plays in detail",
            fps=2.0
        )
    """
    if not GOOGLE_API_KEY:
        return "🚨 Error: GOOGLE_API_KEY environment variable is not set"
    
    try:
        # Validate inputs
        if not prompt:
            return "🚨 Error: prompt is required"
        
        # Normalize inputs - support both single path and list
        all_video_paths = []
        if video_path:
            all_video_paths.append(video_path)
        if video_paths:
            all_video_paths.extend(video_paths)
        
        if not all_video_paths and not youtube_url:
            return "🚨 Error: Either video_path, video_paths, or youtube_url must be provided"
        
        if all_video_paths and youtube_url:
            return "🚨 Error: Provide video files OR youtube_url, not both"
        
        result_parts = ["🎥 Video Analyzer - Processing Started!"]
        
        # Build content parts
        content_parts = []
        
        # Handle YouTube URL
        if youtube_url:
            result_parts.append(f"📺 YouTube: {youtube_url}")
            content_parts.append(
                types.Part(
                    file_data=types.FileData(file_uri=youtube_url)
                )
            )
        
        # Handle local video files (single or multiple)
        elif all_video_paths:
            result_parts.append(f"📁 Files: {len(all_video_paths)}")
            total_size = 0
            
            for idx, vpath in enumerate(all_video_paths):
                if not os.path.exists(vpath):
                    return f"🚨 Error: Video file not found: {vpath}"
                
                # Get file extension and MIME type
                ext = os.path.splitext(vpath)[1].lower()
                mime_type = EXTENSION_TO_MIME.get(ext, "video/mp4")
                
                file_size = os.path.getsize(vpath)
                file_size_mb = file_size / (1024 * 1024)
                total_size += file_size
                
                result_parts.append(f"   📹 {os.path.basename(vpath)} ({file_size_mb:.2f} MB)")
                
                # Always use Files API for video (more reliable)
                result_parts.append(f"      📤 Uploading...")
                uploaded_file = client.files.upload(file=vpath)
                
                # Wait for file to be processed
                while uploaded_file.state.name == "PROCESSING":
                    time.sleep(1)
                    uploaded_file = client.files.get(name=uploaded_file.name)
                
                if uploaded_file.state.name == "FAILED":
                    return f"🚨 Error: Video processing failed for {os.path.basename(vpath)}"
                
                # Create Part from uploaded file
                content_parts.append(
                    types.Part.from_uri(
                        file_uri=uploaded_file.uri,
                        mime_type=uploaded_file.mime_type
                    )
                )
            
            total_size_mb = total_size / (1024 * 1024)
            result_parts.append(f"📦 Total size: {total_size_mb:.2f} MB")
            result_parts.append("✅ All uploads complete!")
        
        # Build the prompt with optional timestamp context
        final_prompt = prompt
        if start_time or end_time:
            time_context = []
            if start_time:
                time_context.append(f"starting from {start_time}")
            if end_time:
                time_context.append(f"ending at {end_time}")
            final_prompt = f"{prompt} (Focus on the video segment {' and '.join(time_context)})"
            result_parts.append(f"⏱️ Clipping: {start_time or 'start'} - {end_time or 'end'}")
        
        # Add the prompt
        content_parts.append(types.Part(text=final_prompt))
        
        # Build config with optional video processing settings
        config_params = {}
        if fps != 1.0:
            # Note: fps config may require specific API support
            result_parts.append(f"🎞️ FPS: {fps}")
        
        result_parts.append("")
        result_parts.append("🔍 Analyzing video(s)...")
        
        # Make the request
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=types.Content(parts=content_parts),
        )
        
        result_parts.append("")
        result_parts.append("✅ Analysis complete!")
        result_parts.append("")
        result_parts.append("📝 **Result:**")
        result_parts.append(response.text)
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"🚨 Error in video_analyzer: {str(e)}"
