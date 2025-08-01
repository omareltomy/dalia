import puppeteer from "puppeteer";
import fs from "fs";
import csv from "csv-parser";
import { parse } from "json2csv";

const INPUT_CSV = "data.csv";
const OUTPUT_CSV = "data_with_desc.csv";
const OUTPUT_JSON = "data_with_desc.json";
const COOKIES_PATH = process.argv[2] || "cookies.json";

if (!fs.existsSync(COOKIES_PATH)) {
  console.error("Missing cookies.json file. Usage: node new_batch.js <cookies.json>");
  process.exit(1);
}

const cookiesRaw = JSON.parse(fs.readFileSync(COOKIES_PATH, "utf-8"));
const validSameSite = ["Strict", "Lax", "None"];
const cookies = cookiesRaw.map(c => {
  if (c.sameSite && !validSameSite.includes(c.sameSite)) c.sameSite = "Lax";
  if (!c.sameSite) c.sameSite = "Lax";
  return c;
});

function readCSV(file) {
  return new Promise((resolve, reject) => {
    const results = [];
    fs.createReadStream(file)
      .pipe(csv())
      .on("data", (data) => results.push(data))
      .on("end", () => resolve(results))
      .on("error", reject);
  });
}

async function fetchDescription(page, url) {
  try {
    await page.goto(url, { waitUntil: "networkidle2", timeout: 60000 });
    try {
      await page.waitForSelector('button.show-more-less-html__button, button[aria-label="Show more"]', { timeout: 5000 });
      await page.click('button.show-more-less-html__button, button[aria-label="Show more"]');
    } catch (e) {}
    await page.waitForSelector("#job-details.jobs-box__html-content", { timeout: 20000 });
    return await page.$eval("#job-details.jobs-box__html-content", el => el.innerText.trim());
  } catch (e) {
    return "";
  }
}

(async () => {
  const jobs = await readCSV(INPUT_CSV);
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setCookie(...cookies);


  for (let i = 0; i < jobs.length; i++) {
    const job = jobs[i];
    const url = job["Job LinkedIn URL"] || job["URL"] || Object.values(job).find(v => typeof v === "string" && v.includes("linkedin.com/jobs/view/"));
    if (!url) {
      job["Job Description"] = "";
    } else {
      job["Job Description"] = await fetchDescription(page, url);
      console.log(`Fetched: ${url}`);
    }

    // Save progress after each job
    try {
      const csvData = parse(jobs);
      fs.writeFileSync(OUTPUT_CSV, csvData, "utf-8");
      fs.writeFileSync(OUTPUT_JSON, JSON.stringify(jobs, null, 2), "utf-8");
    } catch (err) {
      console.error("Error writing output files:", err);
    }
  }

  await browser.close();
  console.log("Done! Output written to", OUTPUT_CSV, "and", OUTPUT_JSON);
})();