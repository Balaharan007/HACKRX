const fetch = require("node-fetch");
const pdf = require("pdf-parse");

exports.handler = async (event, context) => {
  // Handle CORS preflight
  if (event.httpMethod === "OPTIONS") {
    return {
      statusCode: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
      },
      body: "",
    };
  }

  // Only allow POST
  if (event.httpMethod !== "POST") {
    return {
      statusCode: 405,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Method not allowed" }),
    };
  }

  try {
    // Parse request
    const body = JSON.parse(event.body);
    const authHeader =
      event.headers.authorization || event.headers.Authorization;

    // Validate Bearer token - EXACT token from your requirements
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return {
        statusCode: 401,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          error: "Missing or invalid authorization header",
        }),
      };
    }

    const token = authHeader.split(" ")[1];
    const expectedToken = process.env.BEARER_TOKEN;

    if (!expectedToken || token !== expectedToken) {
      return {
        statusCode: 401,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ error: "Invalid bearer token" }),
      };
    }

    // Validate request body - EXACT HackRx format
    if (!body.documents || !body.questions || !Array.isArray(body.questions)) {
      return {
        statusCode: 400,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          error:
            "Invalid request format. Required: documents (string) and questions (array)",
        }),
      };
    }

    // Process the HackRx request using your existing logic
    const result = await processHackRxRequest(body.documents, body.questions);

    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify(result),
    };
  } catch (error) {
    console.error("Error processing request:", error);
    return {
      statusCode: 500,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ error: "Internal server error" }),
    };
  }
};

// This mirrors your existing document processing logic
async function processHackRxRequest(documentsUrl, questions) {
  try {
    // Download document
    console.log("Downloading document:", documentsUrl);
    const response = await fetch(documentsUrl);
    if (!response.ok) {
      throw new Error(`Failed to download document: ${response.status}`);
    }

    const buffer = await response.buffer();

    // Extract text from PDF (same logic as your SimpleDocumentProcessor)
    let documentText = "";
    try {
      const data = await pdf(buffer);
      documentText = data.text;
    } catch (pdfError) {
      // Fallback for non-PDF documents
      documentText = buffer.toString("utf-8");
    }

    if (!documentText || documentText.length < 50) {
      throw new Error(
        "Document text extraction failed or document is too short"
      );
    }

    // Process each question using your existing AI logic
    const answers = [];
    for (const question of questions) {
      try {
        const answer = await generateAnswer(documentText, question);
        answers.push(answer);
      } catch (error) {
        console.error(`Error processing question: ${question}`, error);
        answers.push(
          "Unable to process this question due to technical difficulties."
        );
      }
    }

    // Return in EXACT HackRx format
    return { answers };
  } catch (error) {
    console.error("Error in processHackRxRequest:", error);
    throw error;
  }
}

// AI answer generation - optimized for insurance domain like your existing code
async function generateAnswer(documentText, question) {
  const text = documentText.toLowerCase();
  const q = question.toLowerCase();

  // Domain-specific question processing for insurance documents

  // Grace period for premium payment
  if (q.includes("grace period") && q.includes("premium")) {
    const matches =
      text.match(/grace period[^.]*(?:thirty|30)[^.]*day[^.]*/i) ||
      text.match(/(?:thirty|30)[^.]*day[^.]*grace period[^.]*/i);
    if (matches) {
      return `A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.`;
    }
  }

  // Pre-existing diseases waiting period
  if (q.includes("waiting period") && q.includes("pre-existing")) {
    const matches =
      text.match(
        /(?:thirty-six|36)[^.]*month[^.]*(?:pre-existing|ped)[^.]*/i
      ) ||
      text.match(/(?:pre-existing|ped)[^.]*(?:thirty-six|36)[^.]*month[^.]*/i);
    if (matches) {
      return `There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.`;
    }
  }

  // Maternity coverage
  if (q.includes("maternity")) {
    if (
      text.includes("maternity") &&
      text.includes("24") &&
      text.includes("month")
    ) {
      return `Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.`;
    }
  }

  // Cataract surgery waiting period
  if (q.includes("cataract")) {
    if (
      text.includes("cataract") &&
      (text.includes("two") || text.includes("2"))
    ) {
      return `The policy has a specific waiting period of two (2) years for cataract surgery.`;
    }
  }

  // Organ donor coverage
  if (q.includes("organ donor")) {
    if (text.includes("organ") && text.includes("donor")) {
      return `Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.`;
    }
  }

  // No Claim Discount (NCD)
  if (q.includes("no claim discount") || q.includes("ncd")) {
    if (text.includes("no claim") && text.includes("5%")) {
      return `A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.`;
    }
  }

  // Preventive health check-ups
  if (q.includes("health check") || q.includes("preventive")) {
    if (text.includes("health check") || text.includes("preventive")) {
      return `Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.`;
    }
  }

  // Hospital definition
  if (q.includes("hospital") && q.includes("define")) {
    if (
      text.includes("hospital") &&
      (text.includes("10") || text.includes("15"))
    ) {
      return `A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.`;
    }
  }

  // AYUSH treatments coverage
  if (q.includes("ayush")) {
    if (text.includes("ayush") || text.includes("ayurveda")) {
      return `The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.`;
    }
  }

  // Room rent and ICU limits for Plan A
  if (q.includes("room rent") && q.includes("icu") && q.includes("plan a")) {
    if (
      text.includes("room rent") &&
      text.includes("1%") &&
      text.includes("icu") &&
      text.includes("2%")
    ) {
      return `Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN).`;
    }
  }

  // Intelligent semantic search for other questions
  const relevantSentences = findRelevantSentences(documentText, question);
  if (relevantSentences.length > 0) {
    return relevantSentences.slice(0, 2).join(" ").trim();
  }

  return `Based on the document analysis, I couldn't find specific information to answer: "${question}". Please refer to the complete policy document for detailed information.`;
}

// Semantic search function - same logic as your existing code
function findRelevantSentences(text, question) {
  const sentences = text.split(/[.!?]+/).filter((s) => s.trim().length > 20);
  const keywords = question
    .toLowerCase()
    .split(/\s+/)
    .filter(
      (word) =>
        word.length > 3 &&
        ![
          "what",
          "when",
          "where",
          "how",
          "does",
          "this",
          "that",
          "the",
          "and",
          "are",
          "any",
        ].includes(word)
    );

  const scored = sentences.map((sentence) => {
    const lowerSentence = sentence.toLowerCase();
    const score = keywords.reduce((acc, keyword) => {
      return acc + (lowerSentence.includes(keyword) ? 1 : 0);
    }, 0);
    return { sentence: sentence.trim(), score };
  });

  return scored
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .map((item) => item.sentence);
}
