"""
Document Analyzer - AI Document Understanding with Gemini
Analyze PDFs and documents using Gemini's native vision capabilities.
Supports multiple files, structured output, and complex document layouts.
"""

import os
from typing import List, Optional
from google import genai
from google.genai import types


# Configure API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Google GenAI client
client = None
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)


async def doc_analyzer(
    file_paths: List[str],
    prompt: str,
) -> str:
    """
    📄 DOC ANALYZER - AI Document Understanding with Gemini!
    
    Analyze PDFs and documents using Gemini's native vision capabilities.
    Goes beyond text extraction to understand charts, tables, diagrams, and layouts.
    Uses the state-of-the-art Gemini 3 Flash Preview model.
    
    Args:
        file_paths: List of paths to PDF files to analyze.
                   Supports up to 50MB per file and 1000 pages total.
                   Example: ["report.pdf"] or ["doc1.pdf", "doc2.pdf"]
        
        prompt: Your question or task for the document(s).
                Examples:
                - "Summarize the key findings"
                - "Extract all tables as JSON"
                - "What are the main conclusions?"
                - "Compare these two documents"
                - "List all action items"
                - "Transcribe this document to HTML"
    
    Returns:
        Analysis result from Gemini, or error message
    """
    if not GOOGLE_API_KEY:
        return "🚨 Error: GOOGLE_API_KEY environment variable is not set"
    
    try:
        # Validate inputs
        if not file_paths:
            return "🚨 Error: file_paths cannot be empty"
        
        if not prompt:
            return "🚨 Error: prompt is required"
        
        # Validate all files exist and are PDFs
        for path in file_paths:
            if not os.path.exists(path):
                return f"🚨 Error: File not found: {path}"
            
            ext = os.path.splitext(path)[1].lower()
            if ext != ".pdf":
                return f"🚨 Error: Only PDF files are supported. Got: {path}"
        
        result_parts = [
            "📄 Doc Analyzer - Processing Started!",
            f"📁 Files: {len(file_paths)}",
        ]
        
        # Build content parts
        content_parts = []
        total_size = 0
        
        for path in file_paths:
            file_size = os.path.getsize(path)
            file_size_mb = file_size / (1024 * 1024)
            total_size += file_size
            
            # Use pathlib for safe Unicode path handling
            from pathlib import Path
            file_path = Path(path)
            safe_filename = file_path.name
            
            result_parts.append(f"   📑 {safe_filename} ({file_size_mb:.2f} MB)")
            
            # Check file size limit (50MB per file)
            if file_size_mb > 50:
                return f"🚨 Error: File {safe_filename} exceeds 50MB limit"
            
            # Always use Files API for PDFs (more reliable for vision tasks)
            result_parts.append(f"      📤 Uploading via Files API...")
            
            # Read file as bytes to avoid encoding issues with paths
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Upload using bytes with explicit mime type
            import io
            uploaded_file = client.files.upload(
                file=io.BytesIO(file_content),
                config={"mime_type": "application/pdf", "display_name": safe_filename}
            )
            
            # Wait for file to be processed
            import time
            while uploaded_file.state.name == "PROCESSING":
                time.sleep(1)
                uploaded_file = client.files.get(name=uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                return f"🚨 Error: Document processing failed for {safe_filename}"
            
            # Create Part from uploaded file
            content_parts.append(
                types.Part.from_uri(
                    file_uri=uploaded_file.uri,
                    mime_type=uploaded_file.mime_type or "application/pdf"
                )
            )

        
        # Add the prompt
        content_parts.append(types.Part(text=prompt))
        
        total_size_mb = total_size / (1024 * 1024)
        result_parts.append(f"📦 Total size: {total_size_mb:.2f} MB")
        result_parts.append("")
        result_parts.append("🔍 Analyzing document(s)...")
        
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
        return f"🚨 Error in doc_analyzer: {str(e)}"
