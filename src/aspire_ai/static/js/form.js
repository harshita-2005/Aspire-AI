document.addEventListener('DOMContentLoaded', function() {
    const profileButtons = document.querySelectorAll('.profile-btn');
    const registrationForm = document.getElementById('registrationForm');

    // Handle profile button clicks
    profileButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            profileButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Show the form with animation
            registrationForm.style.display = 'block';
            registrationForm.classList.add('form-visible');
            
            // Get the profile type
            const profileType = this.getAttribute('data-type');
            
            // Generate form fields based on profile type
            generateFormFields(profileType);
        });
    });

    // Generate form fields based on user type passed from template
    if (typeof userType !== 'undefined') {
        generateFormFields(userType);
    }
});

function generateFormFields(profileType) {
    const form = document.getElementById('registrationForm');
    const userTypeInput = form.querySelector('#user_type_input');  // Get the existing hidden input
    let fields = '';

    // Preserve the hidden input if it exists
    if (userTypeInput) {
        fields = userTypeInput.outerHTML;
    }

    // Common fields for all profiles
    fields += `
        <div class="form-section">
            <h2>Personal Information</h2>
            <div class="form-group">
                <label for="full_name">Full Name</label>
                <input type="text" id="full_name" name="full_name" required>
            </div>
            <div class="form-group">
                <label for="email_id">Email ID</label>
                <input type="email" id="email_id" name="email_id" required>
            </div>
            <div class="form-group">
                <label for="location">Location</label>
                <input type="text" id="location" name="location" placeholder="City, State" required>
            </div>
        </div>
        <div class="form-section">
            <h2>Educational Details</h2>
            <div class="form-group dynamic-input-group">
                <label for="education_level">Highest Level of Education</label>
                <select id="education_level" name="education_level" required>
                    <option value="">Select Education Level</option>
                    <option value="high_school">High School / Secondary (9th–10th Grade)</option>
                    <option value="higher_secondary">Higher Secondary / Intermediate (11th–12th Grade)</option>
                    <option value="diploma">Diploma / Vocational Training</option>
                    <option value="associate_degree">Associate Degree (if applicable in your region)</option>
                    <option value="bachelors">Bachelor's Degree (UG)</option>
                    <option value="masters">Master's Degree (PG)</option>
                    <option value="doctorate">Doctorate / PhD</option>
                    <option value="professional_certifications">Professional Certifications (e.g., CA, CFA, PMP, AWS, etc.)</option>
                </select>
                <div class="other-input-container" style="display:none; max-height:0; overflow:hidden; transition:max-height 0.3s ease;">
                    <input type="text" id="education_other" name="education_other" placeholder="Please specify your education level">
                </div>
            </div>
            <div class="form-group dynamic-input-group">
                <label for="field_or_domain">Field/Domain</label>
                <select id="field_or_domain" name="field_or_domain" required>
                    <option value="">Select Field/Domain</option>
                </select>
                <div class="other-input-container" style="display:none; max-height:0; overflow:hidden; transition:max-height 0.3s ease;">
                    <input type="text" id="domain_other" name="domain_other" placeholder="Please specify your field/domain">
                </div>
            </div>
            <div class="form-group">
                <label for="year_of_passing">Year of Passing</label>
                <select id="year_of_passing" name="year_of_passing">
                    ${generateYearOptions()}
                </select>
            </div>
        </div>
        <div class="form-section">
            <h2>Skills & Certifications</h2>
            <div class="form-group">
                <label for="skills">Skills</label>
                <input type="text" id="skills" name="skills" placeholder="Enter skills separated by commas">
            </div>
            <div class="form-group">
                <label for="technical_courses">Additional Courses/Certifications</label>
                <input type="text" id="technical_courses" name="technical_courses" placeholder="Enter certifications separated by commas">
            </div>
        </div>
        <div class="form-section">
            <h2>Career Interests</h2>
            <div class="form-group dynamic-input-group">
                <label for="industry">Preferred Industry</label>
                <select id="industry" name="industry">
                    <option value="">Select Preferred Industry</option>
                    <option value="it_software">Information Technology (IT) & Software</option>
                    <option value="finance_accounting">Finance & Accounting</option>
                    <option value="healthcare_life_sciences">Healthcare & Life Sciences</option>
                    <option value="education_research">Education & Research</option>
                    <option value="engineering_manufacturing">Engineering & Manufacturing</option>
                    <option value="architecture_construction">Architecture & Construction</option>
                    <option value="sales_marketing_advertising">Sales, Marketing & Advertising</option>
                    <option value="media_entertainment_arts">Media, Entertainment & Arts</option>
                    <option value="legal_public_administration">Legal & Public Administration</option>
                    <option value="transportation_logistics_warehousing">Transportation, Logistics & Warehousing</option>
                    <option value="retail_ecommerce">Retail & E-commerce</option>
                    <option value="tourism_hospitality">Tourism & Hospitality</option>
                    <option value="telecom_networking">Telecom & Networking</option>
                    <option value="agriculture_environmental_sciences">Agriculture & Environmental Sciences</option>
                    <option value="automotive_aerospace">Automotive & Aerospace</option>
                    <option value="human_resources_recruitment">Human Resources & Recruitment</option>
                    <option value="skilled_trades_maintenance">Skilled Trades & Maintenance</option>
                    <option value="defense_military_security">Defense, Military & Security Services</option>
                    <option value="social_work_non_profit">Social Work & Non-Profit</option>
                    <option value="religious_community_services">Religious & Community Services</option>
                    <option value="other">Miscellaneous / Other (Please Specify)</option>
                </select>
                <div class="other-input-container" style="display:none; max-height:0; overflow:hidden; transition:max-height 0.3s ease;">
                    <input type="text" id="industry_other" name="industry_other" placeholder="Please specify your preferred industry">
                </div>
            </div>
            <div class="form-group">
                <label for="specificRole">Preferred Role (if any)</label>
                <input type="text" id="specificRole" name="specificRole" placeholder="e.g., Data Scientist, UI/UX Designer, Financial Analyst" />
                <small>Optional – leave blank if you're still exploring or unsure.</small>
            </div>
            <div class="form-group">
                <label for="expected_salary_range">Preferred Monthly Salary Range</label>
                <select id="expected_salary_range" name="expected_salary_range">
                    <option value="5k-10k">5k-10k</option>
                    <option value="10k-20k">10k-20k</option>
                    <option value="20k-30k">20k-30k</option>
                    <option value="30k-40k">30k-40k</option>
                    <option value="50k-60k">50k-60k</option>
                    <option value="60k+">60k+</option>
                </select>
            </div>
        </div>
        <div class="form-section">
            <h2>Extracurricular Activities</h2>
            <div class="form-group">
                <label for="extracurricular_activities">Extracurricular Activities</label>
                <input type="text" id="extracurricular_activities" name="extracurricular_activities" placeholder="Enter activities separated by commas">
            </div>
        </div>
    `;

    // Fields based on user type
    if (profileType === 'professional' || profileType === 'freelancer' || profileType === 'career-shifter' || profileType === 'other') {
        fields += `
            <div class="form-section">
                <h2>Current Job Details</h2>
                <div class="form-group">
                    <label for="current_job_role">Current Job Role</label>
                    <input type="text" id="current_job_role" name="current_job_role">
                </div>
                <div class="form-group">
                    <label for="current_salary">Current Salary</label>
                    <select id="current_salary" name="current_salary">
                        <option value="" disabled selected>Select Current Salary</option>
                        <option value="5k-10k">5k-10k</option>
                        <option value="10k-20k">10k-20k</option>
                        <option value="20k-30k">20k-30k</option>
                        <option value="30k-40k">30k-40k</option>
                        <option value="50k-60k">50k-60k</option>
                        <option value="60k+">60k+</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="years_of_experience">Years of Experience</label>
                    <select id="years_of_experience" name="years_of_experience">
                        <option value="" disabled selected>Select Years of Experience</option>
                        <option value="0-1">0-1</option>
                        <option value="2-5">2-5</option>
                        <option value="6-10">6-10</option>
                        <option value="11+">11+</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="future_aspirations">Future Aspirations</label>
                    <input type="text" id="future_aspirations" name="future_aspirations">
                </div>
            </div>
        `;
    }

    // Fields for all except students and freshers
    if (profileType !== 'student' && profileType !== 'fresher' && profileType !== 'professional' && profileType !== 'freelancer') {
        fields += `
            <div class="form-section">
                <h2>Previous Experience</h2>
                <div class="form-group">
                    <label for="previous_job_roles">Previous Job Roles</label>
                    <input type="text" id="previous_job_roles" name="previous_job_roles" placeholder="Enter roles separated by commas">
                </div>
            </div>
        `;
    }

    // Submit button
    fields += `
        <div class="form-actions">
            <button type="submit" class="submit-btn">
                <i class="fas fa-paper-plane"></i>
                Submit Registration
            </button>
        </div>
    `;

    form.innerHTML = fields;

    // Initialize other form features
    initializeActivityButtons();
    initializeOtherInputs();
    initializeDomainOptions();

    // Add form submit handler
    form.onsubmit = handleFormSubmit;
}

