# Changelog

## 2026-01-20 17:35
- **FIXED**: 500 Internal Server Error and resilience issues in `deep_research.py`
  - Implemented exponential backoff retries using `tenacity` for creation and polling
  - Enhanced error diagnostics for 500 (Server) and 429 (Quota) errors
  - Extended research timeout to 15 minutes for complex queries
  - Switched to asynchronous sleep for more efficient polling
- **REMOVED**: `src/nano_banana.py` (Fast image generation tool)
  - Successfully consolidated all image generation to `nano_banana_pro`
  - Updated `main.py` and `src/__init__.py` to remove deprecated imports
  - Refined project documentation to reflect pro-only engine

## 2026-01-13 21:30
- **FIXED**: `'NoneType' object is not iterable` error in `nano_banana_pro.py`
  - Added robust check for `response.parts` being `None` (usually due to safety filters)
  - Implemented detailed safety block reporting (reports specific categories and probabilities)
  - Added support for reporting other termination reasons (finish_reason)

## 2026-01-12 16:05
- **TASK**: Initiated creation of isometric cartoonish 3D Lottie animation
  - Goal: Generate 3D isometric image → Looping Veo video → Lottie JSON → Web implementation


## 2026-01-12 14:32
- **NEW TOOL**: Added `video_to_lottie.py` - Convert video to Lottie animation
  - Video → Frames → Lottie JSON with embedded base64 images
  - Optional loop mode with start-trim for seamless loops
  - Configurable FPS, width, and optimization

## 2026-01-12 13:40
- **ENHANCEMENT**: Added `cut` operation to `video_editor.py`
  - Extract video segments with `cut_start` and `cut_end` parameters

## 2026-01-12 10:48
- **ENHANCEMENT**: Updated `video_analyzer.py` to support multiple video inputs
  - New `video_paths` parameter accepts list of videos for comparison analysis

## 2026-01-10 15:20
- **MAJOR FEATURE**: Added `deep_research.py` - Deep Research Agent with Gemini 3 Pro
  - Autonomous multi-step research with web search and synthesis
  - Background execution with polling for long-running tasks
  - Customizable output formats (executive summary, technical report, etc.)

## 2026-01-10 14:49
- **MAJOR FEATURE**: Enhanced `video_editor.py` with 19 operations via single `operation` param:
  - `merge`, `text`, `watermark`, `audio_mix`, `volume`, `mute`
  - `filter`, `color`, `rotate`, `flip`, `crop`, `resize`
  - `speed`, `reverse`, `loop`, `gif`, `thumbnail`, `pip`
  - `chroma_key` (Green Screen), `subtitles` (SRT Burning), `remove_silence` (Auto-Cut)

## 2026-01-10 14:36
- **MAJOR FEATURE**: Added `video_analyzer.py` - Video understanding with Gemini
- **MAJOR FEATURE**: Added `doc_analyzer.py` - PDF analysis with Gemini

## 2026-01-10 14:30
- **MAJOR FEATURE**: Added `video_editor.py` - Video editing with MoviePy
- **New Capabilities**:
  - Merge multiple videos into one
  - Fade in/out transitions
  - Crossfade between clips
  - Trim clips (start/end times)
  - Speed adjustment
  - Resolution/FPS control
  - Codec & quality settings (bitrate, preset)
- Added `moviepy>=2.0.0` to requirements.txt
- Updated MCP server registration

## 2026-01-10 14:00
- **MAJOR FEATURE**: Added `veo_banana.py` - Video generation with Google Veo 3.1 API
- **New Capabilities**:
  - Text-to-video generation with native audio (8-second videos)
  - Image-to-video (use image as starting frame)
  - Reference images (up to 3 for subject preservation)
  - Frame interpolation (first + last frame control)
  - Video extension (add 7s, up to 20x)
  - 5 model versions (Veo 3.1, 3.1 Fast, 3.0, 3.0 Fast, 2.0)
  - Aspect ratios (16:9, 9:16), resolutions (720p, 1080p)
  - Duration settings (4, 5, 6, 8 seconds)
  - Negative prompts, person generation settings, seed
