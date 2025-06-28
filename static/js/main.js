document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    lucide.createIcons();
    
    // Tab switching
    const tabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            
            // Update active tab
            tabs.forEach(t => {
                t.classList.remove('active');
                t.classList.add('text-[#9A9A9A]');
            });
            tab.classList.add('active');
            tab.classList.remove('text-[#9A9A9A]');
            tab.classList.add('text-[#E8D0D0]');
            
            // Show active content and manage add button visibility
            tabContents.forEach(content => {
                content.classList.add('hidden');
                if (content.dataset.tab === tabName) {
                    content.classList.remove('hidden');
                    // Ensure the add button container is visible in closet view
                    if (tabName === 'closet') {
                        const addButton = document.querySelector('.add-item-button-container');
                        if (addButton) {
                            addButton.style.display = 'block';
                            addButton.style.zIndex = '9999';
                        }
                    }
                }
            });
        });
    });
    
    // Outfit carousel
    const outfits = window.outfits || [];
    let activeOutfit = 0;
    const slides = document.querySelectorAll('.outfit-slide');
    
    function updateOutfit() {
        slides.forEach((slide, idx) => {
            slide.style.display = (idx === activeOutfit) ? '' : 'none';
        });
    }
    
    window.nextOutfit = function() {
        activeOutfit = (activeOutfit + 1) % outfits.length;
        updateOutfit();
    };
    
    window.prevOutfit = function() {
        activeOutfit = (activeOutfit - 1 + outfits.length) % outfits.length;
        updateOutfit();
    };
    
    updateOutfit();
    
    // Closet filtering
    const categoryBtns = document.querySelectorAll('.category-btn');
    const closetItems = document.querySelectorAll('.closet-item');
    
    categoryBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const category = btn.dataset.category;
            
            // Update active category button
            categoryBtns.forEach(b => {
                b.classList.remove('bg-[#E8D0D0]', 'text-[#333333]', 'border-[#E8D0D0]');
                b.classList.add('bg-transparent', 'text-[#9A9A9A]', 'border-[#E8E8E8]');
            });
            btn.classList.remove('bg-transparent', 'text-[#9A9A9A]', 'border-[#E8E8E8]');
            btn.classList.add('bg-[#E8D0D0]', 'text-[#333333]', 'border-[#E8D0D0]');
            
            // Filter items
            closetItems.forEach(item => {
                if (category === 'All' || item.dataset.category === category) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
});
