// ===========================
// Global Variables
// ===========================
let diagnosisData = null;
let imageFile = null;
let audioFile = null;
let decisionSupportData = null;

// ===========================
// Event Listeners
// ===========================
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeFileUploads();
    initializeScrollAnimations();
});

function initializeEventListeners() {
    // Form submission
    const diagnosisForm = document.getElementById('diagnosisForm');
    if (diagnosisForm) {
        diagnosisForm.addEventListener('submit', handleFormSubmit);
    }

    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', toggleMobileMenu);
    }

    // Navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', handleNavClick);
    });

    const locationSelect = document.getElementById('location');
    if (locationSelect) {
        locationSelect.addEventListener('change', toggleCustomCityInput);
        toggleCustomCityInput();
    }

    // Smooth scroll for anchor links
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
}

function toggleCustomCityInput() {
    const locationSelect = document.getElementById('location');
    const customCityGroup = document.getElementById('customCityGroup');
    const customCityInput = document.getElementById('customCity');

    if (!locationSelect || !customCityGroup || !customCityInput) {
        return;
    }

    const isOther = locationSelect.value === 'other';
    customCityGroup.style.display = isOther ? 'block' : 'none';
    customCityInput.required = isOther;

    if (!isOther) {
        customCityInput.value = '';
    }
}

function initializeFileUploads() {
    // Image upload
    const imageInput = document.getElementById('medicalImage');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            handleImageUpload(e.target.files[0]);
        });
    }

    // Audio upload
    const audioInput = document.getElementById('audioFile');
    if (audioInput) {
        audioInput.addEventListener('change', function(e) {
            handleAudioUpload(e.target.files[0]);
        });
    }
}

// ===========================
// Navigation Functions
// ===========================
function toggleMobileMenu() {
    const navMenu = document.querySelector('.nav-menu');
    navMenu.classList.toggle('active');
}

function handleNavClick(e) {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => link.classList.remove('active'));
    e.target.classList.add('active');
}

function scrollToDiagnosis() {
    const diagnosisSection = document.getElementById('diagnosis');
    if (diagnosisSection) {
        diagnosisSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// ===========================
// File Upload Handling
// ===========================
function handleImageUpload(file) {
    if (!file) return;

    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    const maxSize = 16 * 1024 * 1024; // 16MB

    if (!allowedTypes.includes(file.type)) {
        showNotification('Please upload a valid image file (JPG, PNG)', 'error');
        return;
    }

    if (file.size > maxSize) {
        showNotification('Image size should be less than 16MB', 'error');
        return;
    }

    imageFile = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.getElementById('imagePreview');
        const previewImg = document.getElementById('imagePreviewImg');
        const fileName = document.getElementById('imageFileName');
        const uploadContent = document.querySelector('#imageUploadBox .upload-content');

        previewImg.src = e.target.result;
        fileName.textContent = file.name;
        preview.style.display = 'block';
        uploadContent.style.display = 'none';
    };
    reader.readAsDataURL(file);

    showNotification('Medical image uploaded successfully', 'success');
}

function handleAudioUpload(file) {
    if (!file) return;

    const allowedTypes = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/m4a'];
    const maxSize = 16 * 1024 * 1024; // 16MB

    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|ogg|m4a)$/i)) {
        showNotification('Please upload a valid audio file (MP3, WAV, OGG, M4A)', 'error');
        return;
    }

    if (file.size > maxSize) {
        showNotification('Audio size should be less than 16MB', 'error');
        return;
    }

    audioFile = file;

    // Show preview
    const preview = document.getElementById('audioPreview');
    const fileName = document.getElementById('audioFileName');
    const uploadContent = document.querySelector('#audioUploadBox .upload-content');

    fileName.textContent = file.name;
    preview.style.display = 'block';
    uploadContent.style.display = 'none';

    showNotification('Audio file uploaded successfully', 'success');
}

