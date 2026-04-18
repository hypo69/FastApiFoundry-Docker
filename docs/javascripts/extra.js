// Open all <details> blocks on page load
function openAllDetails() {
    document.querySelectorAll('details').forEach(el => el.setAttribute('open', ''));
}

document.addEventListener('DOMContentLoaded', openAllDetails);
