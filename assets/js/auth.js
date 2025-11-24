// auth.js - Beautiful Login/Signup Modal with Modern Design

// Create stunning auth modal HTML
const modalHTML = `
<div id="auth-modal" class="auth-modal" style="display:none;">
  <div class="auth-modal-overlay"></div>
  <div class="auth-modal-container">
    <div class="auth-modal-content">
      <button class="auth-close" id="auth-close">
        <i class="fas fa-times"></i>
      </button>
      
      <!-- Login Form -->
      <div id="loginForm" class="auth-form active">
        <div class="auth-header">
          <div class="auth-icon">
            <i class="fas fa-plane-departure"></i>
          </div>
          <h2>Welcome Back!</h2>
          <p>Login to continue your journey</p>
        </div>
        
        <form id="loginFormElement" class="auth-inputs">
          <div class="input-group">
            <i class="fas fa-envelope input-icon"></i>
            <input type="email" id="loginEmail" required placeholder="Email Address">
          </div>
          
          <div class="input-group">
            <i class="fas fa-lock input-icon"></i>
            <input type="password" id="loginPassword" required placeholder="Password">
          </div>
          
          <div class="auth-options">
            <label class="remember-me">
              <input type="checkbox" id="rememberMe">
              <span>Remember me</span>
            </label>
            <a href="#" class="forgot-password">Forgot password?</a>
          </div>
          
          <button type="submit" class="auth-btn">
            <span>Sign In</span>
            <i class="fas fa-arrow-right"></i>
          </button>
        </form>
        
        <div class="auth-footer">
          <p>Don't have an account? <a href="#" id="showSignup">Create one</a></p>
        </div>
      </div>

      <!-- Signup Form -->
      <div id="signupForm" class="auth-form">
        <div class="auth-header">
          <div class="auth-icon">
            <i class="fas fa-user-plus"></i>
          </div>
          <h2>Join LuxeTravel</h2>
          <p>Start your premium travel experience</p>
        </div>
        
        <form id="signupFormElement" class="auth-inputs">
          <div class="input-group">
            <i class="fas fa-user input-icon"></i>
            <input type="text" id="signupName" required placeholder="Full Name">
          </div>
          
          <div class="input-group">
            <i class="fas fa-envelope input-icon"></i>
            <input type="email" id="signupEmail" required placeholder="Email Address">
          </div>
          
          <div class="input-group">
            <i class="fas fa-lock input-icon"></i>
            <input type="password" id="signupPassword" required minlength="6" placeholder="Password">
          </div>
          
          <div class="input-group">
            <i class="fas fa-lock input-icon"></i>
            <input type="password" id="signupConfirmPassword" required placeholder="Confirm Password">
          </div>
          
          <label class="terms-check">
            <input type="checkbox" id="agreeTerms" required>
            <span>I agree to the Terms & Conditions</span>
          </label>
          
          <button type="submit" class="auth-btn">
            <span>Create Account</span>
            <i class="fas fa-arrow-right"></i>
          </button>
        </form>
        
        <div class="auth-footer">
          <p>Already have an account? <a href="#" id="showLogin">Sign in</a></p>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
.auth-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease;
}

.auth-modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(5px);
}

.auth-modal-container {
  position: relative;
  z-index: 1;
  width: 90%;
  max-width: 450px;
  animation: slideUp 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.auth-modal-content {
  background: linear-gradient(135deg, rgba(26, 26, 46, 0.95), rgba(20, 20, 35, 0.98));
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 20px;
  padding: 3rem 2.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  position: relative;
}

.auth-close {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background: rgba(212, 175, 55, 0.1);
  border: 1px solid rgba(212, 175, 55, 0.3);
  color: var(--gold);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.auth-close:hover {
  background: rgba(212, 175, 55, 0.2);
  transform: rotate(90deg);
}

.auth-form {
  display: none;
}

.auth-form.active {
  display: block;
  animation: fadeIn 0.3s ease;
}

.auth-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.auth-icon {
  width: 70px;
  height: 70px;
  margin: 0 auto 1.5rem;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(212, 175, 55, 0.1));
  border: 2px solid rgba(212, 175, 55, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--gold);
}

.auth-header h2 {
  color: var(--gold);
  font-size: 2rem;
  margin-bottom: 0.5rem;
  font-family: 'Playfair Display', serif;
}

.auth-header p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.95rem;
}

.auth-inputs {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.input-group {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 1.25rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--gold);
  opacity: 0.7;
}

.input-group input {
  width: 100%;
  padding: 1rem 1rem 1rem 3.5rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 12px;
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.input-group input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--gold);
  box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.auth-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
}

.remember-me input {
  cursor: pointer;
}

.forgot-password {
  color: var(--gold);
  text-decoration: none;
  transition: all 0.3s ease;
}

.forgot-password:hover {
  text-decoration: underline;
}

.terms-check {
  display: flex;
  align-items: start;
  gap: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  cursor: pointer;
}

.terms-check input {
  margin-top: 0.25rem;
  cursor: pointer;
}

.auth-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, var(--gold), #c9a049);
  border: none;
  border-radius: 12px;
  color: #000;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.auth-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(212, 175, 55, 0.4);
}

.auth-btn i {
  transition: transform 0.3s ease;
}

.auth-btn:hover i {
  transform: translateX(5px);
}

.auth-footer {
  text-align: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(212, 175, 55, 0.2);
}

.auth-footer p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.95rem;
}

.auth-footer a {
  color: var(--gold);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
}

.auth-footer a:hover {
  text-decoration: underline;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .auth-modal-content {
    padding: 2rem 1.5rem;
  }
  
  .auth-header h2 {
    font-size: 1.75rem;
  }
}
</style>
`;

