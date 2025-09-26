// Smart Diet Planner - Main JavaScript

// Global variables
let currentChart = null;

// Utility functions
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function formatNumber(num, decimals = 1) {
    return Number(Math.round(num + 'e' + decimals) + 'e-' + decimals);
}

// Food search functionality
function initializeFoodSearch() {
    const searchInput = document.getElementById('foodSearch');
    const foodResults = document.getElementById('foodResults');
    
    if (!searchInput || !foodResults) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            foodResults.innerHTML = '';
            return;
        }
        
        searchTimeout = setTimeout(() => {
            searchFoods(query);
        }, 300);
    });
}

function searchFoods(query) {
    const foodResults = document.getElementById('foodResults');
    const userId = document.querySelector('[data-user-id]')?.dataset.userId;
    
    fetch(`/api/search_foods?q=${encodeURIComponent(query)}&user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                displayFoodResults(data.foods);
            } else {
                foodResults.innerHTML = '<p class="text-muted">No foods found</p>';
            }
        })
        .catch(error => {
            console.error('Error searching foods:', error);
            foodResults.innerHTML = '<p class="text-danger">Error searching foods</p>';
        });
}

function displayFoodResults(foods) {
    const foodResults = document.getElementById('foodResults');
    
    if (foods.length === 0) {
        foodResults.innerHTML = '<p class="text-muted">No foods found</p>';
        return;
    }
    
    const foodsHtml = foods.map(food => `
        <div class="food-item" onclick="selectFood(${food.id}, '${food.name}', ${food.calories_per_100g})">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <div class="food-name">${food.name}</div>
                    <div class="food-details">
                        <span class="food-type-${food.food_type.toLowerCase().replace('-', '')}">${food.food_type}</span>
                        | ${food.category}
                        ${food.gi_index ? ` | GI: ${food.gi_index}` : ''}
                    </div>
                </div>
                <div class="text-end">
                    <div class="food-calories">${food.calories_per_100g} cal</div>
                    <small class="text-muted">per 100g</small>
                </div>
            </div>
        </div>
    `).join('');
    
    foodResults.innerHTML = foodsHtml;
}

function selectFood(foodId, foodName, calories) {
    // Fill in the food selection form
    document.getElementById('selectedFoodId').value = foodId;
    document.getElementById('selectedFoodName').textContent = foodName;
    document.getElementById('foodSearch').value = foodName;
    document.getElementById('foodResults').innerHTML = '';
    
    // Show portion selection
    document.getElementById('portionSection').style.display = 'block';
    
    // Update calories calculation when quantity changes
    updateCaloriesCalculation(calories);
}

function updateCaloriesCalculation(caloriesPer100g) {
    const quantityInput = document.getElementById('quantity');
    const calculatedCalories = document.getElementById('calculatedCalories');
    
    if (quantityInput && calculatedCalories) {
        quantityInput.addEventListener('input', function() {
            const quantity = parseFloat(this.value) || 0;
            const totalCalories = (quantity * caloriesPer100g) / 100;
            calculatedCalories.textContent = formatNumber(totalCalories) + ' calories';
        });
        
        // Trigger initial calculation
        quantityInput.dispatchEvent(new Event('input'));
    }
}

// Meal logging
function logMeal(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Logging...';
    
    fetch('/api/log_meal', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast('Meal logged successfully!', 'success');
            form.reset();
            document.getElementById('portionSection').style.display = 'none';
            document.getElementById('selectedFoodName').textContent = '';
            
            // Refresh dashboard data
            refreshDashboard();
        } else {
            showToast(data.message || 'Error logging meal', 'danger');
        }
    })
    .catch(error => {
        console.error('Error logging meal:', error);
        showToast('Error logging meal', 'danger');
    })
    .finally(() => {
        // Reset button state
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Log Meal';
    });
}

// Dashboard updates
function refreshDashboard() {
    const userId = document.querySelector('[data-user-id]')?.dataset.userId;
    
    if (!userId) return;
    
    fetch(`/api/dashboard_data?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateDashboardStats(data.stats);
                updateProgressBars(data.progress);
                updateRecentMeals(data.recent_meals);
                updateChart(data.chart_data);
            }
        })
        .catch(error => {
            console.error('Error refreshing dashboard:', error);
        });
}

