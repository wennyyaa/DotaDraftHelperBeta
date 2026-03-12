import React, { useEffect, useMemo, useRef, useState } from "react";
import HeroPills from "./HeroPills";

function parseHeroes(raw) {
  return raw
    .split(",")
    .map((name) => name.trim())
    .filter(Boolean);
}

function buildTextWithSelectedHero(raw, heroName) {
  const parts = raw.split(",");
  const completedParts = parts
    .slice(0, -1)
    .map((part) => part.trim())
    .filter(Boolean);

  if (completedParts.includes(heroName)) {
    return completedParts.join(", ") + (completedParts.length ? ", " : "");
  }

  return [...completedParts, heroName].join(", ") + ", ";
}

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

const heroAliases = {
  aa: ["Ancient Apparition"],
  am: ["Anti-Mage"],
  bb: ["Bristleback"],
  bh: ["Bounty Hunter"],
  bm: ["Beastmaster"],
  bs: ["Bloodseeker"],
  ck: ["Chaos Knight"],
  cm: ["Crystal Maiden"],
  cw: ["Centaur Warrunner"],
  ds: ["Dark Seer"],
  dp: ["Death Prophet"],
  dw: ["Dark Willow"],
  es: ["Earth Spirit", "Earthshaker"],
  et: ["Elder Titan"],
  fv: ["Faceless Void"],
  gyro: ["Gyrocopter"],
  kotl: ["Keeper of the Light"],
  lc: ["Legion Commander"],
  ld: ["Lone Druid"],
  ls: ["Lifestealer"],
  mag: ["Magnus"],
  mk: ["Monkey King"],
  morph: ["Morphling"],
  necro: ["Necrophos"],
  np: ["Nature's Prophet"],
  ns: ["Night Stalker"],
  od: ["Outworld Devourer"],
  omni: ["Omniknight"],
  pa: ["Phantom Assassin"],
  pl: ["Phantom Lancer"],
  pango: ["Pangolier"],
  pugna: ["Pugna"],
  qop: ["Queen of Pain"],
  sd: ["Shadow Demon"],
  sf: ["Shadow Fiend"],
  shaman: ["Shadow Shaman"],
  sk: ["Sand King"],
  spec: ["Spectre"],
  ss: ["Storm Spirit", "Shadow Shaman"],
  sb: ["Spirit Breaker"],
  tb: ["Terrorblade"],
  timber: ["Timbersaw"],
  ta: ["Templar Assassin"],
  tide: ["Tidehunter"],
  underlord: ["Underlord"],
  vs: ["Vengeful Spirit", "Void Spirit"],
  veno: ["Venomancer"],
  wk: ["Wraith King"],
  ww: ["Winter Wyvern"],
  wv: ["Winter Wyvern"],
  wr: ["Windranger"],
  shaker: ["Earthshaker"],
  wyvern: ["Winter Wyvern"],
};

