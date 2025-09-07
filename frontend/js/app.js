/**
 * AutoIdeas Simplified App
 * No backend dependencies - just the voice agent and Miro board
 */

class AutoIdeasApp {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.init();
    }
    
    async init() {
        console.log('AutoIdeas App initialized');
        console.log('Session ID:', this.sessionId);
    }
    
    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.autoIdeasApp = new AutoIdeasApp();
});