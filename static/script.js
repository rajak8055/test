class NLPSQLChatbot {
    constructor() {
        this.messagesContainer = document.getElementById('chat-messages');
        this.inputField = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.statusDot = document.querySelector('.status-dot');
        this.statusText = document.querySelector('.status-text');
        
        this.messageId = 0;
        this.isLoading = false;
        
        this.init();
    }
    
    async init() {
        // Event listeners
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Load database schema
        await this.loadDatabaseSchema();
        
        // Check system health
        await this.checkSystemHealth();
        
        // Add welcome message
        this.addMessage('assistant', 'Hello! I\'m your NLP to SQL assistant. Ask me questions about your database, and I\'ll convert them to SQL queries and show you the results.', null, null, null);
    }
    
    async checkSystemHealth() {
        try {
            const response = await fetch('/health');
            const health = await response.json();
            
            if (health.database_connected) {
                this.updateStatus('connected', 'Database Connected');
            } else {
                this.updateStatus('disconnected', 'Database Disconnected');
            }
        } catch (error) {
            console.error('Health check failed:', error);
            this.updateStatus('disconnected', 'System Error');
        }
    }
    
    updateStatus(status, text) {
        this.statusDot.className = `status-dot ${status === 'disconnected' ? 'disconnected' : ''}`;
        this.statusText.textContent = text;
    }
    
    async loadDatabaseSchema() {
        try {
            const response = await fetch('/api/schema');
            const data = await response.json();
            
            if (data.success) {
                this.renderSchema(data.tables);
            } else {
                console.error('Failed to load schema:', data.error);
                this.showSchemaError(data.error);
            }
        } catch (error) {
            console.error('Schema loading error:', error);
            this.showSchemaError('Failed to connect to database');
        }
    }
    
    renderSchema(tables) {
        const schemaContainer = document.getElementById('schema-container');
        
        if (!tables || tables.length === 0) {
            schemaContainer.innerHTML = '<p class="text-secondary">No tables found in database</p>';
            return;
        }
        
        const html = tables.map(table => `
            <div class="table-item">
                <div class="table-header" onclick="this.parentElement.querySelector('.columns-list').classList.toggle('expanded'); this.querySelector('.toggle-icon').classList.toggle('expanded')">
                    <span class="table-name">${this.escapeHtml(table.table_name)}</span>
                    <span class="toggle-icon">▶</span>
                </div>
                <div class="columns-list">
                    ${table.columns.map(column => `
                        <div class="column-item">
                            <span class="column-name">${this.escapeHtml(column.column_name)}</span>
                            <span class="column-type">${this.escapeHtml(column.data_type)}</span>
                            ${column.constraint_type ? `<span class="column-constraints">${this.escapeHtml(column.constraint_type)}</span>` : ''}
                            ${column.is_nullable === 'NO' ? '<span class="column-constraints">NOT NULL</span>' : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
        
        schemaContainer.innerHTML = html;
    }
    
    showSchemaError(error) {
        const schemaContainer = document.getElementById('schema-container');
        schemaContainer.innerHTML = `
            <div class="error-message">
                <strong>Schema Error:</strong> ${this.escapeHtml(error)}
            </div>
        `;
    }
    
    async sendMessage() {
        if (this.isLoading) return;
        
        const message = this.inputField.value.trim();
        if (!message) return;
        
        // Add user message
        this.addMessage('user', message);
        this.inputField.value = '';
        
        // Show loading
        this.setLoading(true);
        const loadingMessage = this.addMessage('assistant', '', null, null, null, true);
        
        try {
            // Send to backend
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: message,
                    context: null
                })
            });
            
            const data = await response.json();
            
            // Remove loading message
            this.removeMessage(loadingMessage);
            
            if (data.success) {
                this.addMessage('assistant', 'Here\'s the SQL query and results:', data.sql_query, data.results, data.execution_time);
            } else {
                this.addMessage('assistant', `Error: ${data.error}`, data.sql_query || null, null, null);
            }
            
        } catch (error) {
            console.error('Query error:', error);
            this.removeMessage(loadingMessage);
            this.addMessage('assistant', `Network error: ${error.message}`, null, null, null);
        } finally {
            this.setLoading(false);
        }
    }
    
    addMessage(sender, content, sqlQuery = null, results = null, executionTime = null, isLoading = false) {
        const messageId = ++this.messageId;
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.dataset.messageId = messageId;
        
        let messageHTML = '';
        
        if (isLoading) {
            messageHTML = `
                <div class="message-content">
                    <div class="loading">
                        <div class="loading-spinner"></div>
                        Processing your query...
                    </div>
                </div>
            `;
        } else {
            messageHTML = `
                <div class="message-content">${this.escapeHtml(content)}</div>
            `;
            
            if (sqlQuery) {
                messageHTML += `
                    <div class="sql-query">
                        <button class="copy-button" onclick="this.parentElement.querySelector('code').select(); document.execCommand('copy')">Copy</button>
                        <code>${this.escapeHtml(sqlQuery)}</code>
                    </div>
                `;
            }
            
            if (results && results.length > 0) {
                messageHTML += this.renderResultsTable(results);
            } else if (results && results.length === 0) {
                messageHTML += '<div class="text-secondary mt-2">No results found.</div>';
            }
            
            const timestamp = new Date().toLocaleTimeString();
            let metaInfo = timestamp;
            if (executionTime) {
                metaInfo += ` • Executed in ${executionTime.toFixed(3)}s`;
            }
            
            messageHTML += `
                <div class="message-meta">
                    <span>${metaInfo}</span>
                </div>
            `;
        }
        
        messageDiv.innerHTML = messageHTML;
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageId;
    }
    
    removeMessage(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            messageElement.remove();
        }
    }
    
    renderResultsTable(results) {
        if (!results || results.length === 0) {
            return '<div class="text-secondary">No results found.</div>';
        }
        
        const columns = Object.keys(results[0]);
        
        let tableHTML = `
            <div class="results-table">
                <table>
                    <thead>
                        <tr>
                            ${columns.map(col => `<th>${this.escapeHtml(col)}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        results.forEach(row => {
            tableHTML += '<tr>';
            columns.forEach(col => {
                const value = row[col];
                const displayValue = value === null ? '<em>NULL</em>' : this.escapeHtml(String(value));
                tableHTML += `<td>${displayValue}</td>`;
            });
            tableHTML += '</tr>';
        });
        
        tableHTML += `
                    </tbody>
                </table>
            </div>
        `;
        
        return tableHTML;
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        this.sendButton.disabled = loading;
        this.inputField.disabled = loading;
        
        if (loading) {
            this.sendButton.textContent = 'Sending...';
        } else {
            this.sendButton.textContent = 'Send';
        }
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Example queries suggestions
const exampleQueries = [
    "Show me all tables in the database",
    "What are the latest 10 records from the users table?",
    "Find all orders placed in the last 7 days",
    "Show me the total sales by month",
    "Which products have low inventory?",
    "List all customers from New York",
    "What's the average order value?",
    "Show me orders with their customer information"
];

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new NLPSQLChatbot();
    
    // Add example queries to the interface
    const examplesList = document.getElementById('examples-list');
    if (examplesList) {
        examplesList.innerHTML = exampleQueries.map(query => 
            `<div class="example-query" onclick="document.getElementById('message-input').value='${query}'">${query}</div>`
        ).join('');
    }
});

// Add copy functionality for SQL queries
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('copy-button')) {
        const codeElement = e.target.parentElement.querySelector('code');
        if (codeElement) {
            navigator.clipboard.writeText(codeElement.textContent).then(() => {
                e.target.textContent = 'Copied!';
                setTimeout(() => {
                    e.target.textContent = 'Copy';
                }, 2000);
            });
        }
    }
});

// Handle window resize
window.addEventListener('resize', () => {
    if (window.chatbot) {
        window.chatbot.scrollToBottom();
    }
});
