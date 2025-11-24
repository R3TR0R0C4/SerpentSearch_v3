document.addEventListener('DOMContentLoaded', function() {

    // Helper: Common options for dark mode visibility + larger fonts
    const commonOptions = {
        responsive: true,
        plugins: {
            legend: {
                labels: { 
                    color: '#e0e0e0',
                    font: { size: 16 }
                }
            },
            tooltip: {
                bodyFont: { size: 16 },
                titleFont: { size: 16 }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: '#333333' },
                ticks: { 
                    color: '#e0e0e0',
                    font: { size: 16 }
                }
            },
            x: {
                grid: { color: '#333333' },
                ticks: { 
                    color: '#e0e0e0',
                    font: { size: 16 }
                }
            }
        }
    };

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
                borderColor: 'rgb(34, 197, 94)', 
                backgroundColor: 'rgba(34, 197, 94, 0.2)', 
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                title: {
                    display: true,
                    text: 'Crawled pages',
                    color: '#e0e0e0',
                    font: { size: 18 }
                }
            },
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Total pages',
                        color: '#e0e0e0',
                        font: { size: 16 }
                    }
                }
            }
        }
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
                borderColor: 'rgb(249, 115, 22)', 
                backgroundColor: 'rgba(249, 115, 22, 0.2)', 
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                title: {
                    display: true,
                    text: 'Pending pages',
                    color: '#e0e0e0',
                    font: { size: 18 }
                }
            },
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Total pages',
                        color: '#e0e0e0',
                        font: { size: 16 }
                    }
                }
            }
        }
    });


const crawledRateCtx = document.getElementById("crawledRateChart").getContext("2d");
const crawledRateChart = new Chart(crawledRateCtx, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "Crawled / min",
            data: [],
            borderWidth: 3,
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.15)',
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        ...commonOptions,
        plugins: {
            ...commonOptions.plugins,
            title: {
                display: true,
                text: 'Crawled pages per minute',
                color: '#e0e0e0',
                font: { size: 18 }
            }
        },
        scales: {
            ...commonOptions.scales,
            y: {
                ...commonOptions.scales.y,
                beginAtZero: true,   // crawled rate is always ≥ 0
                title: {
                    display: true,
                    text: 'Pages / minute',
                    color: '#e0e0e0',
                    font: { size: 16 }
                }
            }
        }
    }
});

// --- PENDING CHANGE RATE CHART (Orange) ---
const pendingRateCtx = document.getElementById("pendingRateChart").getContext("2d");
const pendingRateChart = new Chart(pendingRateCtx, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "Pending change / min",
            data: [],
            borderWidth: 3,
            borderColor: 'rgb(249, 115, 22)',
            backgroundColor: 'rgba(249, 115, 22, 0.15)',
            tension: 0.4,
            fill: true
        }]
    },
    options: {
        ...commonOptions,
        plugins: {
            ...commonOptions.plugins,
            title: {
                display: true,
                text: 'Pending queue change per minute',
                color: '#e0e0e0',
                font: { size: 18 }
            }
        },
        scales: {
            ...commonOptions.scales,
            y: {
                ...commonOptions.scales.y,
                beginAtZero: false,   // MUST be false → pending change can be heavily negative
                title: {
                    display: true,
                    text: 'Pages / minute',
                    color: '#e0e0e0',
                    font: { size: 16 }
                }
            }
        }
    }
});


    let prevCrawled = null;
    let prevPending = null;
    let prevTime = null;

    
    // 2. Fetch Logic
async function fetchStats() {
    try {
        const res = await fetch("/admin/stats");
        const stats = await res.json();
        const label = new Date().toLocaleTimeString();
        const currentTime = Date.now();

        // === Update cumulative charts (unchanged) ===
        crawledChart.data.labels.push(label);
        crawledChart.data.datasets[0].data.push(stats.crawled);
        if (crawledChart.data.labels.length > 50) {
            crawledChart.data.labels.shift();
            crawledChart.data.datasets[0].data.shift();
        }
        crawledChart.update();

        pendingChart.data.labels.push(label);
        pendingChart.data.datasets[0].data.push(stats.pending);
        if (pendingChart.data.labels.length > 50) {
            pendingChart.data.labels.shift();
            pendingChart.data.datasets[0].data.shift();
        }
        pendingChart.update();

        // === Calculate rates only when we have a previous value ===
        if (prevTime !== null) {
            const deltaTimeMin = (currentTime - prevTime) / 60000; // minutes (accurate even if interval drifts)
            const rateCrawled = deltaTimeMin > 0 ? Math.round((stats.crawled - prevCrawled) / deltaTimeMin) : 0;
            const ratePending = deltaTimeMin > 0 ? Math.round((stats.pending - prevPending) / deltaTimeMin) : 0;

            // --- Crawled rate ---
            crawledRateChart.data.labels.push(label);
            crawledRateChart.data.datasets[0].data.push(rateCrawled);
            if (crawledRateChart.data.labels.length > 50) {
                crawledRateChart.data.labels.shift();
                crawledRateChart.data.datasets[0].data.shift();
            }
            crawledRateChart.update();

            // --- Pending change rate ---
            pendingRateChart.data.labels.push(label);
            pendingRateChart.data.datasets[0].data.push(ratePending);
            if (pendingRateChart.data.labels.length > 50) {
                pendingRateChart.data.labels.shift();
                pendingRateChart.data.datasets[0].data.shift();
            }
            pendingRateChart.update();
        }

        // Store for next iteration
        prevCrawled = stats.crawled;
        prevPending = stats.pending;
        prevTime = currentTime;

    } catch (err) {
        console.error("Stats fetch failed:", err);
    }
}
    // 3. Start Loop
    fetchStats();
    setInterval(fetchStats, 5000);
});