function initializeActivityButtons() {
    const activityButtons = document.querySelectorAll('.activity-btn');
    if (!activityButtons.length) return;

    const hiddenActivitiesInput = document.getElementById('selected-activities');
    let selectedActivities = [];

    activityButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.classList.toggle('selected');
            const activity = this.getAttribute('data-activity');
            if (this.classList.contains('selected')) {
                selectedActivities.push(activity);
            } else {
                selectedActivities = selectedActivities.filter(a => a !== activity);
            }
            hiddenActivitiesInput.value = selectedActivities.join(',');
        });
    });
}

function initializeOtherInputs() {
    const dynamicGroups = document.querySelectorAll('.dynamic-input-group');
    if (!dynamicGroups.length) return;

    dynamicGroups.forEach(group => {
        const select = group.querySelector('select');
        const otherContainer = group.querySelector('.other-input-container');
        const otherInput = otherContainer?.querySelector('input');
        
        if (!select || !otherContainer || !otherInput) return;
        
        select.addEventListener('change', function() {
            if (this.value === 'other') {
                otherContainer.style.display = 'block';
                setTimeout(() => {
                    otherContainer.style.maxHeight = otherContainer.scrollHeight + 'px';
                    otherInput.required = true;
                }, 10);
            } else {
                otherContainer.style.maxHeight = '0';
                otherInput.required = false;
                setTimeout(() => {
                    otherContainer.style.display = 'none';
                }, 300);
            }
        });
    });
}

