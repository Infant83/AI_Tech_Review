const search = document.querySelector("#search");
const category = document.querySelector("#category");
const reviewGrid = document.querySelector("#review-grid");
const topicFilter = document.querySelector("#topic-filter");
const cards = Array.from(document.querySelectorAll(".review-card"));
const categoryTriggers = Array.from(document.querySelectorAll("[data-category-filter]"));

function normalize(value) {
  return (value || "").toLocaleLowerCase("ko-KR");
}

function updateCategoryTriggers(value) {
  for (const trigger of categoryTriggers) {
    trigger.classList.toggle("active", trigger.dataset.categoryFilter === value);
  }
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
  updateCategoryTriggers(c);
}

function setCategory(value, scrollTarget) {
  category.value = value;
  applyFilters();
  if (scrollTarget) {
    scrollTarget.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

search.addEventListener("input", applyFilters);
category.addEventListener("change", applyFilters);
for (const trigger of categoryTriggers) {
  trigger.addEventListener("click", (event) => {
    event.preventDefault();
    const value = trigger.dataset.categoryFilter || "";
    setCategory(value, value ? reviewGrid : reviewGrid);
  });
}
document.querySelector('a[href="#topic-filter"]')?.addEventListener("click", (event) => {
  event.preventDefault();
  topicFilter.scrollIntoView({ behavior: "smooth", block: "start" });
});
