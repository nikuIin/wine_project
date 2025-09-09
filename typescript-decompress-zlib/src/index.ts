import { inflateRawSync } from "zlib";
import { marked } from "marked";
import { writeFileSync } from "fs";
import { join } from "path";
import * as cheerio from "cheerio";

/**
 * Decompresses a string that was compressed with Python's zlib (raw) and
 * base64 encoded.
 */
function decompressString(compressedString: string): string {
  const compressedBuffer = Buffer.from(compressedString, "base64");
  const decompressedBuffer = inflateRawSync(compressedBuffer);
  return decompressedBuffer.toString("utf-8");
}

/**
 * Generates a URL-friendly, Latin-based slug from a string.
 */
function slugify(text: string, usedSlugs: Set<string>): string {
  const translitMap: { [key: string]: string } = {
    а: "a",
    б: "b",
    в: "v",
    г: "g",
    д: "d",
    е: "e",
    ё: "yo",
    ж: "zh",
    з: "z",
    и: "i",
    й: "y",
    к: "k",
    л: "l",
    м: "m",
    н: "n",
    о: "o",
    п: "p",
    р: "r",
    с: "s",
    т: "t",
    у: "u",
    ф: "f",
    х: "h",
    ц: "c",
    ч: "ch",
    ш: "sh",
    щ: "shch",
    ъ: "",
    ы: "y",
    ь: "",
    э: "e",
    ю: "yu",
    я: "ya",
  };

  let transliteratedText = "";
  for (let i = 0; i < text.length; i++) {
    const char = text[i].toLowerCase();
    transliteratedText += translitMap[char] || char;
  }

  const baseSlug = transliteratedText
    .toLowerCase()
    .trim()
    .replace(/\s+/g, "-") // Replace spaces with -
    .replace(/[^\w\-]+/g, "") // Remove all non-word chars
    .replace(/\-\-+/g, "-"); // Replace multiple - with single -

  let slug = baseSlug;
  let counter = 1;
  // Ensure the slug is unique
  while (usedSlugs.has(slug)) {
    slug = `${baseSlug}-${counter}`;
    counter++;
  }
  usedSlugs.add(slug);
  return slug;
}

/**
 * Parses HTML content to inject unique IDs into headers and generates a
 * hierarchical Table of Contents.
 */
function generateTocAndInjectIds(htmlContent: string) {
  const $ = cheerio.load(htmlContent);
  const headers: { id: string; text: string; level: number }[] = [];
  const usedSlugs = new Set<string>();

  $("h2, h3, h4, h5, h6").each((_, element) => {
    const header = $(element);
    const text = header.text();
    // Use a type assertion to bypass the strict type check
    const level = parseInt((element as any).tagName.substring(1), 10);
    const id = slugify(text, usedSlugs);

    header.attr("id", id);
    headers.push({ id, text, level });
  });

  let tocHtml = "<ul>";
  for (const header of headers) {
    const indentation = (header.level - 2) * 20; // 20px indent per level
    tocHtml += `
      <li style="margin-left: ${indentation}px;">
        <a href="#${header.id}">${header.text}</a>
      </li>`;
  }
  tocHtml += "</ul>";

  return {
    contentHtml: $.html(),
    tocHtml: tocHtml,
  };
}

/**
 * Creates a full HTML document with a fixed sidebar for the TOC.
 */
function createHtmlDocument(
  title: string,
  tocContent: string,
  bodyContent: string,
): string {
  return `<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
        Helvetica, Arial, sans-serif;
      line-height: 1.6;
      color: #333;
      background-color: #f9f9f9;
      margin: 0;
    }
    .container {
      display: flex;
    }
    .toc {
      position: fixed;
      top: 0;
      left: 0;
      width: 280px;
      height: 100vh;
      padding: 20px;
      background-color: #fff;
      border-right: 1px solid #e0e0e0;
      overflow-y: auto;
      box-sizing: border-box;
    }
    .toc h2 { margin-top: 0; }
    .toc ul { list-style: none; padding-left: 0; }
    .toc a { text-decoration: none; color: #3498db; }
    .toc a:hover { text-decoration: underline; }
    .content {
      margin-left: 320px; /* TOC width + padding */
      padding: 20px 40px;
      max-width: 800px;
    }
    h1, h2, h3, h4, h5, h6 {
      color: #2c3e50;
      scroll-margin-top: 20px; /* Offset for fixed header */
    }
  </style>
</head>
<body>
  <div class="container">
    <nav class="toc">
      <h2>Содержание</h2>
      ${tocContent}
    </nav>
    <main class="content">
      ${bodyContent}
    </main>
  </div>
</body>
</html>`;
}

// --- Main Execution ---
async function main() {
  const pythonCompressed = "U1a4MOtiw8Xmi00XNlzsV7jYCGY0Xey52A8A";
  // Step 1: Decompress the string from Python
  const decompressedMarkdown = decompressString(pythonCompressed);

  // Step 2: Convert the Markdown to HTML asynchronously
  const rawHtml = await marked(decompressedMarkdown);

  // Step 3: Generate TOC and inject IDs into the content
  const { contentHtml, tocHtml } = generateTocAndInjectIds(rawHtml);

  // Step 4: Create a full HTML document
  const finalHtml = createHtmlDocument("Мир Вина", tocHtml, contentHtml);

  // Step 5: Write the HTML to a file
  const outputPath = join(__dirname, "..", "index.html");
  try {
    writeFileSync(outputPath, finalHtml, "utf-8");
    console.log(`✅ Successfully created index.html at: ${outputPath}`);
  } catch (error) {
    console.error("❌ Error writing HTML file:", error);
  }
}

main();