function removeFile(type) {
    if (type === 'image') {
        imageFile = null;
        document.getElementById('medicalImage').value = '';
        document.getElementById('imagePreview').style.display = 'none';
        document.querySelector('#imageUploadBox .upload-content').style.display = 'flex';
    } else if (type === 'audio') {
        audioFile = null;
        document.getElementById('audioFile').value = '';
        document.getElementById('audioPreview').style.display = 'none';
        document.querySelector('#audioUploadBox .upload-content').style.display = 'flex';
    }
    showNotification(`${type.charAt(0).toUpperCase() + type.slice(1)} removed`, 'info');
}

// ===========================
// Form Submission
// ===========================
async function handleFormSubmit(e) {
    e.preventDefault();

    // Validate form
    if (!validateForm()) {
        return;
    }

    // Prepare form data
    const formData = new FormData();
    const selectedLocation = document.getElementById('location').value;
    const customCity = (document.getElementById('customCity')?.value || '').trim();
    const finalLocation = selectedLocation === 'other' && customCity ? customCity : selectedLocation;

    formData.append('patientName', document.getElementById('patientName').value);
    formData.append('age', document.getElementById('age').value);
    formData.append('gender', document.getElementById('gender').value);
    formData.append('contact', document.getElementById('contact').value);
    formData.append('location', finalLocation);
    formData.append('symptoms', document.getElementById('symptoms').value);
    formData.append('duration', document.getElementById('duration').value);
    formData.append('severity', document.getElementById('severity').value);

    if (imageFile) {
        formData.append('medical_image', imageFile);
    }

    if (audioFile) {
        formData.append('audio_file', audioFile);
    }

    // Show loading
    showLoading();

    try {
        const response = await fetch('/api/diagnose', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Diagnosis failed. Please try again.');
        }

        const result = await response.json();
        
        if (result.success) {
            const decisionPayload = buildDecisionSupportPayload(result);
            decisionSupportData = await fetchDecisionSupport(decisionPayload);
            diagnosisData = result;
            diagnosisData.clinical_decision_support_live = decisionSupportData;
            window.diagnosisData = result;  // Make globally accessible
            hideLoading();
            displayResults(result);
            showNotification('Diagnosis completed successfully', 'success');
        } else {
            throw new Error(result.error || 'Diagnosis failed');
        }
    } catch (error) {
        hideLoading();
        showNotification(error.message, 'error');
        console.error('Error:', error);
    }
}

function buildDecisionSupportPayload(result) {
    const symptoms = document.getElementById('symptoms').value || '';
    const age = parseInt(document.getElementById('age').value || '30', 10);
    const severity = document.getElementById('severity').value || 'moderate';
    const duration = document.getElementById('duration').value || '';

    const imageText = result?.multi_modal_data?.image_analysis?.extracted_text || '';
    const clinicalText = [severity, duration, symptoms].join(' | ');

    return {
        age,
        symptoms,
        clinical_text: clinicalText,
        image_text: imageText,
        comorbidities: []
    };
}

async function fetchDecisionSupport(payload) {
    const response = await fetch('/api/decision-support', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        throw new Error('Decision support analysis failed.');
    }

    const data = await response.json();
    if (!data.success) {
        throw new Error(data.error || 'Decision support analysis failed.');
    }
    return data;
}

function validateForm() {
    const requiredFields = [
        { id: 'patientName', name: 'Name' },
        { id: 'age', name: 'Age' },
        { id: 'gender', name: 'Gender' },
        { id: 'location', name: 'Location' },
        { id: 'symptoms', name: 'Symptoms' },
        { id: 'duration', name: 'Duration' },
        { id: 'severity', name: 'Severity' }
    ];

    for (const field of requiredFields) {
        const element = document.getElementById(field.id);
        if (!element.value.trim()) {
            showNotification(`Please fill in ${field.name}`, 'error');
            element.focus();
            return false;
        }
    }

    const locationValue = document.getElementById('location').value;
    const customCityInput = document.getElementById('customCity');
    if (locationValue === 'other' && customCityInput && !customCityInput.value.trim()) {
        showNotification('Please enter your city name', 'error');
        customCityInput.focus();
        return false;
    }

    return true;
}

