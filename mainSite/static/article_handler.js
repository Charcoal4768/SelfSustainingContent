import { getRandomPath, morphToNewPath } from "./svg_animator.js";
document.addEventListener("DOMContentLoaded", function () {
    // Explicitly specify namespace and log connection
    const socket = io("/", { transports: ["websocket"] });
    const PUBLISH_TOKEN = document.querySelector('meta[name="publish_token"]').getAttribute('content');
    const ROOM_ID = document.querySelector('meta[name="room_id"]').getAttribute('content');
    const backgroundPath = document.getElementById("status-background");
    const secondaryPath = document.getElementById("status-secondary");

    let updatesComing = false;
    let whileIdleDoThis;
    function startIdleLoop() {
        whileIdleDoThis = setInterval(() => {
            if (!updatesComing) {
                morphToNewPath(backgroundPath, secondaryPath, getRandomPath());
            }
        }, 3000 + Math.random() * 3000);
    }

    function stopIdleLoop() {
        clearInterval(whileIdleDoThis);
    }

    startIdleLoop();

    socket.on("connect", () => {
        socket.emit("join_room", { room: ROOM_ID });
    });

    socket.on("status_update", (data) => {
        updatesComing = true;
        stopIdleLoop();
        document.getElementById("status-box").textContent = "Status: " + data.status;
        const statusWord = data.status.split(" ")[0].toLowerCase();
        document.getElementById("st-ico").src = "/static/images/" + statusWord + ".png";

        if (data.status === "Generating") {
            document.getElementById("generate-button").disabled = true;
            document.getElementById("publish-article").disabled = true;
        } else if (data.status == "Done") {
            document.getElementById("generate-button").disabled = false;
            document.getElementById("publish-article").disabled = false;
        }

        setTimeout(() => {
            updatesComing = false;
            startIdleLoop();
        }, 10000);
    });

    socket.on("article_ready", (data) => {
        let desc_hidden = document.createElement('input');
        desc_hidden.type = "hidden";
        desc_hidden.name = "description";
        desc_hidden.value = data.description;
        desc_hidden.id = "hidden-description";
        let layerC = document.createElement('div');
        layerC.classList.add('layer', 'c');
        let layerV = document.createElement('div');
        layerV.classList.add('vertical-layer');
        let publishButton = document.createElement('button');
        publishButton.innerText = "Publish";
        publishButton.classList.add('animate', 'up', 'primary-action');
        publishButton.id = "article-publish";
        publishButton.addEventListener("click", () => sendArticleRequest(PUBLISH_TOKEN)); //Wrapped in a lambda, () => so that it dosent just run send request on initialization but on click instead
        let articleContainer = document.createElement('div');
        articleContainer.classList.add('article-container');
        let articleBodyContainer = document.createElement('div');
        articleBodyContainer.classList.add('article-body');
        let titleContainer = document.createElement('h1');
        titleContainer.contentEditable = 'true';
        titleContainer.classList.add('editable', 'article-heading', 'animate', 'right');
        titleContainer.textContent = data.title;
        let tagsContainer = document.createElement('div');
        tagsContainer.classList.add('editable', 'tags-container');
        let article = data.content;
        let tags = article.Tags || [];
        for (let i = 0; i < tags.length; i++) {
            const tagData = (tags[i] || "").trim();
            let tag = document.createElement('p');
            tag.contentEditable = 'true';
            tag.classList.add('editable', 'tag', 'animate', 'right')
            tag.textContent = tagData;
            tagsContainer.appendChild(tag);
        }
        const sections = article.Sections || [];
        for (let i = 0; i < sections.length; i++) {
            const section = sections[i];
            const heading = (section.heading || "").trim();
            const content = (section.content || "").trim();

            let sectionDiv = document.createElement('div');
            sectionDiv.classList.add('section');

            let headingTextarea = document.createElement('h2');
            headingTextarea.classList.add('editable', 'article-subheading');
            headingTextarea.textContent = heading;
            headingTextarea.contentEditable = 'true';
            sectionDiv.appendChild(headingTextarea);

            let contentArea = document.createElement('div');
            contentArea.classList.add('content');

            const paragraphs = content.split('\n').map(p => p.trim()).filter(p => p.length > 0);
            for (let j = 0; j < paragraphs.length; j++) {
                const line = paragraphs[j];
                let paraText = document.createElement('p');
                paraText.classList.add('editable', 'article-bodytext', 'animate', 'right');
                paraText.innerHTML = parseAsterisks(line);
                paraText.contentEditable = 'true';
                contentArea.appendChild(paraText);
            }
            sectionDiv.appendChild(contentArea);
            articleBodyContainer.appendChild(sectionDiv);
        }
        layerV.appendChild(titleContainer);
        layerV.appendChild(tagsContainer);
        articleContainer.appendChild(layerV);
        articleContainer.appendChild(articleBodyContainer);
        articleContainer.appendChild(layerC);
        layerC.appendChild(publishButton);
        let gen = document.getElementById("generated-content")
        gen.appendChild(articleContainer);
        gen.appendChild(desc_hidden);
        window.observeAnimateElements(articleContainer);
        articleContainer.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
            inline: 'nearest'
        });
    });
});

function repackArticle() {
    const articleContainer = document.querySelector(".article-container");
    if (!articleContainer) return null;

    const desc = document.querySelector("#hidden-description");
    const title = (
        articleContainer.querySelector("h1.article-heading")?.textContent || ""
    ).trim();
    const tags = Array.from(
        articleContainer.querySelectorAll(".tags-container > p.tag")
    )
        .map(t => (t.textContent || "").trim())
        .filter(Boolean);

    const sections = Array.from(
        articleContainer.querySelectorAll(".article-body .section")
    ).map(section => {
        const heading = (
            section.querySelector("h2.article-subheading")?.textContent || ""
        ).trim();

        const paragraphs = Array.from(section.querySelectorAll(".content p"))
            .map(p => (p.innerText || "").trim())
            .filter(Boolean);

        return {
            heading,
            content: paragraphs.join("\n")
        };
    });

    return {
        title,
        Tags: tags,
        article_body: {
            Sections: sections
        },
        description: desc?.value || ""
    };
}

function sendArticleRequest(token) {
    const repackedData = repackArticle();
    fetch("/api/publish", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRF-Token": token
        },
        credentials: "include",
        body: JSON.stringify(repackedData)
    });
}