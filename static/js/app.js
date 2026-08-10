// API Base URL
const API_BASE = '/api/tickets';

// Utility: Show toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Utility: Format date
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Utility: Get status class
function getStatusClass(status) {
    const classes = {
        'Open': 'status-open',
        'In Progress': 'status-in-progress',
        'Closed': 'status-closed'
    };
    return classes[status] || '';
}

// Utility: Show loading
function showLoading(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.innerHTML = `
            <div class="flex justify-center items-center py-12">
                <div class="spinner"></div>
            </div>
        `;
    }
}

// ============ TICKET LIST PAGE ============

// Load and display tickets
async function loadTickets(status = '', search = '') {
    showLoading('tickets-container');
    
    let url = API_BASE + '?';
    if (status) url += `status=${encodeURIComponent(status)}&`;
    if (search) url += `search=${encodeURIComponent(search)}&`;
    
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch tickets');
        
        const tickets = await response.json();
        renderTickets(tickets);
        updateStats();
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('tickets-container').innerHTML = `
            <div class="text-center py-12 text-red-500">
                <p class="text-lg">Failed to load tickets</p>
                <p class="text-sm mt-2">Please try again later</p>
            </div>
        `;
    }
}

// Render tickets to DOM
function renderTickets(tickets) {
    const container = document.getElementById('tickets-container');
    
    if (tickets.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12 text-gray-500">
                <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="mt-4 text-lg font-medium">No tickets found</p>
                <p class="mt-1 text-sm">Create a new ticket to get started</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = tickets.map((ticket, index) => `
        <div class="ticket-row bg-white border border-gray-200 rounded-lg p-4 mb-3 cursor-pointer hover:border-blue-300 slide-in" 
             style="animation-delay: ${index * 0.05}s"
             onclick="window.location.href='/tickets/${ticket.ticket_id}'">
            <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-3 mb-1">
                        <span class="text-sm font-mono text-blue-600 font-semibold">${ticket.ticket_id}</span>
                        <span class="px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusClass(ticket.status)}">
                            ${ticket.status}
                        </span>
                    </div>
                    <h3 class="text-gray-900 font-medium truncate">${escapeHtml(ticket.subject)}</h3>
                    <p class="text-sm text-gray-500 mt-1">${escapeHtml(ticket.customer_name)} • ${formatDate(ticket.created_at)}</p>
                </div>
                <svg class="w-5 h-5 text-gray-400 ml-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
            </div>
        </div>
    `).join('');
}

// Update stats display
async function updateStats() {
    try {
        const response = await fetch(API_BASE + '/stats');
        const stats = await response.json();
        
        document.getElementById('stat-total').textContent = stats.total;
        document.getElementById('stat-open').textContent = stats.open;
        document.getElementById('stat-progress').textContent = stats.in_progress;
        document.getElementById('stat-closed').textContent = stats.closed;
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Search functionality (debounced)
let searchTimeout;
function handleSearch(query) {
    clearTimeout(searchTimeout);
    const status = document.querySelector('.filter-active')?.dataset.status || '';
    searchTimeout = setTimeout(() => {
        loadTickets(status, query);
    }, 300);
}

// Filter by status
function filterByStatus(status, element) {
    // Update active filter button
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('filter-active');
    });
    element.classList.add('filter-active');
    
    const search = document.getElementById('search-input')?.value || '';
    loadTickets(status, search);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============ CREATE TICKET PAGE ============

// Handle ticket creation
async function createTicket(event) {
    event.preventDefault();
    
    const submitBtn = document.getElementById('submit-btn');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="spinner inline-block"></span> Creating...';
    submitBtn.disabled = true;
    
    const formData = {
        customer_name: document.getElementById('customer_name').value.trim(),
        customer_email: document.getElementById('customer_email').value.trim(),
        subject: document.getElementById('subject').value.trim(),
        description: document.getElementById('description').value.trim()
    };
    
    try {
        const response = await fetch(API_BASE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create ticket');
        }
        
        const result = await response.json();
        showToast(`Ticket ${result.ticket_id} created successfully!`);
        
        // Redirect to ticket detail after short delay
        setTimeout(() => {
            window.location.href = `/tickets/${result.ticket_id}`;
        }, 1000);
        
    } catch (error) {
        showToast(error.message, 'error');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// ============ TICKET DETAIL PAGE ============

// Load ticket details
async function loadTicketDetail(ticketId) {
    showLoading('ticket-detail');
    showLoading('notes-container');
    
    try {
        const response = await fetch(`${API_BASE}/${ticketId}`);
        if (!response.ok) throw new Error('Ticket not found');
        
        const ticket = await response.json();
        renderTicketDetail(ticket);
        renderNotes(ticket.notes);
    } catch (error) {
        document.getElementById('ticket-detail').innerHTML = `
            <div class="text-center py-12 text-red-500">
                <p class="text-lg">Ticket not found</p>
                <a href="/" class="mt-4 inline-block text-blue-600 hover:underline">← Back to tickets</a>
            </div>
        `;
    }
}

// Render ticket detail
function renderTicketDetail(ticket) {
    const container = document.getElementById('ticket-detail');
    container.innerHTML = `
        <div class="fade-in">
            <div class="flex items-center justify-between mb-6">
                <div>
                    <span class="text-sm font-mono text-blue-600 font-semibold">${ticket.ticket_id}</span>
                    <h1 class="text-2xl font-bold text-gray-900 mt-1">${escapeHtml(ticket.subject)}</h1>
                </div>
                <span class="px-3 py-1 rounded-full text-sm font-medium ${getStatusClass(ticket.status)}">
                    ${ticket.status}
                </span>
            </div>
            
            <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Customer Information</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <p class="text-sm text-gray-500">Name</p>
                        <p class="font-medium text-gray-900">${escapeHtml(ticket.customer_name)}</p>
                    </div>
                    <div>
                        <p class="text-sm text-gray-500">Email</p>
                        <p class="font-medium text-gray-900">${escapeHtml(ticket.customer_email)}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Description</h2>
                <p class="text-gray-700 whitespace-pre-wrap">${escapeHtml(ticket.description)}</p>
            </div>
            
            <div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Timeline</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <p class="text-sm text-gray-500">Created</p>
                        <p class="font-medium text-gray-900">${formatDate(ticket.created_at)}</p>
                    </div>
                    <div>
                        <p class="text-sm text-gray-500">Last Updated</p>
                        <p class="font-medium text-gray-900">${formatDate(ticket.updated_at)}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white border border-gray-200 rounded-lg p-6">
                <h2 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">Update Ticket</h2>
                <form onsubmit="updateTicket(event, '${ticket.ticket_id}')">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
                            <select id="update-status" class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                                <option value="Open" ${ticket.status === 'Open' ? 'selected' : ''}>Open</option>
                                <option value="In Progress" ${ticket.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
                                <option value="Closed" ${ticket.status === 'Closed' ? 'selected' : ''}>Closed</option>
                            </select>
                        </div>
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium text-gray-700 mb-1">Add Note</label>
                        <textarea id="update-note" rows="3" placeholder="Add a note about this update..." class="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"></textarea>
                    </div>
                    <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 font-medium">
                        Update Ticket
                    </button>
                </form>
            </div>
        </div>
    `;
}

// Render notes
function renderNotes(notes) {
    const container = document.getElementById('notes-container');
    
    if (!notes || notes.length === 0) {
        container.innerHTML = `
            <p class="text-gray-500 text-center py-4">No notes yet</p>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="space-y-3">
            ${notes.map((note, index) => `
                <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 slide-in" style="animation-delay: ${index * 0.1}s">
                    <p class="text-gray-700 whitespace-pre-wrap">${escapeHtml(note.note_text)}</p>
                    <p class="text-sm text-gray-400 mt-2">${formatDate(note.created_at)}</p>
                </div>
            `).reverse().join('')}
        </div>
    `;
}

// Update ticket
async function updateTicket(event, ticketId) {
    event.preventDefault();
    
    const status = document.getElementById('update-status').value;
    const note = document.getElementById('update-note').value.trim();
    
    if (!note) {
        showToast('Please add a note when updating', 'error');
        return;
    }
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<span class="spinner inline-block"></span> Updating...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/${ticketId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status, notes: note })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update ticket');
        }
        
        showToast('Ticket updated successfully!');
        
        // Reload ticket details
        setTimeout(() => {
            loadTicketDetail(ticketId);
        }, 500);
        
    } catch (error) {
        showToast(error.message, 'error');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// ============ INITIALIZATION ============

// Initialize based on current page
document.addEventListener('DOMContentLoaded', function() {
    const path = window.location.pathname;
    
    if (path === '/') {
        loadTickets();
    } else if (path.startsWith('/tickets/')) {
        const ticketId = path.split('/tickets/')[1];
        if (ticketId) {
            loadTicketDetail(ticketId);
        }
    }
});