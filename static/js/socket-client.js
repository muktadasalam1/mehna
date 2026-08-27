const socket = io();

socket.on("notification", (d) => {
    updateNotifCount();
});

function getCSRFToken() {
    const t = document.querySelector('input[name="csrf_token"]');
    return t ? t.value : "";
}

function togglePassword(i, b) {
    const inp = document.getElementById(i);
    const icon = b.querySelector("i");
    if (inp.type === "password") {
        inp.type = "text";
        icon.className = "fa-solid fa-eye-slash";
    } else {
        inp.type = "password";
        icon.className = "fa-solid fa-eye";
    }
}

function showFieldError(i, m) {
    const e = document.getElementById(i + "-error");
    const n = document.getElementById(i);
    if (e) {
        e.textContent = m;
        e.classList.add("visible");
    }
    if (n) n.style.borderColor = "var(--red)";
}

function clearFieldError(i) {
    const e = document.getElementById(i + "-error");
    const n = document.getElementById(i);
    if (e) {
        e.textContent = "";
        e.classList.remove("visible");
    }
    if (n) n.style.borderColor = "";
}

function setBtnLoading(btnId, text) {
    const b = document.getElementById(btnId);
    if (b) {
        b.disabled = true;
        b.dataset.original = b.innerHTML;
        b.innerHTML = '<span class="spinner"></span> ' + text;
    }
}

let deleteUrl = "";

function openDeleteModal(e, url) {
    e.preventDefault();
    deleteUrl = url;
    document.getElementById("delete-modal").classList.add("show");
}

function closeDeleteModal() {
    document.getElementById("delete-modal").classList.remove("show");
    deleteUrl = "";
}

document.getElementById("delete-confirm-btn").addEventListener("click", () => {
    if (deleteUrl) window.location.href = deleteUrl;
});

document.getElementById("delete-modal").addEventListener("click", function (e) {
    if (e.target === this) closeDeleteModal();
});

["reg-fullname", "reg-email", "reg-password", "login-email", "login-password", "forgot-email", "reset-password", "reset-confirm-password"].forEach(i => {
    const el = document.getElementById(i);
    el?.addEventListener("input", () => clearFieldError(i));
});
