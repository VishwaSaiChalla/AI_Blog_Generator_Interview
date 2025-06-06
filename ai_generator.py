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
    api_key=os.getenv("OPENAI_API_KEY")
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
    prompt = f"""Write an engaging and educational blog post about {keyword} that's perfect for learners and general audiences.
    
    SEO Metrics:
    - Search Volume: {seo_data['search_volume']}
    - Keyword Difficulty: {seo_data['keyword_difficulty']}
    - Average CPC: ${seo_data['avg_cpc']}
    
    Content Requirements:
    ### 1. Title Creation 
    Create a clear, compelling title that:
        - Accurately represents the content
        - Appeals to beginners and general audiences
        - Avoids clickbait or exaggeration
        - Incorporates the main keyword naturally

    ### 2. Introduction (2 paragraphs, ~5 lines each)
        - Start with a relatable hook or question
        - Clearly explain what the topic is in simple terms
        - Highlight why this matters to everyday readers
        - Give readers a clear idea of what they'll gain from reading

    ### 3. Main Content Structure 
    Instead of rigid sections, create a natural flow that might include:
        - **Simple explanations** using analogies and real-world comparisons
        - **Practical examples** that readers can relate to
        - **Step-by-step breakdowns** when explaining processes
        - **Common misconceptions** addressed clearly
        - **Benefits and challenges** explained in plain language
        - **Current trends** and why they matter
        - **Real-world applications** with specific examples

    *Note: Organize content based on what makes most sense for the topic, not a predetermined structure*

    ### 4. Future Outlook
        - Discuss emerging trends in accessible language
        - Explain potential challenges or opportunities
        - Help readers understand what to watch for

    ### 5. Conclusion
        - Summarize key takeaways in simple bullet points
        - Provide actionable next steps for interested readers
        - Include an engaging call-to-action

    ### 6. Sources (3-5 reputable sources)
    Research and verify each source link before including:
        - **Source Title**: Brief description (replacing {{AFF_LINK_n}} placeholders with dummy URLs.)
        - Prioritize authoritative, accessible sources
        - Ensure all links are functional and lead to relevant content

    ## Writing Guidelines:

        **Tone & Style:**
        - Conversational yet informative
        - Use "you" to address readers directly
        - Explain technical terms when first introduced
        - Include helpful analogies for complex concepts
        - Ask rhetorical questions to engage readers

        **Formatting:**
        - Use proper Markdown formatting
        - Break up text with relevant subheadings
        - Include bullet points for easy scanning
        - Bold key terms and important points
        - Use italics for emphasis sparingly

        **Content Quality:**
        - Target 700-900 words for comprehensive coverage
        - Include relevant statistics with proper context
        - Add practical tips or actionable insights
        - Ensure accuracy and avoid speculation
        - Make content shareable and bookmark-worthy

    ## Special Instructions:
        - If the keyword is ambiguous, choose the most commonly searched interpretation
        - Focus on providing genuine value to readers
        - Prioritize clarity over complexity
        - Include at least 2-3 data points or statistics where relevant
        - End with something memorable or thought-provoking

    **Return only the finished blog post content in Markdown format. Do not include meta-commentary or instructions."""

    #  (https://verified-working-link.com) for source to get actual URLs.
    
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

def check_connection():
    """
    Checks the connection to the OpenAI API by making a small request.
    """
    try:
        # Attempt a simple API call to verify connection
        # Using client.models.list() as a simple check
        client.models.list()
        return True
    except Exception as e:
        logger.error(f"Connection check failed: {str(e)}")
        return False

# Test connection on module load
if __name__ == "__main__":
    print("Testing OpenAI API connection...")
    if check_connection():
        print("Successfully connected to OpenAI API!")
    else:
        print("Failed to connect to OpenAI API. Please check your configuration.")