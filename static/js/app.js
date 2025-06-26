// AIstylist Frontend JavaScript

// Modal functions
function openUploadModal() {
    document.getElementById('uploadModal').classList.remove('hidden');
}

function closeUploadModal() {
    document.getElementById('uploadModal').classList.add('hidden');
    document.getElementById('uploadForm').reset();
    document.getElementById('uploadProgress').classList.add('hidden');
}

function openOutfitModal() {
    document.getElementById('outfitModal').classList.remove('hidden');
}

function closeOutfitModal() {
    document.getElementById('outfitModal').classList.add('hidden');
    document.getElementById('outfitForm').reset();
    document.getElementById('outfitProgress').classList.add('hidden');
}

function closeResultModal() {
    document.getElementById('resultModal').classList.add('hidden');
}

// Upload clothing item
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('clothingFile');
    const progressDiv = document.getElementById('uploadProgress');
    
    if (!fileInput.files[0]) {
        alert('Please select a file');
        return;
    }
    
    formData.append('file', fileInput.files[0]);
    
    // Show progress
    progressDiv.classList.remove('hidden');
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Clothing item analyzed successfully!');
            closeUploadModal();
            // Optionally refresh the closet view
            loadCloset();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Upload failed: ' + error.message);
    } finally {
        progressDiv.classList.add('hidden');
    }
});

// Generate outfit
document.getElementById('outfitForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const weather = document.getElementById('weather').value;
    const occasion = document.getElementById('occasion').value;
    const progressDiv = document.getElementById('outfitProgress');
    
    if (!weather || !occasion) {
        alert('Please select both weather and occasion');
        return;
    }
    
    // Show progress
    progressDiv.classList.remove('hidden');
    
    try {
        const response = await fetch('/generate-outfit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                weather: weather,
                occasion: occasion
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Show result modal
            document.getElementById('generatedImage').src = result.image_url;
            document.getElementById('resultMessage').textContent = result.message;
            document.getElementById('resultModal').classList.remove('hidden');
            closeOutfitModal();
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('Generation failed: ' + error.message);
    } finally {
        progressDiv.classList.add('hidden');
    }
});

// Load closet items
async function loadCloset() {
    try {
        const response = await fetch('/closet');
        const result = await response.json();
        
        if (result.success) {
            // Update closet display
            updateClosetDisplay(result.items);
        } else {
            console.error('Failed to load closet:', result.error);
        }
    } catch (error) {
        console.error('Error loading closet:', error);
    }
}

// Update closet display
function updateClosetDisplay(items) {
    const closetContainer = document.querySelector('[data-tab="closet"] .closet-grid');
    if (!closetContainer) return;
    
    closetContainer.innerHTML = '';
    
    items.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'closet-item bg-white rounded-lg p-4 shadow-sm';
        itemElement.innerHTML = `
            <h4 class="font-medium text-sm mb-2">${item.file.replace('.txt', '')}</h4>
            <p class="text-xs text-gray-600">${item.desc.substring(0, 100)}...</p>
        `;
        closetContainer.appendChild(itemElement);
    });
}

// Tab switching
function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    // Show selected tab content
    const selectedTab = document.querySelector(`[data-tab="${tabName}"]`);
    if (selectedTab) {
        selectedTab.classList.remove('hidden');
    }
    
    // Update active tab indicator
    document.querySelectorAll('.tab-indicator').forEach(indicator => {
        indicator.classList.remove('bg-[#333333]', 'text-white');
        indicator.classList.add('bg-[#F5F0E8]', 'text-[#9A9A9A]');
    });
    
    const activeIndicator = document.querySelector(`[data-tab="${tabName}"] .tab-indicator`);
    if (activeIndicator) {
        activeIndicator.classList.remove('bg-[#F5F0E8]', 'text-[#9A9A9A]');
        activeIndicator.classList.add('bg-[#333333]', 'text-white');
    }
    
    // Load data for specific tabs
    if (tabName === 'closet') {
        loadCloset();
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Set default tab
    switchTab('home');
    
    // Add tab click handlers
    document.querySelectorAll('[data-tab]').forEach(tab => {
        tab.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Close modals when clicking outside
    document.querySelectorAll('.fixed').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.add('hidden');
            }
        });
    });
});

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
} 