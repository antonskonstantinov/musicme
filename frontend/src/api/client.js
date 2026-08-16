import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api/v1",
});

apiClient.interceptors.response.use(
  (response) => {
    const payload = response.data;
    if (payload && typeof payload === "object" && "data" in payload) {
      return payload.data;
    }
    return payload;
  },
  (error) => {
    const apiMessage = error.response?.data?.error?.message;
    const message =
      apiMessage ||
      (!error.response ? "Не удалось загрузить данные" : error.message);
    console.error(message);
    return Promise.reject(new Error(message));
  },
);

export default apiClient;
