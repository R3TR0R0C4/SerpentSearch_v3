# app.py - Flask web app for the crawler

from flask import Flask, request, render_template, redirect, url_for, jsonify
import threading
from crawler import crawl
import config  # For defaults
import models  # For DB operations

app = Flask(__name__)

# Database setup, will only run if the database and/or table don't exist
models.create_database()
models.create_table()

@app.route('/')
def index():
    return redirect(url_for('home'))

# Route for admin home page
@app.route('/admin', methods=['GET'])
def home():
    return render_template('admin.html', default_depth=config.MAX_DEPTH_DEFAULT, message=None)

# Route to handle crawl request
@app.route('/admin/crawl', methods=['POST'])
def start_crawl():
    start_url = request.form.get('start_url')
    max_depth = int(request.form.get('max_depth', config.MAX_DEPTH_DEFAULT))
    
    if not start_url:
        return render_template('admin.html', default_depth=config.MAX_DEPTH_DEFAULT, message="Please provide a start URL.")
    
    try:
        # Clear the table before starting a new crawl
        models.clear_table()
        
        # Run the crawl in a background thread
        thread = threading.Thread(target=crawl, args=(start_url, max_depth))
        thread.start()
        message = f"Crawl started in background for {start_url} with depth {max_depth}. Monitor statistics below."
    except Exception as e:
        message = f"Error starting crawl: {str(e)}"
    
    return render_template('admin.html', default_depth=config.MAX_DEPTH_DEFAULT, message=message)

# Route for statistics (JSON)
@app.route('/admin/stats', methods=['GET'])
def get_stats():
    pending = models.get_pending_count()
    crawled = models.get_crawled_count()
    return jsonify({'pending': pending, 'crawled': crawled})

if __name__ == '__main__':
    app.run(debug=True)