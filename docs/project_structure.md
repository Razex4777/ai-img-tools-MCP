# Project Structure

## Overview
AI Image Tools - Professional MCP server for AI-powered image generation and processing.
Professional Gemini 3 Pro Image model with 4K, Google Search, and Thinking mode.

## 🌳 Directory Tree
```text
ai-image-tools/
├── 📁 docs/                  # Documentation and changelogs
│   ├── 📄 changelog.md       # History of all changes and features
│   └── 📄 project_structure.md # Current architecture (this file)
├── 📁 src/                   # Core application source code
│   ├── 📄 batch_icon_generator.py # Batch processing for icons
│   ├── 📄 deep_research.py   # AI Research Agent with Gemini 3 Pro
│   ├── 📄 doc_analyzer.py    # PDF and document understanding
│   ├── 📄 icon_generator.py  # SVG icon generation tool
│   ├── 📄 nano_banana_pro.py # Pro image generation (3 Pro)
│   ├── 📄 svg_converter.py   # Image to SVG conversion
│   ├── 📄 veo_banana.py      # AI Video generation (Veo 3.1)
│   ├── 📄 video_analyzer.py  # Video analysis and search
│   ├── 📄 video_editor.py    # Main dispatcher for video operations
│   ├── 📄 video_to_lottie.py # Video to Lottie JSON converter
│   └── 📄 __init__.py        # Logic and tool registration
├── 📄 .gitignore             # Git exclusion rules
├── 📄 check_version.py       # Version check utility
├── 📄 main.py                # Local MCP server entry point
├── 📄 mcp_conf.json          # MCP server configuration
├── 📄 pyproject.toml         # Build system and metadata
├── 📄 README.md              # Project overview and usage
├── 📄 reproduce_issue.py     # Script to reproduce current errors
├── 📄 requirements.txt       # Production dependencies
├── 📄 uv.lock                # Dependency lock file
└── 📄 vercel.json            # Vercel manifest
```

## 🏗️ Architecture Summary
- **Main Server**: `main.py` provides the stdio-based MCP interface.
- **Image Engine**: `nano_banana_pro` (Professional/4K/NSFW-Optimized).
- **Video Stack**: `veo_banana` (Generation), `video_editor` (Processing), `video_to_lottie` (Export).
- **Intelligence**: `deep_research` (Agentic Search), `video_analyzer` (Visual Understanding).
- **Deployment**: Configured for both local usage and Vercel serverless functions.
