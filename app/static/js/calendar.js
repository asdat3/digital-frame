// Calendar - show the next 5 upcoming events

function formatEventTime(isoString) {
  if (!isoString) return '';
  const date = new Date(isoString);
  return date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

function isAllDayEvent(beginIsoString, endIsoString) {
  if (!beginIsoString) return false;
  try {
    const beginDate = new Date(beginIsoString);
    const beginHours = beginDate.getHours();
    const beginMinutes = beginDate.getMinutes();
    
    // Check if start time is at midnight (00:00 or 01:00, accounting for timezone)
    if (beginHours !== 0 && beginHours !== 1) return false;
    if (beginMinutes !== 0) return false;
    
    if (!endIsoString) {
      // If no end time, check if it's exactly at midnight
      return beginHours === 0 || beginHours === 1;
    }
    
    const endDate = new Date(endIsoString);
    const endHours = endDate.getHours();
    const endMinutes = endDate.getMinutes();
    
    // Check if end time is also at midnight
    if (endHours !== 0 && endHours !== 1) return false;
    if (endMinutes !== 0) return false;
    
    // Check if start and end times are the same (or very close, within 1 hour)
    const timeDiff = Math.abs(endDate - beginDate);
    const hoursDiff = timeDiff / (1000 * 60 * 60);
    
    // All-day events are either same time or exactly 24 hours apart
    return hoursDiff < 1 || Math.abs(hoursDiff - 24) < 1;
  } catch (e) {
    return false;
  }
}

function formatEventTimeRange(beginIsoString, endIsoString) {
  if (!beginIsoString) return '';
  
  // Check if it's an all-day event
  if (isAllDayEvent(beginIsoString, endIsoString)) {
    return 'All Day';
  }
  
  const beginTime = formatEventTime(beginIsoString);
  if (!beginTime) return '';
  if (!endIsoString) return beginTime;
  const endTime = formatEventTime(endIsoString);
  if (!endTime) return beginTime;
  return `${beginTime} - ${endTime}`;
}

function isToday(isoString) {
  if (!isoString) return false;
  try {
    const eventDate = new Date(isoString);
    if (isNaN(eventDate.getTime())) return false;
    
    const now = new Date();
    
    // Compare year, month, and day in local time
    return (
      eventDate.getFullYear() === now.getFullYear() &&
      eventDate.getMonth() === now.getMonth() &&
      eventDate.getDate() === now.getDate()
    );
  } catch (e) {
    console.error('Error checking if date is today:', e, isoString);
    return false;
  }
}

function isTomorrow(isoString) {
  if (!isoString) return false;
  try {
    const eventDate = new Date(isoString);
    if (isNaN(eventDate.getTime())) return false;
    
    const now = new Date();
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    // Compare year, month, and day in local time
    return (
      eventDate.getFullYear() === tomorrow.getFullYear() &&
      eventDate.getMonth() === tomorrow.getMonth() &&
      eventDate.getDate() === tomorrow.getDate()
    );
  } catch (e) {
    console.error('Error checking if date is tomorrow:', e, isoString);
    return false;
  }
}

function formatEventDate(isoString) {
  if (!isoString) return '';
  try {
    const eventDate = new Date(isoString);
    if (isNaN(eventDate.getTime())) return '';
    
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const eventDay = new Date(eventDate.getFullYear(), eventDate.getMonth(), eventDate.getDate());
    
    if (eventDay.getTime() === today.getTime()) return 'Today';
    if (eventDay.getTime() === tomorrow.getTime()) return 'Tomorrow';
    
    // Format date for future dates (e.g., "Jan 15" or "Dec 25")
    return eventDate.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
    });
  } catch (e) {
    return '';
  }
}

function getEventDayLabel(isoString) {
  if (isToday(isoString)) return 'Today';
  if (isTomorrow(isoString)) return 'Tomorrow';
  return formatEventDate(isoString);
}

