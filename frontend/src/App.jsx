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

  async function handlePredict() {
    setError("");
    setLoading(true);
    setRecommendations([]);

    try {
      const data = await predictDraft(allyHeroes, enemyHeroes);
      setRecommendations(data.recommended || []);
    } catch (err) {
      console.error("Predict failed:", err);
      setError(err.message || "Failed to fetch predictions.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top, #182233 0%, #0c1017 45%, #080b10 100%)",
        color: "#f4f7fb",
        fontFamily: "Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif",
        padding: "32px 20px 48px",
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
        }}      >
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
                Dota 2 AI Draft Assistant
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
                Build both drafts, explore recommendations, and see why each hero
                fits your current composition.
              </p>
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
                <div style={{ fontSize: "11px", color: "#7f90a8", marginBottom: "4px" }}>
                  MODE
                </div>    
                <div style={{ fontSize: "14px", fontWeight: 700 }}>Rule-Based Assistant</div>
              </div>

              <div
                style={{
                  backgroundColor: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: "16px",
                  padding: "12px 14px",
                }}
              >
                <div style={{ fontSize: "11px", color: "#7f90a8", marginBottom: "4px" }}>
                  OUTPUT
                </div>
                <div style={{ fontSize: "14px", fontWeight: 700 }}>Top Recommendations</div>
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
              <div style={{ fontSize: "11px", color: "#7f90a8", marginBottom: "6px" }}>
                ALLIES PICKED
              </div>
              <div style={{ fontSize: "22px", fontWeight: 800 }}>{allyHeroes.length}</div>
            </div>

            <div
              style={{
                backgroundColor: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: "16px",
                padding: "14px",
              }}
            >
              <div style={{ fontSize: "11px", color: "#7f90a8", marginBottom: "6px" }}>
                ENEMIES PICKED
              </div>
              <div style={{ fontSize: "22px", fontWeight: 800 }}>{enemyHeroes.length}</div>
            </div>

            <div
              style={{
                backgroundColor: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: "16px",
                padding: "14px",
              }}
            >
              <div style={{ fontSize: "11px", color: "#7f90a8", marginBottom: "6px" }}>
                RECOMMENDATIONS
              </div>
              <div style={{ fontSize: "22px", fontWeight: 800 }}>{recommendations.length}</div>
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
              display: "flex",
              alignItems: "center",
              gap: "14px",
              flexWrap: "wrap",
              marginTop: "22px",
            }}
          >
            <button
              onClick={handlePredict}
              disabled={loading}
              onMouseEnter={(e) => {
                if (!loading) {
                  e.currentTarget.style.transform = "translateY(-1px)";
                  e.currentTarget.style.boxShadow =
                    "0 14px 28px rgba(20, 103, 255, 0.34)";
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow =
                  "0 10px 24px rgba(20, 103, 255, 0.28)";
              }}
              style={{
                padding: "13px 22px",
                minWidth: "180px",
                background: loading
                  ? "linear-gradient(135deg, #2d5ba8 0%, #1f4d93 100%)"
                  : "linear-gradient(135deg, #2ba1ff 0%, #1467ff 100%)",
                color: "#fff",
                border: "none",
                borderRadius: "12px",
                cursor: loading ? "default" : "pointer",
                fontSize: "14px",
                fontWeight: 700,
                boxShadow: "0 10px 24px rgba(20, 103, 255, 0.28)",
                transition: "transform 0.15s ease, box-shadow 0.15s ease",
              }}
            >
              {loading ? "Predicting..." : "Analyze Draft"}
            </button>

            <div style={{ fontSize: "13px", color: "#8fa0b8" }}>
              Uses handcrafted draft logic and team composition analysis.
            </div>
          </div>

          {error && (
            <div
              style={{
                marginTop: "14px",
                color: "#ff9d9d",
                fontSize: "14px",
                backgroundColor: "rgba(255, 88, 88, 0.08)",
                border: "1px solid rgba(255, 88, 88, 0.18)",
                borderRadius: "12px",
                padding: "12px 14px",
              }}
            >
              {error}
            </div>
          )}
        </section>

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
                <div style={{ fontSize: "11px", color: "#7f90a8", marginBottom: "4px" }}>
                  RESULTS
                </div>
                <div style={{ fontSize: "18px", fontWeight: 800 }}>{recommendations.length}</div>
              </div>

              <div
                style={{
                  backgroundColor: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: "14px",
                  padding: "12px",
                }}
              >
                <div style={{ fontSize: "11px", color: "#7f90a8", marginBottom: "4px" }}>
                  ALLIES
                </div>
                <div style={{ fontSize: "18px", fontWeight: 800 }}>{allyHeroes.length}</div>
              </div>

              <div
                style={{
                  backgroundColor: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.06)",
                  borderRadius: "14px",
                  padding: "12px",
                }}
              >
                <div style={{ fontSize: "11px", color: "#7f90a8", marginBottom: "4px" }}>
                  ENEMIES
                </div>
                <div style={{ fontSize: "18px", fontWeight: 800 }}>{enemyHeroes.length}</div>
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
              <div style={{ fontSize: "16px", fontWeight: 700, color: "#d8e2f1" }}>
                No recommendations yet
              </div>
              <div>
                Build both drafts and click <strong>Analyze Draft</strong> to see the best hero suggestions.
              </div>
            </div>
          ) : (
            <RecommendationList recommendations={recommendations} />
          )}
        </section>
      </div>
    </div>
  );
}

export default App;