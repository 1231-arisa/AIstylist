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
    const outfits = [
        {
            name: "Casual Chic",
            weather: "Sunny, 72°F",
            occasion: "Casual Day Out"
        },
        {
            name: "Office Ready",
            weather: "Sunny, 72°F",
            occasion: "Work Day"
        },
        {
            name: "Evening Casual",
            weather: "Clear, 68°F",
            occasion: "Dinner with Friends"
        },
        {
            name: "Weekend Comfort",
            weather: "Partly Cloudy, 70°F",
            occasion: "Weekend Errands"
        }
    ];
    
    let activeOutfit = 0;
    const outfitSlides = document.querySelectorAll('.outfit-slide');
    const outfitDots = document.querySelectorAll('.outfit-dots div');
    const nameEl = document.querySelector('.outfit-name');
    const weatherEl = document.querySelector('.outfit-weather');
    const occasionEl = document.querySelector('.outfit-occasion');
    
    function updateOutfit() {
        outfitSlides.forEach((slide, index) => {
            slide.classList.toggle('active', index === activeOutfit);
        });
        
        outfitDots.forEach((dot, index) => {
            dot.classList.toggle('bg-[#E8D0D0]', index === activeOutfit);
            dot.classList.toggle('bg-[#E8E8E8]', index !== activeOutfit);
        });
        
        nameEl.textContent = outfits[activeOutfit].name;
        weatherEl.textContent = outfits[activeOutfit].weather;
        occasionEl.textContent = outfits[activeOutfit].occasion;
    }
    
    window.nextOutfit = function() {
        activeOutfit = (activeOutfit + 1) % outfits.length;
        updateOutfit();
    };
    
    window.prevOutfit = function() {
        activeOutfit = (activeOutfit - 1 + outfits.length) % outfits.length;
        updateOutfit();
    };
    
    // Initialize outfit
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
