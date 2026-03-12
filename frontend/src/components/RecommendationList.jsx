import React from "react";

function heroToIconName(hero) {
  const specialNames = {
    "Anti-Mage": "antimage",
    "Centaur Warrunner": "centaur",
    "Clockwerk": "rattletrap",
    "Doom": "doom_bringer",
    "Io": "wisp",
    "Lifestealer": "life_stealer",
    "Magnus": "magnataur",
    "Nature's Prophet": "furion",
    "Necrophos": "necrolyte",
    "Outworld Devourer": "obsidian_destroyer",
    "Queen of Pain": "queenofpain",
    "Shadow Fiend": "nevermore",
    "Timbersaw": "shredder",
    "Treant Protector": "treant",
    "Underlord": "abyssal_underlord",
    "Vengeful Spirit": "vengefulspirit",
    "Windranger": "windrunner",
    "Wraith King": "skeleton_king",
    "Zeus": "zuus",
  };

  if (specialNames[hero]) {
    return specialNames[hero];
  }

  return hero
    .toLowerCase()
    .replace(/-/g, "")
    .replace(/'/g, "")
    .replace(/ /g, "_");
}

function getHeroIcon(heroName) {
  return `https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/${heroToIconName(
    heroName
  )}.png`;
}

function formatScore(score) {
  if (typeof score !== "number") {
    return "+0.0";
  }

  if (score >= 0) {
    return `+${score.toFixed(1)}`;
  }

  return score.toFixed(1);
}

function formatReason(reason) {
  if (!reason) {
    return { text: "", kind: "neutral" };
  }

  const trimmed = reason.trim();

  const counterMatch = trimmed.match(/^\+\d+(\.\d+)?\s+vs\s+(.+?)\s+\(counter\)$/i);
  if (counterMatch) {
    return { text: `Counters ${counterMatch[2]}`, kind: "good" };
  }

  const synergyMatch = trimmed.match(/^\+\d+(\.\d+)?\s+vs\s+(.+?)\s+\(synergy\)$/i);
  if (synergyMatch) {
    return { text: `Synergy with ${synergyMatch[2]}`, kind: "good" };
  }

  const weakMatch = trimmed.match(/^-\d+(\.\d+)?\s+vs\s+(.+?)\s+\(weakness\)$/i);
  if (weakMatch) {
    return { text: `Weak vs ${weakMatch[2]}`, kind: "bad" };
  }

  return {
    text: trimmed.charAt(0).toUpperCase() + trimmed.slice(1),
    kind: "good",
  };
}

function inferTags(rec, goodReasons) {
  const tags = new Set();

  const allText = [
    ...(rec.roles || []),
    ...(goodReasons || []).map((r) => r.text.toLowerCase()),
  ].join(" | ");

  if (allText.includes("counter")) tags.add("Counter");
  if (allText.includes("synergy")) tags.add("Synergy");
  if (allText.includes("frontline")) tags.add("Frontline");
  if (allText.includes("control")) tags.add("Control");
  if (allText.includes("scaling") || allText.includes("late-game")) tags.add("Scaling");
  if (allText.includes("tempo") || allText.includes("early")) tags.add("Tempo");
  if (allText.includes("tower") || allText.includes("push")) tags.add("Push");

  if ((rec.roles || []).includes("carry")) tags.add("Core");
  if ((rec.roles || []).includes("support")) tags.add("Support");

  return Array.from(tags).slice(0, 3);
}

function RecommendationList({ recommendations }) {
  if (!recommendations || recommendations.length === 0) {
    return null;
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
        gap: "16px",
      }}
    >
      {recommendations.map((rec, index) => {
        const formattedReasons = (rec.reasons || []).map(formatReason);
        const goodReasons = formattedReasons.filter((r) => r.kind === "good");
        const badReasons = formattedReasons.filter((r) => r.kind === "bad");
        const quickTags = inferTags(rec, goodReasons);

        return (
          <div
            key={`${rec.hero}-${index}`}
            style={{
              background:
                "linear-gradient(180deg, rgba(25,34,48,0.95) 0%, rgba(17,23,32,0.95) 100%)",
              border: "1px solid rgba(108, 136, 180, 0.14)",
              borderRadius: "18px",
              padding: "16px",
              boxShadow: "0 14px 30px rgba(0,0,0,0.22)",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "flex-start",
                gap: "12px",
                marginBottom: "14px",
              }}
            >
              <img
                src={getHeroIcon(rec.hero)}
                alt={rec.hero}
                width={68}
                height={38}
                style={{
                  borderRadius: "8px",
                  objectFit: "cover",
                  flexShrink: 0,
                  backgroundColor: "#0f1115",
                }}
                onError={(e) => {
                  e.currentTarget.style.opacity = "0.35";
                }}
              />

              <div style={{ minWidth: 0, width: "100%" }}>
                <div
                  style={{
                    fontSize: "17px",
                    fontWeight: 800,
                    color: "#f5f7fb",
                    marginBottom: "6px",
                    lineHeight: 1.1,
                  }}
                >
                  {rec.hero}
                </div>

                {rec.roles && rec.roles.length > 0 && (
                  <div
                    style={{
                      display: "flex",
                      gap: "6px",
                      marginBottom: "8px",
                      flexWrap: "wrap",
                    }}
                  >
                    {rec.roles.map((role) => (
                      <span
                        key={role}
                        style={{
                          fontSize: "10px",
                          padding: "3px 7px",
                          borderRadius: "999px",
                          backgroundColor: "#1b2637",
                          border: "1px solid rgba(108, 136, 180, 0.14)",
                          color: "#d4def0",
                          textTransform: "uppercase",
                          letterSpacing: "0.35px",
                          fontWeight: 700,
                        }}
                      >
                        {role}
                      </span>
                    ))}
                  </div>
                )}

                {quickTags.length > 0 && (
                  <div
                    style={{
                      display: "flex",
                      gap: "6px",
                      marginBottom: "8px",
                      flexWrap: "wrap",
                    }}
                  >
                    {quickTags.map((tag) => (
                      <span
                        key={tag}
                        style={{
                          fontSize: "10px",
                          padding: "3px 7px",
                          borderRadius: "999px",
                          backgroundColor: "rgba(61, 114, 220, 0.12)",
                          border: "1px solid rgba(61, 114, 220, 0.18)",
                          color: "#9bc0ff",
                          letterSpacing: "0.3px",
                          fontWeight: 700,
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    flexWrap: "wrap",
                  }}
                >
                  <div
                    style={{
                      fontSize: "13px",
                      color: rec.score >= 2 ? "#7ee787" : "#f2c14e",
                      fontWeight: 700,
                    }}
                  >
                    Score: {formatScore(rec.score)}
                  </div>

                  <span
                    style={{
                      fontSize: "10px",
                      padding: "3px 8px",
                      borderRadius: "999px",
                      fontWeight: 800,
                      letterSpacing: "0.4px",
                      textTransform: "uppercase",
                      backgroundColor:
                        rec.confidence === "high"
                          ? "#17351f"
                          : rec.confidence === "medium"
                          ? "#3a2d12"
                          : "#2a2f38",
                      color:
                        rec.confidence === "high"
                          ? "#7ee787"
                          : rec.confidence === "medium"
                          ? "#f2c14e"
                          : "#b8c0d1",
                      border:
                        rec.confidence === "high"
                          ? "1px solid #275a34"
                          : rec.confidence === "medium"
                          ? "1px solid #6b5420"
                          : "1px solid #404857",
                    }}
                  >
                    {rec.confidence || "low"} confidence
                  </span>
                </div>
              </div>
            </div>

            {(goodReasons.length > 0 || badReasons.length > 0) && (
              <div style={{ display: "grid", gap: "14px" }}>
                {goodReasons.length > 0 && (
                  <div>
                    <div
                      style={{
                        fontSize: "11px",
                        fontWeight: 800,
                        color: "#7ee787",
                        marginBottom: "7px",
                        textTransform: "uppercase",
                        letterSpacing: "0.4px",
                      }}
                    >
                      Good
                    </div>

                    <ul
                      style={{
                        listStyle: "none",
                        margin: 0,
                        padding: 0,
                        display: "grid",
                        gap: "7px",
                      }}
                    >
                      {goodReasons.map((reason, i) => (
                        <li
                          key={`good-${i}`}
                          style={{
                            display: "flex",
                            alignItems: "flex-start",
                            gap: "7px",
                            fontSize: "13px",
                            color: "#dce5f4",
                            lineHeight: 1.45,
                          }}
                        >
                          <span style={{ color: "#4caf50", marginTop: "1px" }}>✔</span>
                          <span>{reason.text}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {badReasons.length > 0 && (
                  <div>
                    <div
                      style={{
                        fontSize: "11px",
                        fontWeight: 800,
                        color: "#ff9898",
                        marginBottom: "7px",
                        textTransform: "uppercase",
                        letterSpacing: "0.4px",
                      }}
                    >
                      Bad
                    </div>

                    <ul
                      style={{
                        listStyle: "none",
                        margin: 0,
                        padding: 0,
                        display: "grid",
                        gap: "7px",
                      }}
                    >
                      {badReasons.map((reason, i) => (
                        <li
                          key={`bad-${i}`}
                          style={{
                            display: "flex",
                            alignItems: "flex-start",
                            gap: "7px",
                            fontSize: "13px",
                            color: "#ffb3b3",
                            lineHeight: 1.45,
                          }}
                        >
                          <span style={{ color: "#ff6b6b", marginTop: "1px" }}>✖</span>
                          <span>{reason.text}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

export default RecommendationList;