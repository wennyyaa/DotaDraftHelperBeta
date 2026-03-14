import { useEffect, useState } from "react";
import { getHeroes, predictDraft } from "./api";
import HeroInput from "./components/HeroInput";
import RecommendationList from "./components/RecommendationList";

function App() {
  const [alliesText, setAlliesText] = useState("");
  const [enemiesText, setEnemiesText] = useState("");
  const [allyHeroes, setAllyHeroes] = useState([]);
  const [enemyHeroes, setEnemyHeroes] = useState([]);
  const [allHeroes, setAllHeroes] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [draftIdentity, setDraftIdentity] = useState(null);
  const [targetRole, setTargetRole] = useState("any");
  const [occupiedRoles, setOccupiedRoles] = useState([]);
  const [showAdvancedRoles, setShowAdvancedRoles] = useState(false);
  const [draftNeeds, setDraftNeeds] = useState(null);
  useEffect(() => {
    setRecommendations([]);
  }, [allyHeroes, enemyHeroes]);

  const [allySlots, setAllySlots] = useState({
    carry: "",
    mid: "",
    offlane: "",
    support: "",
    hard_support: "",
  });

  const ROLE_LABELS = {
    carry: "Pos 1 / Carry",
    mid: "Pos 2 / Mid",
    offlane: "Pos 3 / Offlane",
    support: "Pos 4 / Support",
    hard_support: "Pos 5 / Hard Support",
  };

  function groupRecommendations(recs) {
    return {
      best: recs.filter((r) => r.confidence === "best-pick"),
      strong: recs.filter((r) => r.confidence === "strong-fit"),
      situational: recs.filter(
        (r) => r.confidence === "situational" || r.confidence === "risky"
      ),
    };
  }

  function inferYourRoleFromSlots(slots, currentAllyHeroes) {
    if (!slots) return null;

    const missingRoles = Object.entries(slots)
      .filter(([, hero]) => !hero)
      .map(([role]) => role);

    const filledCount = Object.values(slots).filter(Boolean).length;

    if (
      missingRoles.length === 1 &&
      currentAllyHeroes.length >= 4 &&
      filledCount >= 3
    ) {
      return missingRoles[0] === "hard_support" ? "support" : missingRoles[0];
    }

    return null;
  }

  const autoDetectedRole =
    targetRole === "any"
      ? inferYourRoleFromSlots(allySlots, allyHeroes)
      : null;

  const groupedRecommendations = groupRecommendations(recommendations || []);

  useEffect(() => {
    async function loadHeroes() {
      try {
        const data = await getHeroes();
        setAllHeroes(data.heroes || []);
      } catch (err) {
        console.error("Failed to load heroes:", err);
      }
    }

    loadHeroes();
  }, []);

  useEffect(() => {
    setAllySlots((prev) => {
      const next = { ...prev };
      let changed = false;

      for (const role of Object.keys(next)) {
        if (next[role] && !allyHeroes.includes(next[role])) {
          next[role] = "";
          changed = true;
        }
      }

      return changed ? next : prev;
    });
  }, [allyHeroes]);

  function updateAllySlot(role, hero) {
    setAllySlots((prev) => ({
      ...prev,
      [role]: prev[role] === hero ? "" : hero,
    }));
  }

  function getAvailableSlotHeroes(currentRole) {
    const selectedInOtherSlots = Object.entries(allySlots)
      .filter(([role, hero]) => role !== currentRole && hero)
      .map(([, hero]) => hero);

    return allyHeroes.filter((hero) => !selectedInOtherSlots.includes(hero));
  }

  function clearAllySlots() {
    setAllySlots({
      carry: "",
      mid: "",
      offlane: "",
      support: "",
      hard_support: "",
    });
  }

  function handleClearDraft() {
    setAlliesText("");
    setEnemiesText("");
    setAllyHeroes([]);
    setEnemyHeroes([]);
    setRecommendations([]);
    setDraftIdentity(null);
    setTargetRole("any");
    setOccupiedRoles([]);
    setError("");
    setDraftNeeds(null);
    clearAllySlots();
  }

  async function handlePredict() {
    setError("");
    setRecommendations([]);

    if (allyHeroes.length === 0 && enemyHeroes.length === 0) {
      setError("Add some heroes to start draft analysis.");
      return;
    }

    if (allyHeroes.length === 0) {
      setError("Add at least one allied hero.");
      return;
    }

    if (enemyHeroes.length === 0) {
      setError("Add at least one enemy hero.");
      return;
    }

    setLoading(true);

    try {
      const normalizedAllySlots = {
        carry: allySlots.carry || null,
        mid: allySlots.mid || null,
        offlane: allySlots.offlane || null,
        support: allySlots.support || null,
        hard_support: allySlots.hard_support || null,
      };

      const rawEffectiveTargetRole =
        targetRole === "any" ? autoDetectedRole : targetRole;

      const effectiveTargetRole =
        rawEffectiveTargetRole === "hard_support"
          ? "support"
          : rawEffectiveTargetRole;

      const data = await predictDraft(
        allyHeroes,
        enemyHeroes,
        effectiveTargetRole,
        occupiedRoles,
        normalizedAllySlots
      );

      setRecommendations(data.recommended || []);
      setDraftIdentity(data.identity || null);
      setDraftNeeds(data.draft_needs || null);

    } catch (err) {
      console.error("Predict failed:", err);

      if (err.message?.includes("Network")) {
        setError("Server connection lost. Try again.");
      } else {
        setError("Draft analysis failed. Please try again.");
      }

    } finally {
      setLoading(false);
    }
  }

  function renderRecommendationSection(title, items) {
    if (!items || items.length === 0) return null;

    return (
      <div style={{ marginTop: "18px" }}>
        <div
          style={{
            fontSize: "13px",
            fontWeight: 800,
            color: "#8fa1bb",
            letterSpacing: "0.5px",
            textTransform: "uppercase",
            marginBottom: "10px",
          }}
        >
          {title}
        </div>

        <RecommendationList recommendations={items} />
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top, #182233 0%, #0c1017 45%, #080b10 100%)",
        color: "#f4f7fb",
        fontFamily:
          "Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
        padding: "20px 20px 48px",
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "1320px",
          margin: "0 auto",
          display: "grid",
          gap: "20px",
        }}
      >
        <section
          style={{
            background:
              "linear-gradient(180deg, rgba(25,34,49,0.96) 0%, rgba(18,24,35,0.96) 100%)",
            border: "1px solid rgba(110, 138, 180, 0.18)",
            borderRadius: "24px",
            padding: "28px",
            boxShadow: "0 20px 60px rgba(0, 0, 0, 0.35)",
          }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: "16px",
              alignItems: "flex-start",
              flexWrap: "wrap",
              marginBottom: "24px",
            }}
          >
            <div>
              <div
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  fontSize: "12px",
                  color: "#8eb7ff",
                  backgroundColor: "rgba(41, 104, 255, 0.12)",
                  border: "1px solid rgba(91, 145, 255, 0.22)",
                  borderRadius: "999px",
                  padding: "6px 10px",
                  marginBottom: "14px",
                  letterSpacing: "0.3px",
                  textTransform: "uppercase",
                  fontWeight: 700,
                }}
              >
                Draft helper beta
              </div>

              <h1
                style={{
                  margin: 0,
                  fontSize: "42px",
                  lineHeight: 1.05,
                  letterSpacing: "-1px",
                }}
              >
                Dota 2 Draft Helper
              </h1>

              <p
                style={{
                  margin: "12px 0 0",
                  fontSize: "15px",
                  color: "#a9b7cb",
                  maxWidth: "720px",
                  lineHeight: 1.6,
                }}
              >
                Build both drafts, explore recommendations, and see why each
                hero fits your current composition.
              </p>
              <div
                style={{
                  marginTop: "14px",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "8px 12px",
                  borderRadius: "12px",
                  border: "1px solid rgba(155,192,255,0.18)",
                  background: "rgba(155,192,255,0.08)",
                  color: "#dbe8ff",
                  fontSize: "13px",
                  fontWeight: 600,
                }}
              >
                Beta feedback: send bugs, weird picks, and screenshots in Discord
              </div>
            </div>

            <div
              style={{
                display: "grid",
                gap: "10px",
                minWidth: "220px",
              }}
            >
              <div
                style={{
                  backgroundColor: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: "16px",
                  padding: "12px 14px",
                }}
              >
                <div
                  style={{
                    fontSize: "11px",
                    color: "#7f90a8",
                    marginBottom: "4px",
                  }}
                >
                  MODE
                </div>
                <div style={{ fontSize: "14px", fontWeight: 700 }}>
                  Rule-Based Assistant
                </div>
              </div>

              <div
                style={{
                  backgroundColor: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: "16px",
                  padding: "12px 14px",
                }}
              >
                <div
                  style={{
                    fontSize: "11px",
                    color: "#7f90a8",
                    marginBottom: "4px",
                  }}
                >
                  OUTPUT
                </div>
                <div style={{ fontSize: "14px", fontWeight: 700 }}>
                  Top Recommendations
                </div>
              </div>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
              gap: "12px",
              marginBottom: "18px",
            }}
          >
            <div
              style={{
                backgroundColor: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: "16px",
                padding: "14px",
              }}
            >
              <div
                style={{
                  fontSize: "11px",
                  color: "#7f90a8",
                  marginBottom: "6px",
                }}
              >
                ALLIES PICKED
              </div>
              <div style={{ fontSize: "22px", fontWeight: 800 }}>
                {allyHeroes.length}
              </div>
            </div>

            <div
              style={{
                backgroundColor: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: "16px",
                padding: "14px",
              }}
            >
              <div
                style={{
                  fontSize: "11px",
                  color: "#7f90a8",
                  marginBottom: "6px",
                }}
              >
                ENEMIES PICKED
              </div>
              <div style={{ fontSize: "22px", fontWeight: 800 }}>
                {enemyHeroes.length}
              </div>
            </div>

            <div
              style={{
                backgroundColor: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: "16px",
                padding: "14px",
              }}
            >
              <div
                style={{
                  fontSize: "11px",
                  color: "#7f90a8",
                  marginBottom: "6px",
                }}
              >
                RECOMMENDATIONS
              </div>
              <div style={{ fontSize: "22px", fontWeight: 800 }}>
                {recommendations.length}
              </div>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "18px",
            }}
          >
            <HeroInput
              label="Allied Heroes"
              text={alliesText}
              onTextChange={setAlliesText}
              onHeroesChange={setAllyHeroes}
              placeholder="Puck, Mars, Dazzle"
              allHeroes={allHeroes}
              excludedHeroes={enemyHeroes}
            />

            <HeroInput
              label="Enemy Heroes"
              text={enemiesText}
              onTextChange={setEnemiesText}
              onHeroesChange={setEnemyHeroes}
              placeholder="Huskar, Lion"
              allHeroes={allHeroes}
              excludedHeroes={allyHeroes}
            />
          </div>

          <div
            style={{
              fontSize: "12px",
              color: "#7b859a",
              marginTop: "6px",
            }}
          >
            Type hero names separated by commas. Example: Mars, Puck
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "14px",
              flexWrap: "wrap",
              marginTop: "22px",
            }}
          >
            <div
              style={{
                display: "flex",
                gap: "10px",
                alignItems: "center",
                flexWrap: "wrap",
              }}
            >
              {targetRole === "any" && autoDetectedRole && (
                <div
                  style={{
                    padding: "10px 12px",
                    borderRadius: "10px",
                    border: "1px solid rgba(126, 231, 135, 0.22)",
                    background: "rgba(126, 231, 135, 0.08)",
                    color: "#bdf7c6",
                    fontSize: "13px",
                    fontWeight: 700,
                  }}
                >
                  You play: {ROLE_LABELS[autoDetectedRole]}
                </div>
              )}

              {allyHeroes.length >= 2 && (
                <button
                  type="button"
                  onClick={() => setShowAdvancedRoles((prev) => !prev)}
                  style={{
                    padding: "8px 12px",
                    borderRadius: "10px",
                    border: "1px solid #2a3342",
                    background: "#111722",
                    color: "#d7deea",
                    fontSize: "12px",
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  {showAdvancedRoles ? "Hide Role Slots" : "Set Ally Roles"}
                </button>
              )}

              {!autoDetectedRole && !showAdvancedRoles && (
                <div
                  style={{
                    display: "flex",
                    gap: "10px",
                    alignItems: "center",
                    flexWrap: "wrap",
                  }}
                >
                  {targetRole === "any" && autoDetectedRole && (
                    <div
                      style={{
                        padding: "10px 12px",
                        borderRadius: "10px",
                        border: "1px solid rgba(126, 231, 135, 0.22)",
                        background: "rgba(126, 231, 135, 0.08)",
                        color: "#bdf7c6",
                        fontSize: "13px",
                        fontWeight: 700,
                      }}
                    >
                      You play: {ROLE_LABELS[autoDetectedRole]}
                    </div>
                  )}

                  {allyHeroes.length >= 2 && (
                    <button
                      type="button"
                      onClick={() => setShowAdvancedRoles((prev) => !prev)}
                      style={{
                        padding: "8px 12px",
                        borderRadius: "10px",
                        border: "1px solid #2a3342",
                        background: "#111722",
                        color: "#d7deea",
                        fontSize: "12px",
                        fontWeight: 700,
                        cursor: "pointer",
                      }}
                    >
                      {showAdvancedRoles ? "Hide Role Slots" : "Set Ally Roles"}
                    </button>
                  )}

                  {!autoDetectedRole && !showAdvancedRoles && (
                    <div
                      style={{
                        position: "relative",
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                        padding: "10px 14px",
                        background: "linear-gradient(180deg,#1a2130,#151b26)",
                        border: "1px solid #2a3342",
                        borderRadius: "12px",
                        boxShadow: "0 6px 14px rgba(0,0,0,0.25)",
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = "#3a4860";
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = "#2a3342";
                      }}
                    >
                      <span
                        style={{
                          fontSize: "11px",
                          color: "#8fa1bb",
                          fontWeight: 700,
                          letterSpacing: "0.6px",
                          textTransform: "uppercase",
                        }}
                      >
                        Role
                      </span>

                      <select
                        value={targetRole}
                        onChange={(e) => setTargetRole(e.target.value)}
                        style={{
                          appearance: "none",
                          WebkitAppearance: "none",
                          MozAppearance: "none",
                          background: "transparent",
                          border: "none",
                          outline: "none",
                          color: "#f4f7fb",
                          fontWeight: 700,
                          fontSize: "14px",
                          paddingRight: "18px",
                          cursor: "pointer",
                        }}
                      >
                        <option value="any" style={{ backgroundColor: "#11161f", color: "#f4f7fb" }}>
                          Any
                        </option>
                        <option value="carry" style={{ backgroundColor: "#11161f", color: "#f4f7fb" }}>
                          Carry
                        </option>
                        <option value="mid" style={{ backgroundColor: "#11161f", color: "#f4f7fb" }}>
                          Mid
                        </option>
                        <option value="offlane" style={{ backgroundColor: "#11161f", color: "#f4f7fb" }}>
                          Offlane
                        </option>
                        <option value="support" style={{ backgroundColor: "#11161f", color: "#f4f7fb" }}>
                          Support
                        </option>
                        <option value="hard_support" style={{ backgroundColor: "#11161f", color: "#f4f7fb" }}>
                          Hard Support
                        </option>
                      </select>

                      <div
                        style={{
                          position: "absolute",
                          right: "10px",
                          pointerEvents: "none",
                          fontSize: "12px",
                          color: "#7c8aa3",
                        }}
                      >
                        ▼
                      </div>
                    </div>
                  )}
                </div>
              )}

              {showAdvancedRoles && allyHeroes.length > 2 && (
                <div
                  style={{
                    padding: "14px",
                    borderRadius: "14px",
                    border: "1px solid #232c39",
                    background:
                      "linear-gradient(180deg, #141a24, #10151d)",
                    boxShadow: "0 8px 24px rgba(0,0,0,0.18)",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      gap: "10px",
                      marginBottom: "4px",
                      flexWrap: "wrap",
                    }}
                  >
                    <div>
                      <div
                        style={{
                          fontSize: "15px",
                          fontWeight: 800,
                          color: "#eef3fb",
                          marginBottom: "3px",
                        }}
                      >
                        Ally Role Slots
                      </div>
                      <div
                        style={{
                          fontSize: "12px",
                          color: "#8d9bb0",
                        }}
                      >
                        Assign roles only from heroes already picked
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={clearAllySlots}
                      style={{
                        padding: "7px 12px",
                        borderRadius: "10px",
                        border: "1px solid #2b3645",
                        background: "#0e131b",
                        color: "#d9e1ee",
                        fontSize: "12px",
                        fontWeight: 700,
                        cursor: "pointer",
                      }}
                    >
                      Clear Roles
                    </button>
                  </div>

                  {[
                    ["carry", "Pos 1", "#7ee787"],
                    ["mid", "Pos 2", "#9bc0ff"],
                    ["offlane", "Pos 3", "#ffcb7d"],
                    ["support", "Pos 4", "#caa6ff"],
                    ["hard_support", "Pos 5", "#ff9c9c"],
                  ].map(([roleKey, shortLabel, accent]) => {
                    const isYourRole =
                      targetRole === "any" &&
                      autoDetectedRole === roleKey &&
                      !allySlots[roleKey];

                    const options = getAvailableSlotHeroes(roleKey);
                    const selectedHero = allySlots[roleKey];

                    return (
                      <div
                        key={roleKey}
                        style={{
                          display: "grid",
                          gridTemplateColumns: "80px 1fr",
                          gap: "10px",
                          alignItems: "start",
                          padding: "10px 0",
                          borderTop: "1px solid rgba(255,255,255,0.04)",
                        }}
                      >
                        <div style={{ paddingTop: "4px" }}>
                          <div
                            style={{
                              fontSize: "12px",
                              fontWeight: 800,
                              color: accent,
                              marginBottom: "3px",
                              letterSpacing: "0.2px",
                            }}
                          >
                            {shortLabel}
                          </div>

                          <div
                            style={{
                              fontSize: "11px",
                              color: isYourRole ? "#7ee787" : "#738196",
                              fontWeight: isYourRole ? 700 : 400,
                            }}
                          >
                            {isYourRole ? (
                              "You play this role"
                            ) : (
                              <>
                                {roleKey === "carry" && "Carry"}
                                {roleKey === "mid" && "Mid"}
                                {roleKey === "offlane" && "Offlane"}
                                {roleKey === "support" && "Support"}
                                {roleKey === "hard_support" && "Hard 5"}
                              </>
                            )}
                          </div>
                        </div>

                        <div
                          style={{
                            display: "flex",
                            gap: "8px",
                            flexWrap: "wrap",
                          }}
                        >
                          {options.length === 0 && !selectedHero ? (
                            <div
                              style={{
                                fontSize: "12px",
                                color: "#6f7d90",
                                padding: "8px 0",
                              }}
                            >
                              No heroes left
                            </div>
                          ) : (
                            options.map((hero) => {
                              const active = selectedHero === hero;

                              return (
                                <button
                                  key={hero}
                                  type="button"
                                  onClick={() =>
                                    updateAllySlot(roleKey, hero)
                                  }
                                  style={{
                                    padding: "8px 12px",
                                    borderRadius: "999px",
                                    border: active
                                      ? `1px solid ${accent}`
                                      : "1px solid #2a3342",
                                    background: active
                                      ? `linear-gradient(180deg, ${accent}22, ${accent}14)`
                                      : "#0f141c",
                                    color: active ? "#f4f8ff" : "#c9d2e1",
                                    fontSize: "12px",
                                    fontWeight: 700,
                                    cursor: "pointer",
                                    transition: "all 0.15s ease",
                                  }}
                                  onMouseEnter={(e) => {
                                    if (!active) {
                                      e.currentTarget.style.borderColor =
                                        "#3a4860";
                                    }
                                  }}
                                  onMouseLeave={(e) => {
                                    if (!active) {
                                      e.currentTarget.style.borderColor =
                                        "#2a3342";
                                    }
                                  }}
                                >
                                  {hero}
                                </button>
                              );
                            })
                          )}

                          {selectedHero && !options.includes(selectedHero) && (
                            <button
                              type="button"
                              onClick={() =>
                                updateAllySlot(roleKey, selectedHero)
                              }
                              style={{
                                padding: "8px 12px",
                                borderRadius: "999px",
                                border: `1px solid ${accent}`,
                                background: `linear-gradient(180deg, ${accent}22, ${accent}14)`,
                                color: "#f4f8ff",
                                fontSize: "12px",
                                fontWeight: 700,
                                cursor: "pointer",
                              }}
                            >
                              {selectedHero}
                            </button>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              <button
                onClick={handlePredict}
                disabled={loading}
                style={{
                  padding: "12px 20px",
                  background: loading
                    ? "linear-gradient(180deg, #31466f, #263758)"
                    : "linear-gradient(180deg, #5b8cff, #3d72dc)",
                  border: loading ? "1px solid #3d5079" : "1px solid #6a9bff",
                  borderRadius: "14px",
                  color: "#ffffff",
                  fontWeight: 800,
                  fontSize: "14px",
                  letterSpacing: "0.2px",
                  cursor: loading ? "default" : "pointer",
                  opacity: loading ? 0.88 : 1,
                  boxShadow: loading
                    ? "0 6px 16px rgba(0,0,0,0.18)"
                    : "0 10px 24px rgba(61,114,220,0.35)",
                  transform: "translateY(0)",
                  transition: "all 0.18s ease",
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.transform = "translateY(-1px)";
                    e.currentTarget.style.boxShadow = "0 14px 28px rgba(61,114,220,0.45)";
                    e.currentTarget.style.filter = "brightness(1.04)";
                  }
                }}
                onMouseLeave={(e) => {
                  if (!loading) {
                    e.currentTarget.style.transform = "translateY(0)";
                    e.currentTarget.style.boxShadow = "0 10px 24px rgba(61,114,220,0.35)";
                    e.currentTarget.style.filter = "brightness(1)";
                  }
                }}
              >
                {loading ? "Analyzing draft…" : "✨ Predict Best Heroes"}
              </button>
              <button
                type="button"
                onClick={handleClearDraft}
                style={{
                  padding: "12px 18px",
                  borderRadius: "14px",
                  border: "1px solid #2d3848",
                  background: "linear-gradient(180deg, #1a2230, #111823)",
                  color: "#d7deea",
                  fontWeight: 800,
                  fontSize: "14px",
                  letterSpacing: "0.2px",
                  cursor: "pointer",
                  boxShadow: "0 8px 18px rgba(0,0,0,0.20)",
                  transform: "translateY(0)",
                  transition: "all 0.18s ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-1px)";
                  e.currentTarget.style.borderColor = "#46556b";
                  e.currentTarget.style.boxShadow = "0 12px 22px rgba(0,0,0,0.28)";
                  e.currentTarget.style.background =
                    "linear-gradient(180deg, #202a3a, #151d29)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.borderColor = "#2d3848";
                  e.currentTarget.style.boxShadow = "0 8px 18px rgba(0,0,0,0.20)";
                  e.currentTarget.style.background =
                    "linear-gradient(180deg, #1a2230, #111823)";
                }}
              >
                ↺ Clear Draft
              </button>
            </div>

            <div style={{ fontSize: "13px", color: "#8fa0b8" }}>
              Uses handcrafted draft logic and team composition analysis.
            </div>
          </div>

          {error && (
            <div
              style={{
                marginTop: "16px",
                padding: "14px 16px",
                borderRadius: "14px",
                background: "rgba(255, 120, 120, 0.08)",
                border: "1px solid rgba(255,120,120,0.18)",
                color: "#ffb3b3",
                fontSize: "14px",
                fontWeight: 600,
                lineHeight: 1.4,
              }}
            >
              {error}
            </div>
          )}
        </section>

        {(draftIdentity || draftNeeds) && (
          <div
            style={{
              marginTop: "18px",
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
              gap: "14px",
            }}
          >
            {draftIdentity && (
              <div
                style={{
                  padding: "16px",
                  borderRadius: "14px",
                  border: "1px solid #232c39",
                  background:
                    "linear-gradient(180deg, #141a24, #10151d)",
                  boxShadow: "0 8px 24px rgba(0,0,0,0.18)",
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: "#8fa1bb",
                    fontWeight: 700,
                    letterSpacing: "0.6px",
                    textTransform: "uppercase",
                    marginBottom: "6px",
                  }}
                >
                  Draft Style
                </div>

                <div
                  style={{
                    fontSize: "20px",
                    fontWeight: 800,
                    color: "#eef3fb",
                    marginBottom: "12px",
                  }}
                >
                  {draftIdentity.style || "Balanced"}
                </div>

                {draftIdentity.strengths?.length > 0 && (
                  <div style={{ marginBottom: "12px" }}>
                    <div
                      style={{
                        fontSize: "12px",
                        color: "#7ee787",
                        fontWeight: 700,
                        marginBottom: "6px",
                        textTransform: "uppercase",
                      }}
                    >
                      Strengths
                    </div>

                    <div
                      style={{
                        display: "flex",
                        gap: "8px",
                        flexWrap: "wrap",
                      }}
                    >
                      {draftIdentity.strengths.map((item) => (
                        <span
                          key={item}
                          style={{
                            padding: "6px 10px",
                            borderRadius: "999px",
                            background: "rgba(126,231,135,0.10)",
                            border:
                              "1px solid rgba(126,231,135,0.20)",
                            color: "#c8f5d0",
                            fontSize: "12px",
                            fontWeight: 700,
                          }}
                        >
                          {item}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {draftIdentity.weaknesses?.length > 0 && (
                  <div>
                    <div
                      style={{
                        fontSize: "12px",
                        color: "#ff9c9c",
                        fontWeight: 700,
                        marginBottom: "6px",
                        textTransform: "uppercase",
                      }}
                    >
                      Weaknesses
                    </div>

                    <div
                      style={{
                        display: "flex",
                        gap: "8px",
                        flexWrap: "wrap",
                      }}
                    >
                      {draftIdentity.weaknesses.map((item) => (
                        <span
                          key={item}
                          style={{
                            padding: "6px 10px",
                            borderRadius: "999px",
                            background: "rgba(255,156,156,0.10)",
                            border:
                              "1px solid rgba(255,156,156,0.20)",
                            color: "#ffd0d0",
                            fontSize: "12px",
                            fontWeight: 700,
                          }}
                        >
                          {item}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {draftNeeds && (
              <div
                style={{
                  padding: "16px",
                  borderRadius: "14px",
                  border: "1px solid #232c39",
                  background:
                    "linear-gradient(180deg, #141a24, #10151d)",
                  boxShadow: "0 8px 24px rgba(0,0,0,0.18)",
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    color: "#8fa1bb",
                    fontWeight: 700,
                    letterSpacing: "0.6px",
                    textTransform: "uppercase",
                    marginBottom: "10px",
                  }}
                >
                  Team Needs
                </div>

                {draftNeeds.needs?.length > 0 ? (
                  <div
                    style={{
                      display: "flex",
                      gap: "8px",
                      flexWrap: "wrap",
                      marginBottom: "12px",
                    }}
                  >
                    {draftNeeds.needs.map((item) => (
                      <span
                        key={item}
                        style={{
                          padding: "6px 10px",
                          borderRadius: "999px",
                          background: "rgba(155,192,255,0.10)",
                          border: "1px solid rgba(155,192,255,0.18)",
                          color: "#dbe8ff",
                          fontSize: "12px",
                          fontWeight: 700,
                        }}
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div
                    style={{
                      color: "#cfd6e6",
                      fontSize: "13px",
                      marginBottom: "12px",
                    }}
                  >
                    No major gaps detected.
                  </div>
                )}

                {draftNeeds.notes?.length > 0 && (
                  <>
                    <div
                      style={{
                        fontSize: "12px",
                        color: "#ffcb7d",
                        fontWeight: 700,
                        marginBottom: "6px",
                        textTransform: "uppercase",
                      }}
                    >
                      Notes
                    </div>

                    <div
                      style={{
                        display: "flex",
                        gap: "8px",
                        flexWrap: "wrap",
                      }}
                    >
                      {draftNeeds.notes.map((item) => (
                        <span
                          key={item}
                          style={{
                            padding: "6px 10px",
                            borderRadius: "999px",
                            background: "rgba(255,203,125,0.10)",
                            border:
                              "1px solid rgba(255,203,125,0.18)",
                            color: "#ffe2b4",
                            fontSize: "12px",
                            fontWeight: 700,
                          }}
                        >
                          {item}
                        </span>
                      ))}
                    </div>
                  </>
                )}
              </div>
            )}
          </div>
        )}

        <section
          style={{
            background:
              "linear-gradient(180deg, rgba(21,28,39,0.95) 0%, rgba(14,18,26,0.95) 100%)",
            border: "1px solid rgba(110, 138, 180, 0.14)",
            borderRadius: "24px",
            padding: "24px 24px 28px",
            boxShadow: "0 18px 42px rgba(0, 0, 0, 0.24)",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1.2fr 0.8fr",
              gap: "16px",
              alignItems: "stretch",
              marginBottom: "18px",
            }}
          >
            <div>
              <h2
                style={{
                  margin: 0,
                  fontSize: "22px",
                  letterSpacing: "-0.3px",
                }}
              >
                Recommendations
              </h2>
              <div
                style={{
                  marginTop: "6px",
                  fontSize: "13px",
                  color: "#8fa0b8",
                }}
              >
                Ranked suggestions based on your current draft state.
              </div>
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                gap: "10px",
              }}
            >
              <div
                style={{
                  backgroundColor: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: "14px",
                  padding: "12px",
                }}
              >
                <div
                  style={{
                    fontSize: "11px",
                    color: "#7f90a8",
                    marginBottom: "4px",
                  }}
                >
                  RESULTS
                </div>
                <div style={{ fontSize: "18px", fontWeight: 800 }}>
                  {recommendations.length}
                </div>
              </div>

              <div
                style={{
                  backgroundColor: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: "14px",
                  padding: "12px",
                }}
              >
                <div
                  style={{
                    fontSize: "11px",
                    color: "#7f90a8",
                    marginBottom: "4px",
                  }}
                >
                  ALLIES
                </div>
                <div style={{ fontSize: "18px", fontWeight: 800 }}>
                  {allyHeroes.length}
                </div>
              </div>

              <div
                style={{
                  backgroundColor: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: "14px",
                  padding: "12px",
                }}
              >
                <div
                  style={{
                    fontSize: "11px",
                    color: "#7f90a8",
                    marginBottom: "4px",
                  }}
                >
                  ENEMIES
                </div>
                <div style={{ fontSize: "18px", fontWeight: 800 }}>
                  {enemyHeroes.length}
                </div>
              </div>
            </div>
          </div>

          {recommendations.length === 0 ? (
            <div
              style={{
                color: "#90a1b8",
                fontSize: "14px",
                border: "1px dashed rgba(144, 161, 184, 0.2)",
                borderRadius: "18px",
                padding: "22px",
                backgroundColor: "rgba(255,255,255,0.02)",
                display: "grid",
                gap: "8px",
              }}
            >
              <div
                style={{
                  fontSize: "16px",
                  fontWeight: 700,
                  color: "#d8e2f1",
                }}
              >
                No recommendations yet
              </div>
              <div>
                Build both drafts and click <strong>Predict Best Heroes</strong>{" "}
                to see the best hero suggestions.
              </div>
            </div>
          ) : (
            <>
              {renderRecommendationSection(
                "Best Picks",
                groupedRecommendations.best
              )}
              {renderRecommendationSection(
                "Strong Picks",
                groupedRecommendations.strong
              )}
              {renderRecommendationSection(
                "Situational",
                groupedRecommendations.situational
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;