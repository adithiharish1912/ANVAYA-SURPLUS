document.addEventListener("DOMContentLoaded", () => {
  const deadline = document.querySelector('input[name="safe_until"]');
  if (deadline) {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    deadline.min = now.toISOString().slice(0, 16);
  }

  const impactDonations = document.getElementById("impact-donations");
  const impactKg = document.getElementById("impact-kg");
  const impactCollected = document.getElementById("impact-collected");
  if (impactDonations && impactKg && impactCollected) {
    fetch("/api/impact")
      .then(response => {
        if (!response.ok) throw new Error("Impact request failed");
        return response.json();
      })
      .then(data => {
        impactDonations.textContent = data.approved_donations;
        impactKg.textContent = `${data.approved_food_kg} kg`;
        impactCollected.textContent = `${data.collected_food_kg} kg`;
      })
      .catch(() => {
        impactDonations.textContent = "0";
        impactKg.textContent = "0 kg";
        impactCollected.textContent = "0 kg";
      });
  }
});
