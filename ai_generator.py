import os
from typing import Dict
# from mistralai import Mistral, UserMessage, SystemMessage
from openai import OpenAI
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    1.Title : Create a compelling, specific, and relevant blog title. Avoid exaggeration or hallucination.
    2.Introduction : Write two paragraphs (about 5 lines each) that:
    - Introduce the topic clearly
    - Explain why it matters today
    - Briefly preview what the reader will learn

    3.Main Content : Organize the blog using 4 sections with relevant subheadings. Use this flow where applicable (adapt based on topic):
    - A bit of background or how the topic originated
    - Why it's important or trending right now
    - Some real-world examples or use cases

    4.What’s next: future trends, challenges, or innovations

    5.Conclusion : Wrap up by summarizing key ideas and offering final thoughts or a call-to-action.

    6.Sources : List 3–5 reputable sources used. Format:
    - Source Title: (https://link.com)

    7.Formatting Guidelines:
    - Use proper Markdown (#, ##, **bold**, *italic*, bullet points, etc.)

    8.Keep tone professional, conversational, and educational

    9.Word count: 600–800 words

    10.If possible, include stats or data points to strengthen the blog

    If the topic is unclear, make a reasonable assumption and proceed.

    Only return the blog content. Do not include any assistant instructions or commentary."""
    
    try:
        logger.info(f"Generating blog post for keyword: {keyword}")
        
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
        logger.info(f"Successfully generated blog post for keyword: {keyword}")
        
        # Replace affiliate link placeholders with dummy URLs
       
        
        return blog_post
        
    except Exception as e:
        logger.error(f"Error generating blog post: {str(e)}")
        raise Exception(f"Error generating blog post: {str(e)}")

# Test connection on module load
if __name__ == "__main__":
    print("Testing OpenAI API connection...")
    if check_connection():
        print("Successfully connected to OpenAI API!")
    else:
        print("Failed to connect to OpenAI API. Please check your configuration.")