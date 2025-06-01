// docscraper.js
// Usage: node docscraper.js https://nextjs.org/docs
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const OUTPUT_FILE = path.join(__dirname, 'scraped-output.txt');
const VISITED_FILE = path.join(__dirname, 'visited.json');

// Load previously visited URLs (if any)
let visited = new Set();
if (fs.existsSync(VISITED_FILE)) {
  try {
    const data = fs.readFileSync(VISITED_FILE, 'utf8');
    const arr = JSON.parse(data);
    arr.forEach(url => visited.add(url));
  } catch (e) {
    console.error("Error loading visited set:", e);
  }
}

// Normalize a link by removing hash and query string
function normalizeLink(link) {
  try {
    const u = new URL(link);
    u.hash = '';
    u.search = '';
    return u.toString();
  } catch {
    return '';
  }
}

// Asynchronously append data to the output file
function appendToFile(data) {
  fs.appendFile(OUTPUT_FILE, data + '\n', 'utf8', (err) => { 
    if (err) console.error(err); 
  });
}

// Save the visited set to disk
function saveVisited() {
  const arr = Array.from(visited);
  fs.writeFile(VISITED_FILE, JSON.stringify(arr, null, 2), 'utf8', (err) => { 
    if (err) console.error("Error saving visited set:", err); 
  });
}

// Helper that retries navigation
async function safeGoto(page, url, retries = 3, delay = 3000) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded' });
      return; // Success
    } catch (err) {
      console.error(`Attempt ${attempt} failed for ${url}:`, err);
      if (attempt < retries) {
        await new Promise(r => setTimeout(r, delay));
      } else {
        throw err;
      }
    }
  }
}

// Process one URL: open a new page, scrape its text, write to file, and collect new links.
async function processUrl(browser, url) {
  let page;
  let discovered = [];
  try {
    page = await browser.newPage();
    await page.setDefaultNavigationTimeout(60000);
    await safeGoto(page, url);

    // Extract the page title and readable content from <main> or <article> if available.
    const pageData = await page.evaluate(() => {
      const title = document.title || '';
      let content = '';
      const mainElem = document.querySelector('main');
      const articleElem = document.querySelector('article');
      if (mainElem && mainElem.innerText.trim().length > 0) {
        content = mainElem.innerText;
      } else if (articleElem && articleElem.innerText.trim().length > 0) {
        content = articleElem.innerText;
      } else {
        content = document.body.innerText;
      }
      return { title: title.trim(), content: content.trim() };
    });

    // Write organized output with title.
    appendToFile(`=== PAGE: ${url} ===\nTitle: ${pageData.title}\n\n${pageData.content}\n\n`);

    // Extract all links on the page.
    let links = await page.$$eval('a', as => as.map(a => a.href));
    const origin = new URL(url).origin;
    for (let link of links) {
      if (!link.startsWith(origin)) continue; // Skip external links
      let normalized = normalizeLink(link);
      // Filter: only follow links that include "/docs" (adjust as needed)
      if (!normalized.includes("/docs")) continue;
      if (normalized && !visited.has(normalized)) {
        visited.add(normalized);
        discovered.push(normalized);
      }
    }
    // Deduplicate discovered links.
    discovered = [...new Set(discovered)];
  } catch (err) {
    console.error(`Error processing ${url}:`, err);
  } finally {
    if (page) await page.close();
  }
  return discovered;
}

(async () => {
  // Dynamically import p-limit (ES module)
  const { default: pLimit } = await import('p-limit');

  const startUrl = process.argv[2];
  if (!startUrl) {
    console.error('Provide a URL, e.g. node docscraper.js https://nextjs.org/docs');
    process.exit(1);
  }
  
  // Normalize start URL and add it to visited if not present.
  const startNormalized = normalizeLink(startUrl);
  if (!visited.has(startNormalized)) {
    visited.add(startNormalized);
  }
  
  // Clear previous output
  fs.writeFileSync(OUTPUT_FILE, '', 'utf8');
  
  const browser = await puppeteer.launch({ headless: 'new' });
  
  // Set a concurrency limit (e.g., 8 pages concurrently)
  const limit = pLimit(8);
  
  // BFS queue of URLs to process
  let queue = [startNormalized];
  
  while (queue.length > 0) {
    console.log(`Processing batch. Queue length: ${queue.length}`);
    // Grab the current batch and clear the queue.
    const currentBatch = queue;
    queue = [];
    
    // Process all URLs in the current batch concurrently.
    const results = await Promise.all(
      currentBatch.map(url => limit(() => processUrl(browser, url)))
    );
    
    // Flatten discovered links into the next queue.
    for (const discovered of results) {
      queue.push(...discovered);
    }
    
    // Persist visited set after each batch.
    saveVisited();
  }
  
  await browser.close();
  console.log('Scraping finished! Check scraped-output.txt');
})();
