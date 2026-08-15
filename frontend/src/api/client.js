const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";


async function request(
  path,
  options = {}
) {
  const response = await fetch(
    `${API_BASE}${path}`,
    options
  );

  if (!response.ok) {
    let message =
      `Request failed: ${response.status}`;

    try {
      const data =
        await response.json();

      message =
        data.detail ||
        data.message ||
        message;
    } catch {
      // Keep fallback message.
    }

    throw new Error(message);
  }

  const contentType =
    response.headers.get(
      "content-type"
    ) || "";

  if (
    contentType.includes(
      "application/json"
    )
  ) {
    return response.json();
  }

  return response.text();
}


// =============================================================================
// HEALTH
// =============================================================================

export function getHealth() {
  return request(
    "/health"
  );
}


// =============================================================================
// APPLICATION INFO
// =============================================================================

export function getInfo() {
  return request(
    "/api/info"
  );
}


// =============================================================================
// DASHBOARD
// =============================================================================

export function getDashboard() {
  return request(
    "/api/dashboard"
  );
}


// =============================================================================
// CANDIDATES
// =============================================================================

export function getCandidates() {
  return request(
    "/api/candidates"
  );
}


export function getCandidate(
  rank
) {
  return request(
    `/api/candidates/${rank}`
  );
}


export function getCandidateByReaction(
  reactionName
) {
  return request(
    `/api/reactions/${encodeURIComponent(
      reactionName
    )}`
  );
}


export function getCandidatesByPriority(
  priority
) {
  return request(
    `/api/candidates/priority/${encodeURIComponent(
      priority
    )}`
  );
}


// =============================================================================
// CANDIDATE CARDS
// =============================================================================

export function getCandidateCards() {
  return request(
    "/api/candidate-cards"
  );
}


// =============================================================================
// METADATA / SAFETY
// =============================================================================

export function getMetadata() {
  return request(
    "/api/metadata"
  );
}


export function getSafety() {
  return request(
    "/api/safety"
  );
}


// =============================================================================
// APPLICATION PAYLOAD
// =============================================================================

export function getPayload() {
  return request(
    "/api/payload"
  );
}


// =============================================================================
// REPORTS
// =============================================================================

export function getReportJson() {
  return request(
    "/api/report/json"
  );
}


export function getReportText() {
  return request(
    "/api/report/text"
  );
}


// =============================================================================
// GENAI ASSISTANT
// =============================================================================

export function getAssistantStatus() {
  return request(
    "/api/assistant/status"
  );
}


export function askAssistant(
  question,
  history = []
) {
  return request(
    "/api/assistant/chat",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        question,
        history,
      }),
    }
  );
}


// =============================================================================
// BASE URL
// =============================================================================

export const API_URL =
  API_BASE;