function updateStats() {
  fetch("/admin/stats")
    .then((response) => response.json())
    .then((data) => {
      // Update counts
      document.getElementById("queue-size").innerText = data.pending;
      document.getElementById("crawled-items").innerText = data.crawled;
      document.getElementById("failed-items").innerText = data.failed;
      document.getElementById('media-items').innerText = data.media;
      
      // Determine and display the main running status
      let statusText;
      if (data.is_running) {
        statusText = "Processing";
      } else if (data.pending > 0) {
        statusText = "Idle";
      } else {
        statusText = "Inactive";
      }
      document.getElementById("crawler-status").innerText = statusText;

      // Determine and display the pause status
      let pauseText = data.is_paused ? "PAUSED" : "Running";
      document.getElementById("pause-status").innerText = pauseText;

      // Button Logic (Keep the existing logic)
      // Resume enabled if paused or (pending > 0 and not running)
      document.getElementById("resume-btn").disabled = !(
        data.is_paused ||
        (data.pending > 0 && !data.is_running)
      );

      // Pause enabled if running and not paused
      document.getElementById("pause-btn").disabled = !(
        data.is_running && !data.is_paused
      );
    })
    .catch((error) => console.error("Error fetching stats:", error));
}

function pauseCrawl() {
  const btn = document.getElementById("pause-btn");
  btn.disabled = true;
  fetch("/admin/pause", { method: "POST" })
    .then((response) => {
      if (!response.ok) throw new Error("Pause request failed");
      return response;
    })
    .then(() => updateStats())
    .catch((error) => {
      console.error("Error pausing:", error);
      btn.disabled = false; // Re-enable on error
    });
}

function resumeCrawl() {
  fetch("/admin/resume", { method: "POST" })
    .then(() => updateStats())
    .catch((error) => console.error("Error resuming:", error));
}

window.onload = updateStats;
setInterval(updateStats, 5000);