// ===========================
// Loading Functions
// ===========================
function showLoading() {
    document.getElementById('diagnosisForm').style.display = 'none';
    document.getElementById('loadingContainer').style.display = 'block';
    document.getElementById('resultsContainer').style.display = 'none';

    // Animate loading steps
    setTimeout(() => {
        document.getElementById('step1').innerHTML = '<i class="fas fa-check-circle"></i> Analyzing symptoms';
    }, 1000);

    setTimeout(() => {
        document.getElementById('step2').innerHTML = '<i class="fas fa-check-circle"></i> Processing medical data';
        document.getElementById('step3').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating diagnosis';
    }, 2000);

    setTimeout(() => {
        document.getElementById('step3').innerHTML = '<i class="fas fa-check-circle"></i> Generating diagnosis';
    }, 3000);
}

function hideLoading() {
    document.getElementById('loadingContainer').style.display = 'none';
}

// ===========================
// Results Display
// ===========================
function displayResults(data) {
    // Display patient info
    displayPatientInfo(data);

    // Display diagnosis
    displayDiagnosis(data.symptom_analysis);

    // Display recommendations
    displayRecommendations(data.symptom_analysis);

    // Display multi-modal results
    displayMultiModalResults(data.multi_modal_data);

    // Display decision support cards
    displayDecisionSupport(data.clinical_decision_support_live || data.clinical_decision_support);

    // Display location-based doctor recommendations
    displayDoctorRecommendations(data.doctor_recommendations);

    // Show results container
    document.getElementById('resultsContainer').style.display = 'block';

    // Scroll to results
    setTimeout(() => {
        document.getElementById('resultsContainer').scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }, 300);
}

function displayDecisionSupport(decisionData) {
    const card = document.getElementById('decisionSupportCard');
    const container = document.getElementById('decisionSupportResult');

    if (!card || !container) {
        return;
    }

    if (!decisionData) {
        card.style.display = 'none';
        return;
    }

    const riskObj = decisionData.risk_stratification || {};
    const riskBand = (riskObj.risk_band || 'low').toLowerCase();
    const riskClass = ['low', 'moderate', 'high'].includes(riskBand) ? riskBand : 'low';
    const confidence = Math.round((decisionData.confidence_score || decisionData.fusion_confidence || 0) * 100);
    const topConditions = decisionData.probable_conditions || [];
    const nextSteps = decisionData.recommended_next_steps || decisionData.next_step_investigations || [];
    const explainability = decisionData.explainability_factors || [];

    const topConditionsHtml = topConditions.length
        ? topConditions.slice(0, 3).map(item => `
            <div class="condition-item">
                <div>
                    <div class="condition-name">${item.condition}</div>
                    <small style="color: var(--text-secondary);">AI probable condition</small>
                </div>
                <div class="confidence-badge" style="background: var(--primary-color);">
                    ${Math.round((item.confidence || 0) * 100)}%
                </div>
            </div>
        `).join('')
        : '<p style="color: var(--text-secondary);">No probable conditions found.</p>';

    const factorsHtml = explainability.length
        ? explainability.slice(0, 2).map(group => {
            const boxes = (group.factors || []).map(f => `
                <div class="factor-box">
                    <strong>${(f.factor || '').replace(/_/g, ' ')}</strong>
                    <div>Score: ${Math.round((f.score || 0) * 100)}%</div>
                </div>
            `).join('');
            return `
                <div style="margin-top: 0.85rem;">
                    <div style="font-weight: 600; color: var(--text-primary);">${group.condition}</div>
                    <div class="factor-grid">${boxes}</div>
                </div>
            `;
        }).join('')
        : '<p style="color: var(--text-secondary);">Explainability factors unavailable.</p>';

    const nextStepsHtml = nextSteps.length
        ? nextSteps.slice(0, 6).map(step => `<li>${step}</li>`).join('')
        : '<li>No additional tests suggested.</li>';

    container.innerHTML = `
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.8rem; margin-bottom: 1rem;">
            <div style="padding: 0.85rem; border-radius: 10px; background: #ECFEFF; border: 1px solid #CFFAFE;">
                <strong>Fusion Confidence</strong>
                <div style="font-size: 1.4rem; font-weight: 700; color: #155E75; margin-top: 0.2rem;">${confidence}%</div>
            </div>
            <div style="padding: 0.85rem; border-radius: 10px; background: #F8FAFC; border: 1px solid #E2E8F0;">
                <strong>Risk Stratification</strong>
                <div style="margin-top: 0.45rem;"><span class="risk-chip risk-${riskClass}">${riskBand}</span></div>
                <div style="margin-top: 0.35rem; color: var(--text-secondary);">Score: ${riskObj.risk_score ?? 0}/100</div>
            </div>
        </div>

        <div>
            <h5 style="margin-bottom: 0.6rem;">Probable Conditions</h5>
            ${topConditionsHtml}
        </div>

        <div style="margin-top: 1rem;">
            <h5 style="margin-bottom: 0.6rem;">Explainable AI Factors</h5>
            ${factorsHtml}
        </div>

        <div style="margin-top: 1rem; padding: 0.9rem; border-radius: 10px; background: #F0FDF4; border: 1px solid #DCFCE7;">
            <h5 style="margin-bottom: 0.5rem; color: #166534;">Recommended Next Investigations</h5>
            <ul style="margin: 0; padding-left: 1.2rem; color: #166534;">${nextStepsHtml}</ul>
        </div>
    `;

    card.style.display = 'block';
}

