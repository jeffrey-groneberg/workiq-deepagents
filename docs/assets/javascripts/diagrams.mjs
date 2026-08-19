import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";

let diagramId = 0;
let renderedScheme;
let renderQueue = Promise.resolve();

const themeVariables = {
  default: {
    background: "#fffdf7",
    primaryColor: "#d9eee9",
    primaryTextColor: "#18211f",
    primaryBorderColor: "#087d72",
    secondaryColor: "#f5ded8",
    tertiaryColor: "#f2e7bd",
    lineColor: "#53615d",
    textColor: "#18211f",
  },
  slate: {
    background: "#1a2220",
    primaryColor: "#193c38",
    primaryTextColor: "#edf1e9",
    primaryBorderColor: "#57cabb",
    secondaryColor: "#482723",
    tertiaryColor: "#413619",
    lineColor: "#b4c0ba",
    textColor: "#edf1e9",
  },
};

function currentScheme() {
  return document.body.dataset.mdColorScheme === "slate" ? "slate" : "default";
}

function initialize(scheme) {
  mermaid.initialize({
    startOnLoad: false,
    securityLevel: "strict",
    theme: "base",
    themeVariables: themeVariables[scheme],
    sequence: {
      actorFontSize: 15,
      messageFontSize: 14,
      noteFontSize: 14,
    },
  });
  renderedScheme = scheme;
}

function accessibleLabel(source) {
  if (source.startsWith("sequenceDiagram")) return "Sequence diagram";
  if (source.startsWith("stateDiagram")) return "State diagram";
  return "Architecture flowchart";
}

async function renderDiagrams() {
  const sources = [...document.querySelectorAll("pre.workiq-diagram-source")];
  if (!sources.length) return;

  const scheme = currentScheme();
  if (renderedScheme !== scheme) initialize(scheme);

  for (const sourceElement of sources) {
    const source = sourceElement.textContent.trim();
    try {
      const result = await mermaid.render(`workiq-diagram-${diagramId++}`, source);
      const container = document.createElement("div");
      container.className = "workiq-diagram";
      container.dataset.source = source;
      container.setAttribute("role", "img");
      container.setAttribute("aria-label", accessibleLabel(source));
      container.innerHTML = result.svg;
      result.bindFunctions?.(container);
      sourceElement.replaceWith(container);
    } catch (error) {
      sourceElement.dataset.renderError = "true";
      console.error("Unable to render WorkIQ diagram", error);
    }
  }
}

function resetDiagrams() {
  for (const diagram of document.querySelectorAll(".workiq-diagram[data-source]")) {
    const sourceElement = document.createElement("pre");
    sourceElement.className = "workiq-diagram-source";
    const code = document.createElement("code");
    code.textContent = diagram.dataset.source;
    sourceElement.append(code);
    diagram.replaceWith(sourceElement);
  }
}

async function renderForCurrentScheme() {
  const scheme = currentScheme();
  if (renderedScheme && renderedScheme !== scheme) resetDiagrams();
  await renderDiagrams();
}

function scheduleRender() {
  renderQueue = renderQueue.then(renderForCurrentScheme).catch((error) => {
    console.error("Unable to update WorkIQ diagrams", error);
  });
}

if (globalThis.document$) {
  globalThis.document$.subscribe(scheduleRender);
} else {
  scheduleRender();
}

new MutationObserver(scheduleRender).observe(document.body, {
  attributes: true,
  attributeFilter: ["data-md-color-scheme"],
});