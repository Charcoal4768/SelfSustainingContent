import { getRandomPath, morphToNewPath } from "./svg_animator.js";
document.addEventListener("DOMContentLoaded", function () {
    const bgPath = document.getElementById("fancy-svg-bg");
    const fgPath = document.getElementById("faqncy-svg-fg");
    let intervalForAnim;
    function animationLoop() {
        intervalForAnim = setInterval(() => {
            morphToNewPath(bgPath, fgPath, getRandomPath());
        }, 2800 + Math.random() * 2000);
    }
    animationLoop()
});