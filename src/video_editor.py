"""
Video Editor - Comprehensive AI Video Editing Tool with MoviePy

A single tool with all video editing operations accessible via the 'operation' parameter.
Supports merging, text overlays, audio mixing, effects, transforms, and exports.
"""

import os
from typing import Optional, List
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip, concatenate_videoclips
import moviepy.video.fx as vfx
import pysrt
import numpy as np


async def video_editor(
    video_paths: List[str],
    save_path: str,
    operation: str = "merge",
    # Merge options
    fade_in: float = 0.0,
    fade_out: float = 0.0,
    crossfade: float = 0.0,
    trim_start: Optional[List[float]] = None,
    trim_end: Optional[List[float]] = None,
    speed: float = 1.0,
    resolution: Optional[str] = None,
    fps: int = 30,
    codec: str = "libx264",
    audio_codec: str = "aac",
    bitrate: str = "8000k",
    preset: str = "medium",
    # Text options
    text: Optional[str] = None,
    text_position: str = "center",
    font_size: int = 50,
    font: str = "Arial",
    text_color: str = "white",
    text_bg_color: Optional[str] = None,
    text_start: float = 0.0,
    text_duration: Optional[float] = None,
    opacity: float = 1.0,
    # Audio options
    audio_path: Optional[str] = None,
    video_volume: float = 1.0,
    audio_volume: float = 0.5,
    loop_audio: bool = True,
    # Effect options
    effect: str = "none",
    brightness: float = 1.0,
    contrast: float = 1.0,
    # Transform options
    angle: int = 90,
    flip_direction: str = "horizontal",
    crop_x1: int = 0,
    crop_y1: int = 0,
    crop_x2: Optional[int] = None,
    crop_y2: Optional[int] = None,
    scale: Optional[float] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    # Speed options
    loops: int = 2,
    # Export options
    gif_fps: int = 10,
    timestamp: float = 0.0,
    # PIP options
    overlay_video_path: Optional[str] = None,
    pip_position: str = "bottom-right",
    pip_scale: float = 0.3,
    overlap: int = 20,
    # Chroma Key options
    color_key: str = "#00FF00",
    thr: float = 0.2,
    # Subtitle options
    subtitles_path: Optional[str] = None,
    # Silence Removal options
    silence_threshold: float = -50.0,
    min_silence_len: float = 0.5,
    # Cut options
    cut_start: float = 0.0,
    cut_end: Optional[float] = None,
) -> str:
    """
    🎬 VIDEO EDITOR - Merge and edit videos with transitions!
    
    Combine multiple videos into one with professional transitions, trimming,
    speed adjustments, and quality settings using MoviePy.
    
    Args:
        video_paths: List of video file paths to merge (in order).
                    Example: ["intro.mp4", "main.mp4", "outro.mp4"]
        
        save_path: Output file path for the merged video.
                  Example: "final_video.mp4"
        
        operation: The editing operation to perform:
                  - "merge" (default) - Combine videos with transitions
                  - "text" - Add text overlay
                  - "watermark" - Add watermark
                  - "audio_mix" - Add background audio
                  - "volume" - Adjust volume
                  - "mute" - Remove audio
                  - "filter" - Apply visual filter (blackwhite, invert, mirror_x, mirror_y)
                  - "color" - Adjust brightness/contrast
                  - "rotate" - Rotate video (90, 180, 270)
                  - "flip" - Flip horizontal/vertical
                  - "crop" - Crop video region
                  - "resize" - Resize video
                  - "speed" - Change playback speed
                  - "reverse" - Play backwards
                  - "loop" - Repeat video
                  - "gif" - Convert to GIF
                  - "thumbnail" - Extract frame
                  - "extract_audio" - Export audio track
                  - "extract_audio" - Export audio track
                  - "pip" - Picture-in-picture
                  - "chroma_key" - Green screen removal
                  - "subtitles" - Burn subtitles from SRT
                  - "remove_silence" - Auto-remove silent parts
                  - "cut" - Extract a segment from video
        
        fade_in: Fade-in duration for the FIRST clip (seconds).
                Default: 0.0 (no fade-in)
                Example: 1.0 (1 second fade from black)
        
        fade_out: Fade-out duration for the LAST clip (seconds).
                 Default: 0.0 (no fade-out)
                 Example: 1.0 (1 second fade to black)
        
        crossfade: Crossfade duration between clips (seconds).
                  Creates smooth transitions by overlapping clips.
                  Default: 0.0 (no crossfade, hard cuts)
                  Example: 0.5 (0.5 second crossfade between each clip)
        
        trim_start: Start time for each clip (seconds).
                   List length must match video_paths.
                   None values keep original start.
                   Example: [0.0, 5.0, 2.0] - skip first 5s of second clip
        
        trim_end: End time for each clip (seconds).
                 List length must match video_paths.
                 None values keep original end.
                 Example: [30.0, None, 10.0] - first clip ends at 30s
        
        speed: Playback speed multiplier for all clips.
              Default: 1.0 (normal speed)
              Example: 1.5 (50% faster), 0.5 (50% slower)
        
        resolution: Output resolution as "WIDTHxHEIGHT".
                   Default: None (keep original resolution)
                   Examples: "1920x1080", "1280x720", "3840x2160"
        
        fps: Output frame rate.
            Default: 30
            Examples: 24, 30, 60
        
        codec: Video codec for encoding.
              Default: "libx264" (H.264, widely compatible)
              Options: "libx264", "libx265", "mpeg4", "prores"
        
        audio_codec: Audio codec for encoding.
                    Default: "aac"
                    Options: "aac", "mp3", "pcm_s16le"
        
        bitrate: Video bitrate (quality vs file size).
                Default: "8000k" (8 Mbps, good quality)
                Examples: "4000k" (smaller), "12000k" (higher quality)
        
        preset: Encoding speed preset (affects quality and encoding time).
               Default: "medium"
               Options: "ultrafast", "superfast", "veryfast", "faster", 
                       "fast", "medium", "slow", "slower", "veryslow"
               Slower = better quality, longer encoding time
    
    Returns:
        Success message with video details, or error message
    
    Examples:
        # Simple merge of 3 videos
        video_editor(
            video_paths=["clip1.mp4", "clip2.mp4", "clip3.mp4"],
            save_path="merged.mp4"
        )
        
        # Professional edit with transitions
        video_editor(
            video_paths=["intro.mp4", "main.mp4", "outro.mp4"],
            save_path="final.mp4",
            fade_in=1.0,
            fade_out=1.0,
            crossfade=0.5,
            fps=60,
            bitrate="12000k",
            preset="slow"
        )
        
        # Trim and speed up clips
        video_editor(
            video_paths=["raw1.mp4", "raw2.mp4"],
            save_path="highlights.mp4",
            trim_start=[10.0, 5.0],
            trim_end=[60.0, 45.0],
            speed=1.25
        )
        
        # High-quality 4K output
        video_editor(
            video_paths=["scene1.mp4", "scene2.mp4"],
            save_path="4k_master.mp4",
            resolution="3840x2160",
            fps=60,
            bitrate="20000k",
            preset="slow"
        )
    """
    try:
        # Validate inputs
        if not video_paths:
            return "🚨 Error: video_paths cannot be empty"
        
        if not save_path:
            return "🚨 Error: save_path is required"
        
        # Create output directory if needed
        parent_dir = os.path.dirname(save_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Route to appropriate operation
        if operation == "merge":
            return await _op_merge(video_paths, save_path, fade_in, fade_out, crossfade,
                                   trim_start, trim_end, speed, resolution, fps, codec,
                                   audio_codec, bitrate, preset)
        elif operation == "text":
            return await _op_text(video_paths[0], save_path, text, text_position, font_size,
                                  font, text_color, text_bg_color, text_start, text_duration,
                                  fps, codec)
        elif operation == "watermark":
            return await _op_watermark(video_paths[0], save_path, text, text_position, opacity,
                                       font_size, text_color, fps, codec)
        elif operation == "audio_mix":
            return await _op_audio_mix(video_paths[0], save_path, audio_path, video_volume,
                                       audio_volume, loop_audio, fps, codec, audio_codec)
        elif operation == "volume":
            return await _op_volume(video_paths[0], save_path, video_volume, fps, codec, audio_codec)
        elif operation == "mute":
            return await _op_mute(video_paths[0], save_path, fps, codec)
        elif operation == "filter":
            return await _op_filter(video_paths[0], save_path, effect, fps, codec, audio_codec)
        elif operation == "color":
            return await _op_color(video_paths[0], save_path, brightness, contrast, fps, codec, audio_codec)
        elif operation == "rotate":
            return await _op_rotate(video_paths[0], save_path, angle, fps, codec, audio_codec)
        elif operation == "flip":
            return await _op_flip(video_paths[0], save_path, flip_direction, fps, codec, audio_codec)
        elif operation == "crop":
            return await _op_crop(video_paths[0], save_path, crop_x1, crop_y1, crop_x2, crop_y2,
                                  fps, codec, audio_codec)
        elif operation == "resize":
            return await _op_resize(video_paths[0], save_path, width, height, scale, fps, codec, audio_codec)
        elif operation == "speed":
            return await _op_speed(video_paths[0], save_path, speed, fps, codec, audio_codec)
        elif operation == "reverse":
            return await _op_reverse(video_paths[0], save_path, fps, codec, audio_codec)
        elif operation == "loop":
            return await _op_loop(video_paths[0], save_path, loops, fps, codec, audio_codec)
        elif operation == "gif":
            return await _op_gif(video_paths[0], save_path, text_start, text_duration, gif_fps, width)
        elif operation == "thumbnail":
            return await _op_thumbnail(video_paths[0], save_path, timestamp)
        elif operation == "extract_audio":
            return await _op_extract_audio(video_paths[0], save_path, audio_codec, bitrate)
        elif operation == "pip":
            return await _op_pip(video_paths[0], overlay_video_path, save_path, pip_position,
                                 pip_scale, text_start, fps, codec, audio_codec)
        elif operation == "chroma_key":
            return await _op_chroma_key(video_paths[0], save_path, color_key, thr, fps, codec, audio_codec)
        elif operation == "subtitles":
            return await _op_subtitles(video_paths[0], save_path, subtitles_path, font_size, font, 
                                       text_color, fps, codec, audio_codec)
        elif operation == "remove_silence":
            return await _op_remove_silence(video_paths[0], save_path, silence_threshold, 
                                            min_silence_len, fps, codec, audio_codec)
        elif operation == "cut":
            return await _op_cut(video_paths[0], save_path, cut_start, cut_end, fps, codec, audio_codec)
        else:
            return f"🚨 Error: Unknown operation '{operation}'"
            
    except Exception as e:
        return f"🚨 Error in video_editor: {str(e)}"


# ============================================================================
# OPERATION IMPLEMENTATIONS
# ============================================================================

async def _op_merge(video_paths, save_path, fade_in, fade_out, crossfade,
                    trim_start, trim_end, speed, resolution, fps, codec,
                    audio_codec, bitrate, preset):
    """Merge multiple videos with transitions."""
    for path in video_paths:
        if not os.path.exists(path):
            return f"🚨 Error: Video file not found: {path}"
    
    if trim_start and len(trim_start) != len(video_paths):
        return "🚨 Error: trim_start length must match video_paths"
    
    if trim_end and len(trim_end) != len(video_paths):
        return "🚨 Error: trim_end length must match video_paths"
    
    clips = []
    total_duration = 0
    
    for i, path in enumerate(video_paths):
        clip = VideoFileClip(path)
        
        start = 0
        end = clip.duration
        
        if trim_start and i < len(trim_start) and trim_start[i] is not None:
            start = trim_start[i]
        
        if trim_end and i < len(trim_end) and trim_end[i] is not None:
            end = trim_end[i]
        
        if start > 0 or end < clip.duration:
            clip = clip.subclipped(start, min(end, clip.duration))
        
        if speed != 1.0:
            speed_fx = vfx.MultiplySpeed(factor=speed)
            clip = speed_fx.apply(clip)
        
        total_duration += clip.duration
        clips.append(clip)
    
    if fade_in > 0 and clips:
        fade_in_fx = vfx.FadeIn(duration=fade_in)
        clips[0] = fade_in_fx.apply(clips[0])
    
    if fade_out > 0 and clips:
        fade_out_fx = vfx.FadeOut(duration=fade_out)
        clips[-1] = fade_out_fx.apply(clips[-1])
    
    if crossfade > 0 and len(clips) > 1:
        final_clip = concatenate_videoclips(clips, method="compose", padding=-crossfade)
    else:
        final_clip = concatenate_videoclips(clips, method="compose")
    
    if resolution:
        try:
            w, h = map(int, resolution.lower().split("x"))
            final_clip = final_clip.resized((w, h))
        except ValueError:
            return f"🚨 Error: Invalid resolution format"
    
    final_clip.write_videofile(save_path, codec=codec, audio_codec=audio_codec,
                               fps=fps, preset=preset, bitrate=bitrate, logger=None)
    
    for clip in clips:
        clip.close()
    final_clip.close()
    
    file_size = os.path.getsize(save_path) / (1024 * 1024)
    return f"🔗 Merged {len(video_paths)} videos! {file_size:.2f} MB, {total_duration:.1f}s. Saved: {save_path}"


async def _op_text(video_path, save_path, text, position, font_size, font, color,
                   bg_color, start_time, duration, fps, codec):
    """Add text overlay to video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    if not text:
        return "🚨 Error: text is required for text operation"
    
    video = VideoFileClip(video_path)
    txt_clip = TextClip(text=text, font_size=font_size, font=font, color=color, bg_color=bg_color)
    
    text_dur = duration if duration else (video.duration - start_time)
    txt_clip = txt_clip.with_duration(text_dur).with_start(start_time)
    
    pos_map = {"center": ("center", "center"), "top": ("center", "top"),
               "bottom": ("center", "bottom"), "top-left": ("left", "top"),
               "top-right": ("right", "top"), "bottom-left": ("left", "bottom"),
               "bottom-right": ("right", "bottom")}
    txt_clip = txt_clip.with_position(pos_map.get(position, ("center", "center")))
    
    final = CompositeVideoClip([video, txt_clip])
    final.write_videofile(save_path, codec=codec, fps=fps, logger=None)
    video.close()
    final.close()
    
    return f"📝 Text added! Saved: {save_path}"


async def _op_watermark(video_path, save_path, text, position, opacity, font_size, color, fps, codec):
    """Add watermark to video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    if not text:
        return "🚨 Error: text is required for watermark operation"
    
    video = VideoFileClip(video_path)
    txt_clip = TextClip(text=text, font_size=font_size, color=color)
    txt_clip = txt_clip.with_duration(video.duration).with_opacity(opacity)
    
    pos_map = {"bottom-right": ("right", "bottom"), "bottom-left": ("left", "bottom"),
               "top-right": ("right", "top"), "top-left": ("left", "top")}
    txt_clip = txt_clip.with_position(pos_map.get(position, ("right", "bottom")))
    
    final = CompositeVideoClip([video, txt_clip])
    final.write_videofile(save_path, codec=codec, fps=fps, logger=None)
    video.close()
    final.close()
    
    return f"💧 Watermark added! Saved: {save_path}"


async def _op_audio_mix(video_path, save_path, audio_path, video_vol, audio_vol, loop_audio, fps, codec, audio_codec):
    """Mix background audio with video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    if not audio_path or not os.path.exists(audio_path):
        return f"🚨 Error: audio_path required for audio_mix operation"
    
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)
    
    if loop_audio and audio.duration < video.duration:
        audio = audio.loop(int(video.duration / audio.duration) + 1)
    audio = audio.subclipped(0, min(audio.duration, video.duration))
    audio = audio.with_volume_scaled(audio_vol)
    
    if video.audio:
        mixed = CompositeAudioClip([video.audio.with_volume_scaled(video_vol), audio])
    else:
        mixed = audio
    
    final = video.with_audio(mixed)
    final.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    video.close()
    audio.close()
    final.close()
    
    return f"🎵 Audio mixed! Saved: {save_path}"


async def _op_volume(video_path, save_path, volume, fps, codec, audio_codec):
    """Adjust video volume."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    if video.audio:
        video = video.with_audio(video.audio.with_volume_scaled(volume))
    video.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    video.close()
    
    return f"🔊 Volume set to {volume}x! Saved: {save_path}"


async def _op_mute(video_path, save_path, fps, codec):
    """Remove audio from video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path).without_audio()
    video.write_videofile(save_path, codec=codec, fps=fps, logger=None)
    video.close()
    
    return f"🔇 Audio removed! Saved: {save_path}"


async def _op_filter(video_path, save_path, effect, fps, codec, audio_codec):
    """Apply visual filter."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    
    if effect == "blackwhite":
        video = vfx.BlackAndWhite().apply(video)
    elif effect == "invert":
        video = vfx.InvertColors().apply(video)
    elif effect == "mirror_x":
        video = vfx.MirrorX().apply(video)
    elif effect == "mirror_y":
        video = vfx.MirrorY().apply(video)
    elif effect != "none":
        return f"🚨 Error: Unknown effect '{effect}'"
    
    video.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    video.close()
    
    return f"🎨 Filter '{effect}' applied! Saved: {save_path}"


async def _op_color(video_path, save_path, brightness, contrast, fps, codec, audio_codec):
    """Adjust brightness/contrast."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    if brightness != 1.0:
        video = vfx.MultiplyColor(factor=brightness).apply(video)
    if contrast != 1.0:
        video = vfx.Gamma(gamma=1/contrast if contrast > 0 else 1).apply(video)
    
    video.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    video.close()
    
    return f"🌈 Color adjusted! Saved: {save_path}"


async def _op_rotate(video_path, save_path, angle, fps, codec, audio_codec):
    """Rotate video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    if angle not in [90, 180, 270]:
        return "🚨 Error: angle must be 90, 180, or 270"
    
    video = VideoFileClip(video_path)
    video = vfx.Rotate(angle=angle).apply(video)
    video.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    video.close()
    
    return f"🔄 Rotated {angle}°! Saved: {save_path}"


async def _op_flip(video_path, save_path, direction, fps, codec, audio_codec):
    """Flip video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    if direction == "horizontal":
        video = vfx.MirrorX().apply(video)
    elif direction == "vertical":
        video = vfx.MirrorY().apply(video)
    else:
        return "🚨 Error: direction must be 'horizontal' or 'vertical'"
    
    video.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    video.close()
    
    return f"🪞 Flipped {direction}! Saved: {save_path}"


async def _op_crop(video_path, save_path, x1, y1, x2, y2, fps, codec, audio_codec):
    """Crop video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    w, h = video.size
    x2 = x2 if x2 is not None else w
    y2 = y2 if y2 is not None else h
    
    video = vfx.Crop(x1=x1, y1=y1, x2=x2, y2=y2).apply(video)
    video.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    video.close()
    
    return f"✂️ Cropped! Saved: {save_path}"


async def _op_resize(video_path, save_path, width, height, scale, fps, codec, audio_codec):
    """Resize video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    if scale:
        video = video.resized(scale)
    elif width and height:
        video = video.resized((width, height))
    elif width:
        video = video.resized(width=width)
    elif height:
        video = video.resized(height=height)
    else:
        return "🚨 Error: Provide width, height, or scale"
    
    new_w, new_h = video.size
    video.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    video.close()
    
    return f"📐 Resized to {new_w}x{new_h}! Saved: {save_path}"


async def _op_speed(video_path, save_path, speed, fps, codec, audio_codec):
    """Change playback speed."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    if speed <= 0:
        return "🚨 Error: speed must be greater than 0"
    
    video = VideoFileClip(video_path)
    video = vfx.MultiplySpeed(factor=speed).apply(video)
    dur = video.duration
    video.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    video.close()
    
    return f"⏩ Speed {speed}x! Duration: {dur:.1f}s. Saved: {save_path}"


async def _op_reverse(video_path, save_path, fps, codec, audio_codec):
    """Reverse video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    video = vfx.TimeMirror().apply(video)
    video.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    video.close()
    
    return f"⏪ Reversed! Saved: {save_path}"


async def _op_loop(video_path, save_path, loops, fps, codec, audio_codec):
    """Loop video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    if loops < 1:
        return "🚨 Error: loops must be at least 1"
    
    video = VideoFileClip(video_path)
    looped = video.loop(n=loops)
    dur = looped.duration
    looped.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    video.close()
    looped.close()
    
    return f"🔁 Looped {loops}x! Duration: {dur:.1f}s. Saved: {save_path}"


async def _op_gif(video_path, save_path, start, duration, fps, width):
    """Convert to GIF."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    end = start + duration if duration else video.duration
    video = video.subclipped(start, min(end, video.duration))
    if width:
        video = video.resized(width=width)
    
    if not save_path.endswith('.gif'):
        save_path += '.gif'
    video.write_gif(save_path, fps=fps, logger=None)
    
    file_size = os.path.getsize(save_path) / (1024 * 1024)
    video.close()
    
    return f"🎞️ GIF created! {file_size:.2f} MB. Saved: {save_path}"


async def _op_thumbnail(video_path, save_path, timestamp):
    """Extract frame."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    if timestamp > video.duration:
        return f"🚨 Error: timestamp exceeds video duration"
    
    video.save_frame(save_path, t=timestamp)
    video.close()
    
    return f"🖼️ Thumbnail at {timestamp}s! Saved: {save_path}"


async def _op_extract_audio(video_path, save_path, audio_codec, bitrate):
    """Extract audio."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    if not video.audio:
        video.close()
        return "🚨 Error: Video has no audio"
    
    video.audio.write_audiofile(save_path, codec=audio_codec, bitrate=bitrate, logger=None)
    file_size = os.path.getsize(save_path) / (1024 * 1024)
    video.close()
    
    return f"🎧 Audio extracted! {file_size:.2f} MB. Saved: {save_path}"


async def _op_pip(main_path, overlay_path, save_path, position, scale, start, fps, codec, audio_codec):
    """Picture-in-picture."""
    if not os.path.exists(main_path):
        return f"🚨 Error: Main video not found: {main_path}"
    if not overlay_path or not os.path.exists(overlay_path):
        return f"🚨 Error: overlay_video_path required for pip operation"
    
    main = VideoFileClip(main_path)
    overlay = VideoFileClip(overlay_path).resized(scale)
    
    margin = 20
    main_w, main_h = main.size
    ov_w, ov_h = overlay.size
    
    positions = {"bottom-right": (main_w - ov_w - margin, main_h - ov_h - margin),
                 "bottom-left": (margin, main_h - ov_h - margin),
                 "top-right": (main_w - ov_w - margin, margin),
                 "top-left": (margin, margin)}
    
    overlay = overlay.with_position(positions.get(position, positions["bottom-right"])).with_start(start)
    if overlay.duration > main.duration - start:
        overlay = overlay.subclipped(0, main.duration - start)
    
    final = CompositeVideoClip([main, overlay])
    final.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    main.close()
    overlay.close()
    final.close()
    
    return f"📺 PIP added! Saved: {save_path}"


async def _op_chroma_key(video_path, save_path, color_key, thr, fps, codec, audio_codec):
    """Remove background color (Chroma Key)."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    # vfx.mask_color defaults: color=[0,255,0] (green), thr=0, s=0
    # We allow hex or [R,G,B]
    
    # Simple hex to RGB conversion if needed, but mask_color expects RGB list
    if isinstance(color_key, str) and color_key.startswith("#"):
        h = color_key.lstrip('#')
        rgb = [int(h[i:i+2], 16) for i in (0, 2, 4)]
    elif color_key.lower() == "green":
        rgb = [0, 255, 0]
    elif color_key.lower() == "blue":
        rgb = [0, 0, 255]
    else:
        rgb = [0, 255, 0] # Default green
        
    masked_clip = vfx.MaskColor(color=rgb, threshold=thr, stiffness=0).apply(video)
    
    # We usually overlay this on something or just export as transparent (requires specific codec)
    # If no background provided, we just export. To keep transparency, use 'png' codec or similar?
    # Usually user wants to verify it works.
    # For transparency in mp4 (rare), usually we need mov with prores or just compose it.
    # Here we just apply the mask. If saved as mp4 h264, transparency becomes black.
    
    masked_clip.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    video.close()
    
    return f"🟢 Chroma Key applied (color={color_key})! Saved: {save_path}"


async def _op_subtitles(video_path, save_path, subtitles_path, font_size, font, color, fps, codec, audio_codec):
    """Burn subtitles into video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    if not subtitles_path or not os.path.exists(subtitles_path):
        return f"🚨 Error: Subtitles file not found: {subtitles_path}"
    
    video = VideoFileClip(video_path)
    
    def generator(txt):
        return TextClip(
            text=txt, 
            font=font, 
            font_size=font_size, 
            color=color, 
            bg_color='transparent',
            method='caption',
            size=(video.w * 0.9, None), # Wrap text
            text_align='center'
        )
    
    try:
        from moviepy.video.tools.subtitles import SubtitlesClip
        subs = SubtitlesClip(subtitles_path, make_textclip=generator)
        
        # Position subtitles at the bottom
        subs = subs.with_position(('center', 0.85), relative=True)
        
        final = CompositeVideoClip([video, subs])
        final.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
        
        video.close()
        final.close()
        return f"📝 Subtitles burned! Saved: {save_path}"
        
    except Exception as e:
        return f"🚨 Error adding subtitles: {str(e)}"


async def _op_remove_silence(video_path, save_path, threshold_db, min_len, fps, codec, audio_codec):
    """Remove silent segments from video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    if not video.audio:
        return "🚨 Error: Video has no audio to analyze"
    
    # Calculate volume chunks
    chunk_duration = 0.1 # 100ms chunks
    t_audio = np.arange(0, video.audio.duration, chunk_duration)
    
    def get_max_volume(t):
        # Scan a small window
        try:
            audio_chunk = video.audio.subclipped(t, t + chunk_duration)
            s = audio_chunk.to_soundarray()
            # Max amplitude
            max_amp = np.abs(s).max()
            # Convert to dB
            if max_amp == 0:
                return -100.0
            return 20 * np.log10(max_amp)
        except:
            return -100.0

    # This can be slow for long videos.
    # Faster approach: get entire sound array?
    # For robustness, we stick to moviepy handling or do coarse pass.
    # Let's use a simpler heuristic for shorter tool run:
    # We iterate and build 'keep' intervals.
    
    volumes = []
    # Optimization: iterate directly on soundarray if possible
    # But lazy loading is safer for memory.
    # Let's do 0.2s steps
    step = 0.2
    times = np.arange(0, video.duration, step)
    keep_segments = []
    current_segment_start = None
    
    # Pre-load audio to array (faster) if video < 10 mins?
    # video.audio.to_soundarray() might be huge.
    # We'll stick to iterating but maybe with larger steps? No, precision matters.
    
    # We will assume user knows what they are doing.
    # Let's try to be efficient:
    
    # Get max volume of audio
    max_vol = video.audio.max_volume()
    # If audio is normalized, 1.0 is max.
    
    # To properly implement this we need pydub or similar for speed, 
    # or just trust moviepy.
    # Let's try to use to_soundarray just for volume detection logic
    # getting array at low sample rate is fast.
    
    try:
        # 4000Hz is enough for volume envelope
        sound_array = video.audio.to_soundarray(fps=4000)
        # sound_array is [N, 2] (stereo)
        # Average channels
        mono = np.mean(np.abs(sound_array), axis=1)
        
        # Convert threshold dB to amplitude
        # db = 20 * log10(amp) => amp = 10^(db/20)
        threshold_amp = 10 ** (threshold_db / 20.0)
        
        # Identify speech segments
        is_speech = mono > threshold_amp
        
        # We need to buffer this to avoid chopping mid-word
        # Simple finite state machine
        
        clips = []
        fps_audio = 4000
        
        # Helper to convert indices to time
        def idx_to_time(idx): return idx / fps_audio
        
        # Group Trues
        # Use numpy diff to find edges
        # Pad with False to detect start/end
        is_speech_padded = np.concatenate(([False], is_speech, [False]))
        edges = np.diff(is_speech_padded.astype(int))
        starts = np.where(edges == 1)[0]
        ends = np.where(edges == -1)[0]
        
        # Now we have speech segments [start, end]
        # Merge if close (silence < min_len)
        merged_segments = []
        if len(starts) > 0:
            current_start = starts[0]
            current_end = ends[0]
            
            for i in range(1, len(starts)):
                next_start = starts[i]
                next_end = ends[i]
                
                silence_gap = idx_to_time(next_start - current_end)
                if silence_gap < min_len:
                    # Merge
                    current_end = next_end
                else:
                    merged_segments.append((current_start, current_end))
                    current_start = next_start
                    current_end = next_end
            merged_segments.append((current_start, current_end))
        
        # Build clips
        final_clips = []
        for start_idx, end_idx in merged_segments:
            start_t = idx_to_time(start_idx)
            end_t = idx_to_time(end_idx)
            # Add small buffer?
            final_clips.append(video.subclipped(max(0, start_t - 0.1), min(video.duration, end_t + 0.1)))
        
        if not final_clips:
            return "🚨 Error: No speech detected (or all silence)"
            
        final = concatenate_videoclips(final_clips)
        final.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
        
        video.close()
        final.close()
        return f"✂️ Removed {video.duration - final.duration:.1f}s of silence! Saved: {save_path}"
        
    except Exception as e:
        return f"🚨 Error in silence removal: {str(e)}"


async def _op_cut(video_path, save_path, start, end, fps, codec, audio_codec):
    """Extract a segment from video."""
    if not os.path.exists(video_path):
        return f"🚨 Error: Video not found: {video_path}"
    
    video = VideoFileClip(video_path)
    
    # Validate times
    if start < 0:
        start = 0
    if start >= video.duration:
        return f"🚨 Error: cut_start ({start}s) exceeds video duration ({video.duration:.1f}s)"
    
    if end is None:
        end = video.duration
    elif end > video.duration:
        end = video.duration
    
    if end <= start:
        return f"🚨 Error: cut_end ({end}s) must be greater than cut_start ({start}s)"
    
    # Extract the segment
    segment = video.subclipped(start, end)
    segment_duration = segment.duration
    
    segment.write_videofile(save_path, codec=codec, audio_codec=audio_codec, fps=fps, logger=None)
    
    video.close()
    segment.close()
    
    return f"✂️ Cut video from {start:.1f}s to {end:.1f}s ({segment_duration:.1f}s). Saved: {save_path}"
