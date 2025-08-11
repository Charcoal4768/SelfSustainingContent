//socket.io client script is loaded on the page
document.addEventListener("DOMContentLoaded", function () {
    const socket = io("/", { transports: ["websocket"] });
    const sendButton = document.getElementById("send-comment-button");
    const commentTextarea = document.getElementById("comment-textarea");
    const post_id = document.querySelector('meta[name="post_id"]').getAttribute("content");
    const commentList = document.querySelector(".comment-list") || createCommentList();
    const room_id = document.querySelector('meta[name="room_id"]').getAttribute("content");

    let publishToken = null;

    function createCommentList() {
        const list = document.createElement("div");
        list.classList.add("comment-list");
        document.querySelector(".comment-section").appendChild(list);
        return list;
    }

    // join the room on connect (so server can emit to it)
    socket.on("connect", () => {
        socket.emit("join_room", { room: room_id });
    });

    // request token and return a Promise that resolves when token arrives
    function requestToken() {
        return new Promise((resolve, reject) => {
            if (publishToken) return resolve(publishToken);

            // one-time listener
            socket.once("comment_token", (data) => {
                publishToken = data.token;
                resolve(publishToken);
            });

            // ask server for a token
            socket.emit("request_comment_token", { article_id: post_id, room_id: room_id });

            // fallback timeout
            setTimeout(() => {
                if (!publishToken) reject(new Error("Timed out waiting for token"));
            }, 5000);
        });
    }

    commentTextarea.addEventListener("focus", () => {
        if (!publishToken) requestToken().catch(() => {});
    });

    commentTextarea.addEventListener("input", () => {
        commentTextarea.style.height = "auto";
        commentTextarea.style.height = `${Math.min(commentTextarea.scrollHeight, 200)}px`;
    });

    async function sendAddComment(commentText) {
        try {
            const token = await requestToken();
            const res = await fetch("/api/comment", {
                method: "POST",
                credentials: "include",            // crucial: send session cookie
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRF-Token": token
                },
                body: JSON.stringify({ comment: commentText, article_id: post_id, action: "add" })
            });
            const data = await res.json();
            if (data.status === "success") {
                // append instantly
                const commentDiv = document.createElement("div");
                commentDiv.classList.add("comment", "animate", "up", "visible");
                commentDiv.innerHTML = `
                    <div class="comment-header">
                        <h4>${data.username || "You"}</h4>
                        <span class="comment-date">${new Date().toLocaleString()}</span>
                    </div>
                    <p>${parseAsterisks(commentText)}</p>
                `;
                commentList.appendChild(commentDiv);

                commentTextarea.value = "";
                commentTextarea.style.height = "auto";
                publishToken = null; // force refresh next time
                if (window.observer) window.observer.observe(commentDiv);
            } else {
                console.error("Failed to add:", data);
            }
        } catch (err) {
            console.error("Error adding comment:", err);
        }
    }

    sendButton.addEventListener("click", function () {
        const commentText = commentTextarea.value.trim();
        if (!commentText) return;
        sendAddComment(commentText);
    });

    commentTextarea.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendButton.click();
        }
    });

    // event delegation for edit/delete
    document.addEventListener("click", async function (e) {
        const editBtn = e.target.closest(".edit-comment");
        const deleteBtn = e.target.closest(".delete-comment");

        if (editBtn) {
            const commentId = editBtn.getAttribute("data-comment-id");
            const commentDiv = editBtn.closest(".comment");
            const commentBody = commentDiv.querySelector("p").textContent;
            const newComment = prompt("Edit your comment:", commentBody);
            if (!newComment) return;

            try {
                const token = await requestToken();
                const res = await fetch("/api/comment", {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRF-Token": token
                    },
                    body: JSON.stringify({ comment: newComment, comment_id: commentId, action: "edit" })
                });
                const data = await res.json();
                if (data.status === "success") {
                    commentDiv.querySelector("p").textContent = newComment;
                    publishToken = null;
                } else {
                    console.error("Edit failed:", data);
                }
            } catch (err) {
                console.error("Edit error:", err);
            }
        }

        if (deleteBtn) {
            const commentId = deleteBtn.getAttribute("data-comment-id");
            const commentDiv = deleteBtn.closest(".comment");
            if (!confirm("Are you sure you want to delete this comment?")) return;

            try {
                const token = await requestToken();
                const res = await fetch("/api/comment", {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRF-Token": token
                    },
                    body: JSON.stringify({ comment_id: commentId, action: "delete" })
                });
                const data = await res.json();
                if (data.status === "success") {
                    commentDiv.remove();
                    publishToken = null;
                } else {
                    console.error("Delete failed:", data);
                }
            } catch (err) {
                console.error("Delete error:", err);
            }
        }
    });
});
