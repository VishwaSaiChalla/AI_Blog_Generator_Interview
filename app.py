from flask import Flask, jsonify, request, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
#import markdown
from dotenv import load_dotenv
from seo_fetcher import get_seo_data
from ai_generator import generate_blog_post

# Load environment variables
load_dotenv()

app = Flask(__name__)
									   

# Initialize scheduler
scheduler = BackgroundScheduler()

def generate_daily_post():
    """Function to generate a daily blog post with a predefined keyword"""
    keyword = "wireless earbuds"  # Predefined keyword
    try:
        seo_data = get_seo_data(keyword)
        blog_post = generate_blog_post(keyword, seo_data)
        
        # Save the generated post to a file
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"generated_posts/post_{timestamp}.md"
        os.makedirs("generated_posts", exist_ok=True)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(blog_post)
        
        print(f"Generated daily post for keyword: {keyword}")
    except Exception as e:
        print(f"Error generating daily post: {str(e)}")

@app.route('/')
def home():
    """Render the main page"""
    return render_template('index.html')															   

@app.route('/generate', methods=['GET'])
def generate_post():
    """Endpoint to generate a blog post for a given keyword"""
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "Keyword parameter is required"}), 400
    
    try:
																   
        # Get SEO data for the keyword
        seo_data = get_seo_data(keyword)
        
        # Generate blog post using AI
        blog_post = generate_blog_post(keyword, seo_data)

        # Convert Markdown to HTML
        # blog_post_html = markdown.markdown(blog_post, extensions=["fenced_code", "nl2br"])
																			   
        return jsonify({
            "keyword": keyword,
            "seo_data": seo_data,
            "blog_post": blog_post
        })
    except Exception as e:
															 
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start the scheduler
    scheduler.add_job(generate_daily_post, 'cron', hour=0)  # Run at midnight every day
    scheduler.start()
    
    # Create generated_posts directory if it doesn't exist
    os.makedirs("generated_posts", exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True)