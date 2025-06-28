// AIstylist Frontend JavaScript

console.log('app.js loaded');
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded fired');

    // Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // Upload clothing item
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const fileInput = document.getElementById('clothingFile');
            const progressDiv = document.getElementById('uploadProgress');
            
            if (!fileInput || !fileInput.files[0]) {
                alert('Please select a file');
                return;
            }
            
            formData.append('file', fileInput.files[0]);
            
            // Show progress
            if (progressDiv) progressDiv.classList.remove('hidden');
            
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
                if (progressDiv) progressDiv.classList.add('hidden');
            }
        });
    }

    // Generate outfit
    const outfitForm = document.getElementById('outfitForm');
    if (outfitForm) {
        outfitForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const weatherSelect = document.getElementById('weather');
            const occasionSelect = document.getElementById('occasion');
            const progressDiv = document.getElementById('outfitProgress');
            
            if (!weatherSelect || !occasionSelect || !weatherSelect.value || !occasionSelect.value) {
                alert('Please select both weather and occasion');
                return;
            }
            
            // Show progress
            if (progressDiv) progressDiv.classList.remove('hidden');
            
            try {
                const response = await fetch('/generate-outfit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        weather: weatherSelect.value,
                        occasion: occasionSelect.value
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Show result modal
                    const generatedImage = document.getElementById('generatedImage');
                    const resultMessage = document.getElementById('resultMessage');
                    const resultModal = document.getElementById('resultModal');
                    
                    if (generatedImage) generatedImage.src = result.image_url;
                    if (resultMessage) resultMessage.textContent = result.message;
                    if (resultModal) resultModal.classList.remove('hidden');
                    closeOutfitModal();
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Generation failed: ' + error.message);
            } finally {
                if (progressDiv) progressDiv.classList.add('hidden');
            }
        });
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

    const addItemButton = document.getElementById('addItemButton');
    const galleryInput = document.getElementById('closetGalleryInput');
    if (addItemButton && galleryInput) {
        addItemButton.addEventListener('click', function() {
            galleryInput.click();
        });
        galleryInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const modalInput = document.getElementById('clothingFile');
                if (modalInput) {
                    const dt = new DataTransfer();
                    dt.items.add(file);
                    modalInput.files = dt.files;
                }
                openUploadModal();
                setTimeout(() => {
                    const uploadForm = document.getElementById('uploadForm');
                    if (uploadForm) {
                        uploadForm.requestSubmit();
                    }
                }, 300);
            }
        });
    }

    // スワイプ対応（スマホ用）
    const carousel = document.querySelector('.bg-[#F5F0E8]');
    if (!carousel) return;
    let touchStartX = null;
    carousel.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
    });
    carousel.addEventListener('touchend', e => {
        if (touchStartX === null) return;
        let dx = e.changedTouches[0].screenX - touchStartX;
        if (dx > 50) prevOutfit();
        if (dx < -50) nextOutfit();
        touchStartX = null;
    });
});

// Modal functions
function openUploadModal() {
    const fileInput = document.getElementById('clothingFile');
    const modal = document.getElementById('uploadModal');
    if (fileInput && !fileInput.files.length) {
        // ファイル未選択ならファイル選択ダイアログを開く
        fileInput.click();
        // ファイルが選ばれたらモーダルを開く
        fileInput.onchange = function() {
            if (fileInput.files.length && modal) {
                modal.classList.remove('hidden');
            }
        };
    } else if (modal) {
        // すでにファイルが選ばれていればそのままモーダルを開く
        modal.classList.remove('hidden');
    }
}

function closeUploadModal() {
    const modal = document.getElementById('uploadModal');
    const form = document.getElementById('uploadForm');
    const progress = document.getElementById('uploadProgress');
    
    if (modal) modal.classList.add('hidden');
    if (form) form.reset();
    if (progress) progress.classList.add('hidden');
}

function openOutfitModal() {
    const modal = document.getElementById('outfitModal');
    if (modal) {
        modal.classList.remove('hidden');
    }
}

function closeOutfitModal() {
    const modal = document.getElementById('outfitModal');
    const form = document.getElementById('outfitForm');
    const progress = document.getElementById('outfitProgress');
    
    if (modal) modal.classList.add('hidden');
    if (form) form.reset();
    if (progress) progress.classList.add('hidden');
}

function closeResultModal() {
    const modal = document.getElementById('resultModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Upload clothing item
document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('clothingFile');
    const progressDiv = document.getElementById('uploadProgress');
    
    if (!fileInput || !fileInput.files[0]) {
        alert('Please select a file');
        return;
    }
    
    formData.append('file', fileInput.files[0]);
    
    // Show progress
    if (progressDiv) progressDiv.classList.remove('hidden');
    
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
        if (progressDiv) progressDiv.classList.add('hidden');
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
    if (progressDiv) progressDiv.classList.remove('hidden');
    
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
        if (progressDiv) progressDiv.classList.add('hidden');
    }
});

let closetItemsCache = [];

function filterAndDisplayCloset(category) {
    if (category === 'All') {
        updateClosetDisplay(closetItemsCache);
    } else {
        updateClosetDisplay(closetItemsCache.filter(item => item.category === category));
    }
}

// Load closet items
async function loadCloset() {
    try {
        const response = await fetch('/closet');
        const result = await response.json();
        if (result.success) {
            closetItemsCache = result.items;
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
            ${item.image ? `<img src="${item.image}" alt="${item.file.replace('.txt', '')}" class="w-full h-32 object-contain mb-2" />` : ''}
            <h4 class="font-medium text-sm mb-2">${item.file.replace('.txt', '')}</h4>
            <p class="text-xs text-gray-600 mb-2">${item.desc.substring(0, 100)}...</p>
            <span class="inline-block text-xs text-[#9A9A9A] mb-2">${item.category}</span>
            <button class="delete-btn bg-red-500 text-white px-2 py-1 rounded text-xs" data-file="${item.file}">Delete</button>
        `;
        closetContainer.appendChild(itemElement);
    });
    // Add delete event listeners
    closetContainer.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', async function() {
            const file = this.getAttribute('data-file');
            if (confirm(`Delete ${file.replace('.txt', '')}?`)) {
                const res = await fetch('/delete-clothing', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ file })
                });
                const result = await res.json();
                if (result.success) {
                    showNotification('Item deleted', 'success');
                    loadCloset();
                } else {
                    showNotification('Delete failed: ' + (result.error || 'Unknown error'), 'error');
                }
            }
        });
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

// Utility function for notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

function showOutfit(index) {
    const outfitSlides = document.querySelectorAll('.outfit-slide');
    const outfitDots = document.querySelectorAll('.outfit-dots .w-1\\.5');
    outfitSlides.forEach((slide, i) => {
        slide.style.display = (i === index) ? 'flex' : 'none';
        slide.classList.toggle('active', i === index);
    });
    outfitDots.forEach((dot, i) => {
        dot.classList.toggle('bg-[#E8D0D0]', i === index);
        dot.classList.toggle('bg-[#E8E8E8]', i !== index);
    });
    currentOutfitIndex = index;
}

// スワイプ対応（スマホ用）
document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.querySelector('.bg-[#F5F0E8]');
    if (!carousel) return;
    let touchStartX = null;
    carousel.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
    });
    carousel.addEventListener('touchend', e => {
        if (touchStartX === null) return;
        let dx = e.changedTouches[0].screenX - touchStartX;
        if (dx > 50) prevOutfit();
        if (dx < -50) nextOutfit();
        touchStartX = null;
    });
}); 