const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        const el = entry.target;
        if (entry.isIntersecting) {
            el.classList.add('visible');
        } else {
            // Wait 500ms after leaving view, then allow re-trigger
            setTimeout(() => {
                if (!isInViewport(el)) {
                    el.classList.remove('visible');
                    observer.observe(el); // re-observe in case it got unobserved earlier
                }
            }, 500);
        }
    });
}, {
    threshold: 0.1
});

function isInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight)
    );
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('.animate').forEach(el => {
        observer.observe(el);
    });
    const search = document.querySelector('div.search');
    const fakebar = document.querySelector('.search-bar');
    const realbar = document.querySelector('textarea#real-search-bar');
    const realsearch = document.querySelector('div.real-search');
    const logo = document.querySelector('div.logo');
    const hamburger = document.querySelector('div.hamburger-bars');
    const sidemenu = document.querySelector('.burger-menu');
    const sidemenuclose = document.querySelector('.close#burger-close');
    const links = document.querySelector('div.links');
    // let isSyncing = false;

    fakebar.addEventListener('input', () => {realbar.value = fakebar.value});
    realbar.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            console.log('Search triggered');
        }
    });
    fakebar.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            console.log('Search triggered');
        }
    });
    hamburger.onclick = () => {
        console.log("Side menu triggered");
        sidemenu.classList.toggle('visible');
    }
    sidemenuclose.onclick = () => {
        console.log("Side menu triggered");
        sidemenu.classList.toggle('visible');
    }
    search.onclick = () => {
        console.log("Search bar clicked");
        realsearch.style.display = 'flex';
        search.style.display = '';
        logo.style.display = 'none';
        hamburger.style.display = 'none';
        links.style.display = 'none';
    };
    document.addEventListener('click', (event) => {
        const isClickInside = realsearch.contains(event.target) || realbar.contains(event.target) || search.contains(event.target);

        if (!isClickInside && realsearch.style.display === 'flex') {
            // reverse all changes 
            realsearch.style.display = 'none';
            search.style.display = ''
            search.style.alignSelf = 'center';
            logo.style.display = '';
            hamburger.style.display = '';
            links.style.display = '';
        }
    });
});


// Expose for later use
window.observeAnimateElements = function (root = document) {
    root.querySelectorAll('.animate').forEach(el => {
        observer.observe(el);
    });
};

function parseAsterisks(text) {
    // Bold-italic: ***text***
    text = text.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');

    // Bold: **text**
    text = text.replace(/(?<!\*)\*\*(?!\*)(.+?)\*\*(?!\*)/g, '<strong>$1</strong>');

    // Italic: *text*
    text = text.replace(/(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)/g, '<em>$1</em>');

    return text;
}