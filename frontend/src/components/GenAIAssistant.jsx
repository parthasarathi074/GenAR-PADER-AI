import {
  Bot,
  LoaderCircle,
  Send,
  ShieldCheck,
  Sparkles,
  User,
  X,
} from "lucide-react";

import {
  useMemo,
  useRef,
  useState,
  useEffect,
} from "react";

import {
  askAssistant,
} from "../api/client";


const SUGGESTIONS = [
  "What is the highest priority candidate?",
  "Explain Acute kidney injury.",
  "Why were ROR and PRR not calculated?",
  "What are the main analytical limitations?",
];


export default function GenAIAssistant() {
  const [open, setOpen] = useState(false);

  const [question, setQuestion] = useState("");

  const [loading, setLoading] = useState(false);

  const [messages, setMessages] = useState([
    {
      role: "assistant",

      content:
        "Ask me about the validated GenAR-PADER-AI results. "
        + "I will answer only from the validated project evidence.",
    },
  ]);

  const messagesEndRef = useRef(null);


  useEffect(() => {
    if (open) {
      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
      });
    }
  }, [messages, loading, open]);


  const history = useMemo(
    () =>
      messages
        .filter(
          (message) =>
            message.role === "user"
            || message.role === "assistant"
        )
        .slice(-6)
        .map((message) => ({
          role: message.role,
          content: message.content,
        })),
    [messages]
  );


  async function submitQuestion(
    suppliedQuestion
  ) {
    const value = (
      suppliedQuestion ?? question
    ).trim();

    if (!value || loading) {
      return;
    }

    const userMessage = {
      role: "user",
      content: value,
    };

    setMessages(
      (current) => [
        ...current,
        userMessage,
      ]
    );

    setQuestion("");
    setLoading(true);

    try {
      const response = await askAssistant(
        value,
        history
      );

      setMessages(
        (current) => [
          ...current,
          {
            role: "assistant",
            content: response.answer,
          },
        ]
      );

    } catch (error) {
      let message =
        "I could not complete the request.";

      if (
        error.message
        ?.toLowerCase()
        .includes("quota")
      ) {
        message =
          "The GenAI backend is connected correctly, "
          + "but the OpenAI API account currently has insufficient quota. "
          + "Add API billing or credits, then try again.";
      } else if (
        error.message
        ?.toLowerCase()
        .includes("api_key")
      ) {
        message =
          "The OpenAI API key is not configured on the backend.";
      } else {
        message =
          `${message} ${error.message || ""}`.trim();
      }

      setMessages(
        (current) => [
          ...current,
          {
            role: "assistant",
            content: message,
            error: true,
          },
        ]
      );

    } finally {
      setLoading(false);
    }
  }


  function handleSubmit(event) {
    event.preventDefault();

    submitQuestion();
  }


  function clearChat() {
    setMessages([
      {
        role: "assistant",

        content:
          "Ask me about the validated GenAR-PADER-AI results. "
          + "I will answer only from the validated project evidence.",
      },
    ]);

    setQuestion("");
  }


  return (
    <>
      <button
        className="ai-launcher"
        onClick={() =>
          setOpen(true)
        }
        aria-label="Open GenAI assistant"
      >
        <Sparkles size={19} />

        Ask GenAI
      </button>


      {open && (
        <aside className="ai-panel">
          <header className="ai-header">
            <div className="ai-title">
              <div className="ai-logo">
                <Bot size={22} />
              </div>

              <div>
                <strong>
                  GenAR Assistant
                </strong>

                <span>
                  Validated evidence only
                </span>
              </div>
            </div>

            <div className="ai-header-actions">
              <button
                className="ai-clear"
                onClick={clearChat}
                type="button"
              >
                Clear
              </button>

              <button
                className="ai-close"
                onClick={() =>
                  setOpen(false)
                }
                aria-label="Close assistant"
                type="button"
              >
                <X size={19} />
              </button>
            </div>
          </header>


          <div className="ai-scope">
            <ShieldCheck size={16} />

            <span>
              Descriptive and exploratory
              pharmacovigilance support only.
              No causal conclusions are established.
            </span>
          </div>


          <div className="ai-messages">
            {messages.map(
              (message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={
                    message.role === "user"
                      ? "ai-message user"
                      : "ai-message assistant"
                  }
                >
                  <div className="ai-avatar">
                    {message.role === "user" ? (
                      <User size={15} />
                    ) : (
                      <Bot size={15} />
                    )}
                  </div>

                  <div
                    className={
                      message.error
                        ? "ai-bubble ai-error"
                        : "ai-bubble"
                    }
                  >
                    {message.content}
                  </div>
                </div>
              )
            )}


            {loading && (
              <div className="ai-message assistant">
                <div className="ai-avatar">
                  <Bot size={15} />
                </div>

                <div className="ai-bubble ai-thinking">
                  <LoaderCircle
                    className="spin"
                    size={16}
                  />

                  Reviewing validated evidence…
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>


          {messages.length <= 1 && (
            <div className="ai-suggestions">
              {SUGGESTIONS.map(
                (suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() =>
                      submitQuestion(
                        suggestion
                      )
                    }
                    type="button"
                  >
                    {suggestion}
                  </button>
                )
              )}
            </div>
          )}


          <form
            className="ai-input-area"
            onSubmit={handleSubmit}
          >
            <textarea
              value={question}
              onChange={(event) =>
                setQuestion(
                  event.target.value
                )
              }
              placeholder={
                "Ask about candidates, counts, priorities, or limitations..."
              }
              rows={2}
              disabled={loading}
              onKeyDown={(event) => {
                if (
                  event.key === "Enter"
                  && !event.shiftKey
                ) {
                  event.preventDefault();

                  submitQuestion();
                }
              }}
            />

            <button
              type="submit"
              disabled={
                loading
                || !question.trim()
              }
              aria-label="Send question"
            >
              <Send size={18} />
            </button>
          </form>


          <footer className="ai-footer">
            Answers are constrained to validated project evidence.
            Reported frequency is not incidence.
          </footer>
        </aside>
      )}
    </>
  );
}