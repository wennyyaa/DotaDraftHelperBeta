import axios from "axios";

const BASE_URL = "https://dotadrafthelperbeta.onrender.com";

export async function getHeroes() {
  try {
    const response = await axios.get(`${BASE_URL}/heroes`);
    return response.data;
  } catch (error) {
    console.error("GET /heroes failed:", error);
    throw error;
  }
}

export async function predictDraft(
  allies,
  enemies,
  role,
  occupiedRoles,
  allySlots
) {
  const payload = {
    allies,
    enemies,
    target_role: role,
    occupied_roles: occupiedRoles,
    ally_slots: allySlots,
  };

  try {
    const response = await axios.post(`${BASE_URL}/predict`, payload);
    return response.data;
} catch (error) {
    console.error("POST /predict failed:");
    console.error("message:", error.message);
    console.error("response:", error.response?.data);
    console.error("detail:", JSON.stringify(error.response?.data?.detail, null, 2));
    console.error("status:", error.response?.status);
    console.error("payload sent:", payload);
    throw error;
  }
}