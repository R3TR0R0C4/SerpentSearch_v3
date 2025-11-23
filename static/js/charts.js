document.addEventListener('DOMContentLoaded', function() {

    // Helper: Common options for dark mode visibility
    const commonOptions = {
        responsive: true,
        plugins: {
            legend: {
                labels: { color: '#e0e0e0' } // Light text for legend
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: '#333333' }, // Dark grey grid lines
                ticks: { color: '#e0e0e0' } // Light text for numbers
            },
            x: {
                grid: { color: '#333333' },
                ticks: { color: '#e0e0e0' }
            }
        }
    };

    // 1. Initialize Charts

    // --- CRAWLED CHART (Green) ---
    const crawledCtx = document.getElementById("crawledChart").getContext("2d");
    const crawledChart = new Chart(crawledCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Crawled",
                data: [],
                borderWidth: 3,
                // Vibrant Green
                borderColor: 'rgb(34, 197, 94)', 
                // Transparent Green Fill
                backgroundColor: 'rgba(34, 197, 94, 0.2)', 
                tension: 0.4, // Smooth curves
                fill: true    // Fills the area under the line
            }]
        },
        options: commonOptions
    });

    // --- PENDING CHART (Orange) ---
    const pendingCtx = document.getElementById("pendingChart").getContext("2d");
    const pendingChart = new Chart(pendingCtx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Pending",
                data: [],
                borderWidth: 3,
                // Vibrant Orange
                borderColor: 'rgb(249, 115, 22)', 
                // Transparent Orange Fill
                backgroundColor: 'rgba(249, 115, 22, 0.2)', 
                tension: 0.4, // Smooth curves
                fill: true
            }]
        },
        options: commonOptions
    });

    // 2. Fetch Logic (Unchanged, but kept for context)
    async function fetchStats() {
        try {
            const res = await fetch("/admin/stats");
            const stats = await res.json();
            const label = new Date().toLocaleTimeString();

            // Update crawled chart
            crawledChart.data.labels.push(label);
            crawledChart.data.datasets[0].data.push(stats.crawled);

            if (crawledChart.data.labels.length > 50) {
                crawledChart.data.labels.shift();
                crawledChart.data.datasets[0].data.shift();
            }
            crawledChart.update();

            // Update pending chart
            pendingChart.data.labels.push(label);
            pendingChart.data.datasets[0].data.push(stats.pending);

            if (pendingChart.data.labels.length > 50) {
                pendingChart.data.labels.shift();
                pendingChart.data.datasets[0].data.shift();
            }
            pendingChart.update();

        } catch (err) {
            console.error("Stats fetch failed:", err);
        }
    }

    // 3. Start Loop
    fetchStats();
    setInterval(fetchStats, 5000);

});