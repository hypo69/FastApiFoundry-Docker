/**
 * support.js — Telegram Support Bot web UI
 *
 * Contains:
 *  - supportLoadDialogs()  — load and render dialog list
 *  - supportLoadProfiles() — load RAG profile list
 *  - supportCreateProfile() — create new RAG profile
 */

let _supportDialogs = {};
let _selectedChatId = null;

// ── Dialogs ───────────────────────────────────────────────────────────────────

export async function supportLoadDialogs() {
    try {
        const data = await fetch(`${window.API_BASE}/helpdesk/dialogs`).then(r => r.json());
        if (!data.success) return;
        _supportDialogs = data.dialogs || {};
        _renderUserList();
    } catch (e) {
        console.error('[support] loadDialogs error:', e);
    }
}

function _renderUserList() {
    const el = document.getElementById('support-users');
    if (!el) return;

    const chatIds = Object.keys(_supportDialogs);
    if (!chatIds.length) {
        el.innerHTML = '<div class="text-muted small p-2">No dialogs yet</div>';
        return;
    }

    el.innerHTML = chatIds.map(id => {
        const msgs = _supportDialogs[id];
        const username = msgs[0]?.username || id;
        const active = id === _selectedChatId ? 'bg-primary text-white' : '';
        return `<div class="p-2 border-bottom cursor-pointer ${active}"
                     style="cursor:pointer" onclick="supportSelectUser('${id}')">
                    <div class="fw-semibold small">${username}</div>
                    <div class="text-muted" style="font-size:0.7rem">${msgs.length} msg</div>
                </div>`;
    }).join('');
}

export function supportSelectUser(chatId) {
    _selectedChatId = chatId;
    _renderUserList();
    _renderMessages(chatId);
}

function _renderMessages(chatId) {
    const el = document.getElementById('support-messages');
    if (!el) return;

    const msgs = _supportDialogs[chatId] || [];
    el.innerHTML = msgs.map(m => {
        const isUser = m.role === 'user';
        const align = isUser ? 'text-end' : 'text-start';
        const bg = isUser ? 'bg-primary text-white' : 'bg-light';
        const ts = m.ts ? new Date(m.ts).toLocaleTimeString() : '';
        return `<div class="mb-2 ${align}">
                    <span class="badge bg-secondary me-1" style="font-size:0.65rem">${ts}</span>
                    <div class="d-inline-block rounded p-2 ${bg}" style="max-width:80%;text-align:left">
                        ${_escHtml(m.text || '')}
                    </div>
                </div>`;
    }).join('');
    el.scrollTop = el.scrollHeight;
}

function _escHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ── RAG Profiles ──────────────────────────────────────────────────────────────

export async function supportLoadProfiles() {
    try {
        const data = await fetch(`${window.API_BASE}/helpdesk/rag-profiles`).then(r => r.json());
        if (!data.success) return;
        _renderProfiles(data.profiles || []);
    } catch (e) {
        console.error('[support] loadProfiles error:', e);
    }
}

function _renderProfiles(profiles) {
    const el = document.getElementById('support-profiles-list');
    if (!el) return;

    if (!profiles.length) {
        el.innerHTML = '<div class="text-muted small">No profiles found</div>';
        return;
    }

    el.innerHTML = profiles.map(p => {
        const badge = p.has_index
            ? '<span class="badge bg-success ms-1">indexed</span>'
            : '<span class="badge bg-warning text-dark ms-1">empty</span>';
        return `<div class="d-flex justify-content-between align-items-center mb-1">
                    <div>
                        <span class="fw-semibold small">${p.name}</span>${badge}
                        ${p.description ? `<div class="text-muted" style="font-size:0.7rem">${p.description}</div>` : ''}
                    </div>
                    <button class="btn btn-sm btn-outline-danger py-0 px-1"
                            onclick="supportDeleteProfile('${p.name}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>`;
    }).join('');
}

export async function supportCreateProfile() {
    const name = document.getElementById('support-new-profile-name')?.value.trim();
    const desc = document.getElementById('support-new-profile-desc')?.value.trim();
    if (!name) return;

    try {
        const data = await fetch(`${window.API_BASE}/helpdesk/rag-profiles`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description: desc }),
        }).then(r => r.json());

        if (data.success) {
            document.getElementById('support-new-profile-name').value = '';
            document.getElementById('support-new-profile-desc').value = '';
            await supportLoadProfiles();
        }
    } catch (e) {
        console.error('[support] createProfile error:', e);
    }
}

export async function supportDeleteProfile(name) {
    try {
        await fetch(`${window.API_BASE}/helpdesk/rag-profiles/${name}`, { method: 'DELETE' });
        await supportLoadProfiles();
    } catch (e) {
        console.error('[support] deleteProfile error:', e);
    }
}

// ── Status ────────────────────────────────────────────────────────────────────

export async function supportLoadStatus() {
    try {
        const data = await fetch(`${window.API_BASE}/helpdesk/config`).then(r => r.json());
        if (!data.success) return;

        const badge = document.getElementById('support-status-badge');
        if (badge) {
            badge.innerHTML = data.enabled
                ? '<span class="badge bg-success">🟢 Bot active</span>'
                : '<span class="badge bg-secondary">⚫ Bot disabled</span>';
        }
        const profileEl = document.getElementById('support-rag-profile-name');
        if (profileEl) profileEl.textContent = data.rag_profile || '—';
    } catch (e) {
        console.error('[support] loadStatus error:', e);
    }
}

// Expose to window for inline onclick handlers
window.supportSelectUser   = supportSelectUser;
window.supportDeleteProfile = supportDeleteProfile;