- Updated `src/__init__.py` to export `veo_banana`
- Updated `main.py` to register veo_banana with MCP server

## 2025-12-15 14:45
- **FIXED**: "Invalid trailing data" in Antigravity by forcing `newline='\n'` in `TextIOWrapper`
- **CHANGED**: Replaced `mcp.run()` with custom `anyio` loop to bypass default Windows CRLF behavior
- **IMPROVED**: Added comprehensive exception handling for the main server loop

## 2025-12-15 14:35
- **FIXED**: "Invalid trailing data" error in Antigravity/MCP on Windows
- **ADDED**: `msvcrt.setmode` to force binary mode on stdin/stdout (prevents CRLF translation)
- **IMPROVED**: Explicitly reconfigured `sys.stderr` for unbuffered output
- **REFINED**: Adjusted stdout redirection strategy to be more robust

## 2025-12-15 14:16
- **FIXED**: Critical stdout pollution causing "invalid trailing data" MCP error
- **CHANGED**: Extended stdout redirection scope in `main.py` to cover FastMCP initialization and tool registration
- **STABILITY**: Ensured strict separation of logging/debug output (stderr) and JSON-RPC transport (stdout)

## 2025-11-22 13:55
- **TEST**: Generated example image `helmet_no_bg.png` using `nano_banana_pro` with background removal
- **VERIFIED**: Confirmed tool functionality and output saving

## 2025-11-21 16:40
- **FIXED**: Added validation check for `image_size` in `nano_banana_pro.py` to prevent crashes on older SDKs
- **IMPROVED**: Added warning message when 4K resolution is requested but not supported by installed SDK
- **STABILITY**: Graceful fallback to default resolution instead of failing

## 2025-11-20 21:52
- **DEPLOYMENT READY**: Created Vercel HTTP bridge in `api/mcp.py`
- **CLEANED**: Removed all test files, extra MD docs, and example images
- **UPDATED**: Enhanced `.gitignore` with comprehensive __pycache__ patterns
- **UPDATED**: Refreshed `project_structure.md` to reflect clean production structure
- **ADDED**: `vercel.json` for Vercel deployment configuration
- **ADDED**: `requirements-vercel.txt` for serverless function dependencies
- Repository ready for GitHub and Vercel deployment

## 2025-11-20 21:42
- **REFACTORED**: `nano_banana_pro.py` now uses temporary files for background removal
- **OPTIMIZATION**: Only saves final transparent image to user's path (no double-write)
- **CLEANUP**: Automatic cleanup of temporary files after processing
- **MATCHING**: Flow now matches `nano_banana.py` pattern perfectly

## 2025-11-20 21:08
- **MAJOR FEATURE**: Added `nano_banana_pro.py` - Professional image generation with Gemini 3 Pro Image Preview
- **New Capabilities**:
  - 4K resolution support (1K, 2K, 4K image sizes)
  - Up to 14 reference images (6 objects + 5 humans for character consistency)
  - Google Search grounding for real-time data (weather, stocks, events)
  - Thinking mode with reasoning process visualization
  - Advanced text rendering for infographics, menus, diagrams
  - 10 aspect ratios (added 2:3, 3:2, 4:5, 5:4, 21:9)
- Updated `src/__init__.py` to export `nano_banana_pro`
- Updated `main.py` to register nano_banana_pro with MCP server
- Updated `docs/project_structure.md` with new file and enhanced formatting
- Created `docs/MODEL_COMPARISON.md` - Comprehensive comparison guide
- Created `docs/NANO_BANANA_PRO.md` - Quick reference and examples
- Model comparison: nano_banana (fast) vs nano_banana_pro (professional quality)
- File size: 295 lines (under 500-line limit ✅)

## 2025-11-18 20:34
- Initialized docs/ directory with changelog.md and project_structure.md
- Validated existing project structure
