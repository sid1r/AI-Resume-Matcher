
import { useState } from "react";
import "./index.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [jdText, setJdText] = useState("");
  const [files, setFiles] = useState([]);
  const [results, setResults] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [summary, setSummary] = useState(null);
  // Authentication states
const [authToken, setAuthToken] = useState(
  () => localStorage.getItem("authToken") || ""
);

const [authMode, setAuthMode] = useState("login");
const [authName, setAuthName] = useState("");
const [authEmail, setAuthEmail] = useState("");
const [authPassword, setAuthPassword] = useState("");
const [authLoading, setAuthLoading] = useState(false);
const [authError, setAuthError] = useState("");
const [authSuccess, setAuthSuccess] = useState("");

// Handle recruiter login and registration
async function handleAuthSubmit(event) {
  event.preventDefault();

  setAuthError("");
  setAuthSuccess("");
  setAuthLoading(true);

  try {
    if (authMode === "register") {
      const registerResponse = await fetch(
        `${API_URL}/auth/register`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: authName,
            email: authEmail,
            password: authPassword,
          }),
        }
      );

      if (!registerResponse.ok) {
        const data = await registerResponse.json();
        throw new Error(data.detail || "Registration failed.");
      }

      setAuthSuccess("Registration successful. Please log in.");
      setAuthMode("login");
      setAuthName("");
      setAuthPassword("");
      return;
    }

    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: authEmail,
        password: authPassword,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Login failed.");
    }

    localStorage.setItem("authToken", data.access_token);
    setAuthToken(data.access_token);

    setAuthPassword("");
    setAuthError("");
  } catch (err) {
    setAuthError(err.message || "Something went wrong.");
  } finally {
    setAuthLoading(false);
  }
}

