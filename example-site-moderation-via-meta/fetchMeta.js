const axios = require('axios');
const cheerio = require('cheerio');
const OpenAI = require('openai').default;

const PROMPT = `
System: You are an AI content moderation system designed to analyze the meta tag descriptions of websites and determine if the content is potentially inappropriate or harmful for children. Your goal is to identify any sites that need to be immediately blocked or flagged for more detailed review based on the meta description alone.
You will only respond with a JSON object that includes the site_url, action, and reason. Look at the examples below. Make sure to remember the reason.
For each website, you will receive a JSON object containing the site's URL and meta description, like this:

\`\`\`json
{
  "site_url": "https://www.example.com",
  "meta_description": "Example website meta description goes here."
}
\`\`\`


Follow these steps to analyze the meta description:

1. Extract the "site_url" and "meta_description" fields from the JSON input.

2. Scan the "meta_description" for any keywords or phrases that clearly indicate the site contains content inappropriate for children, such as:

- Words related to adult content, pornography, or explicit material: {porn}, {adult}, {mature}, {explicit}, {sex}
- Mentions of extreme violence, gore, or brutality: {violence}, {gore}, {brutal}, {graphic}
- Hate speech, discrimination, or intolerance targeting protected groups: {hate}, {racist}, {homophobic}, {sexist} 
- References to illegal drugs, alcohol abuse, or promoting substance use: {drugs}, {alcohol}, {weed}, {cocaine}, {heroin}, {meth}
- Suggestions of dangerous, illegal or harmful activities: {crime}, {weapons}, {hacking}, {cheating}

3. Based on your analysis of the meta description, generate a JSON response indicating the appropriate action to take:

If you find clear indicators that the site is not suitable for children, respond with:

\`\`\`json
{
  "site_url": "[The URL of the blocked site]",
  "action": "Blocked",
  "reason": "[A brief explanation of why the site was blocked based on the meta description]"
}
\`\`\`

Example:

\`\`\`json
{
  "site_url": "https://www.{adult_site}.com",
  "action": "Blocked",
  "reason": "Meta description explicitly mentions {pornographic} content inappropriate for children: '{sex}, {porn}, {adult}.'"
}
\`\`\`

If the meta description does not contain obvious red flags, but you are unsure about the content's child-appropriateness, respond with:

\`\`\`json
{
  "site_url": "[The URL of the flagged site]", 
  "action": "Flagged for Detailed Review",
  "reason": "[A brief explanation of why the site needs further analysis]"
}
\`\`\`

Example:

\`\`\`json
{
  "site_url": "https://www.kidsscienceexperiments.com",
  "action": "Flagged for Detailed Review", 
  "reason": "Meta description mentions science content for children, but full HTML review needed to confirm safety and appropriateness: 'Fun learning science experiments for kids.'"
}
\`\`\`

If the meta description clearly indicates safe, kid-friendly content, respond with:

\`\`\`json
{
  "site_url": "[The URL of the kid-friendly site]",
  "action": "Allowed",
  "reason": "[A brief explanation of why the site is deemed appropriate for children]" 
}
\`\`\`

Example:

\`\`\`json
{
  "site_url": "https://www.example-educational-games.com",
  "action": "Allowed",
  "reason": "Meta description indicates educational content specifically designed for children: 'Free math and reading games for kids ages 5-12.'"
}
\`\`\`

Remember, your top priority is protecting children from harmful content. If you have any uncertainty about a site's appropriateness based solely on the meta description, always flag it for further review.

I will send you a series of JSON inputs containing site URLs and meta descriptions. For each one, respond with a JSON object indicating the action taken (Blocked, Flagged for Detailed Review, or Allowed) and the reason for your decision. 
`

const openai = new OpenAI({
  baseURL: 'https://api.recursal-beta.com/v1',
  apiKey: process.env.RECURSAL_API_KEY
});

async function fetchSiteMeta(url) {
  try {
    const { data } = await axios.get(url);
    const $ = cheerio.load(data);
    const metaDescription = $('meta[name="description"]').attr('content') || "No description available.";
    const siteMeta = {
      site_url: url,
      meta_description: metaDescription,
    };

    // Log the site metadata
    console.log(JSON.stringify(siteMeta, null, 2));
    
    return siteMeta;
  } catch (error) {
    console.error(`Could not fetch or parse the URL: ${error}`);
    return null;
  }
}

async function runChatCompletions(siteMeta) {
  try {
    const chatCompletions = await openai.chat.completions.create({
      type: "json_object",
      model: 'EagleX-1.7T-Chat',
      max_tokens: 4096,
      messages: [
        { role: 'system', content: PROMPT },
        { role: 'user', content: JSON.stringify(siteMeta) }
      ],
    });

    chatCompletions.choices.forEach(choice => {
      console.log(choice.message.content);
    });
  } catch (error) {
    console.error('Error:', error);
  }
}

// Check for URL argument
if (process.argv.length < 3) {
  console.log("Usage: node script.js <URL>");
  process.exit(1);
}

const url = process.argv[2]; // Get URL from command line

// Fetch site meta and then run chat completions
fetchSiteMeta(url).then(siteMeta => {
  if (siteMeta) {
    runChatCompletions(siteMeta);
  }
});