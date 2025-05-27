document.addEventListener('DOMContentLoaded', function() {
    const navElement = document.getElementById('changelist-filter');
    const detailsElements = navElement.querySelectorAll('details');
    detailsElements.forEach((detailsElement) => {
        detailsElement.removeAttribute('open');
    });
});