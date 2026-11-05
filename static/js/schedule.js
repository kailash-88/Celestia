/**
 * MediMitra – Schedule Management JavaScript
 * Controls schedule modal and quick dose actions.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Esc key closes modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('addScheduleModal');
            if (modal) modal.style.display = 'none';
        }
    });

    // Auto-select approximate slot based on target time
    const timeInput = document.getElementById('scheduled_time');
    const slotSelect = document.getElementById('time_of_day');
    if (timeInput && slotSelect) {
        timeInput.addEventListener('change', () => {
            const hour = parseInt(timeInput.value.split(':')[0], 10);
            if (!isNaN(hour)) {
                if (hour >= 5 && hour < 12) slotSelect.value = 'morning';
                else if (hour >= 12 && hour < 17) slotSelect.value = 'afternoon';
                else if (hour >= 17 && hour < 21) slotSelect.value = 'evening';
                else slotSelect.value = 'night';
            }
        });
    }
});
