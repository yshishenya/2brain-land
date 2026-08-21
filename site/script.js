(() => {
  const body = document.body;
  const header = document.querySelector("[data-header]");
  const menuToggle = document.querySelector(".menu-toggle");
  const menuLabel = menuToggle?.querySelector(".sr-only");
  const navigation = document.querySelector("#site-nav");

  const closeMenu = () => {
    body.classList.remove("menu-open");
    menuToggle?.setAttribute("aria-expanded", "false");
    if (menuLabel) menuLabel.textContent = "Открыть меню";
  };

  menuToggle?.addEventListener("click", () => {
    const isOpen = body.classList.toggle("menu-open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
    if (menuLabel) menuLabel.textContent = isOpen ? "Закрыть меню" : "Открыть меню";
  });

  navigation?.addEventListener("click", (event) => {
    if (event.target.closest("a")) closeMenu();
  });

  const updateHeader = () => header?.classList.toggle("is-scrolled", window.scrollY > 16);
  updateHeader();
  window.addEventListener("scroll", updateHeader, { passive: true });
  window.addEventListener("resize", () => {
    if (window.innerWidth > 900) closeMenu();
  });

  const revealElements = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window) {
    const revealObserver = new IntersectionObserver(
      (entries, observer) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -7%", threshold: 0.06 }
    );
    revealElements.forEach((element) => revealObserver.observe(element));
  } else {
    revealElements.forEach((element) => element.classList.add("is-visible"));
  }

  const phases = [...document.querySelectorAll("[data-phase]")];
  phases.forEach((phase) => {
    const button = phase.querySelector(".phase-head");
    const indicator = button?.querySelector("i");
    button?.addEventListener("click", () => {
      const willOpen = !phase.classList.contains("is-active");
      phases.forEach((otherPhase) => {
        otherPhase.classList.remove("is-active");
        otherPhase.querySelector(".phase-head")?.setAttribute("aria-expanded", "false");
        const otherIndicator = otherPhase.querySelector(".phase-head i");
        if (otherIndicator) otherIndicator.textContent = "+";
      });
      if (willOpen) {
        phase.classList.add("is-active");
        button.setAttribute("aria-expanded", "true");
        if (indicator) indicator.textContent = "−";
      }
    });
  });

  const cases = document.querySelectorAll("[data-case]");
  cases.forEach((caseItem) => {
    caseItem.addEventListener("toggle", () => {
      if (!caseItem.open) return;
      cases.forEach((otherCase) => {
        if (otherCase !== caseItem) otherCase.open = false;
      });
    });
  });

  const dialog = document.querySelector("[data-diagnostic-dialog]");
  const dialogClose = dialog?.querySelector("[data-close-diagnostic]");

  const openDialog = () => {
    closeMenu();
    if (!dialog) return;
    body.classList.add("dialog-open");
    dialog.showModal();
    window.setTimeout(() => dialogClose?.focus(), 40);
  };
  const closeDialog = () => {
    if (!dialog) return;
    dialog.close();
    body.classList.remove("dialog-open");
  };

  document.querySelectorAll("[data-open-diagnostic]").forEach((button) => button.addEventListener("click", openDialog));
  dialogClose?.addEventListener("click", closeDialog);
  dialog?.addEventListener("click", (event) => {
    if (event.target === dialog) closeDialog();
  });
  dialog?.addEventListener("close", () => {
    body.classList.remove("dialog-open");
  });

  const productData = {
    airis: {
      title: "AIRIS",
      description: "AIRIS даёт команде единый управляемый доступ к ведущим ИИ-моделям и позволяет выбирать подходящую модель для каждой рабочей задачи.",
      points: [
        "Актуальные модели в одном интерфейсе",
        "Работа с текстом, документами, изображениями и аудио",
        "Централизованный доступ и управление командой"
      ],
      linkLabel: "Открыть AIRIS",
      url: "https://airis.you/"
    },
    graf: {
      title: "ГРАФ",
      description: "ГРАФ записывает и транскрибирует звонки независимо от сервиса, в котором они проходят, и превращает разговор в готовые материалы для работы.",
      points: [
        "Запись без привязки к системе звонка",
        "Транскрибация с разделением по спикерам",
        "Протокол, решения и следующие действия"
      ],
      linkLabel: "Посмотреть ГРАФ",
      url: "https://rec.2brain.pro/"
    },
    astra: {
      title: "Астра",
      description: "Астра связывает опыт, компетенции и интересы сотрудника с карьерными возможностями внутри компании и формирует индивидуальный план развития.",
      points: [
        "Профиль сильных сторон, интересов и компетенций",
        "Реалистичные внутренние карьерные маршруты",
        "Снижение текучести и рост вовлечённости"
      ],
      linkLabel: "Посмотреть Астру",
      url: "https://ykai.tilda.ws/astra"
    },
    tutor: {
      title: "Tutor",
      description: "Tutor собирает программу под цель и стартовый уровень человека, даёт практику на реальных задачах и сопровождает обучение с помощью ИИ-ментора.",
      points: [
        "Диагностика стартового уровня",
        "Практика, адаптированная под цель",
        "Персональный план и обратная связь"
      ],
      linkLabel: "Посмотреть Tutor",
      url: "https://tutor.2brain.pro/"
    }
  };

  const productDialog = document.querySelector("[data-product-dialog]");
  const productDialogClose = productDialog?.querySelector("[data-close-product]");
  const productTitle = productDialog?.querySelector("[data-product-title]");
  const productDescription = productDialog?.querySelector("[data-product-description]");
  const productPoints = productDialog?.querySelector("[data-product-points]");
  const productLink = productDialog?.querySelector("[data-product-link]");
  const productLinkLabel = productDialog?.querySelector("[data-product-link-label]");
  const productCount = productDialog?.querySelector("[data-product-count]");
  const productPrev = productDialog?.querySelector("[data-product-prev]");
  const productNext = productDialog?.querySelector("[data-product-next]");
  const productOrder = ["airis", "graf", "astra", "tutor"];
  let lastProductTrigger = null;
  let currentProductKey = productOrder[0];

  const updateProductDialog = (productKey) => {
    const product = productData[productKey];
    if (!productDialog || !product) return;
    currentProductKey = productKey;
    if (productTitle) productTitle.textContent = product.title;
    if (productDescription) productDescription.textContent = product.description;
    if (productLink) productLink.href = product.url;
    if (productLinkLabel) productLinkLabel.textContent = product.linkLabel;
    if (productPoints) {
      const items = product.points.map((point) => {
        const item = document.createElement("li");
        item.textContent = point;
        return item;
      });
      productPoints.replaceChildren(...items);
    }
    productDialog.querySelectorAll("[data-product-visual]").forEach((visual) => {
      visual.classList.toggle("is-active", visual.dataset.productVisual === productKey);
    });
    const currentIndex = productOrder.indexOf(productKey);
    const previousKey = productOrder[(currentIndex - 1 + productOrder.length) % productOrder.length];
    const nextKey = productOrder[(currentIndex + 1) % productOrder.length];
    if (productCount) productCount.textContent = `${String(currentIndex + 1).padStart(2, "0")} / ${String(productOrder.length).padStart(2, "0")}`;
    if (productPrev) productPrev.setAttribute("aria-label", `Предыдущий продукт: ${productData[previousKey].title}`);
    if (productNext) productNext.setAttribute("aria-label", `Следующий продукт: ${productData[nextKey].title}`);
  };

  const switchProduct = (direction) => {
    const currentIndex = productOrder.indexOf(currentProductKey);
    const nextIndex = (currentIndex + direction + productOrder.length) % productOrder.length;
    updateProductDialog(productOrder[nextIndex]);
  };

  const openProductDialog = (productKey, trigger) => {
    if (!productDialog || !productData[productKey]) return;
    closeMenu();
    lastProductTrigger = trigger;
    updateProductDialog(productKey);
    body.classList.add("dialog-open");
    productDialog.showModal();
    window.setTimeout(() => productDialogClose?.focus(), 40);
  };

  document.querySelectorAll("[data-open-product]").forEach((trigger) => {
    trigger.addEventListener("click", () => openProductDialog(trigger.dataset.openProduct, trigger));
  });
  productPrev?.addEventListener("click", () => switchProduct(-1));
  productNext?.addEventListener("click", () => switchProduct(1));
  productDialogClose?.addEventListener("click", () => productDialog?.close());
  productDialog?.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      switchProduct(-1);
    }
    if (event.key === "ArrowRight") {
      event.preventDefault();
      switchProduct(1);
    }
  });
  productDialog?.addEventListener("click", (event) => {
    if (event.target === productDialog) productDialog.close();
  });
  productDialog?.addEventListener("close", () => {
    body.classList.remove("dialog-open");
    lastProductTrigger?.focus({ preventScroll: true });
  });

  const navLinks = [...document.querySelectorAll('.site-nav a[href^="#"]')];
  const sections = navLinks.map((link) => document.querySelector(link.getAttribute("href"))).filter(Boolean);
  if ("IntersectionObserver" in window && sections.length) {
    const sectionObserver = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (!visible.length) return;
        navLinks.forEach((link) => link.classList.toggle("is-active", link.getAttribute("href") === `#${visible[0].target.id}`));
      },
      { rootMargin: "-28% 0px -60%", threshold: [0, 0.2, 0.5] }
    );
    sections.forEach((section) => sectionObserver.observe(section));
  }

  document.querySelectorAll("[data-year]").forEach((element) => {
    element.textContent = String(new Date().getFullYear());
  });
})();
