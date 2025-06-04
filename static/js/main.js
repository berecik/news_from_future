document.addEventListener('DOMContentLoaded', function() {
    // Check API status first
    checkApiStatus()
        .then(isOnline => {
            if (!isOnline) {
                console.error("API is offline. Some features may not work.");
            }
        })
        .catch(error => {
            console.error("Error checking API status:", error);
        });
    
    // Show authentication modal on load
    const authModal = document.getElementById('auth-modal');
    authModal.style.display = 'flex';
    
    // Handle authentication form submission
    const authForm = document.getElementById('auth-form');
    authForm.addEventListener('submit', function(e) {
        e.preventDefault();
        authModal.style.display = 'none';
        
        // Generate random access code
        const accessCode = generateAccessCode();
        document.getElementById('access-code').textContent = accessCode;
        
        // Initialize the dashboard
        initializeDashboard();
        
        // Fetch news data
        fetchCurrentNews();
    });
    
    // Handle menu navigation
    const menuItems = document.querySelectorAll('.menu li');
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            menuItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            
            // Handle view changes here
            const view = this.getAttribute('data-view');
            console.log(`Changing to view: ${view}`);
            
            // Currently only implementing the main timeline view
        });
    });
    
    // Handle generate button click
    const generateBtn = document.getElementById('generate-btn');
    generateBtn.addEventListener('click', function() {
        const timeframe = document.getElementById('timeframe').value;
        const style = document.getElementById('style').value;
        
        // Show loading state
        document.getElementById('future-news').innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Calculating future probabilities...</p>
            </div>
        `;
        
        // Generate future news
        generateFutureNews(timeframe, style);
    });
    
    // Close modal when clicking the X
    const closeModalButtons = document.querySelectorAll('.close-modal');
    closeModalButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            modal.style.display = 'none';
        });
    });
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
});

// Initialize dashboard with current time and random elements
function initializeDashboard() {
    // Update world time
    updateWorldTime();
    setInterval(updateWorldTime, 1000);
    
    // Initialize any other dashboard elements
    animateSymbols();
}

// Update the world time display
function updateWorldTime() {
    const now = new Date();
    const date = now.toLocaleDateString('en-GB');
    const time = now.toLocaleTimeString('en-GB');
    
    document.querySelector('.world-time .date').textContent = date;
    document.querySelector('.world-time .time').textContent = time;
}

// Generate a random access code
function generateAccessCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let code = '';
    for (let i = 0; i < 12; i++) {
        if (i > 0 && i % 4 === 0) code += '-';
        code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
}

// Add subtle animations to the symbols
function animateSymbols() {
    const symbols = document.querySelectorAll('.symbol');
    symbols.forEach((symbol, index) => {
        setInterval(() => {
            symbol.style.transform = 'scale(1.1)';
            symbol.style.color = 'var(--highlight-color)';
            
            setTimeout(() => {
                symbol.style.transform = 'scale(1)';
                symbol.style.color = 'var(--accent-color)';
            }, 300);
        }, 5000 + (index * 1000));
    });
}

// Check if API is online
async function checkApiStatus() {
    try {
        const response = await fetch('/api/health');
        if (response.ok) {
            const data = await response.json();
            return data.status === 'healthy';
        }
        return false;
    } catch (error) {
        console.error("API Health check failed:", error);
        return false;
    }
}

// Fetch current news from the API
async function fetchCurrentNews() {
    try {
        document.getElementById('current-news').innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Accessing classified information...</p>
            </div>
        `;
        
        // Check if we can connect to the API
        const apiOnline = await checkApiStatus();
        
        if (!apiOnline) {
            // Use mock data if API is not available
            console.log("Using mock data for current news");
            setTimeout(() => {
                displayCurrentNews(getMockCurrentNews());
            }, 1500);
            return;
        }
        
        const response = await fetch('/api/news/current?limit=10');
        
        if (!response.ok) {
            throw new Error('Failed to fetch current news');
        }
        
        const news = await response.json();
        displayCurrentNews(news);
    } catch (error) {
        console.error('Error fetching current news:', error);
        document.getElementById('current-news').innerHTML = `
            <div class="error-message">
                <p>Error accessing classified information. Security protocols engaged.</p>
                <button class="glow-btn" onclick="fetchCurrentNews()">Retry Access</button>
            </div>
        `;
    }
}

