const API_URL = "";

const loginSection = document.getElementById("login-section");
const dashboardSection = document.getElementById("dashboard-section");

const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("login-message");

const logoutButton = document.getElementById("logout-button");

const candidateTableBody = document.getElementById("candidate-table-body");

const candidateModal = document.getElementById("candidate-modal");
const candidateForm = document.getElementById("candidate-form");
const candidateMessage = document.getElementById("candidate-message");

const addCandidateButton = document.getElementById("add-candidate-button");
const closeModalButton = document.getElementById("close-modal");
const cancelButton = document.getElementById("cancel-button");

const modalTitle = document.getElementById("modal-title");

const candidateIdInput = document.getElementById("candidate-id");
const candidateNameInput = document.getElementById("candidate-name");
const candidateEmailInput = document.getElementById("candidate-email");
const candidatePhoneInput = document.getElementById("candidate-phone");

const totalCandidates = document.getElementById("total-candidates");


// =========================
// LOGIN
// =========================

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    loginMessage.textContent = "";

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const formData = new URLSearchParams();

    formData.append("username", username);
    formData.append("password", password);

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            loginMessage.textContent =
                data.detail || "Login failed.";
            return;
        }

        localStorage.setItem("access_token", data.access_token);

        showDashboard();

    } catch (error) {
        loginMessage.textContent =
            "Unable to connect to the server.";
    }
});


// =========================
// DASHBOARD
// =========================

function showDashboard() {
    loginSection.classList.add("hidden");
    dashboardSection.classList.remove("hidden");

    loadCandidates();
}


// =========================
// LOAD CANDIDATES
// =========================

async function loadCandidates() {

    const token = localStorage.getItem("access_token");

    if (!token) {
        showLogin();
        return;
    }

    try {

        const response = await fetch(`${API_URL}/candidates`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            logout();
            return;
        }

        const candidates = await response.json();

        if (!response.ok) {
            throw new Error(
                candidates.detail || "Unable to load candidates."
            );
        }

        candidateTableBody.innerHTML = "";

        totalCandidates.textContent = candidates.length;

        if (candidates.length === 0) {

            candidateTableBody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align:center;">
                        No candidates found.
                    </td>
                </tr>
            `;

            return;
        }

        candidates.forEach(candidate => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${candidate.id}</td>
                <td>${escapeHtml(candidate.name)}</td>
                <td>${escapeHtml(candidate.email)}</td>
                <td>${escapeHtml(candidate.phone)}</td>

                <td>
                    <button
                        class="action-button"
                        onclick="editCandidate(${candidate.id})"
                    >
                        Edit
                    </button>

                    <button
                        class="action-button delete-button"
                        onclick="deleteCandidate(${candidate.id})"
                    >
                        Delete
                    </button>
                </td>
            `;

            candidateTableBody.appendChild(row);
        });

    } catch (error) {

        console.error(error);

        candidateTableBody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align:center;">
                    Unable to load candidates.
                </td>
            </tr>
        `;
    }
}


// =========================
// OPEN ADD CANDIDATE MODAL
// =========================

addCandidateButton.addEventListener("click", () => {

    modalTitle.textContent = "Add Candidate";

    candidateForm.reset();

    candidateIdInput.value = "";

    candidateMessage.textContent = "";

    candidateModal.classList.remove("hidden");
});


// =========================
// CLOSE MODAL
// =========================

closeModalButton.addEventListener("click", closeModal);
cancelButton.addEventListener("click", closeModal);

function closeModal() {
    candidateModal.classList.add("hidden");
}


// =========================
// CREATE / UPDATE CANDIDATE
// =========================

candidateForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    candidateMessage.textContent = "";

    const token = localStorage.getItem("access_token");

    const candidateId = candidateIdInput.value;

    const candidateData = {
        name: candidateNameInput.value,
        email: candidateEmailInput.value,
        phone: candidatePhoneInput.value
    };

    const isEditing = Boolean(candidateId);

    const url = isEditing
        ? `${API_URL}/candidates/${candidateId}`
        : `${API_URL}/candidates`;

    const method = isEditing ? "PUT" : "POST";

    try {

        const response = await fetch(url, {

            method: method,

            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },

            body: JSON.stringify(candidateData)
        });

        const data = await response.json();

        if (!response.ok) {

            candidateMessage.textContent =
                data.detail || "Unable to save candidate.";

            return;
        }

        closeModal();

        await loadCandidates();

    } catch (error) {

        candidateMessage.textContent =
            "Unable to connect to the server.";
    }
});


// =========================
// EDIT CANDIDATE
// =========================

async function editCandidate(candidateId) {

    const token = localStorage.getItem("access_token");

    try {

        const response = await fetch(
            `${API_URL}/candidates/${candidateId}`,
            {
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const candidate = await response.json();

        if (!response.ok) {
            alert(candidate.detail || "Unable to load candidate.");
            return;
        }

        modalTitle.textContent = "Edit Candidate";

        candidateIdInput.value = candidate.id;
        candidateNameInput.value = candidate.name;
        candidateEmailInput.value = candidate.email;
        candidatePhoneInput.value = candidate.phone;

        candidateMessage.textContent = "";

        candidateModal.classList.remove("hidden");

    } catch (error) {

        alert("Unable to connect to the server.");
    }
}


// =========================
// DELETE CANDIDATE
// =========================

async function deleteCandidate(candidateId) {

    const confirmed = confirm(
        "Are you sure you want to delete this candidate?"
    );

    if (!confirmed) {
        return;
    }

    const token = localStorage.getItem("access_token");

    try {

        const response = await fetch(
            `${API_URL}/candidates/${candidateId}`,
            {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Unable to delete candidate.");
            return;
        }

        await loadCandidates();

    } catch (error) {

        alert("Unable to connect to the server.");
    }
}


// =========================
// LOGOUT
// =========================

logoutButton.addEventListener("click", logout);

function logout() {

    localStorage.removeItem("access_token");

    showLogin();
}

function showLogin() {

    dashboardSection.classList.add("hidden");
    loginSection.classList.remove("hidden");

    loginForm.reset();
}


// =========================
// HTML SAFETY
// =========================

function escapeHtml(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// =========================
// CHECK EXISTING LOGIN
// =========================

if (localStorage.getItem("access_token")) {
    showDashboard();
}