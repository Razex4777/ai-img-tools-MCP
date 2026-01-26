"""
Veo Banana - AI Video Generation Tool with Veo 3.1
Generate high-fidelity 8-second 720p/1080p videos with native audio using Google's Veo 3.1 API.
Features: Text-to-video, image-to-video, reference images, frame interpolation, video extension.
"""

import os
import time
import asyncio
from typing import Optional, List
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO


# Configure API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Google GenAI client
client = None
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)


# Model constants
VALID_MODELS = [
    "veo-3.1-generate-preview",      # Latest, best quality, 720p/1080p
    "veo-3.1-fast-generate-preview", # Fast version optimized for speed
    "veo-3.0-generate-001",          # Stable Veo 3
    "veo-3.0-fast-generate-001",     # Fast Veo 3
    "veo-2.0-generate-001",          # Legacy Veo 2
]

VALID_ASPECT_RATIOS = ["16:9", "9:16"]
VALID_RESOLUTIONS = ["720p", "1080p"]
VALID_PERSON_GENERATION = ["allow_all", "allow_adult", "dont_allow"]


async def veo_banana(
    prompt: str,
    negative_prompt: Optional[str] = None,
    model: str = "veo-3.1-generate-preview",
    first_frame: Optional[str] = None,
    last_frame: Optional[str] = None,
    reference_images: Optional[List[str]] = None,
    extend_video: Optional[str] = None,
    aspect_ratio: str = "16:9",
    resolution: str = "720p",
    duration_seconds: Optional[int] = None,
    person_generation: str = "allow_adult",
    seed: Optional[int] = None,
    save_path: Optional[str] = None,
    loop_mode: bool = False,
) -> str:
    """
    🎬 VEO BANANA - Professional AI Video Generation with Veo 3.1!
    
    Generate stunning 8-second 720p/1080p videos with native audio using Google's 
    state-of-the-art Veo 3.1 model. Supports text-to-video, image-to-video, 
    reference images, frame interpolation, and video extension.
    
    Args:
        prompt: Detailed video description. Include dialogue in quotes, sound effects,
                camera movements, and visual details.
                Examples:
                - "Drone shot following a red convertible along a coastal road at sunset"
                - '"This must be the key," he murmured, examining the ancient artifact'
                - "Cinematic close-up of a snow leopard, shallow depth of field"
        
        negative_prompt: Elements to avoid in the video (optional).
                        Use descriptive words, NOT instructive language.
                        ✅ Good: "cartoon, drawing, low quality, blurry"
                        ❌ Bad: "no walls, don't show faces"
        
        model: Veo model version to use:
               - "veo-3.1-generate-preview" (default) - Best quality, 720p/1080p
               - "veo-3.1-fast-generate-preview" - Optimized for speed
               - "veo-3.0-generate-001" - Stable Veo 3
               - "veo-3.0-fast-generate-001" - Fast Veo 3
               - "veo-2.0-generate-001" - Legacy (no audio)
        
        first_frame: Path to an image to use as the starting frame.
                    The video will animate from this image.
                    Example: "start_image.png"
        
        last_frame: Path to an image for the ending frame (interpolation mode).
                   Requires first_frame to also be set.
                   Creates a video that transitions between first and last frames.
                   Example: "end_image.png"
        
        reference_images: List of up to 3 image paths to guide video content.
                         Used for subject/asset preservation.
                         Example: ["person.png", "dress.png", "sunglasses.png"]
        
        extend_video: Path to a previously generated Veo video to extend.
                     Adds 7 seconds to the video (can be extended up to 20 times).
                     Input must be:
                     - Veo-generated video only
                     - Max 141 seconds long
                     - 720p resolution
                     - 16:9 or 9:16 aspect ratio
        
        aspect_ratio: Video dimensions:
                     - "16:9" (default) - Widescreen landscape
                     - "9:16" - Vertical/portrait
        
        resolution: Output quality:
                   - "720p" (default) - Standard HD
                   - "1080p" - Full HD (Veo 3.1 only)
        
        duration_seconds: Video length (4, 5, 6, or 8 seconds).
                         Availability depends on model and mode.
                         Default varies by configuration.
        
        person_generation: Person content filtering:
                          - "allow_all" - Allow all person content
                          - "allow_adult" (default) - Adults only
                          - "dont_allow" - No persons
                          Note: EU/UK regions may have restrictions
        
        seed: Optional seed for slight determinism improvement.
              Does not guarantee identical results but can help.
        
        save_path: Path to save the generated video.
                  If not provided, saves as "veo_output.mp4" in current directory.
                  Example: "C:/videos/my_video.mp4"
        
        loop_mode: Enable seamless loop generation.
                  When True:
                  - Requires first_frame to be set
                  - Auto-sets last_frame = first_frame (same image)
                  - Appends "seamless loop, dolly in camera slow" to prompt
                  Default: False
                  Tip: Use video_to_lottie with loop_trim_start=0.5 after generation
    
    Returns:
        Success message with video details and save location, or error details
    
    Examples:
        # Basic text-to-video with cinematic realism
        veo_banana(
            prompt="Drone shot following a classic red convertible driven by a man "
                   "along a winding coastal road at sunset, waves crashing against "
                   "the rocks below. The convertible accelerates fast and the engine "
                   "roars loudly.",
            save_path="coastal_drive.mp4"
        )
        
        # Text-to-video with dialogue
        veo_banana(
            prompt='A young woman, brown medium length hair, "This must be the key," '
                   'she murmured, and picks up a golden key from an ancient wooden chest.',
            aspect_ratio="16:9",
            resolution="1080p"
        )
        
        # Image-to-video (animate an image)
        veo_banana(
            prompt="Panning wide shot of a calico kitten sleeping in the sunshine",
            first_frame="kitten.png",
            save_path="animated_kitten.mp4"
        )
        
        # Frame interpolation (first and last frame)
        veo_banana(
            prompt="A ghostly woman on a swing slowly fades away into fog",
            first_frame="ghost_start.png",
            last_frame="empty_swing.png"
        )
        
        # Reference images for subject preservation
        veo_banana(
            prompt="A woman in a pink flamingo dress walks through a lagoon",
            reference_images=["woman.png", "dress.png", "sunglasses.png"]
        )
        
        # Extend an existing video
        veo_banana(
            prompt="The butterfly lands on an orange flower. A puppy runs up.",
            extend_video="butterfly_video.mp4"
        )
        
        # Fast generation for testing
        veo_banana(
            prompt="A majestic lion walking in the savannah",
            model="veo-3.1-fast-generate-preview",
            negative_prompt="cartoon, drawing, low quality"
        )
        
        # Seamless loop generation
        veo_banana(
            prompt="Synthwave grid tunnel",
            first_frame="grid.png",
            loop_mode=True,  # Auto-sets last_frame = first_frame
            save_path="loop.mp4"
        )
    """
    if not GOOGLE_API_KEY:
        return "🚨 Error: GOOGLE_API_KEY environment variable is not set"
    
    try:
        # Validate model
        if model not in VALID_MODELS:
            return f"🚨 Error: Invalid model '{model}'. Must be one of {VALID_MODELS}"
        
        # Validate aspect ratio
        if aspect_ratio not in VALID_ASPECT_RATIOS:
            return f"🚨 Error: Invalid aspect_ratio '{aspect_ratio}'. Must be one of {VALID_ASPECT_RATIOS}"
        
        # Validate resolution
        if resolution not in VALID_RESOLUTIONS:
            return f"🚨 Error: Invalid resolution '{resolution}'. Must be one of {VALID_RESOLUTIONS}"
        
        # Resolution 1080p only supported by Veo 3.1
        if resolution == "1080p" and "veo-3.1" not in model:
            return f"🚨 Error: 1080p resolution is only supported by Veo 3.1 models"
        
        # Validate person_generation
        if person_generation not in VALID_PERSON_GENERATION:
            return f"🚨 Error: Invalid person_generation '{person_generation}'. Must be one of {VALID_PERSON_GENERATION}"
        
        # Validate duration_seconds if provided
        valid_durations = [4, 5, 6, 8]
        if duration_seconds is not None and duration_seconds not in valid_durations:
            return f"🚨 Error: Invalid duration_seconds '{duration_seconds}'. Must be one of {valid_durations}"
        
        # Validate last_frame requires first_frame
        if last_frame and not first_frame:
            return "🚨 Error: last_frame requires first_frame to be set for interpolation mode"
        
        # Validate reference images count
        if reference_images and len(reference_images) > 3:
            return "🚨 Error: Maximum 3 reference images allowed"
        
        # Handle loop mode
        if loop_mode:
            if not first_frame:
                return "🚨 Error: loop_mode requires first_frame to be set"
            # Auto-set last_frame to same as first_frame
            last_frame = first_frame
            # Append loop keywords to prompt
            prompt = f"{prompt}, seamless loop, dolly in camera slow"
        
        # Build generation parameters
        image_input = None
        video_input = None
        config_params = {}
        
        # Process first frame (image input)
        if first_frame:
            if not os.path.exists(first_frame):
                return f"🚨 Error: First frame image not found at {first_frame}"
            try:
                img = Image.open(first_frame)
                # Convert to PNG bytes for the API
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                image_input = types.Image(
                    image_bytes=buffer.getvalue(),
                    mime_type="image/png"
                )
            except Exception as e:
                return f"🚨 Error loading first frame image: {str(e)}"
        
        # Process last frame (for interpolation)
        if last_frame:
            if not os.path.exists(last_frame):
                return f"🚨 Error: Last frame image not found at {last_frame}"
            try:
                img = Image.open(last_frame)
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                config_params["last_frame"] = types.Image(
                    image_bytes=buffer.getvalue(),
                    mime_type="image/png"
                )
            except Exception as e:
                return f"🚨 Error loading last frame image: {str(e)}"
        
        # Process reference images
        if reference_images:
            ref_image_configs = []
            for ref_path in reference_images:
                if not os.path.exists(ref_path):
                    return f"🚨 Error: Reference image not found at {ref_path}"
                try:
                    img = Image.open(ref_path)
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    ref_image_configs.append(
                        types.VideoGenerationReferenceImage(
                            image=types.Image(
                                image_bytes=buffer.getvalue(),
                                mime_type="image/png"
                            ),
                            reference_type="asset"
                        )
                    )
                except Exception as e:
                    return f"🚨 Error loading reference image {ref_path}: {str(e)}"
            config_params["reference_images"] = ref_image_configs
        
        # Process video extension
        if extend_video:
            if not os.path.exists(extend_video):
                return f"🚨 Error: Video to extend not found at {extend_video}"
            try:
                with open(extend_video, "rb") as f:
                    video_bytes = f.read()
                video_input = types.Video(video_bytes=video_bytes)
            except Exception as e:
                return f"🚨 Error loading video to extend: {str(e)}"
        
        # Build config
        config_params["aspect_ratio"] = aspect_ratio
        config_params["resolution"] = resolution
        config_params["person_generation"] = person_generation
        
        if negative_prompt:
            config_params["negative_prompt"] = negative_prompt
        
        if duration_seconds:
            config_params["duration_seconds"] = duration_seconds
        
        if seed is not None:
            config_params["seed"] = seed
        
        # Create config
        config = types.GenerateVideosConfig(**config_params)
        
        # Build generation parameters
        gen_params = {
            "model": model,
            "prompt": prompt,
            "config": config,
        }
        
        if image_input:
            gen_params["image"] = image_input
        
        if video_input:
            gen_params["video"] = video_input
        
        # Start video generation (async operation)
        result_parts = [
            "🎬 Veo Banana - Video Generation Started!",
            f"📺 Model: {model}",
            f"📐 Aspect Ratio: {aspect_ratio}",
            f"🎨 Resolution: {resolution}",
        ]
        
        if first_frame:
            result_parts.append(f"🖼️ First Frame: {os.path.basename(first_frame)}")
        if last_frame:
            result_parts.append(f"🖼️ Last Frame: {os.path.basename(last_frame)}")
        if reference_images:
            result_parts.append(f"📎 Reference Images: {len(reference_images)}")
        if extend_video:
            result_parts.append(f"➕ Extending Video: {os.path.basename(extend_video)}")
        if negative_prompt:
            result_parts.append(f"🚫 Negative Prompt: {negative_prompt[:50]}...")
        
        result_parts.append("")
        result_parts.append("⏳ Starting generation (this may take 11 seconds to 6 minutes)...")
        
        # Call the API
        operation = client.models.generate_videos(**gen_params)
        
        # Poll for completion
        poll_count = 0
        max_polls = 60  # ~10 minutes max (10s intervals)
        
        while not operation.done and poll_count < max_polls:
            poll_count += 1
            result_parts.append(f"⏳ Polling... ({poll_count * 10}s elapsed)")
            await asyncio.sleep(10)
            operation = client.operations.get(operation)
        
        if not operation.done:
            return "🚨 Error: Video generation timed out after 10 minutes"
        
        # Check for errors
        if hasattr(operation, 'error') and operation.error:
            return f"🚨 Error in video generation: {operation.error}"
        
        # Process results
        if not hasattr(operation, 'response') or not operation.response:
            return "🚨 Error: No response from video generation"
        
        if not hasattr(operation.response, 'generated_videos') or not operation.response.generated_videos:
            return "🚨 Error: No videos in response"
        
        generated_video = operation.response.generated_videos[0]
        
        # Determine save path
        actual_save_path = save_path or "veo_output.mp4"
        if not actual_save_path.endswith(".mp4"):
            actual_save_path += ".mp4"
        
        # Auto-create parent directory
        parent_dir = os.path.dirname(actual_save_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        # Download and save the video
        client.files.download(file=generated_video.video)
        generated_video.video.save(actual_save_path)
        
        result_parts.append("")
        result_parts.append("✅ Video generation complete!")
        result_parts.append(f"💾 Saved to: {actual_save_path}")
        
        # Get file size
        if os.path.exists(actual_save_path):
            file_size = os.path.getsize(actual_save_path)
            if file_size > 1024 * 1024:
                result_parts.append(f"📦 File size: {file_size / (1024 * 1024):.2f} MB")
            else:
                result_parts.append(f"📦 File size: {file_size / 1024:.2f} KB")
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"🚨 Error in veo_banana: {str(e)}"
