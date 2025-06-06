from flask import Flask, jsonify, request, render_template, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import os
import markdown
from dotenv import load_dotenv
from seo_fetcher import get_seo_data
from ai_generator import generate_blog_post
import json
import re # Import re for robust sanitization


# Load environment variables
load_dotenv()

app = Flask(__name__)

# Directory for storing generated posts and reviews
GENERATED_POSTS_DIR = "generated_posts"
REVIEWS_DIR = "reviews"
BLOG_POSTS_DB = "blog_posts_db.json" # JSON file for key-value storage

# Ensure directories exist
os.makedirs(GENERATED_POSTS_DIR, exist_ok=True)
os.makedirs(REVIEWS_DIR, exist_ok=True)

# Helper functions for JSON database
def load_blog_posts():
    """Loads blog posts from the JSON database file."""
    if not os.path.exists(BLOG_POSTS_DB):
        return {}
    try:
        with open(BLOG_POSTS_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading blog posts database {BLOG_POSTS_DB}: {str(e)}")
        return {}

def save_blog_posts(posts_data):
    """Saves blog posts to the JSON database file."""
    try:
        with open(BLOG_POSTS_DB, 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, indent=4)
    except Exception as e:
        print(f"Error saving blog posts database {BLOG_POSTS_DB}: {str(e)}")

def sanitize_keyword(keyword):
    """Sanitizes keyword for use as a filename and dictionary key."""
    # Replace spaces and potential path separators with hyphens, make lowercase
    sanitized = keyword.lower().replace(' ', '-')
    # Remove any characters that are not alphanumeric or hyphen
    sanitized = re.sub(r'[^a-z0-9-]', '', sanitized)
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')
    # Replace multiple hyphens with a single hyphen
    sanitized = re.sub(r'-+', '-', sanitized)
    
    if not sanitized:
        return "generated-post" # Fallback if keyword sanitizes to empty
    return sanitized

def extract_title_from_markdown(markdown_content):
    """Extracts the H1 title from markdown content, or returns a default."""
    if not markdown_content:
        return "Untitled Post"
        
    lines = markdown_content.strip().split('\n')
    for line in lines[:15]: # Check first 15 lines for performance
        if line.strip().startswith('# '):
            return line.strip()[2:].strip() # Remove '# ' and whitespace
            
    return "Untitled Post" # Return default if no H1 found

# Initialize scheduler
scheduler = BackgroundScheduler()

def generate_daily_post():
    """Function to generate a daily blog post with a predefined keyword"""
    keyword = "wireless earbuds"  # Predefined keyword
    try:
        seo_data = get_seo_data(keyword)
        blog_post = generate_blog_post(keyword, seo_data)

        sanitized_keyword = sanitize_keyword(keyword)
        
        # Load existing posts, add/update the new post, and save
        posts_data = load_blog_posts()
        posts_data[sanitized_keyword] = blog_post
        save_blog_posts(posts_data)

        print(f"Generated daily post for keyword: {keyword}")
    except Exception as e:
        print(f"Error generating daily post: {str(e)}")

@app.route('/')
def home():
    """Render the main page with a list of blog posts"""
    posts_data = load_blog_posts()
    posts = []
    # Sort keywords by descending order to show latest first (assuming newer keywords are added later)
    sorted_keywords = sorted(posts_data.keys(), reverse=True)

    for keyword in sorted_keywords:
        content = posts_data[keyword]
        title = extract_title_from_markdown(content)

        # If no H1 found, use keyword as title
        if title == "Untitled Post":
             title = keyword.replace("-", " ").replace("_", " ")

        posts.append({'filename': keyword, 'title': title}) # Use keyword as filename/identifier
        print(f"DEBUG HOME: Generating link for keyword: {keyword}, URL: {url_for('view_post', filename=keyword)}") # DEBUG: Print generated URL

    return render_template('index.html', posts=posts)

@app.route('/post/<filename>') # filename will be the keyword
def view_post(filename):
    """Render a single blog post with reviews"""
    print(f"Received request for post with filename: {filename}") # Added logging
    print(f"DEBUG VIEW_POST: Received filename: {filename}") # DEBUG: Print received filename
    keyword = filename # Use filename as keyword

    if not keyword:
        print("Error: Received empty keyword for view_post") # Added logging
        print("DEBUG VIEW_POST: Keyword is empty.") # DEBUG: Check if keyword is empty
        return "Post not found (empty keyword)", 404

    posts_data = load_blog_posts()

    blog_post_content = posts_data.get(keyword)

    if not blog_post_content:
        print(f"Error: Post content not found for keyword: {keyword}") # Added logging
        print(f"DEBUG VIEW_POST: Post content not found for keyword: {keyword}") # DEBUG: Check if post content is found
        return "Post not found", 404

    # Extract sources from the blog post content
    sources = []
    sources_section_match = re.search(r'### 6\. Sources.*?(##.*|$)\n', blog_post_content, re.DOTALL)
    if sources_section_match:
        sources_text = sources_section_match.group(0)
        # Regex to find Source Title: (URL)
        source_matches = re.findall(r'-\s*(.*?):\s*((https?://\S+))\n', sources_text)
        for title, url in source_matches:
            sources.append({'title': title.strip(), 'url': url.strip()})

        # Remove the sources section from the main content
        blog_post_content_without_sources = blog_post_content[:sources_section_match.start()] + blog_post_content[sources_section_match.end():]
    else:
        # If no sources section found, use the original content
        blog_post_content_without_sources = blog_post_content

    # Convert Markdown to HTML (of content without sources)
    blog_post_html = markdown.markdown(blog_post_content_without_sources, extensions=["fenced_code", "nl2br"])

    # Load reviews - review filenames are based on the keyword now
    reviews_filepath = os.path.join(REVIEWS_DIR, f"{keyword}_reviews.json") # Renamed review file format
    reviews = []
    if os.path.exists(reviews_filepath):
        try:
            with open(reviews_filepath, "r", encoding="utf-8") as f:
                reviews = json.load(f)
        except Exception as e:
            print(f"Error loading reviews for {keyword}: {str(e)}")
            # Continue without reviews if loading fails
            reviews = []

    # Determine title for the view page - prioritize H1 if available
    view_title = extract_title_from_markdown(blog_post_content)
    if view_title == "Untitled Post":
         view_title = keyword.replace("-", " ").replace("_", " ") # Fallback to keyword

    # Pass extracted sources to the template
    return render_template('post.html', title=view_title, post_html=blog_post_html, reviews=reviews, filename=keyword, sources=sources)

@app.route('/submit_review/<filename>', methods=['POST'])
def submit_review(filename):
    """Handle submission of reviews"""
    keyword = filename # Use filename as keyword
    reviews_filepath = os.path.join(REVIEWS_DIR, f"{keyword}_reviews.json") # Renamed review file format
    reviewer_name = request.form.get('name')
    review_content = request.form.get('review')

    if not reviewer_name or not review_content:
        # Optionally handle error - e.g., redirect back with a message
        return redirect(url_for('view_post', filename=keyword))

    new_review = {
        'name': reviewer_name,
        'review': review_content,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    reviews = []
    if os.path.exists(reviews_filepath):
        try:
            with open(reviews_filepath, "r", encoding="utf-8") as f:
                reviews = json.load(f)
        except Exception as e:
             print(f"Error loading existing reviews for {keyword}: {str(e)}")
             # Start with an empty list if loading fails
             reviews = []

    reviews.append(new_review)

    try:
        with open(reviews_filepath, "w", encoding="utf-8") as f:
            json.dump(reviews, f, indent=4)
    except Exception as e:
         print(f"Error saving new review for {keyword}: {str(e)}")
         # Continue, but the review won't be saved.


    # Redirect back to the post page
    return redirect(url_for('view_post', filename=keyword))

# Endpoint to generate a blog post for a given keyword (used by frontend)
@app.route('/generate', methods=['GET'])
def generate_post():
    """Endpoint to generate a blog post for a given keyword and save it to the JSON DB."""
    keyword = request.args.get('keyword')
    if not keyword:
        return jsonify({"error": "Keyword parameter is required"}), 400

    try:
        # Get SEO data for the keyword
        seo_data = get_seo_data(keyword)

        # Generate blog post using AI
        blog_post = generate_blog_post(keyword, seo_data)

        # Sanitize keyword for use as database key
        sanitized_keyword = sanitize_keyword(keyword)

        # Load existing posts, add/update the new post, and save
        posts_data = load_blog_posts()
        posts_data[sanitized_keyword] = blog_post
        save_blog_posts(posts_data)

        print(f"Generated post for keyword: {keyword} and saved with key: {sanitized_keyword}")

        # Return the generated post data as JSON
        return jsonify({
            "keyword": keyword,
            "seo_data": seo_data,
            "blog_post": blog_post,
            "blog_post_html": markdown.markdown(blog_post, extensions=["fenced_code", "nl2br"]),
            "filename": sanitized_keyword # Return sanitized keyword as identifier
        })

    except Exception as e:
        # Catch exceptions during get_seo_data, generate_blog_post, or file operations
        print(f"Error during blog post generation or saving: {str(e)}")
        return jsonify({"error": f"Error generating or saving post: {str(e)}"}), 500

@app.route('/delete_all_posts', methods=['POST'])
def delete_all_posts():
    """Endpoint to delete all generated blog posts and reviews."""
    try:
        # Load existing posts
        posts_data = load_blog_posts()

        # Get list of keywords (review filenames) before clearing posts_data
        keywords_to_delete = list(posts_data.keys())

        # Delete all posts from the database
        posts_data.clear()
        save_blog_posts(posts_data)

        # Delete all associated review files
        for keyword in keywords_to_delete:
            reviews_filepath = os.path.join(REVIEWS_DIR, f"{keyword}_reviews.json")
            if os.path.exists(reviews_filepath):
                os.remove(reviews_filepath)

        print("All generated posts and reviews deleted.")
        return jsonify({"success": True, "message": "All posts deleted"}), 200
    except Exception as e:
        print(f"Error deleting all posts: {str(e)}")
        return jsonify({"success": False, "message": f"Error deleting posts: {str(e)}"}), 500

@app.route('/delete_post/<keyword>', methods=['POST'])
def delete_post(keyword):
    """Endpoint to delete a specific blog post and its reviews by keyword."""
    try:
        # Load existing posts
        posts_data = load_blog_posts()

        # Check if the keyword exists
        if keyword not in posts_data:
            return jsonify({"success": False, "message": "Post not found"}), 404

        # Delete the post from the database
        del posts_data[keyword]
        save_blog_posts(posts_data)

        # Delete the associated review file if it exists
        reviews_filepath = os.path.join(REVIEWS_DIR, f"{keyword}_reviews.json")
        if os.path.exists(reviews_filepath):
            os.remove(reviews_filepath)

        print(f"Post and reviews for keyword \'{keyword}\' deleted.")
        return jsonify({"success": True, "message": f"Post \'{keyword}\' deleted"}), 200
    except Exception as e:
        print(f"Error deleting post \'{keyword}\': {str(e)}")
        return jsonify({"success": False, "message": f"Error deleting post: {str(e)}"}), 500

@app.route('/reviews/<keyword>')
def view_reviews(keyword):
    """Render a page showing only reviews for a specific post."""
    print(f"Received request for reviews with keyword: {keyword}") # Added logging

    if not keyword:
        print("Error: Received empty keyword for view_reviews") # Added logging
        return "Reviews not found (empty keyword)", 404

    # Load reviews - review filenames are based on the keyword
    reviews_filepath = os.path.join(REVIEWS_DIR, f"{keyword}_reviews.json")
    reviews = []
    if os.path.exists(reviews_filepath):
        try:
            with open(reviews_filepath, "r", encoding="utf-8") as f:
                reviews = json.load(f)
        except Exception as e:
            print(f"Error loading reviews for {keyword}: {str(e)}")
            # Continue without reviews if loading fails
            reviews = []

    # Pass the keyword to the template for the review submission form
    return render_template('reviews_only.html', reviews=reviews, keyword=keyword)

if __name__ == '__main__':
    # Start the scheduler
    scheduler.add_job(generate_daily_post, 'cron', hour=15, minute=10)  # Run at midnight every day
    scheduler.start()

    # Ensure directories exist (already done, but good to be explicit)
    os.makedirs(GENERATED_POSTS_DIR, exist_ok=True)
    os.makedirs(REVIEWS_DIR, exist_ok=True)

    # Run the Flask app
    # Using host='0.0.0.0' makes the server externally visible (useful for testing in some environments)
    # debug=True should be False in production
    app.run(debug=True, host='0.0.0.0')