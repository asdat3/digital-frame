/**
 * Countdown module - calculates and displays days remaining until target date
 */

function updateCountdown() {
  const countdownDate = window.COUNTDOWN_DATE;
  const daysElement = document.getElementById('countdown-days');

  if (!countdownDate || !daysElement) {
    console.error('Countdown date or element not found');
    return;
  }

  try {
    // Parse the target date (format: YYYY-MM-DD)
    const targetDate = new Date(countdownDate + 'T00:00:00');
    const today = new Date();
    
    // Set today to midnight for accurate day calculation
    today.setHours(0, 0, 0, 0);
    targetDate.setHours(0, 0, 0, 0);

    // Calculate difference in milliseconds
    const diffTime = targetDate - today;
    
    // Convert to days
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    // Update the display
    if (diffDays < 0) {
      daysElement.textContent = Math.abs(diffDays);
      const label = document.querySelector('.countdown-label');
      if (label) {
        label.textContent = 'days ago';
      }
    } else if (diffDays === 0) {
      daysElement.textContent = '0';
      const label = document.querySelector('.countdown-label');
      if (label) {
        label.textContent = 'days left';
      }
    } else {
      daysElement.textContent = diffDays;
      const label = document.querySelector('.countdown-label');
      if (label) {
        label.textContent = 'days left';
      }
    }
  } catch (error) {
    console.error('Error calculating countdown:', error);
    daysElement.textContent = '--';
  }
}

// Initialize countdown when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', updateCountdown);
} else {
  updateCountdown();
}

// Update countdown daily at midnight
function scheduleDailyUpdate() {
  const now = new Date();
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(0, 0, 0, 0);
  
  const msUntilMidnight = tomorrow - now;
  
  setTimeout(() => {
    updateCountdown();
    // Schedule next update
    setInterval(updateCountdown, 24 * 60 * 60 * 1000); // Update every 24 hours
  }, msUntilMidnight);
}

// Start the daily update scheduler
scheduleDailyUpdate();

