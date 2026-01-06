/**
 * Survey Admin Application
 * Healthcare AI Research Dashboard
 */

class SurveyAdmin {
    constructor() {
        // API base URL - the admin page is already behind basic auth
        // so we don't need additional API key authentication
        this.baseUrl = window.location.hostname === 'localhost'
            ? 'http://localhost:8080'
            : '/survey/api';
        this.sessions = [];

        this.init();
    }

    init() {
        this.bindElements();
        this.bindEvents();
        this.loadData();
    }

    bindElements() {
        this.statsSection = document.getElementById('stats-section');
        this.actionsSection = document.getElementById('actions-section');
        this.sessionsSection = document.getElementById('sessions-section');
        this.sessionsTbody = document.getElementById('sessions-tbody');
        this.modal = document.getElementById('session-modal');
        this.sessionDetail = document.getElementById('session-detail');
    }

    bindEvents() {
        // Action buttons
        document.getElementById('refresh-btn').addEventListener('click', () => this.loadData());
        document.getElementById('export-csv-btn').addEventListener('click', () => this.exportCSV());
        document.getElementById('export-json-btn').addEventListener('click', () => this.exportJSON());

        // Modal close
        document.getElementById('modal-close').addEventListener('click', () => this.closeModal());
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.closeModal();
        });

        // Keyboard escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeModal();
        });
    }

    async apiRequest(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return response.json();
    }

    async loadData() {
        try {
            const data = await this.apiRequest('/survey/sessions');
            this.sessions = data.sessions || [];

            this.updateStats(data);
            this.renderSessions();
            this.showSections();
        } catch (error) {
            console.error('Failed to load data:', error);
            this.showError('Failed to load data. Please refresh the page.');
        }
    }

    showError(message) {
        this.sessionsTbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; color: var(--highlight-color); padding: 40px;">
                    ${message}
                </td>
            </tr>
        `;
    }

    updateStats(data) {
        const stats = data.stats || {};
        document.getElementById('total-sessions').textContent = stats.total_sessions || 0;
        document.getElementById('completed-sessions').textContent = stats.completed_sessions || 0;
        document.getElementById('in-progress-sessions').textContent = stats.in_progress_sessions || 0;
        document.getElementById('total-answers').textContent = stats.total_answers || 0;
    }

    showSections() {
        this.statsSection.style.display = 'block';
        this.actionsSection.style.display = 'flex';
        this.sessionsSection.style.display = 'block';
    }

    renderSessions() {
        this.sessionsTbody.innerHTML = '';

        if (this.sessions.length === 0) {
            this.sessionsTbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 40px;">
                        No survey sessions yet
                    </td>
                </tr>
            `;
            return;
        }

        this.sessions.forEach(session => {
            const row = document.createElement('tr');
            const isCompleted = !!session.completed_at;

            row.innerHTML = `
                <td title="${session.conversation_id}">${this.truncateId(session.conversation_id)}</td>
                <td>${this.formatDate(session.started_at)}</td>
                <td>
                    <span class="status-badge ${isCompleted ? 'completed' : 'incomplete'}">
                        ${isCompleted ? 'Completed' : 'Incomplete'}
                    </span>
                </td>
                <td>${session.answer_count || 0}</td>
                <td>
                    <button class="btn btn-secondary btn-view" data-id="${session.id}">
                        View Details
                    </button>
                </td>
            `;

            row.querySelector('.btn-view').addEventListener('click', () => {
                this.viewSession(session.id);
            });

            this.sessionsTbody.appendChild(row);
        });
    }

    truncateId(id) {
        if (!id) return '-';
        if (id.length <= 20) return id;
        return id.substring(0, 12) + '...' + id.substring(id.length - 4);
    }

    formatDate(dateStr) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-AU', {
            day: 'numeric',
            month: 'short',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    async viewSession(sessionId) {
        try {
            const data = await this.apiRequest(`/survey/sessions/${sessionId}`);
            this.renderSessionDetail(data);
            this.openModal();
        } catch (error) {
            console.error('Failed to load session:', error);
            alert('Failed to load session details');
        }
    }

    renderSessionDetail(data) {
        const session = data.session;
        const answers = data.answers || [];

        let html = `
            <div class="session-info" style="margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border-color);">
                <p><strong>Conversation ID:</strong> ${session.conversation_id}</p>
                <p><strong>Started:</strong> ${this.formatDate(session.started_at)}</p>
                <p><strong>Completed:</strong> ${session.completed_at ? this.formatDate(session.completed_at) : 'In Progress'}</p>
                <p><strong>Total Answers:</strong> ${answers.length}</p>
            </div>
        `;

        if (answers.length === 0) {
            html += '<p style="color: var(--text-muted);">No answers recorded yet.</p>';
        } else {
            // Group by section
            const sections = {};
            answers.forEach(answer => {
                const section = answer.section_name || 'General';
                if (!sections[section]) sections[section] = [];
                sections[section].push(answer);
            });

            for (const [sectionName, sectionAnswers] of Object.entries(sections)) {
                sectionAnswers.forEach(answer => {
                    html += `
                        <div class="answer-card">
                            <div class="answer-section">${sectionName}</div>
                            <div class="answer-question">${answer.question_text || answer.question_id}</div>
                            ${this.renderAnswer(answer)}
                            <div class="answer-meta">Answered: ${this.formatDate(answer.answered_at)}</div>
                        </div>
                    `;
                });
            }
        }

        this.sessionDetail.innerHTML = html;
    }

    renderAnswer(answer) {
        if (answer.answer_rating !== null && answer.answer_rating !== undefined) {
            return `<div class="answer-rating">${answer.answer_rating} / 5</div>`;
        }
        if (answer.answer_choices && answer.answer_choices.length > 0) {
            return `<div class="answer-text">${answer.answer_choices.join(', ')}</div>`;
        }
        return `<div class="answer-text">${answer.answer_text || '-'}</div>`;
    }

    openModal() {
        this.modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closeModal() {
        this.modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    async exportCSV() {
        try {
            const response = await fetch(`${this.baseUrl}/survey/export?format=csv`);
            if (!response.ok) throw new Error('Export failed');

            const blob = await response.blob();
            this.downloadBlob(blob, `survey-export-${this.getDateStamp()}.csv`);
        } catch (error) {
            console.error('CSV export failed:', error);
            alert('Failed to export CSV');
        }
    }

    async exportJSON() {
        try {
            const response = await fetch(`${this.baseUrl}/survey/export?format=json`);
            if (!response.ok) throw new Error('Export failed');

            const blob = await response.blob();
            this.downloadBlob(blob, `survey-export-${this.getDateStamp()}.json`);
        } catch (error) {
            console.error('JSON export failed:', error);
            alert('Failed to export JSON');
        }
    }

    downloadBlob(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    getDateStamp() {
        const now = new Date();
        return now.toISOString().split('T')[0];
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    window.surveyAdmin = new SurveyAdmin();
});
