(function () {
var __seleniumAtom = (() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };
  var __copyProps = (to, from, except, desc) => {
    if (from && typeof from === "object" || typeof from === "function") {
      for (let key of __getOwnPropNames(from))
        if (!__hasOwnProp.call(to, key) && key !== except)
          __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
    }
    return to;
  };
  var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

  // javascript/atoms/typescript/find-elements.ts
  var find_elements_exports = {};
  __export(find_elements_exports, {
    default: () => findElements
  });

  // javascript/atoms/typescript/core/error.ts
  var INVALID_SELECTOR = "invalid selector";
  var INVALID_ARGUMENT = "invalid argument";
  var NO_SUCH_ELEMENT = "no such element";
  function botError(code, message) {
    const err = new Error(message);
    err["code"] = code;
    return err;
  }

  // javascript/atoms/typescript/core/attribute.ts
  var SPLIT_STYLE_ATTRIBUTE_ON_SEMICOLONS = new RegExp(
    `[;]+(?=(?:(?:[^"]*"){2})*[^"]*$)(?=(?:(?:[^']*'){2})*[^']*$)(?=(?:[^()]*\\([^()]*\\))*[^()]*$)`
  );

  // javascript/atoms/typescript/core/element.ts
  var tagNameDescriptor = null;
  function getTagNameDescriptor() {
    if (tagNameDescriptor === null) {
      tagNameDescriptor = Object.getOwnPropertyDescriptor(Element.prototype, "tagName");
    }
    return tagNameDescriptor;
  }
  function toUpperCaseTag(tagName) {
    return tagName ? tagName.toUpperCase() : void 0;
  }
  function isElement(node, tagName) {
    if (!node || node.nodeType !== 1) {
      return false;
    }
    var asElement = node;
    var descriptor = getTagNameDescriptor();
    var rawTagName = descriptor && typeof descriptor.get === "function" ? descriptor.get.call(asElement) : asElement.tagName;
    var upperTagName = typeof rawTagName === "string" ? rawTagName.toUpperCase() : "";
    var normalizedTagName = toUpperCaseTag(tagName);
    if (upperTagName === "FORM") {
      return !normalizedTagName || normalizedTagName === "FORM";
    }
    return !!upperTagName && (!normalizedTagName || upperTagName === normalizedTagName);
  }
  function getParentElement(node) {
    var current = node.parentNode;
    while (current && current.nodeType !== Node.ELEMENT_NODE && current.nodeType !== Node.DOCUMENT_NODE && current.nodeType !== Node.DOCUMENT_FRAGMENT_NODE) {
      current = current.parentNode;
    }
    return current && current.nodeType === 1 ? current : null;
  }
  function getParentNodeInComposedDom(node) {
    var parent = node.parentNode;
    var slottable = node;
    var parentWithShadow = parent;
    if (parentWithShadow && parentWithShadow.shadowRoot && slottable.assignedSlot !== void 0) {
      return slottable.assignedSlot ? slottable.assignedSlot.parentNode : null;
    }
    return parent;
  }

  // javascript/atoms/typescript/core/geometry.ts
  function createRect(left, top, width, height) {
    return {
      left,
      top,
      right: left + width,
      bottom: top + height,
      width,
      height
    };
  }
  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }
  function getAreaRelativeRect(area) {
    var shape = area.shape.toLowerCase();
    var coords = area.coords.split(",").map(function(value) {
      return Number(value.trim());
    });
    if (shape === "rect" && coords.length === 4) {
      return createRect(coords[0], coords[1], coords[2] - coords[0], coords[3] - coords[1]);
    }
    if (shape === "circle" && coords.length === 3) {
      return createRect(coords[0] - coords[2], coords[1] - coords[2], coords[2] * 2, coords[2] * 2);
    }
    if (shape === "poly" && coords.length > 2) {
      var minX = coords[0];
      var minY = coords[1];
      var maxX = minX;
      var maxY = minY;
      for (var index = 2; index + 1 < coords.length; index += 2) {
        minX = Math.min(minX, coords[index]);
        maxX = Math.max(maxX, coords[index]);
        minY = Math.min(minY, coords[index + 1]);
        maxY = Math.max(maxY, coords[index + 1]);
      }
      return createRect(minX, minY, maxX - minX, maxY - minY);
    }
    return createRect(0, 0, 0, 0);
  }
  function findImageUsingMap(mapName, doc) {
    return doc.querySelector('[usemap="#' + mapName.replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"]');
  }
  function maybeFindImageMap(elem, getRect = getClientRect) {
    var isMap = isElement(elem, "MAP");
    if (!isMap && !isElement(elem, "AREA")) {
      return null;
    }
    var map = isMap ? elem : isElement(elem.parentNode, "MAP") ? elem.parentNode : null;
    var image = null;
    var rect = createRect(0, 0, 0, 0);
    if (isElement(map, "MAP") && map.name) {
      image = findImageUsingMap(map.name, map.ownerDocument);
      if (image) {
        rect = getRect(image);
        if (!isMap && isElement(elem, "AREA") && elem.shape.toLowerCase() !== "default") {
          var relativeRect = getAreaRelativeRect(elem);
          var relativeX = Math.min(Math.max(relativeRect.left, 0), rect.width);
          var relativeY = Math.min(Math.max(relativeRect.top, 0), rect.height);
          var width = Math.min(relativeRect.width, rect.width - relativeX);
          var height = Math.min(relativeRect.height, rect.height - relativeY);
          rect = createRect(relativeX + rect.left, relativeY + rect.top, width, height);
        }
      }
    }
    return { image, rect };
  }
  function getClientRect(elem, getRect) {
    var imageMap = maybeFindImageMap(elem, getRect || getClientRect);
    if (imageMap) {
      return imageMap.rect;
    }
    var elemTagName = typeof elem.tagName === "string" ? elem.tagName : "";
    if (elemTagName.toUpperCase() === "HTML") {
      var doc = elem.ownerDocument;
      var sizeElem = doc.compatMode === "CSS1Compat" ? doc.documentElement : doc.body || doc.documentElement;
      return createRect(0, 0, sizeElem.clientWidth, sizeElem.clientHeight);
    }
    try {
      var nativeRect = elem.getBoundingClientRect();
      return {
        left: nativeRect.left,
        top: nativeRect.top,
        right: nativeRect.right,
        bottom: nativeRect.bottom,
        width: nativeRect.right - nativeRect.left,
        height: nativeRect.bottom - nativeRect.top
      };
    } catch (_error) {
      return createRect(0, 0, 0, 0);
    }
  }
  function getClientRegion(elem, optRegion, getRect = getClientRect) {
    var rect = getRect(elem);
    if (!optRegion) {
      return rect;
    }
    var region = "left" in optRegion ? optRegion : { left: optRegion.x, top: optRegion.y, width: 1, height: 1 };
    var left = clamp(rect.left + region.left, rect.left, rect.right);
    var top = clamp(rect.top + region.top, rect.top, rect.bottom);
    var right = clamp(left + region.width, left, rect.right);
    var bottom = clamp(top + region.height, top, rect.bottom);
    return createRect(left, top, right - left, bottom - top);
  }

  // javascript/atoms/typescript/core/style.ts
  function getEffectiveStyle(elem, propertyName) {
    const win = elem.ownerDocument.defaultView;
    const computed = win ? win.getComputedStyle(elem) : null;
    if (!computed) {
      return null;
    }
    return computed.getPropertyValue(propertyName) || null;
  }

  // javascript/atoms/typescript/core/overflow.ts
  function getOverflowState(elem, optRegion, getStyle = getEffectiveStyle, getRect = getClientRect) {
    var region = getClientRegion(elem, optRegion, getRect);
    var ownerDoc = elem.ownerDocument;
    var htmlElem = ownerDoc.documentElement;
    var bodyElem = ownerDoc.body;
    var htmlOverflowStyle = getStyle(htmlElem, "overflow") || "visible";
    var treatAsFixedPosition = false;
    function canBeOverflowed(container2, position) {
      if (container2 === htmlElem) {
        return true;
      }
      var display = getStyle(container2, "display") || "";
      if (display.indexOf("inline") === 0 || display === "contents") {
        return false;
      }
      if (position === "absolute" && getStyle(container2, "position") === "static") {
        return false;
      }
      return true;
    }
    function getOverflowParent(current) {
      var position = getStyle(current, "position");
      if (position === "fixed") {
        treatAsFixedPosition = true;
        return current === htmlElem ? null : htmlElem;
      }
      var parent = getParentElement(current);
      while (parent && !canBeOverflowed(parent, position)) {
        parent = getParentElement(parent);
      }
      return parent;
    }
    function getOverflowStyles(current) {
      var overflowElem = current;
      if (htmlOverflowStyle === "visible") {
        if (current === htmlElem && bodyElem) {
          overflowElem = bodyElem;
        } else if (current === bodyElem) {
          return { x: "visible", y: "visible" };
        }
      }
      var overflow = {
        x: getStyle(overflowElem, "overflow-x") || "visible",
        y: getStyle(overflowElem, "overflow-y") || "visible"
      };
      if (current === htmlElem) {
        overflow.x = overflow.x === "visible" ? "auto" : overflow.x;
        overflow.y = overflow.y === "visible" ? "auto" : overflow.y;
      }
      return overflow;
    }
    function getScroll(current) {
      if (current === htmlElem) {
        return {
          x: ownerDoc.defaultView ? ownerDoc.defaultView.pageXOffset : 0,
          y: ownerDoc.defaultView ? ownerDoc.defaultView.pageYOffset : 0
        };
      }
      return { x: current.scrollLeft, y: current.scrollTop };
    }
    function overflowStateOf(container2) {
      return getOverflowState(container2, void 0, getStyle, getRect);
    }
    for (var container = getOverflowParent(elem); container; container = getOverflowParent(container)) {
      var containerOverflow = getOverflowStyles(container);
      if (containerOverflow.x === "visible" && containerOverflow.y === "visible") {
        continue;
      }
      var containerRect = getRect(container);
      if (containerRect.width === 0 || containerRect.height === 0) {
        return "hidden";
      }
      var underflowsX = region.right < containerRect.left;
      var underflowsY = region.bottom < containerRect.top;
      if (underflowsX && containerOverflow.x === "hidden" || underflowsY && containerOverflow.y === "hidden") {
        return "hidden";
      }
      if (underflowsX && containerOverflow.x !== "visible" || underflowsY && containerOverflow.y !== "visible") {
        var containerScroll = getScroll(container);
        var unscrollableX = region.right < containerRect.left - containerScroll.x;
        var unscrollableY = region.bottom < containerRect.top - containerScroll.y;
        if (unscrollableX && containerOverflow.x !== "visible" || unscrollableY && containerOverflow.y !== "visible") {
          return "hidden";
        }
        return overflowStateOf(container) === "hidden" ? "hidden" : "scroll";
      }
      var overflowsX = region.left >= containerRect.left + containerRect.width;
      var overflowsY = region.top >= containerRect.top + containerRect.height;
      if (overflowsX && containerOverflow.x === "hidden" || overflowsY && containerOverflow.y === "hidden") {
        return "hidden";
      }
      if (overflowsX && containerOverflow.x !== "visible" || overflowsY && containerOverflow.y !== "visible") {
        if (treatAsFixedPosition) {
          var docScroll = getScroll(container);
          if (region.left >= htmlElem.scrollWidth - docScroll.x || region.right >= htmlElem.scrollHeight - docScroll.y) {
            return "hidden";
          }
        }
        return overflowStateOf(container) === "hidden" ? "hidden" : "scroll";
      }
    }
    return "none";
  }

  // javascript/atoms/typescript/core/shown.ts
  function isShownElement(elem, optIgnoreOpacity) {
    var computedStyleCache = /* @__PURE__ */ new Map();
    var clientRectCache = /* @__PURE__ */ new Map();
    var displayedCache = /* @__PURE__ */ new Map();
    function getEffectiveStyle2(elem2, propertyName) {
      var computed = computedStyleCache.get(elem2);
      if (computed === void 0) {
        var win = elem2.ownerDocument.defaultView;
        computed = win ? win.getComputedStyle(elem2) || null : null;
        computedStyleCache.set(elem2, computed);
      }
      if (!computed) {
        return null;
      }
      var value = computed.getPropertyValue(propertyName);
      return value || null;
    }
    function getOpacity(elem2) {
      var opacityStyle = getEffectiveStyle2(elem2, "opacity");
      var opacity = opacityStyle ? Number(opacityStyle) : 1;
      var parent = getParentElement(elem2);
      return parent ? opacity * getOpacity(parent) : opacity;
    }
    function getClientRect3(elem2) {
      var cachedRect = clientRectCache.get(elem2);
      if (cachedRect) {
        return cachedRect;
      }
      var rect = getClientRect(elem2, getClientRect3);
      clientRectCache.set(elem2, rect);
      return rect;
    }
    function maybeFindImageMap2(elem2) {
      return maybeFindImageMap(elem2, getClientRect3);
    }
    function getClientRegion2(elem2) {
      return getClientRegion(elem2, void 0, getClientRect3);
    }
    function getOverflowState2(elem2) {
      return getOverflowState(elem2, void 0, getEffectiveStyle2, getClientRect3);
    }
    function isShownInternal(elem2, ignoreOpacity, displayedFn) {
      if (!isElement(elem2)) {
        throw new Error("Argument to isShown must be of type Element");
      }
      if (isElement(elem2, "BODY")) {
        return true;
      }
      if (isElement(elem2, "OPTION") || isElement(elem2, "OPTGROUP")) {
        var select = elem2.closest("select");
        return !!select && isShownInternal(select, true, displayedFn);
      }
      var imageMap = maybeFindImageMap2(elem2);
      if (imageMap) {
        return !!imageMap.image && imageMap.rect.width > 0 && imageMap.rect.height > 0 && isShownInternal(imageMap.image, ignoreOpacity, displayedFn);
      }
      if (isElement(elem2, "INPUT") && elem2.type.toLowerCase() === "hidden") {
        return false;
      }
      if (isElement(elem2, "NOSCRIPT")) {
        return false;
      }
      var visibility = getEffectiveStyle2(elem2, "visibility");
      if (visibility === "collapse" || visibility === "hidden") {
        return false;
      }
      if (!displayedFn(elem2)) {
        return false;
      }
      if (!ignoreOpacity && getOpacity(elem2) === 0) {
        return false;
      }
      function positiveSize(element) {
        var rect = getClientRect3(element);
        if (rect.height > 0 && rect.width > 0) {
          return true;
        }
        if (isElement(element, "PATH") && (rect.height > 0 || rect.width > 0)) {
          var strokeWidth = getEffectiveStyle2(element, "stroke-width");
          return !!strokeWidth && parseInt(strokeWidth, 10) > 0;
        }
        var elementVisibility = getEffectiveStyle2(element, "visibility");
        if (elementVisibility === "collapse" || elementVisibility === "hidden") {
          return false;
        }
        if (!displayedFn(element)) {
          return false;
        }
        if (getEffectiveStyle2(element, "overflow") === "hidden") {
          return false;
        }
        for (var index = 0; index < element.childNodes.length; index += 1) {
          var child = element.childNodes[index];
          if (child.nodeType === Node.TEXT_NODE) {
            var text = child.nodeValue || "";
            if (/^[\s]*$/.test(text) && /[\n\r\t]/.test(text)) {
              continue;
            }
            return true;
          }
          if (isElement(child) && positiveSize(child)) {
            return true;
          }
        }
        return false;
      }
      if (!positiveSize(elem2)) {
        return false;
      }
      function hiddenByOverflow(element) {
        if (getOverflowState2(element) !== "hidden") {
          return false;
        }
        for (var index = 0; index < element.childNodes.length; index += 1) {
          var child = element.childNodes[index];
          if (isElement(child) && !hiddenByOverflow(child) && positiveSize(child)) {
            return false;
          }
        }
        return true;
      }
      return !hiddenByOverflow(elem2);
    }
    function displayed(node) {
      var cached = displayedCache.get(node);
      if (cached !== void 0) {
        return cached;
      }
      if (isElement(node)) {
        var display = getEffectiveStyle2(node, "display");
        var contentVisibility = getEffectiveStyle2(node, "content-visibility");
        if (display === "none" || contentVisibility === "hidden") {
          displayedCache.set(node, false);
          return false;
        }
      }
      var parent = getParentNodeInComposedDom(node);
      if (typeof ShadowRoot === "function" && parent instanceof ShadowRoot) {
        if (parent.host.shadowRoot && parent.host.shadowRoot !== parent) {
          displayedCache.set(node, false);
          return false;
        }
        parent = parent.host;
      }
      if (parent && (parent.nodeType === Node.DOCUMENT_NODE || parent.nodeType === Node.DOCUMENT_FRAGMENT_NODE)) {
        displayedCache.set(node, true);
        return true;
      }
      if (isElement(parent, "DETAILS") && !parent.open && !isElement(node, "SUMMARY")) {
        displayedCache.set(node, false);
        return false;
      }
      var result = !!parent && displayed(parent);
      displayedCache.set(node, result);
      return result;
    }
    return isShownInternal(elem, !!optIgnoreOpacity, displayed);
  }
  var shown_default = isShownElement;

  // javascript/atoms/typescript/get-text.ts
  var INLINE_DISPLAY_BOXES = [
    "inline",
    "inline-block",
    "inline-table",
    "none",
    "table-cell",
    "table-column",
    "table-column-group"
  ];
  var CAPITALIZE_PATTERNS = function() {
    var letter = "\\p{L}\\u24B6-\\u24E9";
    var wordCharacter = "'_\\p{M}\\p{N}" + letter;
    try {
      return [
        new RegExp("(^|[^" + wordCharacter + "])([" + letter + "])", "gu"),
        new RegExp(
          "(^|[^" + wordCharacter + "])([_*])([" + letter + "])",
          "gu"
        )
      ];
    } catch (_ignored) {
      var latinLetters = "A-Za-z\\u00C0-\\u02AF\\u1E00-\\u1EFF\\u24B6-\\u24E9";
      var wordChars = "'_0-9" + latinLetters + "\\u0300-\\u036F\\u1AB0-\\u1AFF\\u1DC0-\\u1DFF";
      var lowerLetters = "A-Za-z\\u00C0-\\u02AF\\u1E00-\\u1EFF\\u24D0-\\u24E9";
      return [
        new RegExp("(^|[^" + wordChars + "])([" + latinLetters + "])", "g"),
        new RegExp("(^|[^" + wordChars + "])([_*])([" + lowerLetters + "])", "g")
      ];
    }
  }();
  var BREAKING_SPACE_RE = new RegExp("[ \\f\\t\\v\\u2028\\u2029]+", "g");
  var PRE_SPACE_RE = new RegExp("[ \\f\\t\\v\\u2028\\u2029]", "g");
  function trimExcludingNbsp(str) {
    return str.replace(/^[^\S\xa0]+|[^\S\xa0]+$/g, "");
  }
  function isEmptyOrWhitespace(str) {
    return /^[\s\xa0]*$/.test(str);
  }
  function concatenateCleanedLines(lines) {
    const trimmedLines = lines.map(trimExcludingNbsp);
    const joined = trimmedLines.join("\n");
    const trimmed = trimExcludingNbsp(joined);
    return trimmed.replace(/\xa0/g, " ");
  }
  function appendTextFromTextNode(textNode, lines, whitespace, textTransform) {
    var text = (textNode.nodeValue || "").replace(/[\u200b\u200e\u200f]/g, "");
    text = text.replace(/(\r\n|\r|\n)/g, "\n");
    if (whitespace === "normal" || whitespace === "nowrap") {
      text = text.replace(/\n/g, " ");
    }
    if (whitespace === "pre" || whitespace === "pre-wrap") {
      text = text.replace(PRE_SPACE_RE, "\xA0");
    } else {
      text = text.replace(BREAKING_SPACE_RE, " ");
    }
    if (textTransform === "capitalize") {
      text = text.replace(CAPITALIZE_PATTERNS[0], function() {
        return arguments[1] + arguments[2].toUpperCase();
      });
      text = text.replace(CAPITALIZE_PATTERNS[1], function() {
        return arguments[1] + arguments[2] + arguments[3].toUpperCase();
      });
    } else if (textTransform === "uppercase") {
      text = text.toUpperCase();
    } else if (textTransform === "lowercase") {
      text = text.toLowerCase();
    }
    var currLine = lines.pop() || "";
    if (currLine.endsWith(" ") && text.startsWith(" ")) {
      text = text.substring(1);
    }
    lines.push(currLine + text);
  }
  function appendTextFromElementCommon(elem, lines, isShownFn, childNodeFn) {
    function currLine() {
      var _a;
      return (_a = lines[lines.length - 1]) != null ? _a : "";
    }
    const node = elem;
    if (isElement(node, "BR")) {
      lines.push("");
      return;
    }
    const isTD = isElement(elem, "TD");
    const display = getEffectiveStyle(elem, "display");
    const isBlock = !isTD && !INLINE_DISPLAY_BOXES.includes(display || "");
    const previousElementSibling = elem.previousElementSibling;
    const prevDisplay = previousElementSibling ? getEffectiveStyle(previousElementSibling, "display") : "";
    const thisFloat = getEffectiveStyle(elem, "float");
    const runIntoThis = prevDisplay === "run-in" && thisFloat === "none";
    if (isBlock && !runIntoThis && !isEmptyOrWhitespace(currLine())) {
      lines.push("");
    }
    const shown = isShownFn(elem);
    var whitespace = null;
    var textTransform = null;
    if (shown) {
      whitespace = getEffectiveStyle(elem, "white-space");
      textTransform = getEffectiveStyle(elem, "text-transform");
    }
    for (var i = 0; i < elem.childNodes.length; i++) {
      childNodeFn(elem.childNodes[i], lines, shown, whitespace, textTransform);
    }
    const line = currLine();
    if ((isTD || display === "table-cell") && line && !line.endsWith(" ")) {
      lines[lines.length - 1] += " ";
    }
    if (isBlock && display !== "run-in" && !isEmptyOrWhitespace(line)) {
      lines.push("");
    }
  }
  function appendTextFromElement(elem, lines) {
    appendTextFromElementCommon(
      elem,
      lines,
      shown_default,
      function(node, lines2, shown, whitespace, textTransform) {
        if (node.nodeType === Node.TEXT_NODE && shown) {
          appendTextFromTextNode(
            node,
            lines2,
            whitespace,
            textTransform
          );
        } else if (isElement(node)) {
          appendTextFromElement(node, lines2);
        }
      }
    );
  }
  function isNodeDistributedIntoShadowDom(node) {
    if (node.nodeType === Node.ELEMENT_NODE || node.nodeType === Node.TEXT_NODE) {
      var slottable = node;
      return slottable.assignedSlot != null;
    }
    return false;
  }
  function appendTextFromNodeInComposedDom(node, lines, shown, whitespace, textTransform) {
    if (node.nodeType === Node.TEXT_NODE && shown) {
      appendTextFromTextNode(node, lines, whitespace, textTransform);
    } else if (isElement(node)) {
      const castElem = node;
      if (isElement(node, "SLOT")) {
        var parentNode = node;
        while (parentNode.parentNode) {
          parentNode = parentNode.parentNode;
        }
        if (typeof ShadowRoot === "function" && parentNode instanceof ShadowRoot) {
          const slot = node;
          const assigned = slot.assignedNodes();
          const childrenToTraverse = assigned.length > 0 ? assigned : slot.childNodes;
          for (var i = 0; i < childrenToTraverse.length; i++) {
            appendTextFromNodeInComposedDom(
              childrenToTraverse[i],
              lines,
              shown,
              whitespace,
              textTransform
            );
          }
        } else {
          appendTextFromElementInComposedDom(castElem, lines);
        }
      } else {
        appendTextFromElementInComposedDom(castElem, lines);
      }
    }
  }
  function appendTextFromElementInComposedDom(elem, lines) {
    if (elem.shadowRoot) {
      const whitespace = getEffectiveStyle(elem, "white-space");
      const textTransform = getEffectiveStyle(elem, "text-transform");
      elem.shadowRoot.childNodes.forEach((node) => appendTextFromNodeInComposedDom(node, lines, true, whitespace, textTransform));
    }
    appendTextFromElementCommon(
      elem,
      lines,
      shown_default,
      function(node, lines2, shown, whitespace, textTransform) {
        if (!isNodeDistributedIntoShadowDom(node)) {
          appendTextFromNodeInComposedDom(node, lines2, shown, whitespace, textTransform);
        }
      }
    );
  }
  function getText(element) {
    const lines = [];
    if (typeof ShadowRoot === "function") {
      appendTextFromElementInComposedDom(element, lines);
    } else {
      appendTextFromElement(element, lines);
    }
    return concatenateCleanedLines(lines);
  }
  var get_text_default = getText;

  // javascript/atoms/typescript/core/locators.ts
  function cssEscapeId(s) {
    return s.replace(/[\s'"\\#.:;,!?+<>=~*^$|%&@`{}\-/\[\]()]/g, (c) => "\\" + c);
  }
  function hasCssEscape() {
    return typeof CSS !== "undefined" && typeof CSS.escape === "function";
  }
  function idSelector(target) {
    if (target.indexOf("\0") !== -1) {
      return null;
    }
    if (hasCssEscape()) {
      return "#" + CSS.escape(target);
    }
    return /^\d/.test(target) ? null : "#" + cssEscapeId(target);
  }
  function classSelector(target) {
    return "." + (hasCssEscape() ? CSS.escape(target) : cssEscapeId(target));
  }
  function nameSelector(target) {
    if (target.indexOf("\0") !== -1) {
      return null;
    }
    if (hasCssEscape()) {
      return '[name="' + CSS.escape(target) + '"]';
    }
    if (/[\r\n\f]/.test(target)) {
      return null;
    }
    return '[name="' + target.replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"]';
  }
  function attributeMany(selector, attr, target, root) {
    if (selector !== null) {
      try {
        return Array.from(root.querySelectorAll(selector));
      } catch (_e) {
      }
    }
    return Array.from(root.querySelectorAll("*")).filter((el) => el.getAttribute(attr) === target);
  }
  function normalizeLinkText(s) {
    return s.replace(/\u00a0/g, " ");
  }
  function getLinkText(el) {
    return get_text_default(el).replace(/^[\s]+|[\s]+$/g, "");
  }
  function classNameMany(target, root) {
    if (!target) {
      throw botError(INVALID_SELECTOR, "No class name specified");
    }
    target = target.trim();
    if (target.indexOf(" ") !== -1) {
      throw botError(INVALID_SELECTOR, "Compound class names not permitted");
    }
    try {
      return Array.from(root.querySelectorAll(classSelector(target)));
    } catch (_e) {
      throw botError(INVALID_SELECTOR, "An invalid or illegal class name was specified");
    }
  }
  function cssMany(target, root) {
    try {
      return Array.from(root.querySelectorAll(target));
    } catch (_e) {
      throw botError(INVALID_SELECTOR, "An invalid or illegal CSS selector was specified: " + target);
    }
  }
  function idMany(target, root) {
    if (!target) {
      return [];
    }
    return attributeMany(idSelector(target), "id", target, root);
  }
  function linkTextMany(target, root, partial) {
    target = normalizeLinkText(target);
    return Array.from(root.querySelectorAll("a")).filter((el) => {
      const text = getLinkText(el);
      return partial ? text.indexOf(target) !== -1 : text === target;
    });
  }
  function nameMany(target, root) {
    return attributeMany(nameSelector(target), "name", target, root);
  }
  function tagNameMany(target, root) {
    if (target === "") {
      throw botError(INVALID_SELECTOR, 'Unable to locate an element with the tagName ""');
    }
    if ("getElementsByTagName" in root) {
      return Array.from(root.getElementsByTagName(target));
    }
    const elements = Array.from(root.querySelectorAll("*"));
    if (target === "*") {
      return elements;
    }
    const html = "http://www.w3.org/1999/xhtml";
    const folded = target.toLowerCase();
    return elements.filter((el) => el.namespaceURI === html ? el.localName === folded : el.localName === target);
  }
  var DEFAULT_NS_RESOLVER = /* @__PURE__ */ function() {
    const ns = { svg: "http://www.w3.org/2000/svg" };
    return (prefix) => ns[prefix] || null;
  }();
  var ORDERED_NODE_SNAPSHOT_TYPE = 7;
  function buildNsResolver(target, doc) {
    if (target.indexOf(":") === -1) {
      return null;
    }
    const reversedNs = {};
    const allNodes = doc.getElementsByTagName("*");
    for (let i = 0; i < allNodes.length; i++) {
      const n = allNodes[i];
      const ns = n.namespaceURI;
      if (ns && !reversedNs[ns]) {
        let prefix = n.lookupPrefix(ns);
        if (!prefix) {
          const m = ns.match(".*/(\\w+)/?$");
          prefix = m ? m[1] : "xhtml";
        }
        reversedNs[ns] = prefix;
      }
    }
    const namespaces = {};
    for (const key in reversedNs) {
      namespaces[reversedNs[key]] = key;
    }
    return (prefix) => namespaces[prefix || ""] || null;
  }
  function xpathMany(target, root) {
    const doc = root.documentElement ? root : root.ownerDocument;
    if (!doc.documentElement) {
      return [];
    }
    try {
      const resolver = buildNsResolver(target, doc);
      let result = null;
      try {
        result = doc.evaluate(target, root, resolver, ORDERED_NODE_SNAPSHOT_TYPE, null);
      } catch (te) {
        if (te.name === "TypeError") {
          const fallback = doc.createNSResolver ? doc.createNSResolver(doc.documentElement) : DEFAULT_NS_RESOLVER;
          result = doc.evaluate(target, root, fallback, ORDERED_NODE_SNAPSHOT_TYPE, null);
        } else {
          throw te;
        }
      }
      if (!result) {
        return [];
      }
      const results = [];
      for (let i = 0; i < result.snapshotLength; i++) {
        const node = result.snapshotItem(i);
        if (!node || node.nodeType !== Node.ELEMENT_NODE) {
          throw botError(
            INVALID_SELECTOR,
            'The result of the xpath expression "' + target + '" is: ' + node + ". It should be an element."
          );
        }
        results.push(node);
      }
      return results;
    } catch (ex) {
      if (ex.name === "NS_ERROR_ILLEGAL_VALUE") {
        return [];
      }
      if (ex.code === INVALID_SELECTOR) {
        throw ex;
      }
      throw botError(
        INVALID_SELECTOR,
        "Unable to locate an element with the xpath expression " + target + " because of the following error:\n" + ex
      );
    }
  }
  function getClientRect2(element) {
    const r = element.getBoundingClientRect();
    return { left: r.left, top: r.top, width: r.width, height: r.height };
  }
  function resolveAnchor(selector, outerRoot) {
    if (selector instanceof Element) {
      return selector;
    }
    if (typeof selector === "function") {
      return resolveAnchor(selector(), outerRoot);
    }
    if (selector && typeof selector === "object") {
      let found = outerRoot ? findElements(selector, outerRoot) : [];
      if (!found.length) {
        found = findElements(selector);
      }
      if (!found.length) {
        throw botError(NO_SUCH_ELEMENT, "No element has been found by " + JSON.stringify(selector));
      }
      return found[0];
    }
    throw botError(INVALID_ARGUMENT, "Selector is of wrong type: " + JSON.stringify(selector));
  }
  function makeProximityFilter(selector, outerRoot, test) {
    return (candidate) => test(getClientRect2(resolveAnchor(selector, outerRoot)), getClientRect2(candidate));
  }
  function sortByProximity(anchor, elements) {
    const ar = getClientRect2(anchor);
    const acx = ar.left + Math.max(1, ar.width) / 2;
    const acy = ar.top + Math.max(1, ar.height) / 2;
    return elements.slice().sort((a, b) => {
      const ra = getClientRect2(a);
      const rb = getClientRect2(b);
      const da = Math.sqrt(
        Math.pow(acx - (ra.left + Math.max(1, ra.width) / 2), 2) + Math.pow(acy - (ra.top + Math.max(1, ra.height) / 2), 2)
      );
      const db = Math.sqrt(
        Math.pow(acx - (rb.left + Math.max(1, rb.width) / 2), 2) + Math.pow(acy - (rb.top + Math.max(1, rb.height) / 2), 2)
      );
      return da - db;
    });
  }
  function relativeMany(target, actualRoot, outerRoot) {
    if (!Object.prototype.hasOwnProperty.call(target, "root") || !Object.prototype.hasOwnProperty.call(target, "filters")) {
      throw botError(
        INVALID_ARGUMENT,
        "Locator not suitable for relative locators: " + JSON.stringify(target)
      );
    }
    const filters = target["filters"];
    if (!Array.isArray(filters)) {
      throw botError(INVALID_ARGUMENT, "Targets should be an array: " + JSON.stringify(target));
    }
    let elements;
    const rootTarget = target["root"];
    if (rootTarget instanceof Element) {
      elements = [rootTarget];
    } else {
      elements = findElements(rootTarget, actualRoot);
    }
    if (!elements.length) {
      return [];
    }
    const RELATIVE_STRATEGIES = {
      above: (sel) => makeProximityFilter(sel, outerRoot, (a, c) => c.top + c.height <= a.top),
      below: (sel) => makeProximityFilter(sel, outerRoot, (a, c) => c.top >= a.top + a.height),
      left: (sel) => makeProximityFilter(sel, outerRoot, (a, c) => c.left + c.width <= a.left),
      right: (sel) => makeProximityFilter(sel, outerRoot, (a, c) => c.left >= a.left + a.width),
      near: (sel, distArg) => {
        const distFromSelector = typeof sel["distance"] === "number" ? sel["distance"] : 0;
        const distance = typeof distArg === "number" && distArg > 0 ? distArg : distFromSelector || 50;
        return (candidate) => {
          const anchor = resolveAnchor(sel, outerRoot);
          if (anchor === candidate) return false;
          const a = getClientRect2(anchor);
          const c = getClientRect2(candidate);
          const expanded = {
            left: a.left - distance,
            top: a.top - distance,
            width: a.width + distance * 2,
            height: a.height + distance * 2
          };
          return c.left < expanded.left + expanded.width && c.left + c.width > expanded.left && c.top < expanded.top + expanded.height && c.top + c.height > expanded.top;
        };
      },
      straightAbove: (sel) => makeProximityFilter(
        sel,
        outerRoot,
        (a, c) => c.left < a.left + a.width && c.left + c.width > a.left && c.top + c.height <= a.top
      ),
      straightBelow: (sel) => makeProximityFilter(
        sel,
        outerRoot,
        (a, c) => c.left < a.left + a.width && c.left + c.width > a.left && c.top >= a.top + a.height
      ),
      straightLeft: (sel) => makeProximityFilter(
        sel,
        outerRoot,
        (a, c) => c.top < a.top + a.height && c.top + c.height > a.top && c.left + c.width <= a.left
      ),
      straightRight: (sel) => makeProximityFilter(
        sel,
        outerRoot,
        (a, c) => c.top < a.top + a.height && c.top + c.height > a.top && c.left >= a.left + a.width
      )
    };
    const matched = elements.filter((el) => {
      if (!el) return false;
      return filters.every((filter) => {
        const strategy = RELATIVE_STRATEGIES[filter.kind];
        if (!strategy) {
          throw botError(INVALID_ARGUMENT, "Cannot find filter suitable for " + filter.kind);
        }
        return strategy(...filter.args)(el);
      });
    });
    const finalFilter = filters[filters.length - 1];
    if (!finalFilter || !RELATIVE_STRATEGIES[finalFilter.kind]) {
      return matched;
    }
    const lastAnchor = resolveAnchor(finalFilter.args[0], outerRoot);
    return sortByProximity(lastAnchor, matched);
  }
  function findElements(target, root) {
    const actualRoot = root || document;
    const keys = Object.keys(target).filter((k) => Object.prototype.hasOwnProperty.call(target, k));
    if (!keys.length) {
      throw botError(INVALID_ARGUMENT, "Unsupported locator strategy: (empty)");
    }
    const key = keys[0];
    const value = target[key];
    switch (key) {
      case "className":
      case "class name":
        return classNameMany(value, actualRoot);
      case "css":
      case "css selector":
        return cssMany(value, actualRoot);
      case "id":
        return idMany(value, actualRoot);
      case "linkText":
      case "link text":
        return linkTextMany(value, actualRoot, false);
      case "partialLinkText":
      case "partial link text":
        return linkTextMany(value, actualRoot, true);
      case "name":
        return nameMany(value, actualRoot);
      case "tagName":
      case "tag name":
        return tagNameMany(value, actualRoot);
      case "xpath":
        return xpathMany(value, actualRoot);
      case "relative":
        return relativeMany(value, actualRoot, root);
      default:
        throw botError(INVALID_ARGUMENT, "Unsupported locator strategy: " + key);
    }
  }
  return __toCommonJS(find_elements_exports);
})();
return __seleniumAtom.default;
})()