function updateDashboardStats(stats) {
    const elements = {
        'todayCalories': stats.today_calories,
        'todayProtein': stats.today_protein,
        'todayCarbs': stats.today_carbs,
        'todayFat': stats.today_fat,
        'calorieGoal': stats.calorie_goal
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = formatNumber(value);
        }
    });
}

function updateProgressBars(progress) {
    Object.entries(progress).forEach(([key, value]) => {
        const progressBar = document.getElementById(`${key}Progress`);
        if (progressBar) {
            const percentage = Math.min(100, (value.consumed / value.goal) * 100);
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
        }
    });
}

function updateRecentMeals(meals) {
    const container = document.getElementById('recentMeals');
    if (!container) return;
    
    if (meals.length === 0) {
        container.innerHTML = '<p class="text-muted">No meals logged today</p>';
        return;
    }
    
    const mealsHtml = meals.map(meal => `
        <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
            <div>
                <strong>${meal.food_name}</strong>
                <div class="small text-muted">
                    <span class="meal-badge meal-${meal.meal_type.toLowerCase().replace(' ', '')}">${meal.meal_type}</span>
                    ${meal.quantity_grams}g
                </div>
            </div>
            <div class="text-end">
                <div class="food-calories">${formatNumber(meal.calories)} cal</div>
                <small class="text-muted">${meal.time_logged}</small>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = mealsHtml;
}

// Chart functionality
function initializeChart() {
    const chartCanvas = document.getElementById('nutritionChart');
    if (!chartCanvas) return;
    
    const ctx = chartCanvas.getContext('2d');
    
    // Get initial data
    const userId = document.querySelector('[data-user-id]')?.dataset.userId;
    if (userId) {
        fetch(`/api/chart_data?user_id=${userId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    createChart(ctx, data.chart_data);
                }
            });
    }
}

function createChart(ctx, data) {
    if (currentChart) {
        currentChart.destroy();
    }
    
    currentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Protein', 'Carbs', 'Fat'],
            datasets: [{
                data: [data.protein, data.carbs, data.fat],
                backgroundColor: [
                    '#28a745',
                    '#17a2b8',
                    '#ffc107'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function updateChart(data) {
    if (currentChart && data) {
        currentChart.data.datasets[0].data = [data.protein, data.carbs, data.fat];
        currentChart.update();
    }
}

// Form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        });
    });
}

// CSV Export
function exportToCSV() {
    const userId = document.querySelector('[data-user-id]')?.dataset.userId;
    const dateFrom = document.getElementById('exportDateFrom')?.value;
    const dateTo = document.getElementById('exportDateTo')?.value;
    
    let url = `/api/export_csv?user_id=${userId}`;
    if (dateFrom) url += `&date_from=${dateFrom}`;
    if (dateTo) url += `&date_to=${dateTo}`;
    
    window.open(url, '_blank');
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeFoodSearch();
    initializeChart();
    initializeFormValidation();
    
    // Refresh dashboard data every 5 minutes if on dashboard page
    if (document.getElementById('dashboard')) {
        setInterval(refreshDashboard, 300000);
    }
    
    // Set up meal logging form
    const mealForm = document.getElementById('mealLogForm');
    if (mealForm) {
        mealForm.addEventListener('submit', logMeal);
    }
});

// Admin functions
function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        fetch(`/api/admin/delete_user/${userId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('User deleted successfully', 'success');
                location.reload();
            } else {
                showToast(data.message || 'Error deleting user', 'danger');
            }
        })
        .catch(error => {
            console.error('Error deleting user:', error);
            showToast('Error deleting user', 'danger');
        });
    }
}

function deleteFood(foodId) {
    if (confirm('Are you sure you want to delete this food item?')) {
        fetch(`/api/admin/delete_food/${foodId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('Food item deleted successfully', 'success');
                location.reload();
            } else {
                showToast(data.message || 'Error deleting food item', 'danger');
            }
        })
        .catch(error => {
            console.error('Error deleting food item:', error);
            showToast('Error deleting food item', 'danger');
        });
    }
}