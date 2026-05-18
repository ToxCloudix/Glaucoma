// glaucoma/static/glaucoma/js/login.js
async function login(event) {
    event.preventDefault(); // Останавливает стандартное поведение формы

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
        const response = await fetch('/login/', {
            method: 'POST', // POST-запрос для отправки данных
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded', // Указываем формат JSON
            },
            body: formData.toString()
        });

        const data = await response.json();

        if (response.ok) {
            window.location.href = data.redirect_url || '/glaucoma/home/';
        } else {
            alert(data.message || 'Login failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred during login');
    }
}

// Подключение обработчика событий к форме
const form = document.getElementById('login-form');
form.addEventListener('submit', login);