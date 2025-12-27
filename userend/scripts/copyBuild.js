const fs = require("fs");
const path = require("path");

const sourceDir = path.resolve(__dirname, "..", "build");
const targetDir = path.resolve(__dirname, "..", "..", "build");

function removeDirectory(dir) {
    if (fs.existsSync(dir)) {
        fs.rmSync(dir, { recursive: true, force: true });
    }
}

function copyDirectory(src, dest) {
    const stats = fs.statSync(src);
    if (!stats.isDirectory()) {
        fs.mkdirSync(path.dirname(dest), { recursive: true });
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
    console.error(`Build directory not found at ${sourceDir}`);
    process.exit(1);
}

removeDirectory(targetDir);
copyDirectory(sourceDir, targetDir);
console.log(`Copied build output from ${sourceDir} to ${targetDir}`);

