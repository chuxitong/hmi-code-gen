/// <reference types="@figma/plugin-typings" />

figma.showUI(__html__, { width: 480, height: 700 });

type ExportableNode = FrameNode | ComponentNode | InstanceNode;

function getSelectedFrame(): ExportableNode | null {
  const selection = figma.currentPage.selection;
  if (selection.length === 0) return null;
  const node = selection[0];
  if (node.type !== "FRAME" && node.type !== "COMPONENT" && node.type !== "INSTANCE") {
    return null;
  }
  return node as ExportableNode;
}

async function collectCssHints(node: ExportableNode): Promise<Record<string, Record<string, string>>> {
  const cssHints: Record<string, Record<string, string>> = {};
  try {
    const css = await (node as any).getCSSAsync();
    cssHints[node.name] = css;
    if ("children" in node) {
      for (const child of node.children.slice(0, 10)) {
        if ("getCSSAsync" in child) {
          const childCss = await (child as any).getCSSAsync();
          cssHints[child.name] = childCss;
        }
      }
    }
  } catch {
    // getCSSAsync may not be available in all API versions
  }
  return cssHints;
}

async function collectVariables(): Promise<Record<string, string>> {
  const variables: Record<string, string> = {};
  try {
    const localVars = await figma.variables.getLocalVariablesAsync();
    for (const v of localVars.slice(0, 50)) {
      const collection = await figma.variables.getVariableCollectionById(v.variableCollectionId);
      if (collection && collection.modes.length > 0) {
        const modeId = collection.modes[0].modeId;
        const val = v.valuesByMode[modeId];
        const key = `--${v.name.replace(/\//g, "-")}`;

        if (typeof val === "string") {
          variables[key] = val;
        } else if (typeof val === "number") {
          variables[key] = String(val);
        } else if (typeof val === "object" && val !== null && "r" in val) {
          const c = val as { r: number; g: number; b: number; a: number };
          const r = Math.round(c.r * 255);
          const g = Math.round(c.g * 255);
          const b = Math.round(c.b * 255);
          if (c.a < 1) {
            variables[key] = `rgba(${r}, ${g}, ${b}, ${parseFloat(c.a.toFixed(2))})`;
          } else {
            variables[key] = `#${r.toString(16).padStart(2, "0")}${g.toString(16).padStart(2, "0")}${b.toString(16).padStart(2, "0")}`;
          }
        }
      }
    }
  } catch {
    // Variables API may not be available
  }
  return variables;
}

figma.ui.onmessage = async (msg: { type: string; payload?: any }) => {
  if (msg.type === "export-frame") {
    const node = getSelectedFrame();
    if (!node) {
      figma.ui.postMessage({
        type: "error",
        message: "Please select a Frame, Component or Instance first.",
      });
      return;
    }

    try {
      const pngBytes = await node.exportAsync({
        format: "PNG",
        constraint: { type: "SCALE", value: 2 },
      });
      const base64 = figma.base64Encode(pngBytes);

      const cssHints = msg.payload?.includeCssHints ? await collectCssHints(node) : {};
      const variables = msg.payload?.includeVariables ? await collectVariables() : {};

      figma.ui.postMessage({
        type: "frame-exported",
        data: {
          imageBase64: base64,
          frameName: node.name,
          width: Math.round(node.width),
          height: Math.round(node.height),
          cssHints,
          variables,
        },
      });
    } catch (err: any) {
      figma.ui.postMessage({ type: "error", message: `Export failed: ${err.message}` });
    }
    return;
  }

  if (msg.type === "request-context") {
    // Re-fetch optional context (variables / css hints) without re-exporting
    // the PNG. Used by Refine and Edit so that the user's checkbox state at
    // the moment of action — not at the moment of generation — controls
    // whether the model receives variables / css_hints.
    const node = getSelectedFrame();
    const cssHints =
      node && msg.payload?.includeCssHints ? await collectCssHints(node) : {};
    const variables = msg.payload?.includeVariables ? await collectVariables() : {};
    figma.ui.postMessage({
      type: "context-ready",
      requestId: msg.payload?.requestId,
      data: { cssHints, variables },
    });
    return;
  }

  if (msg.type === "ping") {
    figma.ui.postMessage({ type: "pong", message: "Plugin sandbox is alive." });
  }
};