function displayPatientInfo(data) {
    const patientInfoDiv = document.getElementById('patientInfoResult');
    const patientName = document.getElementById('patientName').value;
    const age = document.getElementById('age').value;
    const gender = document.getElementById('gender').value;
    const locationSelect = document.getElementById('location').value;
    const customCity = (document.getElementById('customCity')?.value || '').trim();
    const locationLabel = locationSelect === 'other' && customCity ? customCity : locationSelect;

    patientInfoDiv.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
            <div style="padding: 1rem; background: white; border-radius: 8px; border-left: 3px solid var(--secondary-color);">
                <strong>Patient ID:</strong><br>
                <span style="color: var(--text-secondary);">${data.patient_id}</span>
            </div>
            <div style="padding: 1rem; background: white; border-radius: 8px; border-left: 3px solid var(--secondary-color);">
                <strong>Name:</strong><br>
                <span style="color: var(--text-secondary);">${patientName}</span>
            </div>
            <div style="padding: 1rem; background: white; border-radius: 8px; border-left: 3px solid var(--secondary-color);">
                <strong>Age:</strong><br>
                <span style="color: var(--text-secondary);">${age} years</span>
            </div>
            <div style="padding: 1rem; background: white; border-radius: 8px; border-left: 3px solid var(--secondary-color);">
                <strong>Gender:</strong><br>
                <span style="color: var(--text-secondary);">${gender.charAt(0).toUpperCase() + gender.slice(1)}</span>
            </div>
            <div style="padding: 1rem; background: white; border-radius: 8px; border-left: 3px solid var(--secondary-color);">
                <strong>Location:</strong><br>
                <span style="color: var(--text-secondary);">${locationLabel.toUpperCase()}</span>
            </div>
        </div>
    `;
}

function displayDoctorRecommendations(doctorData) {
    const card = document.getElementById('doctorRecommendationCard');
    const container = document.getElementById('doctorRecommendationResult');

    if (!card || !container || !doctorData) {
        if (card) {
            card.style.display = 'none';
        }
        return;
    }

    const doctors = doctorData.top_doctors || [];
    const doctorsHtml = doctors.length
        ? doctors.map((d, i) => `
            <div style="padding: 0.85rem; border-radius: 10px; background: #F8FAFC; border: 1px solid #E2E8F0; margin-bottom: 0.6rem;">
                <div style="font-weight: 700; color: #0C4A6E;">${i + 1}. ${d.doctor}</div>
                <div style="color: var(--text-secondary); margin-top: 0.2rem;">${d.hospital}</div>
                <div style="color: #0369A1; margin-top: 0.2rem;">Contact: ${d.contact}</div>
                ${d.map_url ? `<div style="margin-top: 0.35rem;"><a href="${d.map_url}" target="_blank" rel="noopener noreferrer" style="color: #0EA5E9; font-weight: 600; text-decoration: none;">View on Google Maps</a></div>` : ''}
            </div>
        `).join('')
        : '<p style="color: var(--text-secondary);">No doctor recommendations available.</p>';

    container.innerHTML = `
        <div style="padding: 0.9rem; border-radius: 10px; background: #ECFEFF; border: 1px solid #CFFAFE; margin-bottom: 0.9rem;">
            <div><strong>Selected Location:</strong> ${(doctorData.city_display || doctorData.location_input || doctorData.location_normalized || '').toUpperCase()}</div>
            <div><strong>Recommended Specialist:</strong> ${doctorData.recommended_specialty}</div>
        </div>
        ${doctorsHtml}
    `;

    card.style.display = 'block';
}

function displayDiagnosis(analysis) {
    const diagnosisDiv = document.getElementById('diagnosisResult');
    let html = '';

    if (analysis.conditions && analysis.conditions.length > 0) {
        analysis.conditions.forEach((condition, index) => {
            const confidence = analysis.confidence[index];
            const confidencePercent = Math.round(confidence * 100);
            const confidenceColor = confidence > 0.7 ? 'var(--success-color)' : confidence > 0.5 ? 'var(--warning-color)' : 'var(--danger-color)';

            html += `
                <div class="condition-item">
                    <div>
                        <div class="condition-name">${condition}</div>
                        <small style="color: var(--text-secondary);">AI Confidence Level</small>
                    </div>
                    <div class="confidence-badge" style="background: ${confidenceColor};">
                        ${confidencePercent}%
                    </div>
                </div>
            `;
        });

        html += `
            <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(79, 70, 229, 0.1); border-radius: 8px;">
                <strong style="color: var(--primary-color);">Severity Level:</strong>
                <span style="margin-left: 0.5rem; text-transform: capitalize; font-weight: 600;">
                    ${analysis.severity}
                </span>
            </div>
        `;
    } else {
        html = '<p style="color: var(--text-secondary);">No specific conditions detected. General consultation recommended.</p>';
    }

    diagnosisDiv.innerHTML = html;
}

function displayRecommendations(analysis) {
    const recommendationDiv = document.getElementById('recommendationResult');
    
    let html = `
        <div style="padding: 1.5rem; background: white; border-radius: 8px; border-left: 4px solid var(--success-color);">
            <p style="font-size: 1.05rem; line-height: 1.8; color: var(--text-primary); margin-bottom: 1rem;">
                ${analysis.recommendation}
            </p>
            <div style="background: #FEF3C7; padding: 1rem; border-radius: 8px; border-left: 3px solid var(--warning-color);">
                <strong style="color: #92400E;"><i class="fas fa-exclamation-triangle"></i> Important:</strong>
                <p style="color: #92400E; margin: 0.5rem 0 0 0;">
                    This is a preliminary AI-based assessment. Please consult with a qualified healthcare professional for accurate diagnosis and treatment.
                </p>
            </div>
        </div>
    `;

    recommendationDiv.innerHTML = html;
}

function displayMultiModalResults(multiModalData) {
    const multiModalDiv = document.getElementById('multiModalResults');
    let html = '';

    // Check if we have image diagnosis from symbol_analysis
    if (window.diagnosisData && window.diagnosisData.symbol_analysis && window.diagnosisData.symbol_analysis.image_diagnosis) {
        const imgDiag = window.diagnosisData.symbol_analysis.image_diagnosis;
        
        html += `
            <div class="result-card" style="border-left: 4px solid #3B82F6; margin-bottom: 1.5rem;">
                <h4 style="color: #1F2937; margin-bottom: 1rem;"><i class="fas fa-clinic-medical"></i> AI Diagnosis from Medical Image</h4>
                
                <div style="padding: 1rem; background: #F0F9FF; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                        <div>
                            <strong style="color: #0369A1;">Disease Detected:</strong>
                            <p style="color: #1F2937; margin: 0.5rem 0 0 0; font-size: 1.1rem;">${imgDiag.disease_detected || 'Not detected'}</p>
                        </div>
                        <div>
                            <strong style="color: #0369A1;">Confidence Level:</strong>
                            <p style="color: #1F2937; margin: 0.5rem 0 0 0; font-size: 1.1rem;">${Math.round((imgDiag.confidence || 0) * 100)}%</p>
                        </div>
                        <div>
                            <strong style="color: #0369A1;">Specialist Required:</strong>
                            <p style="color: #1F2937; margin: 0.5rem 0 0 0; font-size: 1.1rem;">${imgDiag.specialist_required || 'General'}</p>
                        </div>
                        <div>
                            <strong style="color: #0369A1;">Detection Method:</strong>
                            <p style="color: #1F2937; margin: 0.5rem 0 0 0; font-size: 0.95rem;">${imgDiag.detection_method || 'Standard'}</p>
                        </div>
                    </div>
                </div>

                <!-- WHAT IS PRESENT -->
                ${imgDiag.what_is_present && imgDiag.what_is_present.length > 0 ? `
                    <div style="margin-bottom: 1.5rem;">
                        <h5 style="color: #1F2937; margin-bottom: 0.5rem;"><i class="fas fa-magnifying-glass"></i> What is Present (Findings)</h5>
                        <ul style="margin: 0; padding-left: 1.5rem; color: #374151;">
                            ${imgDiag.what_is_present.map(item => `<li style="margin-bottom: 0.5rem;">${item}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}

                <!-- ACTION PLAN -->
                ${imgDiag.action_plan && imgDiag.action_plan.length > 0 ? `
                    <div style="margin-bottom: 1.5rem; padding: 1rem; background: #ECFDF5; border-radius: 8px;">
                        <h5 style="color: #065F46; margin-bottom: 0.5rem;"><i class="fas fa-tasks"></i> What to Do Next (Action Plan)</h5>
                        <ol style="margin: 0; padding-left: 1.5rem; color: #047857;">
                            ${imgDiag.action_plan.slice(0, 6).map(step => `<li style="margin-bottom: 0.5rem;">${step.replace(/^Step \d+: /, '')}</li>`).join('')}
                        </ol>
                    </div>
                ` : ''}

                <!-- DIET PLAN -->
                ${imgDiag.diet_plan && Object.keys(imgDiag.diet_plan).length > 0 ? `
                    <div style="margin-bottom: 1.5rem; padding: 1rem; background: #FEF3C7; border-radius: 8px;">
                        <h5 style="color: #B45309; margin-bottom: 0.5rem;"><i class="fas fa-apple-alt"></i> Diet Plan</h5>
                        ${imgDiag.diet_plan.foods_to_eat && imgDiag.diet_plan.foods_to_eat.length > 0 ? `
                            <div style="margin-bottom: 1rem;">
                                <strong style="color: #92400E;">Foods to Eat:</strong>
                                <ul style="margin: 0.5rem 0 0 0; padding-left: 1.5rem; color: #92400E;">
                                    ${imgDiag.diet_plan.foods_to_eat.slice(0, 4).map(food => `<li>${food}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        ${imgDiag.diet_plan.foods_to_avoid && imgDiag.diet_plan.foods_to_avoid.length > 0 ? `
                            <div style="margin-bottom: 1rem;">
                                <strong style="color: #92400E;">Foods to Avoid:</strong>
                                <ul style="margin: 0.5rem 0 0 0; padding-left: 1.5rem; color: #92400E;">
                                    ${imgDiag.diet_plan.foods_to_avoid.slice(0, 4).map(food => `<li>${food}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        ${imgDiag.diet_plan.daily_recommendation ? `
                            <div>
                                <strong style="color: #92400E;">Daily Recommendation:</strong>
                                <p style="margin: 0.5rem 0 0 0; color: #92400E;">${imgDiag.diet_plan.daily_recommendation}</p>
                            </div>
                        ` : ''}
                    </div>
                ` : ''}

                <!-- MEDICATIONS -->
                ${imgDiag.recommendations && imgDiag.recommendations.medications ? `
                    <div style="padding: 1rem; background: #F3E8FF; border-radius: 8px;">
                        <h5 style="color: #6D28D9; margin-bottom: 0.5rem;"><i class="fas fa-pills"></i> Medications</h5>
                        ${imgDiag.recommendations.medications.OTC && imgDiag.recommendations.medications.OTC.length > 0 ? `
                            <div style="margin-bottom: 0.5rem;">
                                <strong style="color: #7C3AED;">OTC Medications:</strong>
                                <ul style="margin: 0.5rem 0 0 0; padding-left: 1.5rem; color: #6D28D9;">
                                    ${imgDiag.recommendations.medications.OTC.slice(0, 3).map(med => `<li>${med}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        ${imgDiag.recommendations.medications.Prescription && imgDiag.recommendations.medications.Prescription.length > 0 ? `
                            <div>
                                <strong style="color: #7C3AED;">Prescription Medications:</strong>
                                <ul style="margin: 0.5rem 0 0 0; padding-left: 1.5rem; color: #6D28D9;">
                                    ${imgDiag.recommendations.medications.Prescription.slice(0, 3).map(med => `<li>${med}</li>`).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                ` : ''}

                ${imgDiag.notes ? `
                    <div style="margin-top: 1rem; padding: 0.75rem; background: #E0E7FF; border-radius: 6px; border-left: 3px solid #6366F1;">
                        <p style="color: #312E81; margin: 0; font-size: 0.9rem;"><strong>Note:</strong> ${imgDiag.notes}</p>
                    </div>
                ` : ''}
            </div>
        `;
    }

    // Image analysis results (from multiModalData)
    if (multiModalData.image_analysis) {
        const imgAnalysis = multiModalData.image_analysis;
        html += `
            <div class="result-card" style="border-left: 4px solid #F59E0B;">
                <h4><i class="fas fa-x-ray"></i> Medical Image Analysis Details</h4>
                <div style="padding: 1rem; background: white; border-radius: 8px;">
                    <p><strong>Report Type:</strong> ${imgAnalysis.report_type || 'Unknown'}</p>
                    <p><strong>Confidence:</strong> ${Math.round(imgAnalysis.confidence * 100)}%</p>
                    <div style="margin-top: 1rem;">
                        <strong>Abnormalities:</strong>
                        <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
                            ${imgAnalysis.abnormalities && imgAnalysis.abnormalities.length > 0 ? imgAnalysis.abnormalities.map(item => `<li>${item}</li>`).join('') : '<li>No specific abnormalities detected</li>'}
                        </ul>
                    </div>
                    <p style="margin-top: 1rem; color: var(--text-secondary); font-style: italic;">
                        ${imgAnalysis.notes || 'Analysis completed.'}
                    </p>
                </div>
            </div>
        `;
    }

    // Audio analysis results
    if (multiModalData.audio_analysis) {
        const audioAnalysis = multiModalData.audio_analysis;
        html += `
            <div class="result-card" style="border-left: 4px solid #06B6D4;">
                <h4><i class="fas fa-microphone"></i> Audio Analysis</h4>
                <div style="padding: 1rem; background: white; border-radius: 8px;">
                    <p><strong>Status:</strong> ${audioAnalysis.audio_processed ? 'Processed Successfully' : 'Processing Failed'}</p>
                    <p><strong>Confidence:</strong> ${Math.round(audioAnalysis.confidence * 100)}%</p>
                    <div style="margin-top: 1rem;">
                        <strong>Findings:</strong>
                        <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
                            ${audioAnalysis.voice_symptoms.map(item => `<li>${item}</li>`).join('')}
                        </ul>
                    </div>
                    <p style="margin-top: 1rem; color: var(--text-secondary); font-style: italic;">
                        ${audioAnalysis.notes}
                    </p>
                </div>
            </div>
        `;
    }

    if (html) {
        multiModalDiv.innerHTML = html;
    }
}

// ===========================
// Form Reset
// ===========================
function resetForm() {
    // Reset form
    document.getElementById('diagnosisForm').reset();
    
    // Clear files
    imageFile = null;
    audioFile = null;
    decisionSupportData = null;
    
    // Reset file previews
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('audioPreview').style.display = 'none';
    document.querySelector('#imageUploadBox .upload-content').style.display = 'flex';
    document.querySelector('#audioUploadBox .upload-content').style.display = 'flex';
    
    // Show form, hide results
    document.getElementById('diagnosisForm').style.display = 'block';
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('decisionSupportCard').style.display = 'none';
    const doctorCard = document.getElementById('doctorRecommendationCard');
    if (doctorCard) {
        doctorCard.style.display = 'none';
    }
    
    // Scroll to form
    document.getElementById('diagnosis').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
    
    showNotification('Form reset. Ready for new diagnosis.', 'info');
}

// ===========================
// Report Functions
// ===========================
function downloadReport() {
    if (!diagnosisData) {
        showNotification('No diagnosis data available', 'error');
        return;
    }

    const reportContent = generateReportContent();
    const blob = new Blob([reportContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Medical_Report_${diagnosisData.patient_id}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showNotification('Report downloaded successfully', 'success');
}

function generateReportContent() {
    const patientName = document.getElementById('patientName').value;
    const age = document.getElementById('age').value;
    const gender = document.getElementById('gender').value;
    
    return `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Medical Report - ${diagnosisData.patient_id}</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; }
                h1 { color: #4F46E5; border-bottom: 3px solid #4F46E5; padding-bottom: 10px; }
                .section { margin: 20px 0; padding: 20px; border: 1px solid #E5E7EB; border-radius: 8px; }
                .label { font-weight: bold; color: #374151; }
                .value { color: #6B7280; }
                .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #E5E7EB; font-size: 12px; color: #9CA3AF; }
            </style>
        </head>
        <body>
            <h1>🏥 MediAI - Medical Pre-Diagnosis Report</h1>
            
            <div class="section">
                <h2>Patient Information</h2>
                <p><span class="label">Patient ID:</span> <span class="value">${diagnosisData.patient_id}</span></p>
                <p><span class="label">Name:</span> <span class="value">${patientName}</span></p>
                <p><span class="label">Age:</span> <span class="value">${age} years</span></p>
                <p><span class="label">Gender:</span> <span class="value">${gender}</span></p>
                <p><span class="label">Date:</span> <span class="value">${new Date(diagnosisData.timestamp).toLocaleString()}</span></p>
            </div>
            
            <div class="section">
                <h2>Diagnosis Results</h2>
                ${diagnosisData.symptom_analysis.conditions.map((condition, index) => `
                    <p><span class="label">• ${condition}</span> - Confidence: ${Math.round(diagnosisData.symptom_analysis.confidence[index] * 100)}%</p>
                `).join('')}
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <p>${diagnosisData.symptom_analysis.recommendation}</p>
            </div>
            
            <div class="footer">
                <p><strong>Disclaimer:</strong> This is an AI-generated preliminary assessment. Always consult with a qualified healthcare professional for accurate diagnosis and treatment.</p>
                <p>Generated by MediAI - Advanced Medical Pre-Diagnosis System</p>
            </div>
        </body>
        </html>
    `;
}

function shareReport() {
    if (!diagnosisData) {
        showNotification('No diagnosis data available', 'error');
        return;
    }

    const shareText = `Medical Pre-Diagnosis Report\nPatient ID: ${diagnosisData.patient_id}\nDate: ${new Date(diagnosisData.timestamp).toLocaleString()}`;

    if (navigator.share) {
        navigator.share({
            title: 'Medical Report',
            text: shareText,
            url: window.location.href
        }).then(() => {
            showNotification('Report shared successfully', 'success');
        }).catch(() => {
            copyToClipboard(shareText);
        });
    } else {
        copyToClipboard(shareText);
    }
}

function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    showNotification('Report details copied to clipboard', 'info');
}

// ===========================
// Notification System
// ===========================
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    const colors = {
        success: '#10B981',
        error: '#EF4444',
        warning: '#F59E0B',
        info: '#3B82F6'
    };

    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        color: var(--text-primary);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        z-index: 10000;
        animation: slideInRight 0.3s ease-out;
        border-left: 4px solid ${colors[type]};
        max-width: 400px;
    `;

    notification.innerHTML = `
        <i class="fas ${icons[type]}" style="color: ${colors[type]}; font-size: 1.25rem;"></i>
        <span style="flex: 1;">${message}</span>
        <button onclick="this.parentElement.remove()" style="background: none; border: none; color: var(--text-secondary); cursor: pointer; font-size: 1.25rem;">
            <i class="fas fa-times"></i>
        </button>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// ===========================
// Scroll Animations
// ===========================
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements
    document.querySelectorAll('.feature-card, .result-card').forEach(el => {
        observer.observe(el);
    });
}

// Add CSS for notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
