document.getElementById('signupForm').addEventListener('submit', function(e) {
  e.preventDefault();
  
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  
  if (password !== confirmPassword) {
    alert('Passwords do not match!');
    return;
  }
  
  if (password.length < 8) {
    alert('Password must be at least 8 characters long!');
    return;
  }
  window.location.href = 'chatbot.html';
}); 