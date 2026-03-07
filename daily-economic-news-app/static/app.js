document.addEventListener('DOMContentLoaded', () => {
    const app = {
        // UI Elements
        loginContainer: document.getElementById('login-container'),
        registerContainer: document.getElementById('register-container'),
        dashboardContainer: document.getElementById('dashboard-container'),
        loginForm: document.getElementById('login-form'),
        registerForm: document.getElementById('register-form'),
        preferencesForm: document.getElementById('preferences-form'),
        addStockForm: document.getElementById('add-stock-form'),
        addCurrencyForm: document.getElementById('add-currency-form'),
        stocksList: document.getElementById('stocks-list'),
        currenciesList: document.getElementById('currencies-list'),
        logoutButton: document.getElementById('logout-button'),
        manualSendButton: document.getElementById('manual-send-button'),
        welcomeMessage: document.getElementById('welcome-message'),
        emailTimeInput: document.getElementById('email-time'),
        loginError: document.getElementById('login-error'),
        registerError: document.getElementById('register-error'),
        manualSendStatus: document.getElementById('manual-send-status'),

        // State
        token: localStorage.getItem('accessToken'),
        
        // API Base
        api: {
            async post(endpoint, data, needsAuth = false, isForm = false) {
                const headers = {};
                let body;

                if (isForm) {
                    headers['Content-Type'] = 'application/x-www-form-urlencoded';
                    body = new URLSearchParams(data).toString();
                } else {
                    headers['Content-Type'] = 'application/json';
                    body = JSON.stringify(data);
                }

                if (needsAuth) {
                    if (!app.token) throw new Error('Not authenticated');
                    headers['Authorization'] = `Bearer ${app.token}`;
                }

                try {
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers,
                        body,
                    });
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'An error occurred');
                    }
                    return response.json();
                } catch (error) {
                    console.error(`API Error on POST ${endpoint}:`, error);
                    throw error;
                }
            },
            async get(endpoint, needsAuth = true) {
                const headers = {};
                if (needsAuth) {
                    if (!app.token) throw new Error('Not authenticated');
                    headers['Authorization'] = `Bearer ${app.token}`;
                }
                try {
                    const response = await fetch(endpoint, { headers });
                     if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'An error occurred');
                    }
                    return response.json();
                } catch (error) {
                    console.error(`API Error on GET ${endpoint}:`, error);
                    throw error;
                }
            },
            async delete(endpoint, id) {
                 const headers = {'Authorization': `Bearer ${app.token}`};
                 try {
                    const response = await fetch(`${endpoint}/${id}`, { method: 'DELETE', headers });
                     if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || 'An error occurred');
                    }
                    return response.json();
                } catch (error) {
                    console.error(`API Error on DELETE ${endpoint}/${id}:`, error);
                    throw error;
                }
            },
        },

        // Methods
        init() {
            this.addEventListeners();
            if (this.token) {
                this.showDashboard();
            } else {
                this.showLogin();
            }
        },

        addEventListeners() {
            this.loginForm.addEventListener('submit', this.handleLogin.bind(this));
            this.registerForm.addEventListener('submit', this.handleRegister.bind(this));
            this.logoutButton.addEventListener('click', this.handleLogout.bind(this));
            this.preferencesForm.addEventListener('submit', this.handleUpdateTime.bind(this));
            this.addStockForm.addEventListener('submit', this.handleAddStock.bind(this));
            this.addCurrencyForm.addEventListener('submit', this.handleAddCurrency.bind(this));
            this.manualSendButton.addEventListener('click', this.handleManualSend.bind(this));
            document.getElementById('show-register').addEventListener('click', (e) => { e.preventDefault(); this.showRegister(); });
            document.getElementById('show-login').addEventListener('click', (e) => { e.preventDefault(); this.showLogin(); });
        },

        async handleLogin(e) {
            e.preventDefault();
            this.loginError.textContent = '';
            const data = {
                username: this.loginForm.username.value,
                password: this.loginForm.password.value,
            };
            try {
                const response = await this.api.post('/token', data, false, true);
                this.token = response.access_token;
                localStorage.setItem('accessToken', this.token);
                this.showDashboard();
            } catch (error) {
                this.loginError.textContent = error.message;
            }
        },
        
        async handleRegister(e) {
            e.preventDefault();
            this.registerError.textContent = '';
             const data = {
                username: document.getElementById('reg-username').value,
                email: document.getElementById('reg-email').value,
                password: document.getElementById('reg-password').value,
            };
            try {
                await this.api.post('/register', data);
                alert('Registration successful! Please login.');
                this.showLogin();
            } catch (error) {
                this.registerError.textContent = error.message;
            }
        },

        handleLogout() {
            this.token = null;
            localStorage.removeItem('accessToken');
            this.showLogin();
        },
        
        async handleUpdateTime(e){
            e.preventDefault();
            try {
                await this.api.post('/preferences/', { email_time: this.emailTimeInput.value }, true);
                alert('Email time updated!');
                this.loadDashboardData();
            } catch (error) {
                alert(`Error updating time: ${error.message}`);
            }
        },
        
        async handleAddStock(e){
            e.preventDefault();
            const symbolInput = document.getElementById('stock-symbol');
            try {
                await this.api.post('/stocks/', { symbol: symbolInput.value, is_active: true }, true);
                symbolInput.value = '';
                this.loadDashboardData();
            } catch (error) {
                alert(`Error adding stock: ${error.message}`);
            }
        },

        async handleAddCurrency(e){
            e.preventDefault();
            const symbolInput = document.getElementById('currency-symbol');
            try {
                await this.api.post('/currencies/', { symbol: symbolInput.value, is_active: true }, true);
                symbolInput.value = '';
                this.loadDashboardData();
            } catch (error) {
                alert(`Error adding currency: ${error.message}`);
            }
        },
        
        async handleManualSend(){
            this.manualSendStatus.textContent = 'Sending...';
            try {
                const response = await this.api.post('/send-daily-email', {}, true);
                this.manualSendStatus.textContent = response.message;
            } catch (error) {
                this.manualSendStatus.textContent = `Error: ${error.message}`;
            }
        },

        showLogin() {
            this.loginContainer.classList.remove('hidden');
            this.registerContainer.classList.add('hidden');
            this.dashboardContainer.classList.add('hidden');
        },
        
        showRegister() {
            this.loginContainer.classList.add('hidden');
            this.registerContainer.classList.remove('hidden');
            this.dashboardContainer.classList.add('hidden');
        },

        showDashboard() {
            this.loginContainer.classList.add('hidden');
            this.registerContainer.classList.add('hidden');
            this.dashboardContainer.classList.remove('hidden');
            this.loadDashboardData();
        },

        async loadDashboardData() {
            try {
                const user = await this.api.get('/users/me/');
                this.welcomeMessage.textContent = `Welcome, ${user.username}!`;
                
                // Populate preferences
                const preferences = await this.api.get('/preferences/');
                if (preferences.length > 0) {
                    this.emailTimeInput.value = preferences[0].email_time;
                }

                // Populate stocks
                const stocks = await this.api.get('/stocks/');
                this.stocksList.innerHTML = '';
                stocks.forEach(stock => {
                    const li = document.createElement('li');
                    li.textContent = stock.symbol;
                    const deleteBtn = document.createElement('button');
                    deleteBtn.textContent = 'Remove';
                    deleteBtn.onclick = async () => {
                        try {
                            await this.api.delete('/stocks', stock.id);
                            this.loadDashboardData();
                        } catch (error) {
                            alert(`Error removing stock: ${error.message}`);
                        }
                    };
                    li.appendChild(deleteBtn);
                    this.stocksList.appendChild(li);
                });

                // Populate currencies
                const currencies = await this.api.get('/currencies/');
                this.currenciesList.innerHTML = '';
                currencies.forEach(currency => {
                    const li = document.createElement('li');
                    li.textContent = currency.symbol;
                    const deleteBtn = document.createElement('button');
                    deleteBtn.textContent = 'Remove';
                    deleteBtn.onclick = async () => {
                        try {
                             await this.api.delete('/currencies', currency.id);
                             this.loadDashboardData();
                        } catch (error) {
                            alert(`Error removing currency: ${error.message}`);
                        }
                    };
                    li.appendChild(deleteBtn);
                    this.currenciesList.appendChild(li);
                });

            } catch (error) {
                console.error('Failed to load dashboard data:', error);
                this.handleLogout(); // If token is invalid or user not found, log out.
            }
        },
    };

    app.init();
});
