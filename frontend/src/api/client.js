export async function fetchApiRoot() {
  const response = await fetch("/api/v1/");
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json();
}
