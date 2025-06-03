# AI-Powered Blog Post Generator

This Flask application automatically generates SEO-optimized blog posts using OpenAI's GPT model. It includes a daily scheduler to automatically generate posts for predefined keywords.

## Features

- Generate blog posts from keywords using OpenAI's GPT model
- Mock SEO data generation (search volume, keyword difficulty, CPC)
- Daily automated post generation
- REST API endpoint for on-demand post generation
- Automatic affiliate link placeholder replacement
- Markdown-formatted output

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-blog-generator-interview-Vishwa_Sai_Challa.git
cd ai-blog-generator-interview-Vishwa_Sai_Challa
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Running the Application

Start the Flask application:
```bash
python app.py
```

The application will:
- Start the Flask server on `http://localhost:5000`
- Initialize the daily scheduler to generate posts at midnight
- Create a `generated_posts` directory to store the generated content

### API Endpoints

#### Generate Blog Post
```
GET /generate?keyword=your_keyword
```

Example:
```bash
curl "http://localhost:5000/generate?keyword=wireless%20earbuds"
```

Response:
```json
{
    "keyword": "wireless earbuds",
    "seo_data": {
        "search_volume": 50000,
        "keyword_difficulty": 65,
        "avg_cpc": 2.5
    },
    "blog_post": "# Generated blog post content in Markdown..."
}
```

### Generated Posts

The application automatically generates posts daily for the predefined keyword ("wireless earbuds" by default). Generated posts are saved in the `generated_posts` directory with filenames in the format `post_YYYYMMDD.md`.

## Customization

- To change the default keyword for daily generation, modify the `keyword` variable in the `generate_daily_post()` function in `app.py`
- To adjust the scheduling time, modify the cron schedule in `app.py`
- To customize the blog post generation prompt, edit the prompt template in `ai_generator.py`

## Error Handling

The application includes error handling for:
- Missing API keys
- OpenAI API errors
- Invalid keywords
- File system operations

## License

MIT License 