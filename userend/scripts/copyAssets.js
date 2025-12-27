const fs = require("fs");
const path = require("path");

const sourceDir = path.resolve(__dirname, "..", "public", "assets");
const targetDir = path.resolve(__dirname, "..", "build", "assets");

function copyDirectory(src, dest) {
    if (!fs.existsSync(src)) {
        return;
    }

    const stats = fs.statSync(src);
    if (!stats.isDirectory()) {
        fs.copyFileSync(src, dest);
        return;
    }

    if (!fs.existsSync(dest)) {
        fs.mkdirSync(dest, { recursive: true });
    }

    for (const entry of fs.readdirSync(src)) {
        const srcPath = path.join(src, entry);
        const destPath = path.join(dest, entry);
        copyDirectory(srcPath, destPath);
    }
}

if (!fs.existsSync(sourceDir)) {
    console.log("No public/assets directory found. Skipping asset copy.");
    process.exit(0);
}

copyDirectory(sourceDir, targetDir);
console.log(`Copied assets from ${sourceDir} to ${targetDir}`);

