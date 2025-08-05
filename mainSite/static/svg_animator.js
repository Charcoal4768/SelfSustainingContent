import svg_paths from "./svg_paths.js";

export function getRandomPath() {
    return svg_paths[Math.floor(Math.random() * svg_paths.length)];
}

export function morphToNewPath(backgroundPath, secondaryPath, newPath, duration = 2000) {
    const from = backgroundPath.getAttribute("d");
    const to = newPath;
    const interp = flubber.interpolate(from, to);
    let start = null;

    function animate(ts) {
        if (!start) start = ts;
        const t = Math.min((ts - start) / duration, 1);
        const d = interp(t);
        backgroundPath.setAttribute("d", d);
        if (secondaryPath) secondaryPath.setAttribute("d", d);
        if (t < 1) requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
}