// Add modal to page
document.body.insertAdjacentHTML('beforeend', modalHTML);

// Get elements
const modal = document.getElementById('auth-modal');
const closeBtn = document.getElementById('auth-close');
const loginBtn = document.getElementById('loginBtn');
const showSignup = document.getElementById('showSignup');
const showLogin = document.getElementById('showLogin');
const loginFormElement = document.getElementById('loginFormElement');
const signupFormElement = document.getElementById('signupFormElement');
const overlay = document.querySelector('.auth-modal-overlay');

// Show modal
function openModal() {
  modal.style.display = 'flex';
  document.body.style.overflow = 'hidden';
}

// Close modal
function closeModal() {
  modal.style.display = 'none';
  document.body.style.overflow = 'auto';
}

// Event listeners
if (loginBtn) {
  loginBtn.addEventListener('click', function (e) {
    e.preventDefault();
    openModal();
    document.getElementById('loginForm').classList.add('active');
    document.getElementById('signupForm').classList.remove('active');
  });
}

closeBtn.addEventListener('click', closeModal);
overlay.addEventListener('click', closeModal);

showSignup.addEventListener('click', function (e) {
  e.preventDefault();
  document.getElementById('loginForm').classList.remove('active');
  document.getElementById('signupForm').classList.add('active');
});

showLogin.addEventListener('click', function (e) {
  e.preventDefault();
  document.getElementById('signupForm').classList.remove('active');
  document.getElementById('loginForm').classList.add('active');
});

// Handle login
loginFormElement.addEventListener('submit', async function (e) {
  e.preventDefault();
  const email = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;

  try {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (data.success) {
      localStorage.setItem('luxetravel_user', JSON.stringify(data.user));
      closeModal();
      updateNavbar(data.user);
      showToast(`Welcome back, ${data.user.name}!`);
    } else {
      showToast(data.message || 'Login failed', 'error');
    }
  } catch (error) {
    console.error('Login error:', error);
    showToast('Login failed. Please try again.', 'error');
  }
});

// Handle signup
signupFormElement.addEventListener('submit', async function (e) {
  e.preventDefault();
  const name = document.getElementById('signupName').value;
  const email = document.getElementById('signupEmail').value;
  const password = document.getElementById('signupPassword').value;
  const confirmPassword = document.getElementById('signupConfirmPassword').value;

  if (password !== confirmPassword) {
    showToast('Passwords do not match!', 'error');
    return;
  }

  try {
    const response = await fetch('http://localhost:8000/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });

    const data = await response.json();

    if (data.success) {
      localStorage.setItem('luxetravel_user', JSON.stringify(data.user));
      closeModal();
      updateNavbar(data.user);
      showToast(`Welcome to LuxeTravel, ${data.user.name}!`);
    } else {
      showToast(data.message || 'Signup failed', 'error');
    }
  } catch (error) {
    console.error('Signup error:', error);
    showToast('Signup failed. Please try again.', 'error');
  }
});

// Update navbar after login
function updateNavbar(user) {
  const loginBtn = document.getElementById('loginBtn');
  if (loginBtn && user) {
    loginBtn.innerHTML = `<i class="fas fa-user-circle"></i> ${user.name}`;
    loginBtn.onclick = function (e) {
      e.preventDefault();
      if (confirm('Do you want to logout?')) {
        localStorage.removeItem('luxetravel_user');
        location.reload();
      }
    };
  }
}

// Check if user is logged in
const savedUser = localStorage.getItem('luxetravel_user');
if (savedUser) {
  const user = JSON.parse(savedUser);
  updateNavbar(user);
}

// Toast notification helper
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: ${type === 'success' ? 'linear-gradient(135deg, #10b981, #059669)' : 'linear-gradient(135deg, #ef4444, #dc2626)'};
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    z-index: 10001;
    animation: slideIn 0.3s ease;
  `;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}
