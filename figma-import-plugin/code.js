figma.showUI(__html__, { visible: false });

const GAP = 80;
let xOffset = 0;
let importCount = 0;

figma.currentPage.name = "Industrial HMI Mockups";

figma.ui.onmessage = (msg) => {
  if (msg.type === "image-data") {
    try {
      const image = figma.createImage(msg.bytes);
      const frame = figma.createFrame();
      frame.name = msg.name;
      frame.x = xOffset;
      frame.y = 0;
      frame.resize(1280, 720);
      frame.fills = [{
        type: "IMAGE",
        imageHash: image.hash,
        scaleMode: "FILL",
      }];
      xOffset += 1280 + GAP;
      importCount++;
      figma.notify("Imported " + msg.index + "/" + msg.total + ": " + msg.name, { timeout: 2000 });
    } catch (err) {
      figma.notify("Failed: " + msg.name + " - " + err.message, { timeout: 5000, error: true });
    }
  }

  if (msg.type === "error") {
    figma.notify("Failed to fetch: " + msg.name + " - " + msg.message, { timeout: 5000, error: true });
  }

  if (msg.type === "done") {
    figma.viewport.scrollAndZoomIntoView(figma.currentPage.children);
    figma.notify("Done! Imported " + importCount + " HMI mockup frames.", { timeout: 5000 });
    figma.closePlugin();
  }
};
