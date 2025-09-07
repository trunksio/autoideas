/**
 * ElevenLabs Voice Agent Integration
 * Simplified version for embedded widget
 */

let conversationContext = {};

/**
 * Initialize voice agent context when workshop is selected
 */
window.initializeVoiceAgent = function(agentConfig) {
    console.log('Voice agent ready with config:', agentConfig);
    
    // Store context for the conversation
    conversationContext = {
        workshop_id: agentConfig.workshop_id,
        agent_id: agentConfig.agent_id,
        questions: agentConfig.questions || []
    };
    
    // Get the ElevenLabs widget element
    const widget = document.querySelector('elevenlabs-convai');
    
    if (widget) {
        // Set up event listeners for the widget if needed
        setupWidgetListeners(widget);
        
        // Update widget with workshop-specific configuration
        if (agentConfig.agent_id && agentConfig.agent_id !== widget.getAttribute('agent-id')) {
            widget.setAttribute('agent-id', agentConfig.agent_id);
        }
    }
};

/**
 * Set up event listeners for the ElevenLabs widget
 */
function setupWidgetListeners(widget) {
    // Listen for custom events from the widget (if supported)
    widget.addEventListener('message', (event) => {
        console.log('Widget message:', event);
        handleWidgetMessage(event.detail);
    });
    
    // Listen for conversation events
    widget.addEventListener('conversationstart', (event) => {
        console.log('Conversation started');
        updateAgentStatus('active');
    });
    
    widget.addEventListener('conversationend', (event) => {
        console.log('Conversation ended');
        updateAgentStatus('idle');
    });
}

/**
 * Handle messages from the widget
 */
function handleWidgetMessage(message) {
    // Extract message content
    const { type, content, metadata } = message || {};
    
    switch (type) {
        case 'transcript':
            // User's speech was transcribed
            console.log('User said:', content);
            // Could send to backend here if needed
            submitTranscriptToBackend(content, metadata);
            break;
            
        case 'response':
            // Agent's response
            console.log('Agent response:', content);
            break;
            
        case 'tool_call':
            // Agent is calling a tool
            console.log('Tool call:', content);
            if (content.tool === 'submit_idea') {
                handleIdeaSubmission(content.parameters);
            }
            break;
            
        default:
            console.log('Unknown message type:', type);
    }
}

/**
 * Submit transcript to the backend
 */
async function submitTranscriptToBackend(transcript, metadata = {}) {
    const userNickname = document.getElementById('user-nickname').value || 'Anonymous';
    
    try {
        const response = await fetch('/api/voice/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                workshop_id: conversationContext.workshop_id || 'caresuper',
                session_id: window.autoIdeasApp?.sessionId || generateSessionId(),
                user_nickname: userNickname,
                question_id: metadata.question_id || 'general',
                transcript: transcript,
                metadata: {
                    ...metadata,
                    timestamp: new Date().toISOString(),
                    source: 'voice_widget'
                }
            })
        });
        
        const result = await response.json();
        console.log('Transcript submitted:', result);
        
        // Show success message
        if (window.autoIdeasApp) {
            window.autoIdeasApp.showStatus('Your idea is being processed', 'success');
        }
        
        return result;
    } catch (error) {
        console.error('Failed to submit transcript:', error);
        if (window.autoIdeasApp) {
            window.autoIdeasApp.showStatus('Failed to submit idea', 'error');
        }
    }
}

/**
 * Handle idea submission from the agent
 */
async function handleIdeaSubmission(parameters) {
    const { transcript, question_id, category } = parameters;
    
    console.log('Submitting idea:', { transcript, question_id, category });
    
    // Submit to backend
    await submitTranscriptToBackend(transcript, {
        question_id,
        category,
        from_agent: true
    });
}

/**
 * Update agent status in UI
 */
function updateAgentStatus(status) {
    const container = document.getElementById('elevenlabs-widget');
    
    if (container) {
        // Add status class
        container.className = `agent-status-${status}`;
    }
    
    // Update app status if available
    if (window.autoIdeasApp) {
        const statusText = status === 'active' ? 'Voice agent active' : 'Voice agent ready';
        window.autoIdeasApp.showStatus(statusText, 'info');
    }
}

/**
 * Generate a session ID if needed
 */
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 15);
}

/**
 * Monitor for widget load
 */
window.addEventListener('DOMContentLoaded', () => {
    // Check if widget is loaded
    const checkWidget = setInterval(() => {
        const widget = document.querySelector('elevenlabs-convai');
        if (widget) {
            console.log('ElevenLabs widget detected');
            clearInterval(checkWidget);
            
            // Initialize with default workshop if available
            const defaultWorkshop = {
                workshop_id: 'caresuper',
                agent_id: 'agent_9901k4jby1pbf7przmt61zskpkfe'
            };
            
            initializeVoiceAgent(defaultWorkshop);
        }
    }, 1000);
    
    // Stop checking after 10 seconds
    setTimeout(() => clearInterval(checkWidget), 10000);
});