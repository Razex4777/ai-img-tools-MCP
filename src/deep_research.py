"""
Deep Research - AI Research Agent with Gemini
Performs complex, long-running research tasks using the Gemini Deep Research Agent.
Produces detailed, cited reports from web and file sources.
"""

import os
import time
from typing import Optional
from google import genai
from google.genai import errors
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    RetryError
)


# Configure API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Google GenAI client
client = None
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)


# Agent name for Deep Research
DEEP_RESEARCH_AGENT = "deep-research-pro-preview-12-2025"


def is_retryable_error(exception):
    """Check if the exception is a transient API error that should be retried."""
    if isinstance(exception, errors.APIError):
        # Retry on 5xx (Server) and 429 (Rate Limit) errors
        return exception.status_code in [429, 500, 502, 503, 504]
    return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=20),
    retry=retry_if_exception(is_retryable_error),
    reraise=True
)
def _create_research_interaction(research_input: str):
    """Internal helper to create interaction with retries."""
    return client.interactions.create(
        input=research_input,
        agent=DEEP_RESEARCH_AGENT,
        background=True
    )


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception(is_retryable_error),
    reraise=True
)
def _get_interaction_status(interaction_id: str):
    """Internal helper to get interaction status with retries."""
    return client.interactions.get(interaction_id)


async def deep_research(
    query: str,
    output_format: Optional[str] = None,
    poll_interval: int = 10,
) -> str:
    """
    🔬 DEEP RESEARCH - AI Research Agent with Gemini!
    
    Perform complex, long-running research tasks using the Gemini Deep Research Agent.
    The agent autonomously plans, searches, reads, and synthesizes multi-step research
    to produce detailed, cited reports.
    
    This is an agentic workflow - a single request triggers an autonomous loop of
    planning, searching, reading, and reasoning. Research tasks can take several
    minutes to complete.
    
    Args:
        query: Your research topic or question.
               Be specific and detailed for better results.
               Examples:
               - "Research the history of Google TPUs"
               - "Compare the latest AI models from OpenAI, Google, and Anthropic"
               - "Analyze the current state of quantum computing and its applications"
               - "Research best practices for building scalable microservices"
        
        output_format: Optional formatting instructions for the report.
                      Examples:
                      - "executive summary with bullet points"
                      - "technical deep-dive with code examples"
                      - "casual blog post style"
                      - "structured report with sections: Overview, Key Players, Trends, Conclusion"
        
        poll_interval: How often to check for completion (seconds).
                      Default: 10 seconds
                      Minimum: 5 seconds
    
    Returns:
        Detailed research report with citations, or error message
    
    Examples:
        # Basic research
        deep_research(
            query="Research the evolution of transformer architectures in NLP"
        )
        
        # Formatted report
        deep_research(
            query="Analyze the impact of AI on healthcare",
            output_format="executive summary for non-technical stakeholders"
        )
        
        # Technical deep-dive
        deep_research(
            query="Compare WebAssembly vs JavaScript performance",
            output_format="technical report with benchmarks and code examples"
        )
    """
    if not GOOGLE_API_KEY:
        return "🚨 Error: GOOGLE_API_KEY environment variable is not set"
    
    try:
        # Validate inputs
        if not query:
            return "🚨 Error: query is required"
        
        if poll_interval < 5:
            poll_interval = 5
        
        result_parts = [
            "🔬 Deep Research - Starting Research Task!",
            f"📋 Query: {query[:100]}{'...' if len(query) > 100 else ''}",
        ]
        
        # Build the research prompt
        research_input = query
        if output_format:
            research_input = f"{query}\n\nOutput format: {output_format}"
            result_parts.append(f"📝 Format: {output_format}")
        
        result_parts.append("")
        result_parts.append("🚀 Starting autonomous research agent...")
        result_parts.append("⏳ This may take several minutes...")
        
        try:
            # Start the research task in background mode with retries
            interaction = _create_research_interaction(research_input)
        except Exception as e:
            if isinstance(e, errors.APIError):
                error_detail = ""
                if e.status_code == 500:
                    error_detail = "\n(Internal Server Error - This is a known issue with the preview agent. Retrying did not help.)"
                elif e.status_code == 429:
                    error_detail = "\n(Quota Exceeded - Please check your API usage limits.)"
                return f"🚨 API Error ({e.status_code}): {e.message}{error_detail}"
            return f"🚨 Error creating research task: {str(e)}"
        
        result_parts.append(f"🔑 Research ID: {interaction.id}")
        
        # Poll for results
        start_time = time.time()
        import asyncio
        while True:
            try:
                interaction = _get_interaction_status(interaction.id)
            except Exception as e:
                # If polling fails consistently, we report it but keep trying for a bit
                result_parts.append(f"⚠️ Polling warning: {str(e)}")
                await asyncio.sleep(poll_interval)
                continue
            
            if interaction.status == "completed":
                elapsed = time.time() - start_time
                result_parts.append(f"⏱️ Completed in {elapsed:.1f} seconds")
                result_parts.append("")
                result_parts.append("✅ Research complete!")
                result_parts.append("")
                result_parts.append("📝 **Research Report:**")
                result_parts.append("")
                
                # Get the final output
                if interaction.outputs:
                    result_parts.append(interaction.outputs[-1].text)
                else:
                    result_parts.append("No output generated.")
                break
                
            elif interaction.status == "failed":
                error_msg = getattr(interaction, 'error', 'Unknown error')
                return f"🚨 Research failed: {error_msg}. Interaction ID: {interaction.id}"
            
            # Still in progress
            elapsed = time.time() - start_time
            if elapsed > 900:  # 15 minute timeout (extended from 10)
                return f"🚨 Research timed out after 15 minutes. Interaction ID: {interaction.id}"
            
            await asyncio.sleep(poll_interval)
        
        return "\n".join(result_parts)
        
    except Exception as e:
        return f"🚨 Error in deep_research: {str(e)}"
