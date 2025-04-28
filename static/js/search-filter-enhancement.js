/**
 * Enhanced Filter System Script
 * Provides modern interactive filtering for the inventory management system
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get filter elements
    const levelFilter = document.getElementById('levelFilter');
    const itemFilter = document.getElementById('itemTypeFilter');
    const sizeFilter = document.getElementById('sizeFilter');
    const stockFilter = document.getElementById('stockFilter');
    const resetFiltersBtn = document.getElementById('resetFilters');
    const filterBadge = document.querySelector('.filter-badge');
    const filterCount = document.querySelector('.filter-count');
    const filterTitle = document.querySelector('.filter-title');
    const filterTabs = document.querySelector('.filter-tabs');
    const filterContainer = document.querySelector('.filter-container');
    const filterToggleBtn = document.getElementById('filterToggleBtn');
    const filterSelects = document.querySelectorAll('.filter-select');
    const customSelects = document.querySelectorAll('.custom-select');
    const inventoryCards = document.querySelectorAll('.inventory-card');
    const itemsCountBadge = document.querySelector('.items-count-badge');
    const itemsCount = document.querySelector('.items-count');
    const sortButton = document.getElementById('sortButton');
    
    // Initialize filter state
    let filtersCollapsed = false;
    let activeFilters = {
        level: 'all',
        itemType: 'all',
        size: 'all',
        stock: 'all'
    };
    
    // Check for dark mode preference
    const prefersDarkMode = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Apply dark mode class if needed
    if (prefersDarkMode) {
        document.body.classList.add('dark-mode');
    }
    
    // Listen for changes in color scheme preference
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (e.matches) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    });
    
    // Create premium dropdowns
    function createPremiumDropdowns() {
        const selectElements = document.querySelectorAll('.filter-select');
        
        // Create backdrop for closing dropdowns when clicking outside
        const backdrop = document.createElement('div');
        backdrop.classList.add('dropdown-backdrop');
        document.body.appendChild(backdrop);
        
        // Track open dropdown
        let openDropdown = null;
        
        selectElements.forEach(select => {
            // Get parent container
            const customSelect = select.closest('.custom-select');
            if (!customSelect) return;
            
            // Create premium dropdown container
            const dropdown = document.createElement('div');
            dropdown.classList.add('premium-dropdown');
            customSelect.appendChild(dropdown);
            
            // Add dropdown options
            const options = Array.from(select.options);
            options.forEach((option, index) => {
                const dropdownOption = document.createElement('div');
                dropdownOption.classList.add('dropdown-option');
                dropdownOption.textContent = option.textContent;
                dropdownOption.dataset.value = option.value;
                dropdownOption.style.animationDelay = `${index * 0.03}s`;
                
                // Mark as selected if it's the current value
                if (option.value === select.value) {
                    dropdownOption.classList.add('selected');
                }
                
                // Add click handler
                dropdownOption.addEventListener('click', function() {
                    select.value = this.dataset.value;
                    
                    // Update selected option visual
                    dropdown.querySelectorAll('.dropdown-option').forEach(opt => {
                        opt.classList.remove('selected');
                    });
                    this.classList.add('selected');
                    
                    // Add selection animation
                    this.style.animation = 'selectActivate 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
                    setTimeout(() => {
                        this.style.animation = '';
                    }, 500);
                    
                    // Trigger change event
                    const event = new Event('change', { bubbles: true });
                    select.dispatchEvent(event);
                    
                    // Close dropdown
                    closeDropdown();
                });
                
                dropdown.appendChild(dropdownOption);
            });
            
            // Replace native select behavior with premium dropdown
            customSelect.addEventListener('click', function(e) {
                // If select is disabled, don't open dropdown
                if (select.disabled) return;
                
                // Toggle dropdown
                if (dropdown === openDropdown) {
                    closeDropdown();
                } else {
                    openDropdown();
                }
                
                function openDropdown() {
                    // Close any open dropdown first
                    if (openDropdown) {
                        openDropdown.classList.remove('open');
                        openDropdown.closest('.custom-select').classList.remove('open');
                    }
                    
                    // Show this dropdown
                    dropdown.classList.add('open');
                    customSelect.classList.add('open');
                    customSelect.classList.add('focused');
                    backdrop.classList.add('active');
                    openDropdown = dropdown;
                    
                    // Add ripple effect
                    const ripple = document.createElement('span');
                    ripple.classList.add('select-ripple');
                    customSelect.appendChild(ripple);
                    
                    // Clean up ripple after animation
                    setTimeout(() => ripple.remove(), 800);
                    
                    // Scroll selected option into view
                    const selectedOption = dropdown.querySelector('.dropdown-option.selected');
                    if (selectedOption) {
                        setTimeout(() => {
                            selectedOption.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
                            
                            // Check if dropdown has overflow and show scroll hint if needed
                            if (dropdown.scrollHeight > dropdown.clientHeight) {
                                customSelect.classList.add('has-overflow');
                            } else {
                                customSelect.classList.remove('has-overflow');
                            }
                        }, 10);
                    }
                }
            });
            
            // Prevent dropdown toggle when clicking on the dropdown itself
            dropdown.addEventListener('click', function(e) {
                e.stopPropagation();
            });
        });
        
        // Function to close dropdowns
        function closeDropdown() {
            if (openDropdown) {
                openDropdown.classList.remove('open');
                openDropdown.closest('.custom-select').classList.remove('open');
                openDropdown.closest('.custom-select').classList.remove('focused');
                openDropdown.closest('.custom-select').classList.remove('has-overflow');
                backdrop.classList.remove('active');
                openDropdown = null;
            }
        }
        
        // Close dropdown when clicking outside
        backdrop.addEventListener('click', closeDropdown);
        
        // Close dropdown on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && openDropdown) {
                closeDropdown();
            }
        });
        
        // Close dropdown when scrolling the page
        window.addEventListener('scroll', function() {
            if (openDropdown) {
                closeDropdown();
            }
        }, { passive: true });
    }
    
    // Initialize premium dropdowns
    createPremiumDropdowns();
    
    // Fix filter icon visibility issues
    function fixFilterIcons() {
        // Target all filter icons
        const filterIcons = document.querySelectorAll('.filter-group label i, .filter-title h3 i, .reset-filters-btn i');
        
        filterIcons.forEach(icon => {
            // Ensure icons are properly displayed
            icon.style.position = 'relative';
            icon.style.zIndex = '5';
            icon.style.display = 'inline-flex';
            icon.style.alignItems = 'center';
            icon.style.justifyContent = 'center';
            icon.style.width = '20px';
            icon.style.height = '20px';
            icon.style.backgroundColor = 'transparent';
        });
    }
    
    // Call the function to fix icons
    fixFilterIcons();
    
    // Add filter toggle functionality
    if (filterToggleBtn && filterTabs) {
        filterToggleBtn.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent event bubbling to filter-title
            toggleFilters();
            
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.classList.add('button-ripple');
            this.appendChild(ripple);
            
            // Remove ripple after animation
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    }
    
    // Update the toggleFilters function to include animations
    function toggleFilters() {
        filtersCollapsed = !filtersCollapsed;
        
        if (filtersCollapsed) {
            filterTabs.classList.add('collapsed');
            filterContainer.classList.add('collapsed');
            if (filterToggleBtn) {
                filterToggleBtn.classList.add('active');
                filterToggleBtn.setAttribute('title', 'Show filters');
                filterToggleBtn.querySelector('i').className = 'fas fa-chevron-down';
                // Add subtle bounce animation to the toggle button
                filterToggleBtn.style.animation = 'none';
                void filterToggleBtn.offsetWidth; // Force reflow
                filterToggleBtn.style.animation = 'badgeBounce 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
            }
        } else {
            filterTabs.classList.remove('collapsed');
            filterContainer.classList.remove('collapsed');
            if (filterToggleBtn) {
                filterToggleBtn.classList.remove('active');
                filterToggleBtn.setAttribute('title', 'Hide filters');
                filterToggleBtn.querySelector('i').className = 'fas fa-chevron-up';
                // Add subtle bounce animation to the toggle button
                filterToggleBtn.style.animation = 'none';
                void filterToggleBtn.offsetWidth; // Force reflow
                filterToggleBtn.style.animation = 'badgeBounce 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
            }
            
            // Trigger staggered animation for filter groups
            setTimeout(() => {
                const filterGroups = document.querySelectorAll('.filter-group');
                filterGroups.forEach((group, index) => {
                    group.style.opacity = '0';
                    group.style.transform = 'translateY(15px)';
                    setTimeout(() => {
                        group.style.transition = 'opacity 0.3s ease, transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
                        group.style.opacity = '1';
                        group.style.transform = 'translateY(0)';
                    }, 50 * index);
                });
            }, 100);
        }
    }
    
    // Remove the click handler from filterTitle to prevent confusion with two toggles
    if (filterTitle && filterTabs) {
        // Instead of toggle, only allow expand
        filterTitle.addEventListener('click', function(e) {
            // Don't toggle if clicking on the toggle button (that has its own handler)
            if (e.target.closest('.filter-toggle-btn')) {
                return;
            }
            
            // If filters are collapsed, expand them
            if (filtersCollapsed) {
                toggleFilters();
            }
        });
    }
    
    // Make filter dropdowns touch-friendly for mobile
    initTouchFriendlyDropdowns();
    
    // Apply initial filtering
    applyFilters();
    
    // Add focus and hover effects for select dropdowns
    customSelects.forEach(select => {
        const selectElement = select.querySelector('select');
        
        // Add focus class when select is focused
        if (selectElement) {
            selectElement.addEventListener('focus', function() {
                select.classList.add('focused');
                
                // Add subtle animation to label
                const label = select.closest('.filter-group').querySelector('label');
                if (label) {
                    label.style.color = 'var(--primary-blue)';
                    label.querySelector('i').style.transform = 'scale(1.2)';
                }
            });
            
            selectElement.addEventListener('blur', function() {
                select.classList.remove('focused');
                
                // Reset label styling
                const label = select.closest('.filter-group').querySelector('label');
                if (label) {
                    label.style.color = '';
                    label.querySelector('i').style.transform = '';
                }
            });
            
            // Add change animation
            selectElement.addEventListener('change', function() {
                select.classList.add('changed');
                
                // Add a ripple effect when changing selection
                const ripple = document.createElement('span');
                ripple.classList.add('select-ripple');
                select.appendChild(ripple);
                
                // Highlight the active filter value
                highlightActiveFilters();
                
                // Animated count of active filters
                updateFilterCounter();
                
                // Update filter badge
                updateFilterBadge();
                
                // Remove ripple after animation completes
                setTimeout(() => {
                    ripple.remove();
                    select.classList.remove('changed');
                }, 500);
            });
        }
        
        // Add hover effects
        select.addEventListener('mouseenter', function() {
            this.classList.add('hover');
        });
        
        select.addEventListener('mouseleave', function() {
            this.classList.remove('hover');
        });
    });
    
    // Enhanced filter function for the new system
    function applyFilters() {
        const selectedLevel = levelFilter ? levelFilter.value : 'all';
        const selectedItem = itemFilter ? itemFilter.value : 'all';
        const selectedSize = sizeFilter ? sizeFilter.value : 'all';
        const selectedStock = stockFilter ? stockFilter.value : 'all';
        
        const cards = document.querySelectorAll('.inventory-card');
        let visibleCount = 0;
        
        // Add animation class to filter system
        const filterSystem = document.querySelector('.filter-system');
        if (filterSystem) {
            filterSystem.classList.add('filtering');
            setTimeout(() => {
                filterSystem.classList.remove('filtering');
            }, 400);
        }
        
        // Enhanced circular motion animation for filter container
        if (filterContainer) {
            // Comment out the circular motion effect
            // filterContainer.classList.add('filtering');
            
            // Remove the creation of additional animation element
            /* 
            // Create an additional animation element for more dramatic effect
            const spinEffect = document.createElement('div');
            spinEffect.style.position = 'absolute';
            spinEffect.style.top = '50%';
            spinEffect.style.left = '50%';
            spinEffect.style.width = '80px';
            spinEffect.style.height = '80px';
            spinEffect.style.borderRadius = '50%';
            
            // Check for dark mode
            if (document.body.classList.contains('dark-mode') || window.matchMedia('(prefers-color-scheme: dark)').matches) {
                spinEffect.style.border = '4px solid rgba(59, 130, 246, 0.3)';
                spinEffect.style.borderTopColor = 'rgba(59, 130, 246, 0.8)';
            } else {
                spinEffect.style.border = '4px solid rgba(26, 115, 232, 0.3)';
                spinEffect.style.borderTopColor = 'rgba(26, 115, 232, 0.8)';
            }
            
            spinEffect.style.transform = 'translate(-50%, -50%)';
            spinEffect.style.animation = 'spin 1s cubic-bezier(0.34, 1.56, 0.64, 1)';
            spinEffect.style.zIndex = '2';
            spinEffect.style.pointerEvents = 'none';
            
            filterContainer.appendChild(spinEffect);
            
            // Add keyframes for spin animation if it doesn't exist
            if (!document.querySelector('#spin-keyframes')) {
                const keyframes = document.createElement('style');
                keyframes.id = 'spin-keyframes';
                keyframes.textContent = `
                    @keyframes spin {
                        0% { transform: translate(-50%, -50%) rotate(0deg); }
                        100% { transform: translate(-50%, -50%) rotate(360deg); }
                    }
                `;
                document.head.appendChild(keyframes);
            }
            
            // Remove the elements after animation completes
            setTimeout(() => {
                filterContainer.classList.remove('filtering');
                spinEffect.remove();
            }, 1000);
            */
        }
        
        // Add class to inventory grid for filter change animation
        const inventoryGrid = document.getElementById('inventoryGrid');
        if (inventoryGrid) {
            inventoryGrid.classList.add('filter-applying');
            setTimeout(() => {
                inventoryGrid.classList.remove('filter-applying');
            }, 600);
        }
        
        // Stagger the animations for a more pleasant visual effect
        let delay = 0;
        const filteredCards = [];
        
        // First pass - determine which cards match the filters
        cards.forEach(card => {
            // Extract data attributes (will need to be updated in the card elements)
            const level = card.dataset.level || 'all';
            const itemType = card.dataset.itemType || 'all';
            const size = card.dataset.size || 'all';
            const stockStatus = card.dataset.status || 'all';
            
            // Check if card matches all selected filters
            const matchesLevel = selectedLevel === 'all' || level === selectedLevel;
            const matchesItem = selectedItem === 'all' || itemType === selectedItem;
            const matchesSize = selectedSize === 'all' || size === selectedSize;
            const matchesStock = selectedStock === 'all' || stockStatus === selectedStock;
            
            // If all criteria match, prepare for display
            if (matchesLevel && matchesItem && matchesSize && matchesStock) {
                filteredCards.push(card);
                visibleCount++;
            } else {
                // Hide non-matching cards with fade-out effect
                card.style.opacity = '0';
                card.style.transform = 'scale(0.95)';
                
                setTimeout(() => {
                    card.style.display = 'none';
                    card.classList.remove('show');
                }, 300);
            }
        });
        
        // Apply staggered animation to visible cards
        filteredCards.forEach((card, index) => {
            delay = index * 0.05;
            
            // First ensure it's not visible during setup
            if (card.style.display === 'none') {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.95)';
            }
            
            // Then show and animate it
            setTimeout(() => {
                card.style.display = 'block';
                
                // Force browser reflow
                void card.offsetWidth;
                
                card.style.opacity = '1';
                card.style.transform = 'scale(1)';
                
                // Remove and re-add animation class for a fresh animation
                card.classList.remove('fade-in-up');
                void card.offsetWidth; // Force reflow to ensure animation restarts
                card.classList.add('fade-in-up', 'show');
            }, delay * 1000 + 300); // The 300ms allows for the fade-out of hidden cards
        });
        
        // Update the item count display with animation
        if (itemsCount) {
            const countText = `(${visibleCount})`;
            
            // Animate count change
            itemsCount.style.transform = 'scale(1.2)';
            itemsCount.style.color = 'var(--primary-blue)';
            itemsCount.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
            
            setTimeout(() => {
                itemsCount.textContent = countText;
                
                setTimeout(() => {
                    itemsCount.style.transform = '';
                    itemsCount.style.color = '';
                }, 300);
            }, 300);
        }
        
        // Update the filter summary with animation
        updateFilterSummary(selectedLevel, selectedItem, selectedSize, selectedStock, visibleCount);
        
        // Highlight active filters with animation
        highlightActiveFilters();
        
        // Update filter counter and badge with animations
        updateFilterCounter();
        updateFilterBadge();
        
        // Enhance low stock indicators
        enhanceLowStockIndicators();
        
        return visibleCount;
    }
    
    // Make dropdowns touch-friendly on mobile
    function initTouchFriendlyDropdowns() {
        const selectElements = document.querySelectorAll('.filter-select');
        
        selectElements.forEach(select => {
            // Add 'touching' class on touchstart
            select.addEventListener('touchstart', function(e) {
                const customSelect = this.closest('.custom-select');
                if (customSelect) {
                    customSelect.classList.add('touching');
                }
            });
            
            // Remove 'touching' class on touchend
            select.addEventListener('touchend', function(e) {
                const customSelect = this.closest('.custom-select');
                if (customSelect) {
                    setTimeout(() => {
                        customSelect.classList.remove('touching');
                    }, 300);
                }
            });
        });
    }
    
    // Update the filter summary text
    function updateFilterSummary(level, item, size, stock, count) {
        const filterSummary = document.querySelector('.filter-summary');
        if (!filterSummary) return;
        
        let summaryText = '';
        let activeCount = 0;
        
        // Build summary text based on active filters
        if (level !== 'all') {
            summaryText += `Level: ${formatFilterValue(level)}`;
            activeCount++;
        }
        
        if (item !== 'all') {
            if (summaryText) summaryText += ' • ';
            summaryText += `Type: ${formatFilterValue(item)}`;
            activeCount++;
        }
        
        if (size !== 'all') {
            if (summaryText) summaryText += ' • ';
            summaryText += `Size: ${formatFilterValue(size)}`;
            activeCount++;
        }
        
        if (stock !== 'all') {
            if (summaryText) summaryText += ' • ';
            summaryText += `Status: ${formatFilterValue(stock)}`;
            activeCount++;
        }
        
        // Only show summary if at least one filter is active
        if (activeCount > 0) {
            filterCount.textContent = summaryText;
            filterSummary.classList.add('active');
            
            // Add animation if not already present
            if (!filterSummary.classList.contains('animate')) {
                filterSummary.classList.add('animate');
                setTimeout(() => {
                    filterSummary.classList.remove('animate');
                }, 500);
            }
        } else {
            filterCount.textContent = '';
            filterSummary.classList.remove('active');
        }
        
        // Store active filter count
        activeFilters = {
            level: level,
            itemType: item,
            size: size,
            stock: stock
        };
    }
    
    // Format filter values for display
    function formatFilterValue(value) {
        if (!value) return '';
        
        // Replace hyphens with spaces and capitalize words
        return value.split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
    
    // Reset all filters to default
    function resetFilters() {
        if (levelFilter) levelFilter.value = 'all';
        if (itemFilter) itemFilter.value = 'all';
        if (sizeFilter) sizeFilter.value = 'all';
        if (stockFilter) stockFilter.value = 'all';
        
        // Add reset animation to button with enhanced effect
        resetFiltersBtn.classList.add('resetting');
        const icon = resetFiltersBtn.querySelector('i');
        
        // Apply the enhanced spinning animation
        icon.style.animation = 'resetButtonSpin 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
        
        // Clear animation after it completes
        setTimeout(() => {
            resetFiltersBtn.classList.remove('resetting');
            icon.style.animation = '';
        }, 600);
        
        // Apply the reset filters
        applyFilters();
        
        // Clear any highlighting with animated transitions
        const customSelects = document.querySelectorAll('.custom-select');
        customSelects.forEach(select => {
            select.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
            select.classList.remove('active-filter');
        });
        
        // Update premium dropdown selections with smooth transitions
        document.querySelectorAll('.premium-dropdown').forEach(dropdown => {
            const select = dropdown.closest('.custom-select').querySelector('select');
            if (select) {
                dropdown.querySelectorAll('.dropdown-option').forEach(option => {
                    option.style.transition = 'all 0.3s ease';
                    if (option.dataset.value === 'all') {
                        option.classList.add('selected');
                    } else {
                        option.classList.remove('selected');
                    }
                });
            }
        });
        
        // Reset filter groups with a subtle animation
        document.querySelectorAll('.filter-group').forEach((group, index) => {
            setTimeout(() => {
                group.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
                group.classList.remove('active-group');
            }, index * 50);
        });
        
        // Reset filter summary with animation
        const filterSummary = document.querySelector('.filter-summary');
        if (filterSummary) {
            filterSummary.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
            filterSummary.classList.remove('active');
        }
        
        // Reset filter badge with animation
        if (filterBadge) {
            filterBadge.style.transition = 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
            filterBadge.textContent = 'Active';
            filterBadge.classList.remove('active');
        }
        
        // Reset filter counter
        filterCount.textContent = '';
        activeFilters = {
            level: 'all',
            itemType: 'all',
            size: 'all',
            stock: 'all'
        };
    }
    
    // Reset filters button click handler
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', function(e) {
            e.preventDefault();
            resetFilters();
        });
    }
    
    // Update the active filter counter
    function updateFilterCounter() {
        const activeCount = [
            levelFilter && levelFilter.value !== 'all',
            itemFilter && itemFilter.value !== 'all',
            sizeFilter && sizeFilter.value !== 'all',
            stockFilter && stockFilter.value !== 'all'
        ].filter(Boolean).length;
        
        // Animate if the count changed
        if (activeCount > 0) {
            const filterSystem = document.querySelector('.filter-system');
            if (filterSystem && !filterSystem.classList.contains('active-filters')) {
                filterSystem.classList.add('active-filters');
            }
        } else {
            const filterSystem = document.querySelector('.filter-system');
            if (filterSystem) {
                filterSystem.classList.remove('active-filters');
            }
        }
    }
    
    // Update the filter badge state
    function updateFilterBadge() {
        if (!filterBadge) return;
        
        const activeCount = Object.values(activeFilters).filter(val => val !== 'all').length;
        if (activeCount > 0) {
            // Store previous text for comparison
            const previousText = filterBadge.textContent;
            const newText = `${activeCount} Active`;
            
            filterBadge.textContent = newText;
            filterBadge.classList.add('active');
            
            // Only add animation if the text has changed
            if (previousText !== newText) {
                // Clear any existing animation
                filterBadge.style.animation = 'none';
                void filterBadge.offsetWidth; // Force reflow
                filterBadge.style.animation = 'badgeBounce 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)';
            }
        } else {
            filterBadge.textContent = 'Active';
            filterBadge.classList.remove('active');
        }
    }
    
    // Highlight active filters in premium dropdowns
    function highlightActiveFilters() {
        // Update for premium dropdowns
        const dropdowns = document.querySelectorAll('.premium-dropdown');
        
        dropdowns.forEach(dropdown => {
            const select = dropdown.closest('.custom-select').querySelector('select');
            const options = dropdown.querySelectorAll('.dropdown-option');
            
            options.forEach(option => {
                if (option.dataset.value === select.value) {
                    option.classList.add('selected');
                } else {
                    option.classList.remove('selected');
                }
            });
            
            // Add/remove active-filter class
            if (select.value !== 'all') {
                select.closest('.custom-select').classList.add('active-filter');
                select.closest('.filter-group').classList.add('active-group');
            } else {
                select.closest('.custom-select').classList.remove('active-filter');
                select.closest('.filter-group').classList.remove('active-group');
            }
        });
    }
    
    // Enhance low stock indicators with animations
    function enhanceLowStockIndicators() {
        const lowStockCards = document.querySelectorAll('.inventory-card[data-status="low-stock"]');
        const outOfStockCards = document.querySelectorAll('.inventory-card[data-status="out-of-stock"]');
        
        // Add pulsing effect to low stock items
        lowStockCards.forEach(card => {
            if (!card.classList.contains('low-stock-pulse')) {
                card.classList.add('low-stock-pulse');
            }
        });
        
        // Add warning effect to out-of-stock items
        outOfStockCards.forEach(card => {
            if (!card.classList.contains('out-of-stock-effect')) {
                card.classList.add('out-of-stock-effect');
            }
        });
    }
    
    // Add CSS for enhanced filter animations
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        /* Animation for filter system */
        @keyframes filter-pulse {
            0% { transform: translateY(0) scale(1); }
            50% { transform: translateY(-2px) scale(1.02); }
            100% { transform: translateY(0) scale(1); }
        }
        
        .filter-system.filtering {
            animation: filter-pulse 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
        }
        
        /* Active filter label styles */
        .active-label {
            color: #1a73e8 !important;
            font-weight: 600 !important;
        }
        
        /* Active filter select styles */
        .custom-select.active-filter {
            border-color: #1a73e8 !important;
            box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.2) !important;
        }
        
        .custom-select.active-filter::after {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 4px;
            height: 100%;
            background: #1a73e8;
            border-radius: 0 8px 8px 0;
        }
        
        .custom-select.active-filter .select-arrow {
            color: #1a73e8 !important;
        }
        
        /* Hover effects */
        .custom-select.hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);
        }
        
        /* Focus effects */
        .custom-select.focused {
            border-color: #1a73e8;
            box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.2);
        }
        
        /* Change animation */
        .custom-select.changed {
            animation: select-change 0.5s ease;
        }
        
        /* Select ripple effect */
        .select-ripple {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            width: 100%;
            height: 100%;
            background: rgba(26, 115, 232, 0.2);
            border-radius: 8px;
            pointer-events: none;
            animation: ripple 0.5s ease-out;
            z-index: 0;
        }
        
        /* Button ripple effect */
        .button-ripple {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0);
            width: 200%;
            height: 200%;
            background: rgba(26, 115, 232, 0.2);
            border-radius: 50%;
            pointer-events: none;
            animation: ripple 0.5s ease-out;
            z-index: 0;
        }
        
        @keyframes ripple {
            0% { transform: translate(-50%, -50%) scale(0); opacity: 1; }
            100% { transform: translate(-50%, -50%) scale(1); opacity: 0; }
        }
        
        @keyframes select-change {
            0% { background-color: rgba(26, 115, 232, 0.1); }
            100% { background-color: transparent; }
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .reset-filters-btn.rotating i {
            animation: rotate 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); background-color: rgba(26, 115, 232, 0.2); }
            100% { transform: scale(1); }
        }
        
        .items-count-badge.pulse {
            animation: pulse 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
        }
        
        .inventory-title.updating {
            opacity: 0;
            transform: translateY(-5px);
            transition: all 0.3s ease;
        }
        
        /* Tooltip for active filters */
        .custom-select[data-filter-active="true"]::before {
            content: attr(data-selected-value);
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            background: #1a73e8;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
            white-space: nowrap;
            text-transform: capitalize;
            z-index: 10;
        }
        
        .custom-select[data-filter-active="true"]:hover::before {
            opacity: 1;
        }
        
        /* Sort Dropdown Styles */
        .sort-dropdown {
            position: fixed;
            bottom: 65px;
            right: 20px;
            background: white;
            border-radius: 10px;
            padding: 10px 0;
            width: 200px;
            z-index: 999;
            box-shadow: 0 5px 25px rgba(0, 0, 0, 0.15);
            transform: translateY(20px);
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            border: 1px solid rgba(0, 0, 0, 0.1);
        }
        
        .sort-dropdown.show {
            transform: translateY(0);
            opacity: 1;
            visibility: visible;
        }
        
        .sort-option {
            padding: 10px 15px;
            cursor: pointer;
            transition: all 0.2s ease;
            transform: translateX(-10px);
            opacity: 0;
            font-size: 0.9rem;
        }
        
        .sort-option.show {
            transform: translateX(0);
            opacity: 1;
        }
        
        .sort-option:hover {
            background: rgba(26, 115, 232, 0.08);
            color: var(--primary-blue);
        }
        
        .sort-indicator {
            margin-left: 10px;
            font-size: 0.85rem;
            background: var(--primary-blue);
            color: white;
            padding: 5px 10px;
            border-radius: 100px;
            opacity: 0;
            transform: translateY(5px);
            transition: all 0.3s ease;
        }
        
        .sort-indicator.show {
            opacity: 1;
            transform: translateY(0);
        }
        
        .floating-action-button.active {
            background: var(--primary-blue) !important;
            transform: translateY(-5px) !important;
            box-shadow: 0 8px 25px rgba(26, 115, 232, 0.3) !important;
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .custom-select.active-filter {
                border-color: #4285f4 !important;
                box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.2) !important;
            }
            
            .custom-select.active-filter::after {
                background: #4285f4;
            }
            
            .active-label {
                color: #4285f4 !important;
            }
            
            .custom-select.active-filter .select-arrow {
                color: #4285f4 !important;
            }
            
            .select-ripple, .button-ripple {
                background: rgba(66, 133, 244, 0.3);
            }
            
            .custom-select[data-filter-active="true"]::before {
                background: #4285f4;
            }
            
            .sort-dropdown {
                background: #1e293b;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 5px 25px rgba(0, 0, 0, 0.3);
            }
            
            .sort-option {
                color: rgba(255, 255, 255, 0.9);
            }
            
            .sort-option:hover {
                background: rgba(59, 130, 246, 0.15);
                color: #93c5fd;
            }
            
            .sort-indicator {
                background: #3b82f6;
            }
        }
    `;
    document.head.appendChild(styleElement);
    
    // Make functions available globally
    window.resetFilters = resetFilters;
    window.applyFilters = applyFilters;
    
    // Add event listeners for all relevant filters
    [levelFilter, itemFilter, sizeFilter, stockFilter].forEach(filter => {
        if (filter) {
            filter.addEventListener('change', applyFilters);
        }
    });
    
    // Function to display sort options 
    function showSortOptions() {
        // Check if sort dropdown already exists
        let sortDropdown = document.querySelector('.sort-dropdown');
        
        // Also check for any lingering backdrops and remove them
        const existingBackdrops = document.querySelectorAll('.dropdown-backdrop');
        existingBackdrops.forEach(backdrop => backdrop.remove());
        
        if (sortDropdown) {
            // If dropdown exists, we're closing it
            sortDropdown.classList.remove('show');
            setTimeout(() => {
                sortDropdown.remove();
            }, 300);
            return;
        }
        
        // Create sort dropdown
        sortDropdown = document.createElement('div');
        sortDropdown.classList.add('sort-dropdown');
        
        // Add options
        const sortOptions = [
            { label: 'Item Name (A-Z)', value: 'name-asc' },
            { label: 'Item Name (Z-A)', value: 'name-desc' },
            { label: 'Price (Low to High)', value: 'price-asc' },
            { label: 'Price (High to Low)', value: 'price-desc' },
            { label: 'Stock Level (Low to High)', value: 'stock-asc' },
            { label: 'Stock Level (High to Low)', value: 'stock-desc' }
        ];
        
        sortOptions.forEach(option => {
            const optionElement = document.createElement('div');
            optionElement.classList.add('sort-option');
            optionElement.textContent = option.label;
            optionElement.dataset.value = option.value;
            
            // Add click handler
            optionElement.addEventListener('click', function() {
                sortInventory(option.value);
                closeSortDropdown();
            });
            
            sortDropdown.appendChild(optionElement);
        });
        
        // Position the dropdown above the button on mobile
        const isMobile = window.innerWidth < 768;
        sortDropdown.style.bottom = isMobile ? '70px' : '65px';
        sortDropdown.style.right = isMobile ? '10px' : '20px';
        
        // Add the dropdown to the page
        document.body.appendChild(sortDropdown);
        
        // Add backdrop to close dropdown when clicking outside
        const backdrop = document.createElement('div');
        backdrop.classList.add('dropdown-backdrop');
        backdrop.classList.add('active');
        backdrop.addEventListener('click', closeSortDropdown);
        document.body.appendChild(backdrop);
        
        // Animation for options
        setTimeout(() => {
            sortDropdown.classList.add('show');
            sortDropdown.querySelectorAll('.sort-option').forEach((option, index) => {
                setTimeout(() => {
                    option.classList.add('show');
                }, index * 50);
            });
        }, 10);
        
        // Add escape key handler to close dropdown
        function handleEscKey(e) {
            if (e.key === 'Escape') {
                closeSortDropdown();
                document.removeEventListener('keydown', handleEscKey);
            }
        }
        document.addEventListener('keydown', handleEscKey);
    }
    
    // Helper function to close the sort dropdown
    function closeSortDropdown() {
        const sortDropdown = document.querySelector('.sort-dropdown');
        const backdrop = document.querySelector('.dropdown-backdrop');
        
        if (sortDropdown) {
            sortDropdown.classList.remove('show');
            setTimeout(() => {
                sortDropdown.remove();
            }, 300);
        }
        
        if (backdrop) {
            backdrop.classList.remove('active');
            setTimeout(() => {
                backdrop.remove();
            }, 300);
        }
    }
    
    // Function to sort inventory items
    function sortInventory(sortValue) {
        const inventoryGrid = document.getElementById('inventoryGrid');
        if (!inventoryGrid) return;
        
        const cards = Array.from(inventoryGrid.querySelectorAll('.inventory-card'));
        
        // Sort the cards
        cards.sort((a, b) => {
            switch(sortValue) {
                case 'name-asc':
                    return a.querySelector('.item-name').textContent.localeCompare(
                        b.querySelector('.item-name').textContent
                    );
                case 'name-desc':
                    return b.querySelector('.item-name').textContent.localeCompare(
                        a.querySelector('.item-name').textContent
                    );
                case 'price-asc':
                    return parseFloat(a.querySelector('.detail-value.shine-effect').textContent.replace('₱', '')) - 
                           parseFloat(b.querySelector('.detail-value.shine-effect').textContent.replace('₱', ''));
                case 'price-desc':
                    return parseFloat(b.querySelector('.detail-value.shine-effect').textContent.replace('₱', '')) - 
                           parseFloat(a.querySelector('.detail-value.shine-effect').textContent.replace('₱', ''));
                case 'stock-asc':
                    return parseInt(a.querySelector('.stock-input').value) - 
                           parseInt(b.querySelector('.stock-input').value);
                case 'stock-desc':
                    return parseInt(b.querySelector('.stock-input').value) - 
                           parseInt(a.querySelector('.stock-input').value);
                default:
                    return 0;
            }
        });
        
        // Apply animations to sorted cards
        cards.forEach((card, index) => {
            // Remove the card from its current position
            card.remove();
            
            // Add animation delay based on new position
            card.style.animationDelay = `${index * 0.05}s`;
            
            // Remove and re-add animation class
            card.classList.remove('fade-in-up');
            void card.offsetWidth; // Force reflow
            card.classList.add('fade-in-up');
            
            // Add card back to the grid
            inventoryGrid.appendChild(card);
        });
        
        // Show a sort indicator
        showSortIndicator(sortValue);
    }
    
    // Function to show sort indicator
    function showSortIndicator(sortValue) {
        // Map sort values to readable text
        const sortLabels = {
            'name-asc': 'Name (A-Z)',
            'name-desc': 'Name (Z-A)',
            'price-asc': 'Price (Low to High)',
            'price-desc': 'Price (High to Low)',
            'stock-asc': 'Stock (Low to High)',
            'stock-desc': 'Stock (High to Low)'
        };
        
        // Create or update sort indicator
        let sortIndicator = document.querySelector('.sort-indicator');
        if (!sortIndicator) {
            sortIndicator = document.createElement('div');
            sortIndicator.classList.add('sort-indicator');
            document.querySelector('.inventory-summary').appendChild(sortIndicator);
        }
        
        sortIndicator.textContent = `Sorted by: ${sortLabels[sortValue]}`;
        sortIndicator.classList.add('show');
        
        // Hide after a few seconds
        setTimeout(() => {
            sortIndicator.classList.remove('show');
        }, 3000);
        
        // Update sort button icon to show active state
        const sortButton = document.getElementById('sortButton');
        if (sortButton) {
            sortButton.classList.add('active');
            sortButton.querySelector('i').className = 'fas fa-sort-amount-down';
            
            // Reset after a delay
            setTimeout(() => {
                sortButton.classList.remove('active');
                sortButton.querySelector('i').className = 'fas fa-sort';
            }, 3000);
        }
    }
    
    // Add hover animations for filter groups
    function initFilterGroupAnimations() {
        const filterGroups = document.querySelectorAll('.filter-group');
        
        filterGroups.forEach(group => {
            // Add hover effect with subtle lift and shadow
            group.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.transition = 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
            });
            
            group.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
            
            // Add click effect
            group.addEventListener('click', function() {
                // Temporarily add a more pronounced transform
                this.style.transform = 'scale(0.98)';
                
                // Return to normal after a short delay
                setTimeout(() => {
                    this.style.transform = 'translateY(0)';
                }, 150);
            });
        });
    }
    
    // Initialize filter group animations
    initFilterGroupAnimations();
    
    // Add enter/exit animations for inventory cards
    function enhanceCardAnimations() {
        const cards = document.querySelectorAll('.inventory-card');
        
        cards.forEach(card => {
            // Add hover effect with smooth transition
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
                this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)';
                this.style.transition = 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '';
            });
        });
    }
    
    // Initialize enhanced card animations
    enhanceCardAnimations();
}); 