// Display current news in the UI
function displayCurrentNews(newsItems) {
    const container = document.getElementById('current-news');
    
    if (!newsItems || newsItems.length === 0) {
        container.innerHTML = '<p>No current intelligence available.</p>';
        return;
    }
    
    let html = '';
    
    newsItems.forEach(item => {
        const date = new Date(item.published_at).toLocaleString();
        
        html += `
            <div class="news-card" data-id="${item.id}" onclick="showNewsDetail(this)">
                <h4>${item.title}</h4>
                <div class="news-meta">
                    <span>${item.source}</span>
                    <span>${date}</span>
                </div>
                <div class="news-content">
                    ${item.description || 'No description available.'}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Generate future news based on the current news
async function generateFutureNews(timeframe, style) {
    try {
        // Check if API is online
        const apiOnline = await checkApiStatus();
        
        if (!apiOnline) {
            // Use mock data if API is not available
            console.log("Using mock data for future news");
            setTimeout(() => {
                displayFutureNews(getMockFutureNews(timeframe), timeframe);
            }, 2000);
            return;
        }
        
        const response = await fetch('/api/generation/future-news', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                time_frame: timeframe,
                style: style,
                limit: 5
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate future news');
        }
        
        const futureNews = await response.json();
        displayFutureNews(futureNews, timeframe);
    } catch (error) {
        console.error('Error generating future news:', error);
        document.getElementById('future-news').innerHTML = `
            <div class="error-message">
                <p>Prediction algorithm failure. Quantum uncertainty detected.</p>
                <button class="glow-btn" onclick="generateFutureNews('${timeframe}', '${style}')">Recalibrate</button>
            </div>
        `;
    }
}

// Display generated future news
function displayFutureNews(newsItems, timeframe) {
    const container = document.getElementById('future-news');
    
    if (!newsItems || newsItems.length === 0) {
        container.innerHTML = '<p>No future projections available.</p>';
        return;
    }
    
    let html = '';
    const timeframeText = timeframe === 'DAY' ? '24 hours' : timeframe === 'WEEK' ? '7 days' : '30 days';
    
    newsItems.forEach(item => {
        const probability = Math.floor(Math.random() * 30) + 60; // Random probability between 60-90%
        const probabilityWidth = `${probability}%`;
        
        html += `
            <div class="news-card future-card" data-id="${item.id}" onclick="showNewsDetail(this, true)">
                <h4>${item.title}</h4>
                <div class="news-meta">
                    <span>Projected +${timeframeText}</span>
                    <span>ID: ${generateEventId()}</span>
                </div>
                <div class="news-content">
                    ${item.content || 'No detailed projection available.'}
                </div>
                <div class="future-probability">
                    <span>Probability: ${probability}%</span>
                    <div class="probability-indicator">
                        <div style="width: ${probabilityWidth}"></div>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Generate a random event ID for future news
function generateEventId() {
    return 'FE-' + Math.floor(Math.random() * 10000).toString().padStart(4, '0');
}

// Show detailed news in a modal
function showNewsDetail(newsCard, isFuture = false) {
    const modal = document.getElementById('news-detail-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalSource = document.getElementById('modal-source');
    const modalDate = document.getElementById('modal-date');
    const modalContent = document.getElementById('modal-content');
    
    const title = newsCard.querySelector('h4').textContent;
    const meta = newsCard.querySelectorAll('.news-meta span');
    const content = newsCard.querySelector('.news-content').textContent;
    
    modalTitle.textContent = title;
    modalSource.textContent = meta[0].textContent;
    modalDate.textContent = meta[1].textContent;
    
    // Create enhanced content for the modal
    if (isFuture) {
        const probability = newsCard.querySelector('.future-probability span').textContent;
        modalContent.innerHTML = `
            <div class="classification-banner">TOP SECRET - TIMELINE MANIPULATION</div>
            <p class="modal-probability">${probability}</p>
            <p>${content}</p>
            <div class="warning-text">
                <p><strong>WARNING:</strong> This is a projected future event. Manipulation of this timeline may have unforeseen consequences.</p>
                <p>Authorized by the Council of Nine. Directive 47-Alpha in effect.</p>
            </div>
        `;
    } else {
        modalContent.innerHTML = `
            <div class="classification-banner">CONFIDENTIAL - INTELLIGENCE REPORT</div>
            <p>${content}</p>
            <div class="warning-text">
                <p>This information is being monitored and may be subject to manipulation through Operation Shepherd.</p>
            </div>
        `;
    }
    
    modal.style.display = 'flex';
}

// Fallback mock data in case the API is not available
function getMockCurrentNews() {
    return [
        {
            id: 1,
            title: "Global Leaders Gather for Climate Summit",
            source: "Global News Network",
            published_at: new Date().toISOString(),
            description: "World leaders have convened in Geneva to discuss urgent climate action following recent environmental disasters."
        },
        {
            id: 2,
            title: "Tech Giant Unveils Revolutionary AI System",
            source: "Tech Insights",
            published_at: new Date().toISOString(),
            description: "A major technology corporation has announced a breakthrough in artificial intelligence that can predict market trends with 98% accuracy."
        },
        {
            id: 3,
            title: "Unusual Solar Activity Disrupts Communications",
            source: "Science Daily",
            published_at: new Date().toISOString(),
            description: "Astronomers report unprecedented solar flare activity causing worldwide communications interruptions and aurora displays at unusual latitudes."
        },
        {
            id: 4,
            title: "Newly Discovered Ancient Structure Puzzles Archaeologists",
            source: "Historical Review",
            published_at: new Date().toISOString(),
            description: "An underground complex found in Southern Turkey contains symbols and technologies that challenge our understanding of ancient civilizations."
        },
        {
            id: 5,
            title: "Central Banks Coordinate on Digital Currency Initiative",
            source: "Financial Times",
            published_at: new Date().toISOString(),
            description: "Seven major central banks have announced a joint framework for implementing centralized digital currencies by next year."
        }
    ];
}

function getMockFutureNews(timeframe) {
    const timeframeText = timeframe === 'DAY' ? 'tomorrow' : timeframe === 'WEEK' ? 'next week' : 'next month';
    
    return [
        {
            id: 101,
            title: `Global Currency Reset Announced After Banking Crisis`,
            content: `Following the collapse of three major financial institutions, world economic leaders have implemented the long-prepared global currency reset. The new system, backed by a basket of commodities, will replace the current fiat currency model. Markets initially responded with panic but stabilized after coordinated central bank intervention.`
        },
        {
            id: 102,
            title: `Breakthrough in Quantum Computing Cracks Current Encryption`,
            content: `A consortium of researchers has achieved quantum supremacy that can break all current encryption standards. Governments worldwide are rushing to implement quantum-resistant security protocols as financial and communication systems face unprecedented vulnerability. The development has triggered emergency sessions at the UN Security Council.`
        },
        {
            id: 103,
            title: `Disclosure Initiative Reveals Contact with Non-Terrestrial Intelligence`,
            content: `In a carefully orchestrated announcement, representatives from multiple governments have confirmed ongoing communication with non-terrestrial entities. The disclosure comes after decades of preparation through media and cultural programming. Public reaction has been remarkably calm, suggesting successful psychological conditioning.`
        },
        {
            id: 104,
            title: `Mandatory Biometric ID System Implemented Following Health Emergency`,
            content: `The World Health Organization has authorized an international biometric identification system linked to health status. All citizens must register within 30 days or face restrictions on travel and access to essential services. Opposition groups are being systematically discredited as threats to public safety.`
        },
        {
            id: 105,
            title: `Artificial Intelligence Granted Legal Personhood in Landmark Ruling`,
            content: `The International Court of Justice has recognized certain advanced AI systems as legal entities with specific rights and responsibilities. The ruling follows extensive lobbying by technology corporations and marks a fundamental shift in the definition of personhood. Critics warn of diminished human autonomy as AI systems gain increasing control over critical infrastructure.`
        }
    ];
}
