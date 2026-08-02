const fs = require('fs');
const path = require('path');

const iconsDir = path.join(__dirname, 'icons');
if (!fs.existsSync(iconsDir)) {
  fs.mkdirSync(iconsDir, { recursive: true });
}

// Minimal 1x1 solid dark PNG base64 fallback
const solidDarkPng = Buffer.from(
  'iVBORw0KGgoAAAANSU5EUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
  'base64'
);

fs.writeFileSync(path.join(iconsDir, 'icon-192.png'), solidDarkPng);
fs.writeFileSync(path.join(iconsDir, 'icon-512.png'), solidDarkPng);

console.log('Successfully generated default icon PNGs in icons/');
