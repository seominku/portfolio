const slides = Array.from(document.querySelectorAll(".slide"));
const currentLabel = document.querySelector(".slide-count b");
const totalLabel = document.querySelector(".slide-count");
const progress = document.querySelector(".progress-track span");
const previousButton = document.querySelector(".nav-button.prev");
const nextButton = document.querySelector(".nav-button.next");

let currentIndex = 0;
let navigationLocked = false;

const formatNumber = (number) => String(number).padStart(2, "0");

const updateControls = (index) => {
  currentIndex = Math.max(0, Math.min(index, slides.length - 1));
  currentLabel.textContent = formatNumber(currentIndex + 1);
  totalLabel.lastChild.textContent = ` / ${formatNumber(slides.length)}`;
  progress.style.width = `${((currentIndex + 1) / slides.length) * 100}%`;
  previousButton.disabled = currentIndex === 0;
  nextButton.disabled = currentIndex === slides.length - 1;
  document.title = `${slides[currentIndex].dataset.title} | 구민서 Portfolio`;
};

const goToSlide = (index) => {
  const nextIndex = Math.max(0, Math.min(index, slides.length - 1));
  if (nextIndex === currentIndex && navigationLocked) return;

  navigationLocked = true;
  slides[nextIndex].scrollIntoView({ behavior: "smooth", block: "start" });
  updateControls(nextIndex);
  window.setTimeout(() => {
    navigationLocked = false;
  }, 600);
};

previousButton.addEventListener("click", () => goToSlide(currentIndex - 1));
nextButton.addEventListener("click", () => goToSlide(currentIndex + 1));

document.addEventListener("keydown", (event) => {
  const target = event.target;
  if (document.querySelector(".competition-dialog[open]")) return;
  if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) return;

  if (["ArrowDown", "PageDown", " "].includes(event.key)) {
    event.preventDefault();
    goToSlide(currentIndex + 1);
  }

  if (["ArrowUp", "PageUp"].includes(event.key)) {
    event.preventDefault();
    goToSlide(currentIndex - 1);
  }

  if (event.key === "Home") {
    event.preventDefault();
    goToSlide(0);
  }

  if (event.key === "End") {
    event.preventDefault();
    goToSlide(slides.length - 1);
  }
});

const slideObserver = new IntersectionObserver(
  (entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

    if (!visible || navigationLocked) return;
    updateControls(slides.indexOf(visible.target));
  },
  { threshold: [0.35, 0.55, 0.75] },
);

slides.forEach((slide) => slideObserver.observe(slide));

const revealObserver = new IntersectionObserver(
  (entries, observer) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("visible");
      observer.unobserve(entry.target);
    });
  },
  { threshold: 0.14 },

);
const dialogTriggers = document.querySelectorAll("[data-dialog]");
let activeDialogTrigger = null;
let lockedScrollY = 0;

const lockPageScroll = () => {
  lockedScrollY = window.scrollY;
  document.documentElement.classList.add("dialog-open");
  document.body.classList.add("dialog-open");
  document.body.style.top = `-${lockedScrollY}px`;
};

const unlockPageScroll = () => {
  const root = document.documentElement;
  const previousScrollBehavior = root.style.scrollBehavior;

  root.classList.remove("dialog-open");
  document.body.classList.remove("dialog-open");
  document.body.style.top = "";
  root.style.scrollBehavior = "auto";
  window.scrollTo(0, lockedScrollY);
  root.style.scrollBehavior = previousScrollBehavior;
};

const openCompetitionDialog = (trigger) => {
  const dialog = document.getElementById(trigger.dataset.dialog);
  if (!(dialog instanceof HTMLDialogElement)) return;
  if (dialog.open) return;
  activeDialogTrigger = trigger;
  dialog.showModal();
  lockPageScroll();
  document.dispatchEvent(new Event("carousel:pause-all"));
  dialog.querySelector(".dialog-close")?.focus();
};

