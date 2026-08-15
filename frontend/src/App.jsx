import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Bot,
  CheckCircle2,
  Database,
  HeartPulse,
  Loader2,
  MessageSquare,
  RefreshCw,
  Send,
  ShieldCheck,
} from "lucide-react";

import {
  getDashboard,
  getCandidates,
  getAssistantStatus,
  askAssistant,
} from "./api/client";

import "./App.css";

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dashboardError, setDashboardError] = useState("");

  const [assistantStatus, setAssistantStatus] = useState(null);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello. I am the GenAR-PADER-AI pharmacovigilance assistant. " +
        "I answer only from the validated project evidence.",
    },
  ]);

  const [assistantLoading, setAssistantLoading] = useState(false);
  const [assistantError, setAssistantError] = useState("");

  async function loadApplicationData() {
    try {
      setLoading(true);
      setDashboardError("");

      const [dashboardData, candidateData] =
        await Promise.all([
          getDashboard(),
          getCandidates(),
        ]);

      setDashboard(dashboardData);

      setCandidates(
        Array.isArray(candidateData?.candidates)
          ? candidateData.candidates
          : []
      );
    } catch (error) {
      setDashboardError(
        error.message ||
          "Unable to connect to backend."
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadAssistantStatus() {
    try {
      const status =
        await getAssistantStatus();

      setAssistantStatus(status);
    } catch (error) {
      setAssistantStatus({
        configured: false,
        error: error.message,
      });
    }
  }

  useEffect(() => {
    loadApplicationData();
    loadAssistantStatus();
  }, []);

  const priorityCounts = useMemo(() => {
    const distribution =
      dashboard?.priority_distribution || {};

    return {
      higher:
        distribution.higher_priority_candidate ?? 0,
      moderate:
        distribution.moderate_priority_candidate ?? 0,
      lower:
        distribution.lower_priority_candidate ?? 0,
    };
  }, [dashboard]);

  async function handleAssistantSubmit(event) {
    event.preventDefault();

    const cleanQuestion = question.trim();

    if (!cleanQuestion || assistantLoading) {
      return;
    }

    setAssistantError("");

    const userMessage = {
      role: "user",
      content: cleanQuestion,
    };

    const previousMessages = messages;

    setMessages([
      ...previousMessages,
      userMessage,
    ]);

    setQuestion("");
    setAssistantLoading(true);

    try {
      const history = previousMessages.map(
        (message) => ({
          role: message.role,
          content: message.content,
        })
      );

      const result = await askAssistant(
        cleanQuestion,
        history
      );

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            result.answer ||
            "The assistant returned no answer.",
        },
      ]);
    } catch (error) {
      setAssistantError(error.message);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "I could not generate a response. " +
            error.message,
          error: true,
        },
      ]);
    } finally {
      setAssistantLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <Loader2
          size={42}
          className="spinner"
        />
        <h2>Loading GenAR-PADER-AI</h2>
        <p>
          Loading validated pharmacovigilance data...
        </p>
      </div>
    );
  }

  if (dashboardError) {
    return (
      <div className="loading-screen">
        <AlertTriangle size={44} />
        <h2>Backend connection failed</h2>
        <p>{dashboardError}</p>
        <button
          className="primary-button"
          onClick={loadApplicationData}
        >
          <RefreshCw size={18} />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="app-shell">

      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <HeartPulse size={28} />
          </div>

          <div>
            <h1>GenAR-PADER-AI</h1>
            <p>
              Pharmacovigilance Decision Support
            </p>
          </div>
        </div>

        <div className="topbar-status">
          <div className="status-pill">
            <CheckCircle2 size={16} />
            Validated Pipeline
          </div>

          <div className="status-pill">
            <Database size={16} />
            {dashboard?.total_safety_reports ?? 0}
            {" "}
            Reports
          </div>
        </div>
      </header>

      <main className="main-content">

        <section className="hero-section">
          <div>
            <span className="eyebrow">
              GENAR-PADER-AI
            </span>

            <h2>
              Pharmacovigilance Safety Dashboard
            </h2>

            <p>
              Validated descriptive and exploratory
              review of Bisoprolol case patterns.
            </p>
          </div>
        </section>

        <section className="safety-banner">
          <ShieldCheck size={24} />

          <div>
            <strong>
              Analytical Safety Boundary
            </strong>

            <p>
              Review priorities represent triage
              categories only. They do not establish
              incidence, causality, disproportionality,
              confirmed safety signals, or confirmed
              drug-drug interactions.
            </p>
          </div>
        </section>

        <section className="metric-grid">
          <MetricCard
            icon={<Database size={22} />}
            title="Total Reports"
            value={
              dashboard?.total_safety_reports ?? 0
            }
          />

          <MetricCard
            icon={<Activity size={22} />}
            title="Candidate Reactions"
            value={
              dashboard?.candidate_reactions ?? 0
            }
          />

          <MetricCard
            icon={<AlertTriangle size={22} />}
            title="Higher Priority"
            value={priorityCounts.higher}
          />

          <MetricCard
            icon={<Activity size={22} />}
            title="Moderate Priority"
            value={priorityCounts.moderate}
          />
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">
                REVIEW PRIORITY
              </span>

              <h3>
                Highest Priority Candidate
              </h3>
            </div>
          </div>

          <div className="top-candidate">
            <div>
              <span className="candidate-rank">
                Rank #1
              </span>

              <h2>
                {dashboard?.top_candidate?.reaction ||
                  "Unavailable"}
              </h2>

              <p>
                Review priority only; this is not a
                confirmed safety signal.
              </p>
            </div>

            <div className="top-candidate-number">
              <strong>
                {
                  dashboard?.top_candidate
                    ?.reported_cases ?? 0
                }
              </strong>

              <span>reported cases</span>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">
                CANDIDATE EVIDENCE
              </span>

              <h3>
                Candidate Review Table
              </h3>
            </div>

            <span className="record-count">
              {candidates.length} candidates
            </span>
          </div>

          <div className="table-wrapper">
            <table className="candidate-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Reaction</th>
                  <th>Cases</th>
                  <th>% Cases</th>
                  <th>Serious</th>
                  <th>Deaths</th>
                  <th>Hospitalization</th>
                  <th>Priority</th>
                </tr>
              </thead>

              <tbody>
                {candidates.map(
                  (candidate) => (
                    <tr
                      key={
                        candidate.reaction ||
                        candidate.rank
                      }
                    >
                      <td>
                        #{candidate.rank}
                      </td>

                      <td className="reaction-name">
                        {candidate.reaction}
                      </td>

                      <td>
                        {
                          candidate.reported_cases
                        }
                      </td>

                      <td>
                        {
                          candidate.percentage_of_all_cases
                        }
                        %
                      </td>

                      <td>
                        {
                          candidate.serious_cases
                        }
                      </td>

                      <td>
                        {
                          candidate.death_cases ?? 0
                        }
                      </td>

                      <td>
                        {
                          candidate.hospitalization_cases ??
                          0
                        }
                      </td>

                      <td>
                        <PriorityBadge
                          priority={
                            candidate.review_priority ||
                            candidate.priority
                          }
                        />
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="assistant-panel">
          <div className="assistant-header">
            <div className="assistant-title">
              <div className="assistant-icon">
                <Bot size={25} />
              </div>

              <div>
                <span className="eyebrow">
                  PRODUCT STAGE 3
                </span>

                <h3>
                  GenAI Evidence Assistant
                </h3>
              </div>
            </div>

            <AssistantStatus
              status={assistantStatus}
            />
          </div>

          <div className="assistant-description">
            <MessageSquare size={20} />

            <p>
              Ask questions about the validated
              GenAR-PADER-AI evidence.
            </p>
          </div>

          <div className="chat-window">
            {messages.map(
              (message, index) => (
                <div
                  key={index}
                  className={
                    message.role === "user"
                      ? "message-row user-row"
                      : "message-row assistant-row"
                  }
                >
                  <div
                    className={
                      message.role === "user"
                        ? "message user-message"
                        : message.error
                        ? "message assistant-message error-message"
                        : "message assistant-message"
                    }
                  >
                    <div className="message-label">
                      {message.role === "user"
                        ? "You"
                        : "GenAR-PADER-AI"}
                    </div>

                    <div className="message-content">
                      {message.content}
                    </div>
                  </div>
                </div>
              )
            )}

            {assistantLoading && (
              <div className="message-row assistant-row">
                <div className="message assistant-message">
                  <div className="message-label">
                    GenAR-PADER-AI
                  </div>

                  <div className="typing-indicator">
                    <Loader2
                      size={17}
                      className="spinner"
                    />
                    Analyzing validated evidence...
                  </div>
                </div>
              </div>
            )}
          </div>

          {assistantError && (
            <div className="assistant-error">
              <AlertTriangle size={18} />
              <span>
                {assistantError}
              </span>
            </div>
          )}

          <form
            className="assistant-form"
            onSubmit={handleAssistantSubmit}
          >
            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              placeholder="Ask about candidates, seriousness, priorities or limitations..."
              rows={3}
              disabled={assistantLoading}
            />

            <button
              type="submit"
              className="send-button"
              disabled={
                assistantLoading ||
                !question.trim()
              }
            >
              {assistantLoading ? (
                <Loader2
                  size={19}
                  className="spinner"
                />
              ) : (
                <Send size={19} />
              )}

              Send
            </button>
          </form>

          <div className="assistant-boundary">
            <ShieldCheck size={16} />

            <span>
              Evidence-only assistant • No causal
              conclusions • No incidence interpretation
            </span>
          </div>
        </section>

      </main>
    </div>
  );
}

function MetricCard({
  icon,
  title,
  value,
}) {
  return (
    <div className="metric-card">
      <div className="metric-icon">
        {icon}
      </div>

      <div>
        <span>{title}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

function PriorityBadge({
  priority,
}) {
  let label = "Lower";
  let className =
    "priority-badge priority-lower";

  if (
    priority ===
    "higher_priority_candidate"
  ) {
    label = "Higher";
    className =
      "priority-badge priority-higher";
  }

  if (
    priority ===
    "moderate_priority_candidate"
  ) {
    label = "Moderate";
    className =
      "priority-badge priority-moderate";
  }

  return (
    <span className={className}>
      {label}
    </span>
  );
}

function AssistantStatus({
  status,
}) {
  if (!status) {
    return (
      <span className="assistant-status checking">
        Checking...
      </span>
    );
  }

  if (status.configured) {
    return (
      <span className="assistant-status online">
        <span className="status-dot" />
        Assistant configured
      </span>
    );
  }

  return (
    <span className="assistant-status offline">
      <span className="status-dot" />
      Assistant unavailable
    </span>
  );
}

export default App;
