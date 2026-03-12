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

function HeroPills({ heroes = [], onRemove }) {
  if (!heroes.length) {
    return null;
  }

  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: "8px",
        marginTop: "12px",
      }}
    >
      {heroes.map((hero) => (
        <button
          key={hero}
          type="button"
          onClick={() => onRemove(hero)}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "8px",
            padding: "7px 10px 7px 7px",
            borderRadius: "999px",
            border: "1px solid rgba(98, 130, 174, 0.24)",
            backgroundColor: "#172131",
            color: "#e5edf9",
            fontSize: "12px",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          <img
            src={`https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes/${heroToIconName(
              hero
            )}.png`}
            alt={hero}
            width={26}
            height={15}
            style={{
              borderRadius: "4px",
              objectFit: "cover",
              flexShrink: 0,
              backgroundColor: "#0f1115",
            }}
            onError={(e) => {
              e.currentTarget.style.opacity = "0.35";
            }}
          />
          <span>{hero}</span>
          <span style={{ color: "#9db8ea", fontWeight: 700 }}>×</span>
        </button>
      ))}
    </div>
  );
}

export default HeroPills;