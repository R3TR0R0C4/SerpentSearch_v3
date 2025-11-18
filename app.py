import threading

from flask import Flask, request, render_template, redirect, url_for, jsonify

import control
import models
from crawler import crawl

models.create_database()
models.create_table()


app = Flask(__name__)

def run_crawl():
    with control.lock:
        control.is_running = True
    
    print("Crawl thread started...")
    try:
        crawl() 
    except Exception as e:
        print(f"Error in crawl thread: {e}")
    finally:
        # Once the crawl loop finishes (no more pending items), 
        # set running to false
        with control.lock:
            control.is_running = False
        print("Crawl thread finished.")

@app.route('/')
def index():
    return redirect(url_for('home'))

# Route for admin home page
@app.route('/admin', methods=['GET'])
def home():
    return render_template('admin.html', message=None)

# Route to add to queue
@app.route('/admin/add_to_queue', methods=['POST'])
def add_to_queue():
    start_url = request.form.get('start_url')
    try:
        max_depth = int(request.form.get('max_depth', 0))
    except ValueError:
        return render_template('admin.html', message="Max Depth must be an integer.")
    
    if not start_url:
        return render_template('admin.html', message="Please provide a start URL.")

    # A safety check for a reasonable depth
    if max_depth <= 0:
        return render_template('admin.html', message="Max Depth must be 1 or greater.")
    
    try:
        models.insert_pending(start_url, None, 0, max_depth)

        with control.lock:
            if not control.is_running:
                control.is_running = True
                control.crawl_thread = threading.Thread(target=run_crawl)
                control.crawl_thread.start()
        message = f"Added {start_url} to queue with Max Depth {max_depth}. If paused, use Resume to continue."
    except Exception as e:
        message = f"Error adding to queue: {str(e)}"    
    return render_template('admin.html', message=message)

# Route to pause crawling
@app.route('/admin/pause', methods=['POST'])
def pause_crawl():
    with control.lock:
        control.is_paused = True
    return jsonify({'status': 'paused'})

# Route to resume crawling
@app.route('/admin/resume', methods=['POST'])
def resume_crawl():
    with control.lock:
        control.is_paused = False
        if not control.is_running and models.get_pending_count() > 0:
            control.crawl_thread = threading.Thread(target=run_crawl)
            control.crawl_thread.start()
    return jsonify({'status': 'resumed'})

# Route for statistics and status (JSON)
@app.route('/admin/stats', methods=['GET'])
def get_stats():
    with control.lock:
        status = {
            'pending': models.get_pending_count(),
            'crawled': models.get_crawled_count(),
            'failed': models.get_failed_count() if hasattr(models, 'get_failed_count') else 0,
            'is_running': control.is_running,
            'is_paused': control.is_paused
        }
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True)