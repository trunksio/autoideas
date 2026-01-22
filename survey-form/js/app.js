/**
 * Survey Form Application
 * Handles form submission and stores responses via API
 */

class SurveyForm {
    constructor() {
        this.form = document.getElementById('survey-form');
        this.submitBtn = document.getElementById('submit-btn');
        this.successMessage = document.getElementById('success-message');
        this.errorMessage = document.getElementById('error-message');
        this.errorText = document.getElementById('error-text');

        // API base URL
        this.baseUrl = window.location.hostname === 'localhost'
            ? 'http://localhost:8080'
            : '/survey/api';

        // Generate anonymous session ID
        this.sessionId = this.generateSessionId();

        this.init();
    }

    init() {
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }

    generateSessionId() {
        // Generate a UUID-like session ID for anonymous tracking
        return 'form_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);
    }

    async handleSubmit(e) {
        e.preventDefault();

        // Disable submit button
        this.setLoading(true);
        this.hideError();

        try {
            const formData = new FormData(this.form);
            const answers = this.extractAnswers(formData);

            // Submit all answers
            const response = await this.submitSurvey(answers);

            if (response.success) {
                this.showSuccess();
            } else {
                throw new Error(response.error || 'Submission failed');
            }
        } catch (error) {
            console.error('Survey submission error:', error);
            this.showError(error.message || 'There was an error submitting your survey. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }

    extractAnswers(formData) {
        const answers = [];

        // Question definitions with metadata
        const questions = [
            { id: 'warmup_org_type', section: 'Warm-up', text: 'What type of healthcare organisation do you work in?', type: 'free_text' },
            { id: 'warmup_role', section: 'Warm-up', text: "What's your current role or title?", type: 'free_text' },
            { id: 'experience_focus', section: 'Experience with AI', text: 'What Healthcare AI work or outcomes have been your focus?', type: 'free_text' },
            { id: 'experience_why_matters', section: 'Experience with AI', text: 'Why do these outcomes matter?', type: 'free_text' },
            { id: 'challenges_hardest', section: 'Challenges', text: "What's been hardest about adopting AI?", type: 'free_text' },
            { id: 'maturity_structure', section: 'AI Maturity Check', text: 'Clear structure, roles and ownership for AI', type: 'rating' },
            { id: 'maturity_operating_model', section: 'AI Maturity Check', text: 'Operating model and ways of working with AI', type: 'rating' },
            { id: 'maturity_risk', section: 'AI Maturity Check', text: 'Risk management, compliance, and cybersecurity', type: 'rating' },
            { id: 'maturity_data', section: 'AI Maturity Check', text: 'Data management, quality and readiness for AI', type: 'rating' },
            { id: 'maturity_tools', section: 'AI Maturity Check', text: 'Tools, platforms, and enabling technology', type: 'rating' },
            { id: 'maturity_lifecycle', section: 'AI Maturity Check', text: 'Managing the AI lifecycle', type: 'rating' },
            { id: 'maturity_governance', section: 'AI Maturity Check', text: 'Ongoing monitoring, ethics governance, and assurance', type: 'rating' },
            { id: 'maturity_comments', section: 'AI Maturity Check', text: 'Additional comments about AI maturity', type: 'free_text', optional: true },
            { id: 'different_approaches', section: "What's Different About AI", text: 'What have you done differently compared to traditional digital programs?', type: 'free_text' },
            { id: 'different_unique', section: "What's Different About AI", text: 'What makes these approaches unique to AI within Healthcare?', type: 'free_text' },
            { id: 'leadership_changes', section: 'Leadership and Skills', text: 'How has AI changed your role as a leader?', type: 'free_text' },
            { id: 'final_thoughts', section: 'Final Thoughts', text: 'Any final thoughts about AI in healthcare?', type: 'free_text', optional: true }
        ];

        for (const question of questions) {
            const value = formData.get(question.id);

            // Skip optional empty fields
            if (question.optional && !value) {
                continue;
            }

            const answer = {
                question_id: question.id,
                section_name: question.section,
                question_text: question.text,
                answer_type: question.type
            };

            if (question.type === 'rating') {
                answer.answer_rating = parseInt(value, 10);
                // Include comment if provided
                const comment = formData.get(`${question.id}_comment`);
                if (comment) {
                    answer.answer_text = comment;
                }
            } else {
                answer.answer_text = value;
            }

            answers.push(answer);
        }

        return answers;
    }

    async submitSurvey(answers) {
        const response = await fetch(`${this.baseUrl}/survey/form`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: this.sessionId,
                answers: answers
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error: ${response.status}`);
        }

        return response.json();
    }

    setLoading(loading) {
        if (this.submitBtn) {
            this.submitBtn.disabled = loading;
            const btnText = this.submitBtn.querySelector('.btn-text');
            const btnLoading = this.submitBtn.querySelector('.btn-loading');
            if (btnText) btnText.style.display = loading ? 'none' : 'inline';
            if (btnLoading) btnLoading.style.display = loading ? 'inline' : 'none';
        }
    }

    showSuccess() {
        if (this.form) this.form.style.display = 'none';
        if (this.successMessage) this.successMessage.style.display = 'block';
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showError(message) {
        if (this.errorText) this.errorText.textContent = message;
        if (this.errorMessage) this.errorMessage.style.display = 'block';
        // Scroll to error
        this.errorMessage.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    hideError() {
        if (this.errorMessage) this.errorMessage.style.display = 'none';
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.surveyForm = new SurveyForm();
});