function initializeDomainOptions() {
    const educationLevelSelect = document.getElementById('education_level');
    const fieldDomainSelect = document.getElementById('field_or_domain');
    const domainOtherContainer = document.querySelector('#field_or_domain + .other-input-container');
    const domainOtherInput = domainOtherContainer.querySelector('input');

    const domainOptions = {
        'high_school': [
            'Not Applicable'
        ],
        'higher_secondary': [
            'Physics, Chemistry, Mathematics (PCM)', 'Physics, Chemistry, Biology (PCB)', 'Computer Science',
            'Electronics', 'Commerce', 'Accountancy', 'Business Studies', 'Economics', 'Arts / Humanities',
            'Psychology', 'Home Science', 'Vocational Stream'
        ],
        'diploma': [
            'Computer Applications', 'Mechanical Engineering', 'Electrical Engineering', 'Civil Engineering',
            'Electronics & Communication', 'Automobile Engineering', 'Fashion Designing', 'Graphic Designing',
            'Nursing', 'Hotel Management', 'Refrigeration & AC', 'Web Development', 'Health and Sanitation',
            'Beauty & Wellness', 'Carpentry', 'Welding', 'Other Technical/Vocational'
        ],
        'associate_degree': [
            'Liberal Arts', 'Business Administration', 'Information Technology', 'Computer Science',
            'Engineering Technology', 'Health Sciences', 'Paralegal Studies', 'Criminal Justice',
            'Early Childhood Education', 'Social Sciences', 'Graphic Design', 'Environmental Studies'
        ],
        'bachelors': [
            'Computer Science / IT', 'Electronics / ECE / EEE', 'Mechanical Engineering', 'Civil Engineering',
            'Biotechnology', 'Data Science / AI / ML', 'Business Administration (BBA)', 'Commerce (B.Com)',
            'Economics', 'Psychology', 'English Literature', 'Journalism / Mass Communication', 'Education / B.Ed',
            'Law / LLB', 'Nursing / B.Sc Nursing', 'Pharmacy', 'Architecture / B.Arch', 'Fine Arts / Design / Animation',
            'Agriculture / Forestry', 'Hotel Management', 'Tourism & Hospitality'
        ],
        'masters': [
            'M.Tech (Any Specialization)', 'M.Sc (Science Subjects)', 'MBA (HR, Finance, Marketing, Operations, etc.)',
            'M.Com', 'MA (English, History, Psychology, Sociology, etc.)', 'MCA (Computer Applications)', 'LLM (Law)',
            'M.Ed (Education)', 'Public Health / MPH', 'M.Des (Design)', 'MSW (Social Work)', 'M.Pharm (Pharmacy)',
            'Clinical Research', 'Data Science / Business Analytics', 'Other (user-defined)'
        ],
        'doctorate': [
            'Engineering (Specialized Field)', 'Sciences (Physics, Chemistry, Biology, etc.)', 'Social Sciences',
            'Literature & Languages', 'Education', 'Psychology', 'Law', 'Public Health',
            'Management', 'Artificial Intelligence / Robotics', 'Humanities / Cultural Studies',
            'Agriculture / Environmental Science', 'Interdisciplinary Studies', 'Other (user-defined)'
        ],
        'professional_certifications': [
            'Chartered Accountant (CA)', 'Certified Financial Analyst (CFA)', 'Company Secretary (CS)',
            'PMP (Project Management Professional)', 'Six Sigma (Green/Black Belt)', 'AWS / Azure / Google Cloud',
            'DevOps', 'Data Science / Machine Learning', 'Cybersecurity', 'Full-Stack Development',
            'Digital Marketing', 'UI/UX Design', 'Ethical Hacking', 'Networking (CCNA, CompTIA)',
            'HR Certifications (SHRM, HRCI)', 'Teaching Certifications (TESOL, CELTA, etc.)',
            'Medical Coding', 'Pharmacy Technician Certification', 'Other (user-defined)'
        ],
        'other': []
    };

    educationLevelSelect.addEventListener('change', function() {
        const selectedLevel = this.value;
        const options = domainOptions[selectedLevel] || [];

        fieldDomainSelect.innerHTML = options.map(option => `<option value="${option}">${option}</option>`).join('');
        fieldDomainSelect.disabled = options.length === 0;

        if (selectedLevel === 'other') {
            domainOtherContainer.style.display = 'block';
            setTimeout(() => {
                domainOtherContainer.style.maxHeight = domainOtherContainer.scrollHeight + 'px';
                domainOtherInput.required = true;
            }, 10);
        } else {
            domainOtherContainer.style.maxHeight = '0';
            domainOtherInput.required = false;
            setTimeout(() => {
                domainOtherContainer.style.display = 'none';
            }, 300);
        }
    });
}