// Handle recruiter logout
function handleLogout() {
  localStorage.removeItem("authToken");
  setAuthToken("");
  setAuthPassword("");
  setFiles([]);
  setResults([]);
  setSelectedCandidate(null);
  setSummary(null);
  setJdText("");
}

  // Handle resume file selection
  function handleFileChange(event) {
    const selectedFiles = Array.from(event.target.files || []);

    const validFiles = selectedFiles.filter((file) =>
      /\.(pdf|docx)$/i.test(file.name)
    );

    if (validFiles.length !== selectedFiles.length) {
      setError("Only PDF and DOCX files are supported.");
    } else {
      setError("");
    }

    setFiles(validFiles);
    setResults([]);
    setSelectedCandidate(null);
    setSummary(null);
  }

  // Run AI matching
  async function handleMatch() {
    setError("");

    if (!jdText.trim()) {
      setError("Please enter a job description.");
      return;
    }

    if (files.length < 1) {
      setError("Please upload at least one PDF or DOCX resume.");
      return;
    }

    const formData = new FormData();

    formData.append("jd_text", jdText);

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      setLoading(true);
      setResults([]);
      setSelectedCandidate(null);
      setSummary(null);

      const response = await fetch(`${API_URL}/matching/batch`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${authToken}`,
  },
  body: formData,
});

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || "Matching request failed.");
      }

      const data = await response.json();

      setResults(data.ranked_candidates || []);

      setSummary({
        total: data.total_uploaded,
        successful: data.successful,
        failed: data.failed,
        failedFiles: data.failed_files || [],
      });

      if (data.ranked_candidates?.length > 0) {
        setSelectedCandidate(data.ranked_candidates[0]);
      }

      if (!data.ranked_candidates?.length) {
        setError("No resumes could be processed successfully.");
      }
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Cannot connect to the backend. Make sure FastAPI is running."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  // Format experience
  function formatExperience(value) {
    if (value === null || value === undefined) {
      return "Not identified";
    }

    return `${value} ${value === 1 ? "year" : "years"}`;
  }

  const candidateInfo =
    selectedCandidate?.candidate_information || {};

  const analysis =
    selectedCandidate?.matching_analysis || {};

if (!authToken) {
  return (
    <div className="app auth-page">
      <div className="auth-card">
        <div className="brand-icon auth-logo">AI</div>

        <h2>Resume Matcher</h2>
        <p className="auth-subtitle">
          AI-powered candidate evaluation
        </p>

        <h3>
          {authMode === "login"
            ? "Recruiter Login"
            : "Create Recruiter Account"}
        </h3>

        <form onSubmit={handleAuthSubmit}>
          {authMode === "register" && (
            <input
              type="text"
              placeholder="Full name"
              value={authName}
              onChange={(e) => setAuthName(e.target.value)}
              required
              minLength={2}
            />
          )}

          <input
            type="email"
            placeholder="Email address"
            value={authEmail}
            onChange={(e) => setAuthEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password (minimum 8 characters)"
            value={authPassword}
            onChange={(e) => setAuthPassword(e.target.value)}
            required
            minLength={8}
          />

          {authError && (
            <div className="error-message">{authError}</div>
          )}

          {authSuccess && (
            <p className="auth-success">{authSuccess}</p>
          )}

          <button
            type="submit"
            className="match-button auth-submit"
            disabled={authLoading}
          >
            {authLoading
              ? "Please wait..."
              : authMode === "login"
              ? "Login"
              : "Register"}
          </button>
        </form>

        <p className="auth-switch">
          {authMode === "login"
            ? "Don't have an account?"
            : "Already have an account?"}

          <button
            type="button"
            onClick={() => {
              setAuthMode(
                authMode === "login" ? "register" : "login"
              );
              setAuthError("");
              setAuthSuccess("");
            }}
          >
            {authMode === "login" ? "Register" : "Login"}
          </button>
        </p>
      </div>
    </div>
  );
}


  return (
    <div className="app">

      {/* Header */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">AI</div>

          <div>
            <h1>Resume Matcher</h1>
            <p>AI-powered candidate evaluation</p>
          </div>
        </div>

        <div className="header-actions">
  <span className="header-label">Recruiter Dashboard</span>
  <button
    className="logout-button"
    onClick={handleLogout}
  >
    Logout
  </button>
</div>
      </header>

      <main className="dashboard">

        {/* Page Heading */}
        <section className="page-heading">
          <div>
            <p className="eyebrow">TALENT ACQUISITION</p>

            <h2>Candidate Matching Dashboard</h2>

            <p className="subtitle">
              Compare resumes against job requirements and identify the
              strongest candidates.
            </p>
          </div>
        </section>

        {/* Input Section */}
        <section className="input-grid">

          {/* Job Description */}
          <div className="panel jd-panel">
            <div className="section-heading">
              <div className="step-number">01</div>

              <div>
                <h3>Job Description</h3>
                <p>Enter the job requirements below.</p>
              </div>
            </div>

            <textarea
              className="jd-input"
              placeholder="Paste the complete job description here..."
              value={jdText}
              onChange={(event) => setJdText(event.target.value)}
            />

            <div className="input-footer">
              <span>{jdText.length} characters</span>
              <span>Required</span>
            </div>
          </div>

          {/* Resume Upload */}
          <div className="panel upload-panel">
            <div className="section-heading">
              <div className="step-number">02</div>

              <div>
                <h3>Upload Resumes</h3>
                <p>Select multiple candidate resumes.</p>
              </div>
            </div>

            <label className="upload-area">
              <input
                type="file"
                accept=".pdf,.docx"
                multiple
                onChange={handleFileChange}
              />

              <div className="upload-icon">↑</div>

              <strong>Click to upload resumes</strong>

              <span>PDF and DOCX files only</span>

              <span className="upload-limit">
                Upload one or more PDF/DOCX resumes
              </span>
            </label>

            <div className="file-summary">
              <span>{files.length} files selected</span>

              {files.length >= 1 ? (
                <span className="valid-text">
                  Ready to process
                </span>
              ) : (
                <span>Select at least one resume</span>
              )}
            </div>

            {files.length > 0 && (
              <div className="file-list">
                {files.map((file, index) => (
                  <div
                    className="file-item"
                    key={`${file.name}-${index}`}
                  >
                    <span className="file-icon">
                      {file.name.toLowerCase().endsWith(".pdf")
                        ? "PDF"
                        : "DOCX"}
                    </span>

                    <span className="file-name">
                      {file.name}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Matching Button */}
        <div className="action-row">
          <button
            className="match-button"
            onClick={handleMatch}
            disabled={loading}
          >
            {loading ? "Analyzing resumes..." : "Run AI Matching"}

            {!loading && <span>→</span>}
          </button>

          {loading && (
            <span className="loading-message">
              Processing resumes. This may take a little time.
            </span>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {/* Summary Cards */}
        {summary && (
          <section className="summary-grid">

            <div className="summary-card">
              <span>Total uploaded</span>
              <strong>{summary.total}</strong>
            </div>

            <div className="summary-card">
              <span>Successfully processed</span>

              <strong className="success-number">
                {summary.successful}
              </strong>
            </div>

            <div className="summary-card">
              <span>Failed</span>

              <strong className="failed-number">
                {summary.failed}
              </strong>
            </div>

          </section>
        )}

        {/* Failed Files */}
        {summary?.failedFiles?.length > 0 && (
          <div className="failed-files">
            <h4>Files that could not be processed</h4>

            {summary.failedFiles.map((file, index) => (
              <p key={index}>
                <strong>{file.filename}:</strong> {file.error}
              </p>
            ))}
          </div>
        )}

        {/* Matching Results */}
        {results.length > 0 && (
          <>
            <section className="results-section">

              <div className="results-heading">
                <div>
                  <p className="eyebrow">MATCHING RESULTS</p>

                  <h3>Ranked Candidates</h3>

                  <p>
                    Click a candidate to view their detailed analysis.
                  </p>
                </div>

                <span className="result-count">
                  {results.length} candidates
                </span>
              </div>

              {/* Ranking Table */}
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Rank</th>
                      <th>Candidate</th>
                      <th>Experience</th>
                      <th>Match score</th>
                      <th>Matched skills</th>
                      <th>Action</th>
                    </tr>
                  </thead>

                  <tbody>
                    {results.map((candidate) => {
                      const info =
                        candidate.candidate_information || {};

                      const match =
                        candidate.matching_analysis || {};

                      const matchedSkills =
                        match.matched_skills || [];

                      const missingSkills =
                        match.missing_skills || [];

                      const isSelected =
                        selectedCandidate?.rank === candidate.rank;

                      return (
                        <tr
                          key={candidate.rank}
                          className={isSelected ? "selected-row" : ""}
                        >
                          <td>
                            <span className="rank-number">
                              #{candidate.rank}
                            </span>
                          </td>

                          <td>
                            <strong>
                              {info.name || candidate.filename}
                            </strong>

                            <small>
                              {info.email || "Email not identified"}
                            </small>
                          </td>

                          <td>
                            {formatExperience(info.experience_years)}
                          </td>

                          <td>
                            <span className="score-value">
                              {match.overall_matching_score ?? 0}%
                            </span>
                          </td>

                          <td>
                             {match.matched_requirement_count ?? matchedSkills.length} /{" "}
                             {match.total_requirement_count ??
                                matchedSkills.length + missingSkills.length}
                          </td>

                          <td>
                            <button
                              className="view-button"
                              onClick={() =>
                                setSelectedCandidate(candidate)
                              }
                            >
                              View analysis
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Candidate Analysis */}
            {selectedCandidate && (
              <section className="analysis-section">

                <div className="results-heading">
                  <div>
                    <p className="eyebrow">CANDIDATE DETAILS</p>

                    <h3>Candidate Analysis</h3>

                    <p>
                      Detailed evaluation of the selected candidate against
                      the job description.
                    </p>
                  </div>

                  <span className="rank-badge">
                    Rank #{selectedCandidate.rank}
                  </span>
                </div>

                <div className="analysis-grid">

                  {/* Basic Candidate Information */}
                  <div className="panel candidate-panel">
                    <h4>Candidate Information</h4>

                    <div className="candidate-name">
                      {candidateInfo.name ||
                        selectedCandidate.filename}
                    </div>

                    <div className="info-list">

                      <div>
                        <span>Email</span>

                        <strong>
                          {candidateInfo.email || "Not identified"}
                        </strong>
                      </div>

                      <div>
                        <span>Phone</span>

                        <strong>
                          {candidateInfo.phone || "Not identified"}
                        </strong>
                      </div>

                      <div>
                        <span>Experience</span>

                        <strong>
                          {formatExperience(
                            candidateInfo.experience_years
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>Education</span>

                        <strong>
                          {candidateInfo.education?.length
                            ? candidateInfo.education.join(", ")
                            : "Not identified"}
                        </strong>
                      </div>

                      <div>
                        <span>Resume</span>

                        <strong>
                          {selectedCandidate.filename}
                        </strong>
                      </div>

                    </div>
                  </div>

                  {/* Additional Candidate Details */}
                  <div className="panel profile-details-panel">
                    <h4>Additional Candidate Details</h4>

                    <div className="info-list">

                      <div>
                        <span>Technical Skills</span>

                        <strong>
                          {(
                            candidateInfo.technical_skills ||
                            candidateInfo.skills ||
                            []
                          ).join(", ") || "Not identified"}
                        </strong>
                      </div>

                      <div>
                        <span>Functional Skills</span>

                        <strong>
                          {candidateInfo.functional_skills?.join(", ") ||
                            "Not identified"}
                        </strong>
                      </div>

                      <div>
                        <span>Previous Companies</span>

                        <strong>
                          {candidateInfo.previous_companies?.join(", ") ||
                            "Not identified"}
                        </strong>
                      </div>

                      <div>
                        <span>Designations</span>

                        <strong>
                          {candidateInfo.designations?.join(", ") ||
                            "Not identified"}
                        </strong>
                      </div>

                      <div>
                        <span>Certifications</span>

                        <strong>
                          {candidateInfo.certifications?.join(", ") ||
                            "Not identified"}
                        </strong>
                      </div>

                      <div>
                        <span>Projects</span>

                        <strong>
                          {candidateInfo.projects?.join(" | ") ||
                            "Not identified"}
                        </strong>
                      </div>

                    </div>
                  </div>

                  {/* Matching Score */}
                  <div className="panel score-panel">
                    <h4>Overall Matching Score</h4>

                    <div className="large-score">
                      {analysis.overall_matching_score ?? 0}%
                    </div>

                    <div className="score-track">
                      <div
                        className="score-fill"
                        style={{
                          width: `${analysis.overall_matching_score ?? 0}%`,
                        }}
                      />
                    </div>

                    <div className="score-breakdown">

                      <div>
                        <span>Skill score</span>

                        <strong>
                          {analysis.skill_score ?? 0}%
                        </strong>
                      </div>

                      <div>
                        <span>Semantic similarity</span>

                        <strong>
                          {analysis.semantic_similarity ?? 0}%
                        </strong>
                      </div>

                      <div>
                        <span>Experience score</span>

                        <strong>
                          {analysis.experience_score ?? 0}%
                        </strong>
                      </div>

                    </div>
                  </div>

                  {/* Matched Skills */}
                  <div className="panel skills-panel">
                    <h4>Matched Skills</h4>

                    <p>
                      Skills found in the candidate's resume.
                    </p>

                    <div className="skill-list">
                      {analysis.matched_skills?.length > 0 ? (
                        analysis.matched_skills.map((skill) => (
                          <span
                            className="skill-tag matched"
                            key={skill}
                          >
                            ✓ {skill}
                          </span>
                        ))
                      ) : (
                        <span className="empty-text">
                          No matched skills found.
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Missing Skills */}
                  <div className="panel skills-panel">
                    <h4>Missing Skills</h4>

                    <p>
                      Required skills not found in the resume.
                    </p>

                    <div className="skill-list">
                      {analysis.missing_skills?.length > 0 ? (
                        analysis.missing_skills.map((skill) => (
                          <span
                            className="skill-tag missing"
                            key={skill}
                          >
                            {skill}
                          </span>
                        ))
                      ) : (
                        <span className="empty-text">
                          No missing skills.
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Experience Comparison */}
                  <div className="panel experience-panel">
                    <h4>Experience Comparison</h4>

                    <div className="experience-comparison">

                      <div>
                        <span>Candidate experience</span>

                        <strong>
                          {formatExperience(
                            analysis.candidate_experience_years
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>Required experience</span>

                        <strong>
                          {formatExperience(
                            analysis.required_experience_years
                          )}
                        </strong>
                      </div>

                    </div>
                  </div>

                  {/* Score Reasons */}
                  <div className="panel reasons-panel">
                    <h4>Reasons Behind the Score</h4>

                    <ul>
                      {(analysis.reasons || []).map(
                        (reason, index) => (
                          <li key={index}>{reason}</li>
                        )
                      )}
                    </ul>
                  </div>

                </div>
              </section>
            )}
          </>
        )}

      </main>

      {/* Footer */}
      <footer>
        AI Resume Matcher · Candidate evaluation and ranking system
      </footer>

    </div>
  );
}

export default App;
