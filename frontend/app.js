const authView = document.getElementById('auth-view');
const dashboardView = document.getElementById('dashboard-view');
const authForm = document.getElementById('auth-form');
const logoutBtn = document.getElementById('logout-btn');
const authTitle = document.getElementById('auth-title');
const authSubtitle = document.getElementById('auth-subtitle');
const registerFields = document.getElementById('register-fields');
const authBtn = document.getElementById('auth-btn');
const switchText = document.getElementById('switch-text');
const noteCreatorForm = document.getElementById('note-creator-form');
const notesGrid = document.getElementById('notes-grid');
const toastEl = document.getElementById('toast');

let isLoginMode = true;

function toggleMode() {
    isLoginMode = !isLoginMode;
    if(isLoginMode) {
        authTitle.innerText = "Welcome Back";
        authSubtitle.innerText = "Log in to safely access your personal notes.";
        authBtn.innerText = "Log In";
        switchText.innerHTML = `Don't have an account? <span id="switch-action">Sign up</span>`;
        registerFields.style.display = "none";
        document.getElementById('auth-email').required = false;
    } else {
        authTitle.innerText = "Create Account";
        authSubtitle.innerText = "Sign up to start saving your brilliant ideas.";
        authBtn.innerText = "Sign Up";
        switchText.innerHTML = `Already have an account? <span id="switch-action">Log in</span>`;
        registerFields.style.display = "block";
        document.getElementById('auth-email').required = true;
    }
    document.getElementById('switch-action').addEventListener('click', toggleMode);
}

document.getElementById('switch-action').addEventListener('click', toggleMode);

function showToast(msg, isError = false) {
    toastEl.innerText = msg;
    toastEl.style.backgroundColor = isError ? "var(--danger-color)" : "var(--success-color)";
    toastEl.classList.add('show');
    setTimeout(() => {
        toastEl.classList.remove('show');
    }, 3000);
}

async function checkAuthStatus() {
    try {
        const res = await fetch('/notes', { credentials: 'include' });
        if(res.ok) {
            const data = await res.json();
            showDashboard(data);
        } else {
            showAuth();
        }
    } catch (err) {
        showAuth();
    }
}

function showDashboard(notes) {
    authView.classList.add('hidden');
    dashboardView.classList.remove('hidden');
    renderNotes(notes);
}

function showAuth() {
    authView.classList.remove('hidden');
    dashboardView.classList.add('hidden');
}

authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('auth-username').value;
    const password = document.getElementById('auth-password').value;
    
    if(isLoginMode) {
        try {
            const res = await fetch(`/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`, {
                method: 'POST',
                credentials: 'include'
            });
            if(res.ok) {
                showToast("Logged in successfully!");
                document.getElementById('auth-password').value = "";
                checkAuthStatus();
            } else {
                const data = await res.json();
                showToast(data.detail || "Login failed", true);
            }
        } catch(err) {
            showToast("Network error", true);
        }
    } else {
        const email = document.getElementById('auth-email').value;
        try {
            const res = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            if(res.ok) {
                showToast("Registered successfully! Please log in.");
                toggleMode();
            } else {
                const data = await res.json();
                showToast(data.detail || "Registration failed", true);
            }
        } catch(err) {
            showToast("Network error", true);
        }
    }
});

logoutBtn.addEventListener('click', async () => {
    try {
        await fetch('/logout', { method: 'POST', credentials: 'include' });
        showAuth();
        showToast("Logged out");
    } catch(err) {
        console.error(err);
    }
});

noteCreatorForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const titleEl = document.getElementById('note-title');
    const contentEl = document.getElementById('note-content');
    
    try {
        const res = await fetch('/notes', {
            method: 'POST',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: titleEl.value, content: contentEl.value })
        });
        
        if(res.ok) {
            showToast("Note created!");
            titleEl.value = "";
            contentEl.value = "";
            checkAuthStatus();
        } else {
            showToast("Failed to create note", true);
        }
    } catch(err) {
        showToast("Error creating note", true);
    }
});

async function deleteNote(id) {
    try {
        const res = await fetch(`/notes/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        if(res.ok) {
            showToast("Note deleted");
            checkAuthStatus();
        } else {
            showToast("Failed to delete note", true);
        }
    } catch(err) {
        showToast("Error deleting note", true);
    }
}

function renderNotes(notes) {
    notesGrid.innerHTML = "";
    if(notes.length === 0) {
        notesGrid.innerHTML = `<p style="color: var(--text-secondary); grid-column: 1/-1;">You don't have any notes yet.</p>`;
        return;
    }
    
    notes.forEach(note => {
        const card = document.createElement('div');
        card.className = 'note-card';
        
        const dateStr = new Date(note.created_at).toLocaleDateString(undefined, {
            year: 'numeric', month: 'short', day: 'numeric'
        });

        card.innerHTML = `
            <div>
                <h3 class="note-title">${escapeHTML(note.title)}</h3>
                <div class="note-content">${escapeHTML(note.content).replace(/\n/g, '<br>')}</div>
            </div>
            <div class="note-footer">
                <span>${dateStr}</span>
                <button class="btn-danger" onclick="deleteNote(${note.id})">Delete</button>
            </div>
        `;
        notesGrid.appendChild(card);
    });
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
        tag => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            "'": '&#39;',
            '"': '&quot;'
        }[tag] || tag)
    );
}

checkAuthStatus();
