from threading import Lock

crawl_thread = None
is_paused = False
is_running = False
lock = Lock()