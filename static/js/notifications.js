function updateNotifCount() {
    fetch("/api/notifications/count")
        .then(r => r.json())
        .then(d => {
            const b = document.getElementById("notif-badge");
            if (b) {
                b.textContent = d.count;
                b.style.cssText = d.count > 0 ? "display:flex !important" : "display:none !important";
            }
        })
        .catch(() => {});
}

document.addEventListener("DOMContentLoaded", function() {
    const notifPopup = document.createElement("div");
    notifPopup.id = "notif-popup";
    notifPopup.style.cssText = "position:fixed;top:80px;left:50%;transform:translateX(-50%);background:white;border-radius:16px;padding:20px;max-width:400px;width:90%;max-height:400px;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,0.3);z-index:3000;display:none;direction:rtl;";
    notifPopup.innerHTML = '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;"><h3 style="font-size:18px;font-weight:800;">🔔 الإشعارات</h3><button id="notif-close" style="background:none;border:none;font-size:24px;cursor:pointer;color:var(--gray-dark);">&times;</button></div><div id="notif-popup-list" style="color:var(--gray-dark);"><p style="text-align:center;">تحميل...</p></div><button id="notif-mark-read" style="margin-top:12px;width:100%;padding:8px;border-radius:12px;background:rgba(0,0,0,0.05);border:none;cursor:pointer;font-family:inherit;font-size:13px;font-weight:600;color:var(--dark);">✅ تحديد الكل كمقروء</button>';
    document.body.appendChild(notifPopup);

    const notifOverlay = document.createElement("div");
    notifOverlay.id = "notif-overlay";
    notifOverlay.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,0.3);z-index:2999;display:none;";
    notifOverlay.addEventListener("click", closeNotifPopup);
    document.body.appendChild(notifOverlay);

    document.getElementById("notif-btn")?.addEventListener("click", function(e) {
        e.stopPropagation();
        const popup = document.getElementById("notif-popup");
        const overlay = document.getElementById("notif-overlay");
        if (popup.style.display === "block") {
            closeNotifPopup();
        } else {
            popup.style.display = "block";
            overlay.style.display = "block";
            loadNotifsToPopup();
        }
    });

    document.getElementById("notif-close")?.addEventListener("click", closeNotifPopup);

    document.getElementById("notif-mark-read")?.addEventListener("click", function() {
        fetch("/api/notifications/read-all", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRF-TOKEN": getCSRFToken()
            },
            body: "csrf_token=" + encodeURIComponent(getCSRFToken())
        }).then(() => {
            loadNotifsToPopup();
            updateNotifCount();
        });
    });

    function closeNotifPopup() {
        document.getElementById("notif-popup").style.display = "none";
        document.getElementById("notif-overlay").style.display = "none";
    }

    function loadNotifsToPopup() {
        const c = document.getElementById("notif-popup-list");
        if (!c) return;
        c.innerHTML = '<p style="text-align:center;color:var(--gray-dark);">تحميل...</p>';
        fetch("/api/notifications")
            .then(r => r.json())
            .then(n => {
                if (!n || n.length === 0) {
                    c.innerHTML = '<p style="text-align:center;color:var(--gray-dark);padding:20px;">📭 لا توجد اشعارات</p>';
                    return;
                }
                c.innerHTML = n.map(x => `<div style="padding:12px;margin-bottom:8px;background:rgba(0,0,0,0.02);border-radius:12px;border-right:3px solid var(--primary);"><p style="font-size:14px;font-weight:600;margin-bottom:4px;">${x.message}</p><span style="font-size:11px;color:var(--gray-dark);">${new Date(x.created_at).toLocaleString('ar-IQ')}</span></div>`).join("");
            })
            .catch(() => {
                c.innerHTML = '<p style="text-align:center;color:var(--red);">تعذر تحميل الاشعارات</p>';
            });
    }
});
