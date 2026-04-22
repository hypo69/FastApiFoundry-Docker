/**
 * i18n.js — Minimal i18next wrapper for the installer SPA
 */

const LOCALES_BASE = '/static/locales';

export async function initI18n(lang = 'en') {
    const bundle = await _loadBundle(lang);
    i18next.init({
        lng: lang,
        fallbackLng: 'en',
        resources: { [lang]: { translation: bundle } },
        interpolation: { escapeValue: false },
    });
    applyTranslations();
}

export async function switchLang(lang) {
    localStorage.setItem('installer_lang', lang);
    const bundle = await _loadBundle(lang);
    if (!i18next.hasResourceBundle(lang, 'translation')) {
        i18next.addResourceBundle(lang, 'translation', bundle);
    }
    await i18next.changeLanguage(lang);
    applyTranslations();
}

export function t(key, opts) {
    return i18next.t(key, opts);
}

export function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        const val = i18next.t(key);
        if (val !== key) el.textContent = val;
    });
}

async function _loadBundle(lang) {
    try {
        const r = await fetch(`${LOCALES_BASE}/${lang}.json`);
        return r.ok ? await r.json() : {};
    } catch {
        return {};
    }
}
