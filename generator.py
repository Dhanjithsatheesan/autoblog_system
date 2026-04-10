import json
import logging
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY)

def generate_blog_post(topic):
    """
    Given a trending topic, orchestrates the generation of a full SEO-optimized
    blog post using the Groq API.
    Returns a dictionary containing 'title' and 'content' (HTML format).
    """
    logger.info(f"Generating blog post about: {topic}")
    
    import urllib.parse
    
    # We use a structured JSON prompt approach so we can easily parse out the title, image prompt, and content.
    system_prompt = """
    You are a Senior SEO Content Marketer and expert copywriter.
    Your task is to write a highly engaging, human-like, SEO-optimized blog post about the given topic.
    You must output valid JSON with three exact keys: "title", "image_prompt", and "html_content".
    
    Requirements for output:
    1. "title": A highly clickable, SEO-optimized long-tail title (max 60 characters). Emphasize user intent.
    2. "image_prompt": A highly detailed prompt string describing the perfect hero image for this article. Add stylistic descriptors (e.g., 'cinematic lighting, ultra-realistic', or 'flat vector art style', etc.) choosing whatever best matches the topic.
    3. "html_content": The body of the article formatted in rich HTML.
        - Must be 1000+ words.
        - The first paragraph MUST contain the main keyword and spark curiosity immediately.
        - Use appropriate heading tags (<h2>, <h3>) to break up sections. 
        - DO NOT use an <h1> tag in the body (the WordPress theme will handle the title as H1).
        - Maintain high semantic density (use LSI and related keywords naturally).
        - Use ultra-short paragraphs (2-3 sentences max) for high readability / low bounce rate.
        - Include bullet points or numbered lists dynamically.
        - Include an FAQ section at the end with 3-4 common long-tail questions (Schema friendly).
        - Use bold tags (`<strong>`) strategically to highlight important concepts to the skimmer.
        - Tone should be authoritative, engaging, and professional without using robotic fluff ("In today's fast-paced world...").
        
    IMPORTANT: ONLY return valid JSON. Example format:
    {
      "title": "Your SEO Title",
      "image_prompt": "A cinematic shot of a glowing AI neural network overlaying an office skyscraper, cyberpunk style",
      "html_content": "<p>Introduction here...</p><h2>Subheading</h2><p>Content...</p>"
    }
    """
    
    user_prompt = f"Topic: {topic}\nPlease write the complete blog post according to the system rules."
    
    try:
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        response_text = completion.choices[0].message.content
        if not response_text:
            logger.error("Empty response from Groq. Possibly blocked by safety filter.")
            return None
            
        logger.debug(f"Raw API Response: {response_text[:200]}...")
        
        import re
        # Find the first { and the last } to extract the JSON block
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not match:
            logger.error("No JSON block found in response.")
            return None
            
        clean_json = match.group(0)
        
        # Parse the JSON
        try:
            data = json.loads(clean_json)
        except json.JSONDecodeError as e:
            logger.error(f"JSON Parsing Error: {e} - Raw text: {clean_json[:100]}")
            return None
        
        title = data.get("title", f"Insightful take on {topic}")
        image_prompt = data.get("image_prompt", f"High quality stock photo about {topic}")
        html_content = data.get("html_content", "<p>Failed to generate content body.</p>")
        
        # Build the dynamic AI Image URL
        encoded_img_prompt = urllib.parse.quote(image_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_img_prompt}?width=1200&height=630&nologo=true"
        
        # Inject the image into the HTML content
        import requests
        try:
            # Quickly verify the image URL is alive without downloading the whole file
            img_response = requests.head(image_url, timeout=10)
            # Some services might return 405 for HEAD, so if it's 2xx or 3xx it's good. 
            # Or just assume it works if we don't get a connection error, but let's be strict:
            if img_response.status_code < 400 or img_response.status_code == 405:
                hero_image_html = f'<img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px; margin-bottom: 20px;">\n\n'
                final_content = hero_image_html + html_content
            else:
                logger.warning(f"Image generation returned status {img_response.status_code}. Skipping image.")
                final_content = html_content
        except Exception as e:
            logger.warning(f"Image generation failed: {e}. Skipping image.")
            final_content = html_content
        
        logger.info(f"Successfully generated post: '{title}' with dynamic image")
        return {
            "title": title,
            "content": final_content
        }
        
    except Exception as e:
        logger.error(f"Failed to generate blog post for topic '{topic}': {e}")
        return None

if __name__ == "__main__":
    # Test generation
    result = generate_blog_post("Artificial Intelligence in 2024")
    if result:
        print(f"Title: {result['title']}")
        print(f"Content length: {len(result['content'])} characters")
