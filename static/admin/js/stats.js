document.addEventListener('DOMContentLoaded', function() {
    let profitChartInstance = null;
    let roomChartInstance = null;

    function createProfitChart() {
        const profitCanvas = document.getElementById('profitChart');
        if (profitCanvas) {
            const profitCtx = profitCanvas.getContext('2d');

            // Destroy existing chart before creating a new one
            if (profitChartInstance) {
                profitChartInstance.destroy();
            }

            profitChartInstance = new Chart(profitCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Monthly Profit',
                        data: [12000, 19000, 3000, 5000, 2000, 3000],
                        borderColor: '#CDA274',
                        tension: 0.4,
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    }

    function createRoomChart() {
        const roomCanvas = document.getElementById('roomTypeChart');
        if (roomCanvas) {
            const roomCtx = roomCanvas.getContext('2d');

            // Destroy existing chart before creating a new one
            if (roomChartInstance) {
                roomChartInstance.destroy();
            }

            roomChartInstance = new Chart(roomCtx, {
                type: 'pie',
                data: {
                    labels: ['Standard', 'Deluxe', 'Suite'],
                    datasets: [{
                        data: [300, 150, 50],
                        backgroundColor: ['#CDA274', '#2BBE2A', '#F44842']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    }

    createProfitChart();
    createRoomChart();
});