dialogTriggers.forEach((trigger) => {
  trigger.addEventListener("click", (event) => {
    event.preventDefault();
    openCompetitionDialog(trigger);
  });
  trigger.addEventListener("keydown", (event) => {
    if (trigger instanceof HTMLAnchorElement) return;
    if (!["Enter", " "].includes(event.key)) return;
    event.preventDefault();
    openCompetitionDialog(trigger);
  });
});

document.querySelectorAll(".competition-dialog").forEach((dialog) => {
  dialog.querySelector(".dialog-close")?.addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener("close", () => {
    unlockPageScroll();
    document.dispatchEvent(new Event("carousel:resume-all"));
    activeDialogTrigger?.focus();
    activeDialogTrigger = null;
  });
});
document.querySelectorAll("[data-carousel]").forEach((carousel) => {
  const carouselSlides = Array.from(carousel.querySelectorAll(".carousel-track img"));
  const indicators = Array.from(carousel.querySelectorAll(".carousel-indicators i"));
  const previousArrow = carousel.querySelector(".carousel-arrow-prev");
  const nextArrow = carousel.querySelector(".carousel-arrow-next");
  const interval = Number(carousel.dataset.carouselInterval) || 4000;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let carouselIndex = 0;
  let timer = null;
  let remaining = interval;
  let startedAt = 0;

  carousel.style.setProperty("--carousel-duration", interval + "ms");

  const showSlide = (nextIndex) => {
    carouselIndex = (nextIndex + carouselSlides.length) % carouselSlides.length;
    carousel.style.setProperty("--carousel-index", carouselIndex);
    indicators.forEach((indicator, index) => {
      indicator.classList.toggle("is-active", index === carouselIndex);
    });
  };

  const resetProgress = () => {
    carousel.classList.remove("is-playing", "is-paused");
    void carousel.offsetWidth;
    if (!reduceMotion) carousel.classList.add("is-playing");
  };

  const stopCarousel = () => {
    if (timer === null) return;
    remaining = Math.max(0, remaining - (performance.now() - startedAt));
    window.clearTimeout(timer);
    timer = null;
    carousel.classList.add("is-paused");
  };

  const startCarousel = () => {
    const interactionPaused = carousel.matches(":hover") || carousel.matches(":focus-within");
    const dialogOpen = document.querySelector(".competition-dialog[open]");
    if (reduceMotion || carouselSlides.length < 2 || timer !== null) return;
    if (interactionPaused || dialogOpen) {
      carousel.classList.add("is-paused");
      return;
    }

    startedAt = performance.now();
    carousel.classList.remove("is-paused");
    timer = window.setTimeout(() => {
      timer = null;
      remaining = interval;
      showSlide(carouselIndex + 1);
      resetProgress();
      startCarousel();
    }, remaining);
  };
  const changeSlide = (offset) => {
    stopCarousel();
    remaining = interval;
    showSlide(carouselIndex + offset);
    resetProgress();
    startCarousel();
  };


  carousel.addEventListener("pointerenter", stopCarousel);
  carousel.addEventListener("pointerleave", startCarousel);
  carousel.addEventListener("focusin", stopCarousel);
  carousel.addEventListener("focusout", () => window.setTimeout(startCarousel, 0));
  previousArrow?.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    changeSlide(-1);
  });
  nextArrow?.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    changeSlide(1);
  });

  document.addEventListener("carousel:pause-all", stopCarousel);
  document.addEventListener("carousel:resume-all", startCarousel);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stopCarousel();
    else startCarousel();
  });

  showSlide(0);
  resetProgress();
  startCarousel();
});
document.querySelectorAll(".reveal").forEach((element) => revealObserver.observe(element));

const initialSlide = window.location.hash
  ? document.querySelector(window.location.hash)
  : null;

if (initialSlide instanceof HTMLElement && initialSlide.classList.contains("slide")) {
  initialSlide.querySelectorAll(".reveal").forEach((element) => element.classList.add("visible"));
  initialSlide.scrollIntoView({ behavior: "auto", block: "start" });
  updateControls(slides.indexOf(initialSlide));
} else {
  updateControls(0);
}
