import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000";

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
  targetRole = null,
  occupiedRoles = []
) {
  const payload = {
    allies,
    enemies,
    target_role: targetRole,
    occupied_roles: occupiedRoles,
  };

  try {
    const response = await axios.post(`${BASE_URL}/predict`, payload);
    return response.data;
  } catch (error) {
    console.error("POST /predict failed:");
    console.error("message:", error.message);
    console.error("response:", error.response?.data);
    console.error("status:", error.response?.status);
    throw error;
  }
}