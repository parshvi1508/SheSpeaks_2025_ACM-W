document.addEventListener('DOMContentLoaded', () => {
  // Form elements
  const form = document.getElementById('sheSpeaksForm');
  const sections = document.querySelectorAll('.form-section');
  const progressFill = document.getElementById('progressFill');
  const progressText = document.getElementById('progressText');
  const thankYou = document.getElementById('thankYou');
  const submitBtn = document.getElementById('submitBtn');
  const finalSubmitBtn = document.getElementById('finalSubmitBtn');
  
  // Navigation buttons
  const nextButtons = document.querySelectorAll('.next-btn');
  const prevButtons = document.querySelectorAll('.prev-btn');
  
  // Range sliders
  const sliders = document.querySelectorAll('input[type="range"]');
  
  // Current section tracker
  let currentSection = 1;
  const totalSections = sections.length;
  
  // Update progress bar
  const updateProgress = () => {
    const progressPercentage = ((currentSection - 1) / (totalSections - 1)) * 100;
    progressFill.style.width = `${progressPercentage}%`;
    
    // Update progress text
    if (currentSection === 1) {
      progressText.textContent = "Let's begin your story...";
    } else if (currentSection === totalSections) {
      progressText.textContent = "Final step — almost done!";
    } else {
      progressText.textContent = `Section ${currentSection} of ${totalSections}`;
    }
  };
  
  // Show a specific section
  const showSection = (sectionNumber) => {
    sections.forEach(section => {
      section.classList.remove('active');
      section.style.display = 'none';
    });
    
    const targetSection = document.querySelector(`.form-section[data-section="${sectionNumber}"]`);
    if (targetSection) {
      targetSection.classList.add('active');
      targetSection.style.display = 'block';
      
      // Smooth scroll to top of section
      window.scrollTo({
        top: targetSection.offsetTop - 50,
        behavior: 'smooth'
      });
    }
    
    updateProgress();
  };
  
  // Initialize form - show first section
  const initForm = () => {
    sections.forEach((section, index) => {
      if (index === 0) {
        section.classList.add('active');
        section.style.display = 'block';
      } else {
        section.style.display = 'none';
      }
    });
    
    updateProgress();
  };
  
  // Next button handler
  nextButtons.forEach(button => {
    button.addEventListener('click', () => {
      if (currentSection < totalSections) {
        currentSection++;
        showSection(currentSection);
      }
    });
  });
  
  // Previous button handler
  prevButtons.forEach(button => {
    button.addEventListener('click', () => {
      if (currentSection > 1) {
        currentSection--;
        showSection(currentSection);
      }
    });
  });
  
  // Final submit button handler
  finalSubmitBtn.addEventListener('click', () => {
    submitBtn.click(); // Trigger the actual form submission
  });
  
  // Handle form submission
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    
    // Hide form
    form.style.display = 'none';
    
    // Show thank you message
    thankYou.style.display = 'block';
    
    // Clear progress bar and text
    progressFill.style.width = '100%';
    progressText.textContent = 'Thank you for your voice!';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // In a real app, you would send the form data to your server here
    console.log('Form submitted');
  });
  
  // Update slider values when moved
  sliders.forEach(slider => {
    const valueDisplay = document.querySelector(`.slider-value[data-slider="${slider.name}"]`);
    
    slider.addEventListener('input', () => {
      if (valueDisplay) {
        valueDisplay.textContent = slider.value;
      }
    });
  });
  
  // Initialize form
  initForm();
});