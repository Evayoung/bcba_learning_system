(() => {
  "use strict";

  function showBusyState(element, label) {
    if (!element || element.dataset.loading === "true") return;

    element.dataset.loading = "true";
    element.setAttribute("aria-busy", "true");

    if ("disabled" in element) {
      element.disabled = true;
    } else {
      element.setAttribute("aria-disabled", "true");
      element.classList.add("app-loading-link");
    }

    const spinner = document.createElement("span");
    spinner.className = "spinner-border spinner-border-sm app-action-spinner";
    spinner.setAttribute("aria-hidden", "true");
    element.replaceChildren(spinner, document.createTextNode(label));
  }

  document.addEventListener("submit", (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;

    if (form.dataset.submitting === "true") {
      event.preventDefault();
      return;
    }

    const submitter = event.submitter;
    const label =
      submitter?.dataset.loadingText || form.dataset.loadingText;
    if (!label || !submitter) return;

    form.dataset.submitting = "true";

    // Disabled submit buttons are omitted from the submitted form data. Preserve
    // named controls such as the tutor-mode and mock-exam action buttons.
    if (submitter.name) {
      const hidden = document.createElement("input");
      hidden.type = "hidden";
      hidden.name = submitter.name;
      hidden.value = submitter.value;
      form.append(hidden);
    }

    showBusyState(submitter, label);
  });

  document.addEventListener(
    "click",
    (event) => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;

      const target = event.target;
      if (!(target instanceof Element)) return;

      const link = target.closest("a[data-loading-text]");
      if (!link || link.target === "_blank") return;

      const destination = new URL(link.href, window.location.href);
      if (destination.origin !== window.location.origin) return;

      const control = link.querySelector("button") || link;
      showBusyState(control, link.dataset.loadingText);
    },
    true,
  );
})();