function generateYearOptions() {
    const currentYear = new Date().getFullYear();
    let options = '<option value="">Select Year</option>';
    for (let i = 0; i < 6; i++) {
        const year = currentYear + i;
        options += `<option value="${year}">${year}</option>`;
    }
    return options;
}

function generateCheckboxes(items, name) {
    return items.map(item => `
        <div class="checkbox-item">
            <input type="checkbox" id="${name}_${item.toLowerCase().replace(/\s+/g, '_')}" 
                   name="${name}[]" value="${item.toLowerCase().replace(/\s+/g, '_')}">
            <label for="${name}_${item.toLowerCase().replace(/\s+/g, '_')}">${item}</label>
        </div>
    `).join('');
}

function handleFormSubmit(e) {
    e.preventDefault();
    const form = e.target;
    form.classList.add('loading');

    // Add debugging logs
    const formData = new FormData(form);
    
    // Ensure user_type is included
    const userTypeInput = form.querySelector('#user_type_input');
    if (userTypeInput && userTypeInput.value) {
        console.log('User type from hidden input:', userTypeInput.value);
    }

    console.log('Form Data being submitted:');
    for (let pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
    }

    // Send data to server
    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams(formData).toString()
    })
    .then(response => {
        form.classList.remove('loading');
        if (response.ok) {
            // Redirect to a new page on success
            window.location.href = '/success'; // Change '/success' to your desired URL
        } else {
            showErrorMessage('An error occurred during submission.');
        }
    })
    .catch(error => {
        form.classList.remove('loading');
        showErrorMessage('An error occurred during submission.');
        console.error('Error:', error);
    });
}

function showSuccessMessage() {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.innerHTML = '<i class="fas fa-check-circle"></i> Registration submitted successfully!';
    document.querySelector('.registration-container').appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.remove();
    }, 5000);
}

function showErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    document.querySelector('.registration-container').appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registrationForm');
    if (form) {
        const submitBtn = form.querySelector('.submit-btn');
        if (submitBtn) {
            form.addEventListener('submit', (e) => {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Submitting...`;
            });
        }
    }
});