function updateStats() {
    fetch('/admin/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('queue-size').innerText = data.pending;
            document.getElementById('crawled-items').innerText = data.crawled;
        })
        .catch(error => console.error('Error fetching stats:', error));
}

window.onload = updateStats;
setInterval(updateStats, 5000);