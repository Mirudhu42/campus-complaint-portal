/**
 * Chart helper utilities for Campus Complaint Portal
 */

function fetchAndUpdateAdminCharts() {
  fetch('/admin/api/chart-data')
    .then(res => res.json())
    .then(data => {
      console.log('Live chart data loaded:', data);
    })
    .catch(err => console.error('Failed to fetch chart data:', err));
}
