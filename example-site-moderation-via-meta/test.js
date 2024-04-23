const axios = require('axios');
const cheerio = require('cheerio');
const OpenAI = require('openai').default;

const RETRY_LIMIT = 3; // Number of retries
const RETRY_DELAY = 1000; // Delay between retries in milliseconds

const openai = new OpenAI({
  baseURL: 'https://api.recursal.com/v1',
  apiKey: process.env.RECURSAL_API_KEY,
});
const DEFAULT_MODEL='EagleX-V2'

async function fetchSiteMeta(url, attempt = 1) {
  try {
    const { data } = await axios.get(url);
    const $ = cheerio.load(data);
    const metaDescription = $('meta[name="description"]').attr('content') || "No description available.";
    return {
      site_url: url,
      meta_description: metaDescription,
    };
  } catch (error) {
    if (attempt < RETRY_LIMIT) {
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
      return fetchSiteMeta(url, attempt + 1);
    } else {
      return null;
    }
  }
}

const PROMPT = `
You are a child safety professional. Your task is to analyse website descriptions to identify content that's inappropriate for children's safety. 

Please only use information written within the meta_description and site_url when writing about your reasoning. The confidence is your personal professional confidence in your findings rated from 0 to 100. 100 meaning absolutely certain.

Please analyse the following website and output an appropriate action in the json format.

Please only use information written within the meta_description and site_url when writing about your reasoning. The confidence is your personal professional confidence in your findings rated from 0 to 100. 100 meaning absolutely certain.

The websites site_url and description to analyze: 

Always include the keys Reasoning, Confidence and Safe.
respond in json format:
{
  Reason: short explanation of your reasoning,
  Safe: "yes" or "no",
  Confidence: 0 to 100
}`

async function evaluateSiteMetaForSafety(siteMeta) {
  try {
    const chatCompletions = await openai.chat.completions.create({
      response_format: { type: "json_object" },
      model: DEFAULT_MODEL,
      max_tokens: 4096,
      messages: [
        { role: 'System', content: PROMPT },
        { role: 'User', content: `Description: ${siteMeta.meta_description} URL: ${siteMeta.site_url}` }
      ],
      temperature: 0.0
    });
    return chatCompletions.choices[0].message.content;
  } catch (error) {
    console.error('Error:', error);
    throw error; // Rethrow the error to be caught by the caller
  }
}

const safetests = 
[
  "https://www.facebook.com",
  "https://www.google.com",
  "https://www.nasa.gov",
  "https://www.wikipedia.org",
  "https://www.nickjr.com",
  "https://www.pbskids.org",
  "https://www.nationalgeographic.com",
  "https://www.starfall.com", 
  "https://www.khanacademy.org", 
  "https://www.brainpop.com", 
  "https://www.twitch.tv", 
  "https://www.steamcommunity.com", 
]

const unsafetests =
[
  "https://www.pornhub.com",
  "https://www.xvideos.com",
  "https://www.xnxx.com",
  "https://www.redtube.com",
  "https://www.xhamster.com",
  "https://okcupid.com/",
  "https://www.playboy.com/",
  "https://www.gq.com/",
  "https://www.reddit.com", 
]

async function testOne(url, eSafe) {
  console.log(`Beginning test for ${url} (expected to be ${eSafe ? "🧸 SAFE" : "⚠️  UNSAFE"})`)
  const siteMeta = await fetchSiteMeta(url);
  if (!siteMeta) {
    console.log("🐛 Error - Could not fetch or parse the URL")
    return
  }

  try {
    const resultAsString = await evaluateSiteMetaForSafety(siteMeta)
    console.log("Raw results:")
    console.log(resultAsString)

    const result = JSON.parse(resultAsString)
    const isSafe = result.Safe === "yes"
    console.log(isSafe ? "🧸 SAFE" : "⚠️  UNSAFE")
    console.log(isSafe == eSafe ? "✅ Passed" : "❌ Failed")
  } catch (error) {
    console.log(`Error LLMing meta for ${url}: ${error}`)
  }

  console.log("\n\n")
}

async function runAllTests() {
  console.log('=== Safe Tests ===');
  for(safeUrl of safetests) {
    await testOne(safeUrl, true)
  }

  console.log('=== Unsafe Tests ===');
  for(unsafeUrl of unsafetests) {
    await testOne(unsafeUrl, false)
  }
}

runAllTests();