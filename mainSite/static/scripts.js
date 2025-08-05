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

function repackArticle() {
    const articleContainer = document.querySelector(".article-container");
    if (!articleContainer) return null;

    // Get title
    const title = (
        articleContainer.querySelector("h1.article-heading")?.textContent || ""
    ).trim();

    // Get tags
    const tags = Array.from(
        articleContainer.querySelectorAll(".tags-container > p.tag")
    )
        .map(t => (t.textContent || "").trim())
        .filter(Boolean);

    // Get sections
    const sections = Array.from(
        articleContainer.querySelectorAll(".article-body .section")
    ).map(section => {
        const heading = (
            section.querySelector("h2.article-subheading")?.textContent || ""
        ).trim();

        const paragraphs = Array.from(section.querySelectorAll(".content p"))
            .map(p => (p.innerText || "").trim())  // Using innerText for visible-only text
            .filter(Boolean);

        return {
            heading,
            content: paragraphs.join("\n")
        };
    });

    return {
        title,
        article_body: {
            Tags: tags,
            Sections: sections
        }
    };
}
