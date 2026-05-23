const search = document.querySelector("#search");
const category = document.querySelector("#category");
const cards = Array.from(document.querySelectorAll(".review-card"));

function normalize(value) {
  return (value || "").toLocaleLowerCase("ko-KR");
}

function applyFilters() {
  const q = normalize(search.value);
  const c = category.value;
  for (const card of cards) {
    const haystack = normalize(`${card.dataset.title} ${card.dataset.tags} ${card.textContent}`);
    const categoryMatch = !c || card.dataset.category === c;
    const searchMatch = !q || haystack.includes(q);
    card.classList.toggle("hidden", !(categoryMatch && searchMatch));
  }
}

search.addEventListener("input", applyFilters);
category.addEventListener("change", applyFilters);
