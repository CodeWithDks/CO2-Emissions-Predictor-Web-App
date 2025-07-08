document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prediction-form');
    const resultContainer = document.getElementById('result-container');
    const resultContent = document.getElementById('result-content');
    const predictBtn = form.querySelector('.predict-btn');
    
    // Store original button content
    const originalBtnContent = predictBtn.innerHTML;
    
    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(form);
        const data = {
            fuel_consumption: parseFloat(formData.get('fuel_consumption')),
            fuel_efficiency: parseFloat(formData.get('fuel_efficiency')),
            fuel_type: formData.get('fuel_type')
        };
        
        // Validate form data
        if (!validateFormData(data)) {
            return;
        }
        
        // Show loading state
        showLoading();
        
        try {
            // Make prediction request
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showResult(result);
            } else {
                showError(result.error || 'An error occurred during prediction');
            }
            
        } catch (error) {
            console.error('Error:', error);
            showError('Network error: Unable to connect to the server');
        } finally {
            hideLoading();
        }
    });
    
    // Validation function
    function validateFormData(data) {
        const errors = [];
        
        // Validate fuel consumption
        if (!data.fuel_consumption || data.fuel_consumption <= 0) {
            errors.push('Fuel consumption must be greater than 0');
        } else if (data.fuel_consumption > 50) {
            errors.push('Fuel consumption seems too high (>50 L/100km)');
        }
        
        // Validate fuel efficiency
        if (!data.fuel_efficiency || data.fuel_efficiency <= 0) {
            errors.push('Fuel efficiency must be greater than 0');
        } else if (data.fuel_efficiency > 150) {
            errors.push('Fuel efficiency seems too high (>150 mpg)');
        }
        
        // Validate fuel type
        if (!data.fuel_type) {
            errors.push('Please select a fuel type');
        }
        
        // Check for logical consistency (rough validation)
        if (data.fuel_consumption && data.fuel_efficiency) {
            // Very rough conversion check: L/100km * mpg should be roughly in a certain range
            const product = data.fuel_consumption * data.fuel_efficiency;
            if (product < 50 || product > 1000) {
                errors.push('Fuel consumption and efficiency values seem inconsistent');
            }
        }
        
        if (errors.length > 0) {
            showError(errors.join('. '));
            return false;
        }
        
        return true;
    }
    
    // Show loading state
    function showLoading() {
        predictBtn.disabled = true;
        predictBtn.innerHTML = '<div class="loading"></div> Predicting...';
        hideResult();
    }
    
    // Hide loading state
    function hideLoading() {
        predictBtn.disabled = false;
        predictBtn.innerHTML = originalBtnContent;
    }
    
    // Show successful result
    function showResult(result) {
        const html = `
            <div class="result-success">
                <h3><i class="fas fa-check-circle"></i> Prediction Complete</h3>
                <div class="emission-value">
                    ${result.prediction}
                    <span class="emission-unit">g/km</span>
                </div>
                <div class="result-details">
                    <h4><i class="fas fa-info-circle"></i> Input Summary</h4>
                    <div class="input-summary">
                        <div class="input-item">
                            <span class="input-label">Fuel Consumption:</span>
                            <span class="input-value">${result.input_data.fuel_consumption} L/100km</span>
                        </div>
                        <div class="input-item">
                            <span class="input-label">Fuel Efficiency:</span>
                            <span class="input-value">${result.input_data.fuel_efficiency} mpg</span>
                        </div>
                        <div class="input-item">
                            <span class="input-label">Fuel Type:</span>
                            <span class="input-value">${result.fuel_type_name}</span>
                        </div>
                    </div>
                </div>
                <div class="environmental-impact">
                    <h4><i class="fas fa-leaf"></i> Environmental Impact</h4>
                    <p>${getEnvironmentalMessage(result.prediction)}</p>
                </div>
            </div>
        `;
        
        resultContent.innerHTML = html;
        resultContainer.classList.add('show');
        
        // Scroll to result
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Show error message
    function showError(message) {
        const html = `
            <div class="result-error">
                <h3><i class="fas fa-exclamation-triangle"></i> Error</h3>
                <p>${message}</p>
            </div>
        `;
        
        resultContent.innerHTML = html;
        resultContainer.classList.add('show');
    }
    
    // Hide result
    function hideResult() {
        resultContainer.classList.remove('show');
    }
    
    // Get environmental message based on CO2 emissions
    function getEnvironmentalMessage(emission) {
        if (emission < 100) {
            return `🌱 Excellent! Your vehicle has very low CO2 emissions (${emission} g/km). This is environmentally friendly and helps reduce your carbon footprint.`;
        } else if (emission < 150) {
            return `🌿 Good! Your vehicle has moderate CO2 emissions (${emission} g/km). Consider eco-friendly driving practices to reduce emissions further.`;
        } else if (emission < 200) {
            return `⚠️ Your vehicle has moderate-high CO2 emissions (${emission} g/km). Consider carpooling, public transport, or a more fuel-efficient vehicle.`;
        } else if (emission < 250) {
            return `🔶 Your vehicle has high CO2 emissions (${emission} g/km). This significantly impacts the environment. Consider eco-friendly alternatives.`;
        } else {
            return `🚨 Your vehicle has very high CO2 emissions (${emission} g/km). This has a major environmental impact. Consider switching to a more efficient vehicle or alternative transportation.`;
        }
    }
    
    // Input validation and formatting
    const fuelConsumptionInput = document.getElementById('fuel-consumption');
    const fuelEfficiencyInput = document.getElementById('fuel-efficiency');
    
    // Real-time validation feedback
    fuelConsumptionInput.addEventListener('input', function() {
        validateInput(this, 0, 50, 'Fuel consumption should be between 0 and 50 L/100km');
    });
    
    fuelEfficiencyInput.addEventListener('input', function() {
        validateInput(this, 0, 150, 'Fuel efficiency should be between 0 and 150 mpg');
    });
    
    function validateInput(input, min, max, message) {
        const value = parseFloat(input.value);
        const helpText = input.parentElement.querySelector('.help-text');
        
        if (value && (value < min || value > max)) {
            input.style.borderColor = '#e74c3c';
            helpText.style.color = '#e74c3c';
            helpText.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        } else {
            input.style.borderColor = '#e0e0e0';
            helpText.style.color = '#7f8c8d';
            // Reset to original help text
            const originalText = getOriginalHelpText(input.id);
            helpText.innerHTML = `<i class="fas fa-info-circle"></i> ${originalText}`;
        }
    }
    
    function getOriginalHelpText(inputId) {
        const helpTexts = {
            'fuel-consumption': 'How many liters of fuel per 100 kilometers (typical range: 4-20 L/100km)',
            'fuel-efficiency': 'Miles per gallon - higher is better (typical range: 15-50 mpg)'
        };
        return helpTexts[inputId] || '';
    }
    
    // Add smooth scrolling for all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading animation to form when page loads
    setTimeout(() => {
        form.style.opacity = '1';
        form.style.transform = 'translateY(0)';
    }, 100);
});

// Add some initial styling for smooth transitions
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prediction-form');
    form.style.opacity = '0';
    form.style.transform = 'translateY(20px)';
    form.style.transition = 'all 0.5s ease';
});