function renderCalendar(events) {
  const container = document.getElementById('calendar-entries');
  if (!container) {
    console.error('Calendar container not found');
    return;
  }
  const row = container.querySelector('.calendar-row');
  if (!row) {
    console.error('Calendar row not found');
    return;
  }

  const slots = Array.from(row.querySelectorAll('.calendar-item'));
  if (!slots.length) {
    console.error('No calendar slots found');
    return;
  }

  // Filter to future events, sort by start time, and take only the next 5
  const now = new Date();
  const relevantEvents = (events || [])
    .filter((e) => {
      if (!e || !e.begin) return false;
      // Only show events that haven't started yet
      const eventDate = new Date(e.begin);
      return eventDate >= now;
    })
    .sort((a, b) => {
      // Sort by start time (earliest first)
      return new Date(a.begin) - new Date(b.begin);
    })
    .slice(0, 3); // Take only the next 5 events

  console.log('Total events received:', events?.length || 0);
  console.log('Next 5 upcoming events:', relevantEvents.length, relevantEvents);

  // Fill available slots with the next 5 upcoming events
  for (let i = 0; i < slots.length; i++) {
    const slot = slots[i];
    const ev = relevantEvents[i];

    // Normalize type classes on the slot
    slot.className = 'calendar-item';
    if (ev && ev.calendarType) {
      slot.classList.add(`calendar-item-${ev.calendarType}`);
    }

    const dateEl = slot.querySelector('.calendar-date');
    const titleEl = slot.querySelector('.calendar-title');
    const timeEl = slot.querySelector('.calendar-time');

    if (!ev) {
      // Only show "No events" in the first empty slot if no events at all
      if (i === 0 && relevantEvents.length === 0) {
        slot.classList.remove('calendar-item-empty');
        if (dateEl) dateEl.textContent = '';
        if (titleEl) titleEl.textContent = 'No upcoming events.';
        if (timeEl) timeEl.textContent = '';
      } else {
        // Hide empty slots
        slot.classList.add('calendar-item-empty');
        if (dateEl) dateEl.textContent = '';
        if (titleEl) titleEl.textContent = '';
        if (timeEl) timeEl.textContent = '';
      }
      continue;
    }

    // Show event slot
    slot.classList.remove('calendar-item-empty');

    const timeRange = formatEventTimeRange(ev.begin, ev.end);
    const dayLabel = getEventDayLabel(ev.begin);
    if (dateEl) {
      // Combine day label with time range
      let dateText = '';
      if (dayLabel && timeRange) {
        dateText = `${dayLabel} · ${timeRange}`;
      } else if (dayLabel) {
        dateText = dayLabel;
      } else if (timeRange) {
        dateText = timeRange;
      }
      dateEl.textContent = dateText;
      if (!timeRange && !dayLabel) {
        console.warn('Empty time range and date for event:', ev);
      }
    }
    if (titleEl) titleEl.textContent = ev.name || 'Untitled';
    if (timeEl) timeEl.textContent = '';
  }
}

function initCalendar(Events) {
  // Hide all calendar items initially while loading
  const container = document.getElementById('calendar-entries');
  if (container) {
    const slots = container.querySelectorAll('.calendar-item');
    slots.forEach(slot => {
      slot.classList.add('calendar-item-empty');
    });
  }

  async function update() {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    try {
      const res = await fetch('/api/calendar', { signal: controller.signal });
      clearTimeout(timeout);
      
      if (!res.ok) {
        console.warn('Calendar fetch failed:', res.status, res.statusText);
        renderCalendar([]);
        return;
      }
      
      const data = await res.json();
      const calendars = data?.calendars || {};
      
      // Extract events from each calendar and add calendarType
      const allEvents = [];
      const calendarTypes = ['personal', 'holidays', 'garbage'];
      
      for (const calendarType of calendarTypes) {
        const calendarData = calendars[calendarType];
        if (calendarData && Array.isArray(calendarData.events)) {
          const events = calendarData.events.map((ev) => ({ ...ev, calendarType }));
          allEvents.push(...events);
          console.log(`Calendar ${calendarType} fetched:`, events.length, 'events');
        } else if (calendarData?.error) {
          console.warn(`Calendar ${calendarType} error:`, calendarData.error);
        }
      }
      
      console.log('Total events from all calendars:', allEvents.length);
      renderCalendar(allEvents);
      Events.emit('calendar:update', allEvents);
      
    } catch (e) {
      clearTimeout(timeout);
      if (e.name === 'AbortError') {
        console.error('Calendar fetch timeout');
      } else {
        console.error('Calendar fetch error:', e);
      }
      renderCalendar([]);
    }
  }

  // Initial paint and periodic refresh
  update();
  setInterval(update, 1000 * 60 * 15); // Refresh every 15 minutes
}

