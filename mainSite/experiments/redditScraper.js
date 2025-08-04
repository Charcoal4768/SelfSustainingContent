import fetch from 'node-fetch';
import cheerio from 'cheerio';
import fs from 'fs';

const userAgents = [
  "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
  "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
];

const headers = {
  'User-Agent': userAgents[Math.floor(Math.random() * userAgents.length)],
  'Accept-Language': 'en-US,en;q=0.9'
};

async function subredditValidator(subreddits) {
  const validSubs = [];

  for (const sub of subreddits) {
    if (!sub || sub.trim() === '') continue;
    const url = `https://www.reddit.com/${sub}/`;

    try {
      const res = await fetch(url, { headers });
      const html = await res.text();
      const $ = cheerio.load(html);

      if (!$('.text-24.s\\:text-20').length) {
        validSubs.push(sub);
      }
    } catch {
      continue;
    }
  }

  return validSubs;
}

function extractCommentsRecursive(comments, depth = 0, maxDepth = 3, limit = 10) {
  const extracted = [];

  for (const comment of comments) {
    if (comment.kind !== 't1') continue;
    const data = comment.data || {};
    const body = data.body?.trim() || "";
    const score = data.score || 0;

    if (score > 1 && body.length > 20) extracted.push(body);
    if (depth < maxDepth && data.replies?.data?.children) {
      extracted.push(...extractCommentsRecursive(data.replies.data.children, depth + 1, maxDepth, limit));
    }
    if (extracted.length >= limit) break;
  }

  return extracted;
}

async function extractFromDiscussion(discussions) {
  for (const discussion of discussions) {
    for (let url of discussion.url) {
      url = url.replace(/\/$/, '') + '.json';

      try {
        const res = await fetch(url, { headers });
        const data = await res.json();

        const postTitle = data[0]?.data?.children?.[0]?.data?.title || 'unknown';
        const comments = data[1]?.data?.children || [];

        discussion.title = postTitle;
        discussion.comments = extractCommentsRecursive(comments);
      } catch {
        console.log(`Failed to fetch ${url}`);
      }
    }
    delete discussion.url;
  }

  return discussions;
}

async function findDiscussions(url, amount) {
  const discussions = [];

  try {
    const res = await fetch(url, { headers });
    const html = await res.text();
    const $ = cheerio.load(html);

    $('a[data-testid="post-title-text"]').each((_, el) => {
      if (amount <= 0) return;
      discussions.push("https://www.reddit.com" + $(el).attr('href'));
      amount--;
    });
  } catch {
    return discussions;
  }

  console.log(`Found ${discussions.length} discussions on ${url}`);
  return discussions;
}

async function search(amount = 2, terms = [[null, null], [null, null]], subs = [[null, null], [null, null]]) {
  const linksFound = [];

  if (!terms || amount <= 0) return linksFound;

  const baseURL = subs?.flat().filter(Boolean).length
    ? "https://www.reddit.com/{}/search/?q={}"
    : "https://www.reddit.com/search/?q={}";

  for (let i = 0; i < 2; i++) {
    const termGroup = terms[i];
    const subGroup = subs[i];

    for (const term of termGroup) {
      if (subs?.[0]?.[0] == null) {
        const url = baseURL.replace("{}", term);
        await new Promise(r => setTimeout(r, 500));
        linksFound.push({ url: await findDiscussions(url, amount) });
      } else {
        for (const sub of subGroup) {
          const url = baseURL.replace("{}", sub).replace("{}", term);
          await new Promise(r => setTimeout(r, 500));
          linksFound.push({ url: await findDiscussions(url, amount) });
        }
      }
    }
  }

  return linksFound;
}

// Run once
(async () => {
  const links = await search(
    2,
    [["Digital Ocean", "DO", "cloud hosting", "VPS"], ["Hostinger", "web hosting", "shared hosting", "cheap hosting"]],
    [["r/digitalocean", "r/cloudcomputing", "r/selfhosted"], ["r/webhosting", "r/hosting", "r/hostinger"]]
  );

  for (const post of links) {
    const data = await extractFromDiscussion([post]);
    if (!data || !data[0]?.title) continue;

    const title = data[0].title.replace(/\//g, '-');
    const filename = title.split(' ')[0] || 'output';
    fs.writeFileSync(`${filename}.json`, JSON.stringify(data, null, 2));
  }
})();
