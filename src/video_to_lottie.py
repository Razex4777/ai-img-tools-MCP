"""
Video to Lottie - Convert video to Lottie animation
Converts video → GIF → Lottie JSON with embedded frames.
Supports optional loop optimization for seamless looping.
"""

import os
import json
import base64
from typing import Optional
from PIL import Image
from moviepy import VideoFileClip


async def video_to_lottie(
    video_path: str,
    save_path: str,
    fps: int = 15,
    width: Optional[int] = None,
    loop: bool = True,
    loop_trim_start: float = 0.0,
    optimize: bool = True,
    chroma_key: Optional[list[int]] = None,
    chroma_threshold: int = 30,
) -> str:
    """
    🎬 VIDEO TO LOTTIE - Convert video to Lottie animation!
    
    Converts a video file to Lottie JSON format by extracting frames
    and embedding them as base64 images. Perfect for creating web-ready
    animations from video content.
    
    Pipeline: Video → Frames → Lottie JSON (embedded images)
    
    Args:
        video_path: Path to the input video file.
                   Supported: mp4, mov, avi, webm
                   Example: "animation.mp4"
        
        save_path: Path to save the Lottie JSON file.
                  Example: "animation.json"
        
        fps: Frame rate for the Lottie animation.
             Lower = smaller file, choppier animation.
             Higher = larger file, smoother animation.
             Default: 15 (good balance)
             Recommended: 10-30
        
        width: Optional width to resize frames (maintains aspect ratio).
              Smaller = smaller file size.
              Default: None (original size)
              Example: 256 (for icons), 512 (for web)
        
        loop: Whether the Lottie should loop.
             Default: True
        
        loop_trim_start: Seconds to trim from the START of video.
                        Useful for removing AI video "stutter" at the beginning.
                        Default: 0.0 (no trim)
                        Recommended: 0.3-0.5 for Veo-generated loops
        
        optimize: Reduce file size by compressing images.
                 Default: True
        
        chroma_key: Optional RGB color to make transparent [R, G, B].
                   Example: [0, 255, 0] for bright green.
        
        chroma_threshold: Sensitivity for chroma keying (0-255).
                         Higher = more colors removed.
                         Default: 30
    
    Returns:
        Success message with file details and Lottie preview info
    
    Examples:
        # Basic conversion
        video_to_lottie(
            video_path="animation.mp4",
            save_path="animation.json"
        )
        
        # Looping video with trim (for Veo-generated content)
        video_to_lottie(
            video_path="veo_loop.mp4",
            save_path="seamless_loop.json",
            loop=True,
            loop_trim_start=0.5  # Remove stutter
        )
        
        # Small icon animation
        video_to_lottie(
            video_path="icon_spin.mp4",
            save_path="icon.json",
            width=128,
            fps=12
        )
    """
    # Validate inputs
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    if not save_path.endswith(".json"):
        save_path += ".json"
    
    try:
        result_parts = ["🎬 Video to Lottie - Converting..."]
        result_parts.append(f"📹 Input: {os.path.basename(video_path)}")
        
        # Load video
        video = VideoFileClip(video_path)
        original_duration = video.duration
        result_parts.append(f"⏱️ Duration: {original_duration:.2f}s")
        
        # Apply loop trim if specified
        if loop_trim_start > 0 and loop_trim_start < video.duration:
            video = video.subclipped(loop_trim_start, video.duration)
            result_parts.append(f"✂️ Trimmed start: {loop_trim_start}s")
        
        # Calculate dimensions
        if width:
            height = int(video.h * (width / video.w))
        else:
            width = video.w
            height = video.h
        
        result_parts.append(f"📐 Size: {width}x{height}")
        result_parts.append(f"🎞️ FPS: {fps}")
        
        # Extract frames
        frames = []
        frame_duration = 1 / fps
        total_frames = int(video.duration * fps)
        
        result_parts.append(f"🖼️ Extracting {total_frames} frames...")
        
        for i in range(total_frames):
            t = i * frame_duration
            if t >= video.duration:
                break
            
            # Get frame as PIL Image
            frame_array = video.get_frame(t)
            img = Image.fromarray(frame_array)
            
            # Resize if needed
            if img.size != (width, height):
                img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # Apply chroma key if specified
            if chroma_key:
                if i == 0:
                    result_parts.append(f"🔍 Chroma Key active: {chroma_key}, Threshold: {chroma_threshold}")
                
                img = img.convert("RGBA")
                datas = img.getdata()
                new_data = []
                removed_count = 0
                for item in datas:
                    is_green = False
                    # Check for pure green screen (#00FF00) or similar
                    r, g, b = item[0], item[1], item[2]
                    
                    # Distance check
                    dist = ((r-chroma_key[0])**2 + (g-chroma_key[1])**2 + (b-chroma_key[2])**2)**0.5
                    if dist < chroma_threshold:
                        is_green = True
                    
                    # Dominant green check (heuristic for green screen)
                    if not is_green and g > 100 and g > r + 30 and g > b + 30:
                        is_green = True
                            
                    if is_green:
                        new_data.append((0, 0, 0, 0)) # Fully transparent
                        removed_count += 1
                    else:
                        new_data.append(item)
                
                img.putdata(new_data)
                is_transparent_frame = True # Ensure we use PNG
                if i % 10 == 0:
                    result_parts.append(f"🪄 Frame {i}: Removed {removed_count} pixels")
            else:
                is_transparent_frame = False
            
            # Convert to base64
            from io import BytesIO
            buffer = BytesIO()
            img_format = "PNG" if (is_transparent_frame or not optimize) else "WEBP"
            quality = 80 if optimize else 100
            img.save(buffer, format=img_format, quality=quality if img_format == "WEBP" else None)
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            mime_type = "image/png" if img_format == "PNG" else "image/webp"
            frames.append({
                "data": f"data:{mime_type};base64,{img_base64}",
                "duration": frame_duration
            })
        
        video.close()
        
        # Build Lottie JSON structure
        # Lottie uses a specific format for image sequences
        lottie = {
            "v": "5.7.4",  # Lottie version
            "fr": fps,     # Frame rate
            "ip": 0,       # In point
            "op": len(frames),  # Out point (total frames)
            "w": width,
            "h": height,
            "nm": os.path.splitext(os.path.basename(video_path))[0],
            "ddd": 0,      # 3D layers disabled
            "assets": [],
            "layers": []
        }
        
        # Add image assets
        for i, frame in enumerate(frames):
            lottie["assets"].append({
                "id": f"image_{i}",
                "w": width,
                "h": height,
                "u": "",
                "p": frame["data"],
                "e": 1  # Embedded
            })
        
        # Create image sequence layer
        # Each frame shows for 1 frame duration
        layer = {
            "ddd": 0,
            "ind": 1,
            "ty": 2,  # Image layer
            "nm": "Frame Sequence",
            "refId": "image_0",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},  # Opacity 100%
                "r": {"a": 0, "k": 0},    # Rotation 0
                "p": {"a": 0, "k": [width/2, height/2, 0]},  # Position center
                "a": {"a": 0, "k": [width/2, height/2, 0]},  # Anchor center
                "s": {"a": 0, "k": [100, 100, 100]}  # Scale 100%
            },
            "ip": 0,
            "op": len(frames),
            "st": 0,
            "bm": 0
        }
        
        # For true frame sequence, we need to use time remapping
        # This creates keyframes that switch between images
        # Simpler approach: create multiple layers, each visible for 1 frame
        lottie["layers"] = []
        for i in range(len(frames)):
            frame_layer = {
                "ddd": 0,
                "ind": i + 1,
                "ty": 2,
                "nm": f"Frame {i}",
                "refId": f"image_{i}",
                "sr": 1,
                "ks": {
                    "o": {"a": 0, "k": 100},
                    "r": {"a": 0, "k": 0},
                    "p": {"a": 0, "k": [width/2, height/2, 0]},
                    "a": {"a": 0, "k": [width/2, height/2, 0]},
                    "s": {"a": 0, "k": [100, 100, 100]}
                },
                "ip": i,      # In point = this frame
                "op": i + 1,  # Out point = next frame
                "st": 0,
                "bm": 0
            }
            lottie["layers"].append(frame_layer)
        
        # Set loop property in metadata
        if loop:
            lottie["markers"] = [{"cm": "loop", "tm": 0, "dr": len(frames)}]
        
        # Create output directory if needed
        parent_dir = os.path.dirname(save_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Save Lottie JSON
        with open(save_path, 'w') as f:
            json.dump(lottie, f, separators=(',', ':') if optimize else None)
        
        # Get file size
        file_size = os.path.getsize(save_path)
        if file_size > 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{file_size / 1024:.2f} KB"
        
        result_parts.append("")
        result_parts.append("✅ Lottie created successfully!")
        result_parts.append(f"💾 Saved: {save_path}")
        result_parts.append(f"📦 Size: {size_str}")
        result_parts.append(f"🔄 Loop: {'Yes' if loop else 'No'}")
        result_parts.append(f"🖼️ Frames: {len(frames)}")
        result_parts.append("")
        result_parts.append("🌐 Preview: Use https://lottiefiles.com/preview to view")
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"🚨 Error in video_to_lottie: {str(e)}"