function HeroInput({
  label,
  text,
  onTextChange,
  onHeroesChange,
  placeholder,
  allHeroes = [],
  excludedHeroes = [],
}) {
  const [activeIndex, setActiveIndex] = useState(-1);
  const inputRef = useRef(null);

  const currentHeroes = useMemo(() => parseHeroes(text), [text]);

  const suggestions = useMemo(() => {
    const parts = text.split(",");
    const currentToken = parts[parts.length - 1].trim().toLowerCase();

    if (!currentToken) {
      return [];
    }

    const aliasMatches = heroAliases[currentToken] || [];

    return allHeroes
      .filter((hero) => typeof hero === "string")
      .filter((hero) => {
        const heroName = hero.toLowerCase();

        if (heroName.includes(currentToken)) {
          return true;
        }

        return aliasMatches.includes(hero);
      })
      .filter((hero) => !currentHeroes.includes(hero))
      .filter((hero) => !excludedHeroes.includes(hero))
      .slice(0, 8);
  }, [text, allHeroes, currentHeroes, excludedHeroes]);

  useEffect(() => {
    if (suggestions.length === 0) {
      setActiveIndex(-1);
    } else {
      setActiveIndex(0);
    }
  }, [suggestions]);

  function updateText(raw) {
    onTextChange(raw);
    onHeroesChange(parseHeroes(raw));
  }

  function handleChange(e) {
    updateText(e.target.value);
  }

  function handleSuggestionClick(heroName) {
    const newText = buildTextWithSelectedHero(text, heroName);
    updateText(newText);
    setActiveIndex(-1);

    requestAnimationFrame(() => {
      inputRef.current?.focus();
    });
  }

  function handleRemoveHero(heroToRemove) {
    const updatedHeroes = currentHeroes.filter((hero) => hero !== heroToRemove);
    const newText = updatedHeroes.length > 0 ? `${updatedHeroes.join(", ")}, ` : "";

    updateText(newText);

    requestAnimationFrame(() => {
      inputRef.current?.focus();
    });
  }

  function handleKeyDown(e) {
    if (e.key === "Escape") {
      setActiveIndex(-1);
      return;
    }

    if (suggestions.length === 0) {
      return;
    }

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
      return;
    }

    if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
      return;
    }

    if (e.key === "Enter" || e.key === "Tab") {
      e.preventDefault();

      const indexToUse = activeIndex >= 0 ? activeIndex : 0;

      if (suggestions[indexToUse]) {
        handleSuggestionClick(suggestions[indexToUse]);
      }
    }
  }

  return (
    <section
      style={{
        position: "relative",
        backgroundColor: "rgba(255,255,255,0.02)",
        border: "1px solid rgba(255,255,255,0.06)",
        borderRadius: "18px",
        padding: "18px",
      }}
    >
      <label
        style={{
          display: "block",
          marginBottom: "10px",
          fontSize: "13px",
          fontWeight: 700,
          color: "#dce6f5",
          letterSpacing: "0.2px",
        }}
      >
        {label}
      </label>

      <input
        ref={inputRef}
        type="text"
        value={text}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        style={{
          width: "100%",
          padding: "13px 14px",
          borderRadius: "12px",
          border: "1px solid rgba(110, 138, 180, 0.18)",
          backgroundColor: "#0f141d",
          color: "#f5f7fb",
          fontSize: "14px",
          boxSizing: "border-box",
          outline: "none",
        }}
      />

      {suggestions.length > 0 && (
        <div
          style={{
            position: "absolute",
            top: "calc(100% - 8px)",
            left: "18px",
            right: "18px",
            marginTop: "10px",
            border: "1px solid rgba(110, 138, 180, 0.18)",
            borderRadius: "12px",
            backgroundColor: "#101720",
            overflow: "hidden",
            zIndex: 30,
            boxShadow: "0 16px 32px rgba(0, 0, 0, 0.38)",
          }}
        >
          {suggestions.map((hero, index) => {
            const isActive = index === activeIndex;

            return (
              <button
                key={hero}
                type="button"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => handleSuggestionClick(hero)}
                onMouseEnter={() => setActiveIndex(index)}
                style={{
                  width: "100%",
                  textAlign: "left",
                  padding: "10px 12px",
                  backgroundColor: isActive ? "#213148" : "transparent",
                  color: "#f5f5f5",
                  border: "none",
                  borderBottom:
                    index !== suggestions.length - 1
                      ? "1px solid rgba(255,255,255,0.05)"
                      : "none",
                  cursor: "pointer",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                  }}
                >
                  <img
                    src={`https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/${heroToIconName(
                      hero
                    )}.png`}
                    alt={hero}
                    width={34}
                    height={20}
                    style={{
                      borderRadius: "5px",
                      objectFit: "cover",
                      flexShrink: 0,
                    }}
                    onError={(e) => {
                      e.currentTarget.style.opacity = "0.35";
                    }}
                  />
                  <span style={{ fontSize: "14px" }}>{hero}</span>
                </div>
              </button>
            );
          })}
        </div>
      )}

      <HeroPills heroes={currentHeroes} onRemove={handleRemoveHero} />

      <div
        style={{
          marginTop: "10px",
          fontSize: "12px",
          color: "#8ea0b8",
        }}
      >
        Use ↑ ↓, Enter or Tab to select heroes quickly.
      </div>
    </section>
  );
}

export default HeroInput;