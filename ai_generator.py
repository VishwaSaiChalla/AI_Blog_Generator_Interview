import os
from typing import Dict
# from mistralai import Mistral, UserMessage, SystemMessage
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client with GitHub models endpoint
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4.1-nano"
# client = Mistral(api_key=os.getenv("GITHUB_TOKEN"), server_url=endpoint)
client = OpenAI(
    base_url=endpoint,
    api_key="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"
)

def generate_blog_post(keyword: str, seo_data: Dict[str, float]) -> str:
    """
    Generate a blog post using GitHub Models API based on the keyword and SEO data.
    
    Args:
        keyword (str): The main keyword for the blog post
        seo_data (Dict[str, float]): SEO metrics for the keyword
        
    Returns:
        str: Generated blog post in Markdown format
    """
    # Construct the prompt
    prompt = f"""Write a comprehensive blog post about {keyword}. 
    The post should be informative, engaging, and optimized for SEO.
    
    SEO Metrics:
    - Search Volume: {seo_data['search_volume']}
    - Keyword Difficulty: {seo_data['keyword_difficulty']}
    - Average CPC: ${seo_data['avg_cpc']}
    
    Requirements:
    1. Include a compelling title
    2. Write an engaging introduction
    3. Include at least 3 main sections with subheadings
    4. Add a conclusion
    5. Include 3-5 affiliate link placeholders using {{AFF_LINK_n}} format
    6. Use proper Markdown formatting
    7. Keep the tone professional but conversational
    8. Include relevant statistics and data where appropriate
    
    Format the response in Markdown."""
    
    try:
        # Call GitHub Models API
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "developer",
                    "content": "You are a professional blog writer specializing in creating SEO-optimized content."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract and return the generated content
        blog_post = response.choices[0].message.content
        
        # Replace affiliate link placeholders with dummy URLs
       
        
        return blog_post
        
    except Exception as e:
        raise Exception(f"Error generating blog post: {str(e)}")