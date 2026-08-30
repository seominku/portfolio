'use client';

import documentHtml from '../index.html?raw';
import scriptSource from '../script.js?raw';
import styleSource from '../styles.css?raw';

const imageModules = import.meta.glob<string>(
  '../assets/**/*.{png,jpg,jpeg,webp,gif,svg}',
  { eager: true, query: '?url', import: 'default' },
);

function composePortfolioDocument() {
  let html = documentHtml
    .replace(
      '<link rel="stylesheet" href="styles.css" />',
      `<style>${styleSource}</style>`,
    )
    .replace(
      '<script src="script.js"></script>',
      `<script>${scriptSource.replaceAll('</script>', '<\\/script>')}</script>`,
    );

  for (const [modulePath, publicUrl] of Object.entries(imageModules)) {
    const sourcePath = modulePath.replace(/^\.\.\//, '');
    html = html.replaceAll(sourcePath, publicUrl);
  }

  return html;
}

const portfolioDocument = composePortfolioDocument();

export default function PortfolioFrame() {
  return (
    <iframe
      className="portfolio-frame"
      srcDoc={portfolioDocument}
      title={'\uad6c\ubbfc\uc11c \ud3ec\ud2b8\ud3f4\ub9ac\uc624'}
    />
  );
}