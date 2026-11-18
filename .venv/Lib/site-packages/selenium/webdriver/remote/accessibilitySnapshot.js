(function () {
var __seleniumAtom = (() => {
  var __defProp = Object.defineProperty;
  var __defProps = Object.defineProperties;
  var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
  var __getOwnPropDescs = Object.getOwnPropertyDescriptors;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __getOwnPropSymbols = Object.getOwnPropertySymbols;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __propIsEnum = Object.prototype.propertyIsEnumerable;
  var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
  var __spreadValues = (a, b) => {
    for (var prop in b || (b = {}))
      if (__hasOwnProp.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    if (__getOwnPropSymbols)
      for (var prop of __getOwnPropSymbols(b)) {
        if (__propIsEnum.call(b, prop))
          __defNormalProp(a, prop, b[prop]);
      }
    return a;
  };
  var __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));
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

  // javascript/atoms/typescript/accessibility-snapshot-wire.ts
  var accessibility_snapshot_wire_exports = {};
  __export(accessibility_snapshot_wire_exports, {
    default: () => wire_default
  });

  // javascript/atoms/typescript/core/attribute.ts
  var SPLIT_STYLE_ATTRIBUTE_ON_SEMICOLONS = new RegExp(
    `[;]+(?=(?:(?:[^"]*"){2})*[^"]*$)(?=(?:(?:[^']*'){2})*[^']*$)(?=(?:[^()]*\\([^()]*\\))*[^()]*$)`
  );
  function getProperty(element, propertyName) {
    return element[propertyName];
  }

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

  // javascript/atoms/typescript/core/accessibility/roles.ts
  var CONCRETE_ROLES = /* @__PURE__ */ new Set([
    "alert",
    "alertdialog",
    "application",
    "article",
    "banner",
    "blockquote",
    "button",
    "caption",
    "cell",
    "checkbox",
    "code",
    "columnheader",
    "combobox",
    "complementary",
    "contentinfo",
    "definition",
    "deletion",
    "dialog",
    "directory",
    "document",
    "emphasis",
    "feed",
    "figure",
    "form",
    "generic",
    "grid",
    "gridcell",
    "group",
    "heading",
    "img",
    "insertion",
    "link",
    "list",
    "listbox",
    "listitem",
    "log",
    "main",
    "marquee",
    "math",
    "menu",
    "menubar",
    "menuitem",
    "menuitemcheckbox",
    "menuitemradio",
    "meter",
    "navigation",
    "none",
    "note",
    "option",
    "paragraph",
    "presentation",
    "progressbar",
    "radio",
    "radiogroup",
    "region",
    "row",
    "rowgroup",
    "rowheader",
    "scrollbar",
    "search",
    "searchbox",
    "separator",
    "slider",
    "spinbutton",
    "status",
    "strong",
    "subscript",
    "superscript",
    "switch",
    "tab",
    "table",
    "tablist",
    "tabpanel",
    "term",
    "textbox",
    "time",
    "timer",
    "toolbar",
    "tooltip",
    "tree",
    "treegrid",
    "treeitem",
    "graphics-document",
    "graphics-object",
    "graphics-symbol"
  ]);
  var GLOBAL_ARIA_ATTRIBUTES = [
    "aria-atomic",
    "aria-busy",
    "aria-controls",
    "aria-current",
    "aria-describedby",
    "aria-description",
    "aria-details",
    "aria-disabled",
    "aria-dropeffect",
    "aria-errormessage",
    "aria-flowto",
    "aria-grabbed",
    "aria-haspopup",
    "aria-hidden",
    "aria-invalid",
    "aria-keyshortcuts",
    "aria-label",
    "aria-labelledby",
    "aria-live",
    "aria-owns",
    "aria-relevant",
    "aria-roledescription"
  ];
  var NATIVELY_FOCUSABLE = /* @__PURE__ */ new Set(["button", "iframe", "input", "select", "summary", "textarea"]);
  var FRAME_ELEMENTS = /* @__PURE__ */ new Set(["frame", "iframe"]);
  var SECTIONING_CONTENT = /* @__PURE__ */ new Set(["article", "aside", "nav", "section"]);
  var HEADER_FOOTER_SCOPES = /* @__PURE__ */ new Set(["article", "aside", "main", "nav", "section"]);
  var HEADER_FOOTER_SCOPE_ROLES = /* @__PURE__ */ new Set(["article", "complementary", "main", "navigation", "region"]);
  var LIST_PARENTS = /* @__PURE__ */ new Set(["menu", "ol", "ul"]);
  function isPresentational(role) {
    return role === "none" || role === "presentation";
  }
  function explicitRole(element) {
    const attribute2 = element.getAttribute("role");
    if (!attribute2) {
      return null;
    }
    for (const token2 of attribute2.trim().toLowerCase().split(/\s+/)) {
      if (CONCRETE_ROLES.has(token2)) {
        return token2;
      }
    }
    return null;
  }
  function hasGlobalAriaAttribute(element) {
    return GLOBAL_ARIA_ATTRIBUTES.some((name) => element.hasAttribute(name));
  }
  function canTakeFocus(element) {
    const name = element.localName;
    if (NATIVELY_FOCUSABLE.has(name)) {
      if (name === "input" && element.type === "hidden") {
        return false;
      }
      return !("disabled" in element && element.disabled);
    }
    const tabindex = element.getAttribute("tabindex");
    if (tabindex !== null && /^\s*[-+]?\d+\s*$/.test(tabindex)) {
      return true;
    }
    if (name === "a" || name === "area") {
      return element.hasAttribute("href");
    }
    return element.isContentEditable === true;
  }
  function hasAuthorName(element) {
    const label = element.getAttribute("aria-label");
    if (label !== null && label.trim() !== "") {
      return true;
    }
    const labelledBy = element.getAttribute("aria-labelledby");
    if (labelledBy !== null && labelledBy.trim() !== "") {
      const root = element.getRootNode();
      for (const id of labelledBy.trim().split(/\s+/)) {
        const target = root.getElementById(id);
        if (target && hasTextAlternative(target)) {
          return true;
        }
      }
    }
    const title = element.getAttribute("title");
    return title !== null && title.trim() !== "";
  }
  var ALTERNATIVE_ATTRIBUTES = ["aria-label", "alt", "title", "value"];
  function hasTextAlternative(target) {
    if ((target.textContent || "").trim() !== "") {
      return true;
    }
    const elements = [target, ...Array.from(target.querySelectorAll("*"))];
    return elements.some(
      (candidate) => ALTERNATIVE_ATTRIBUTES.some((attribute2) => (candidate.getAttribute(attribute2) || "").trim() !== "")
    );
  }
  function ownerIsPresentational(owner, lookup) {
    return owner !== null && isPresentational(lookup(owner));
  }
  function hasAncestor(element, names, roles = null) {
    for (let parent = element.parentElement; parent; parent = parent.parentElement) {
      if (names.has(parent.localName)) {
        return true;
      }
      if (roles !== null) {
        const role = explicitRole(parent);
        if (role !== null && roles.has(role)) {
          return true;
        }
      }
    }
    return false;
  }
  function inputRole(input) {
    const type = input.type;
    const hasList = input.hasAttribute("list");
    switch (type) {
      case "button":
      case "image":
      case "reset":
      case "submit":
        return "button";
      case "checkbox":
        return "checkbox";
      case "radio":
        return "radio";
      case "range":
        return "slider";
      case "number":
        return "spinbutton";
      case "search":
        return hasList ? "combobox" : "searchbox";
      case "email":
      case "tel":
      case "text":
      case "url":
        return hasList ? "combobox" : "textbox";
      case "password":
        return "textbox";
      default:
        return "generic";
    }
  }
  function tableCellRole(cell, lookup) {
    const table = cell.closest("table");
    if (!table) {
      return "cell";
    }
    const tableRole = lookup(table);
    if (isPresentational(tableRole)) {
      return "generic";
    }
    return tableRole === "grid" || tableRole === "treegrid" ? "gridcell" : "cell";
  }
  function tableHeaderRole(header, lookup) {
    if (ownerIsPresentational(header.closest("table"), lookup)) {
      return "generic";
    }
    const scope = (header.getAttribute("scope") || "").toLowerCase();
    return scope === "row" || scope === "rowgroup" ? "rowheader" : "columnheader";
  }
  function tablePartRole(part, role, lookup) {
    return ownerIsPresentational(part.closest("table"), lookup) ? "generic" : role;
  }
  function implicitRole(element, lookup = computeRole) {
    switch (element.localName) {
      case "a":
      case "area":
        return element.hasAttribute("href") ? "link" : "generic";
      case "address":
      case "details":
      case "fieldset":
      case "hgroup":
      case "optgroup":
        return "group";
      case "article":
        return "article";
      case "aside":
        if (!hasAncestor(element, SECTIONING_CONTENT)) {
          return "complementary";
        }
        return hasAuthorName(element) ? "complementary" : "generic";
      case "blockquote":
        return "blockquote";
      case "button":
        return "button";
      case "caption":
        return "caption";
      case "code":
        return "code";
      case "datalist":
        return "listbox";
      case "dd":
        return "definition";
      case "del":
        return "deletion";
      case "dfn":
      case "dt":
        return "term";
      case "dialog":
        return "dialog";
      case "em":
        return "emphasis";
      case "figure":
        return "figure";
      case "footer":
        return hasAncestor(element, HEADER_FOOTER_SCOPES, HEADER_FOOTER_SCOPE_ROLES) ? "generic" : "contentinfo";
      case "form":
        return hasAuthorName(element) ? "form" : "generic";
      case "frame":
      case "iframe":
        return "iframe";
      case "h1":
      case "h2":
      case "h3":
      case "h4":
      case "h5":
      case "h6":
        return "heading";
      case "header":
        return hasAncestor(element, HEADER_FOOTER_SCOPES, HEADER_FOOTER_SCOPE_ROLES) ? "generic" : "banner";
      case "hr":
        return "separator";
      case "html":
        return "document";
      case "img":
        if (element.getAttribute("alt") === "" && !hasGlobalAriaAttribute(element) && !canTakeFocus(element)) {
          return "presentation";
        }
        return "img";
      case "input":
        return inputRole(element);
      case "ins":
        return "insertion";
      case "li": {
        const parent = element.parentElement;
        if (!parent || !LIST_PARENTS.has(parent.localName) || ownerIsPresentational(parent, lookup)) {
          return "generic";
        }
        return "listitem";
      }
      case "main":
        return "main";
      case "math":
        return "math";
      case "menu":
      case "ol":
      case "ul":
        return "list";
      case "meter":
        return "meter";
      case "nav":
        return "navigation";
      case "option":
        return "option";
      case "output":
        return "status";
      case "p":
        return "paragraph";
      case "progress":
        return "progressbar";
      case "search":
        return "search";
      case "section":
        return hasAuthorName(element) ? "region" : "generic";
      case "select": {
        const select = element;
        return select.multiple || select.size > 1 ? "listbox" : "combobox";
      }
      case "strong":
        return "strong";
      case "sub":
        return "subscript";
      case "summary":
        return "button";
      case "sup":
        return "superscript";
      case "svg":
        return "graphics-document";
      case "table":
        return "table";
      case "tbody":
      case "tfoot":
      case "thead":
        return tablePartRole(element, "rowgroup", lookup);
      case "td":
        return tableCellRole(element, lookup);
      case "textarea":
        return "textbox";
      case "th":
        return tableHeaderRole(element, lookup);
      case "time":
        return "time";
      case "tr":
        return tablePartRole(element, "row", lookup);
      default:
        return "generic";
    }
  }
  function computeRole(element, lookup = computeRole) {
    if (FRAME_ELEMENTS.has(element.localName)) {
      return "iframe";
    }
    const explicit = explicitRole(element);
    if (explicit === null) {
      return implicitRole(element, lookup);
    }
    if (isPresentational(explicit) && (canTakeFocus(element) || hasGlobalAriaAttribute(element))) {
      return implicitRole(element, lookup);
    }
    return explicit;
  }

  // javascript/atoms/typescript/core/accessibility/context.ts
  function createContext(options) {
    return {
      interestingOnly: options === void 0 || options === null || options.interestingOnly !== false,
      roles: /* @__PURE__ */ new Map(),
      hidden: /* @__PURE__ */ new Map(),
      imageMaps: /* @__PURE__ */ new Map(),
      styles: /* @__PURE__ */ new Map(),
      names: /* @__PURE__ */ new Map(),
      descriptions: /* @__PURE__ */ new Map(),
      descendantTexts: /* @__PURE__ */ new Map(),
      contentTexts: /* @__PURE__ */ new Map(),
      referenceTexts: /* @__PURE__ */ new Map(),
      generated: /* @__PURE__ */ new Map(),
      generatedScopes: /* @__PURE__ */ new Map(),
      placed: /* @__PURE__ */ new Set(),
      owned: /* @__PURE__ */ new Map(),
      claimed: /* @__PURE__ */ new Set()
    };
  }
  function roleOf(element, context) {
    let role = context.roles.get(element);
    if (role === void 0) {
      role = computeRole(element, (owner) => roleOf(owner, context));
      context.roles.set(element, role);
    }
    return role;
  }
  function styleOf(element, context, pseudo = "") {
    let perPseudo = context.styles.get(element);
    if (!perPseudo) {
      perPseudo = /* @__PURE__ */ new Map();
      context.styles.set(element, perPseudo);
    }
    let style = perPseudo.get(pseudo);
    if (style === void 0) {
      const view = element.ownerDocument.defaultView;
      style = view ? view.getComputedStyle(element, pseudo || null) : null;
      perPseudo.set(pseudo, style);
    }
    return style;
  }

  // javascript/atoms/typescript/core/accessibility/hidden.ts
  var DOCUMENT_NODE = 9;
  var DOCUMENT_FRAGMENT_NODE = 11;
  var NOT_RENDERED = Symbol("not rendered");
  function isAriaHidden(element) {
    const value = element.getAttribute("aria-hidden");
    return value !== null && value.trim().toLowerCase() === "true";
  }
  function areaState(area, context) {
    const map = area.closest("map");
    const name = map ? map.getAttribute("name") : null;
    if (!name) {
      return "subtree";
    }
    const known = context.imageMaps.get(name);
    if (known !== void 0) {
      return known;
    }
    let state = "subtree";
    const images = area.ownerDocument.querySelectorAll("img[usemap]");
    for (let i = 0; i < images.length; i++) {
      const image = images[i];
      const usemap = (image.getAttribute("usemap") || "").replace(/^#/, "");
      if (usemap === name && hiddenState(image, context) === "rendered" && !isHiddenByAncestor(image, context)) {
        state = "rendered";
        break;
      }
    }
    context.imageMaps.set(name, state);
    return state;
  }
  function isClosedDetails(element) {
    return element.localName === "details" && !element.hasAttribute("open");
  }
  function isSlot(element) {
    return element.localName === "slot" && "assignedNodes" in element;
  }
  function flatTreeParent(node) {
    const parent = node.parentNode;
    if (!parent) {
      return NOT_RENDERED;
    }
    if (node.assignedSlot) {
      return node.assignedSlot;
    }
    if (parent.nodeType === DOCUMENT_FRAGMENT_NODE) {
      const host = parent.host;
      return host ? host : NOT_RENDERED;
    }
    if (parent.nodeType === DOCUMENT_NODE) {
      return null;
    }
    const parentElement = parent;
    if (parentElement.shadowRoot) {
      return NOT_RENDERED;
    }
    if (isSlot(parentElement) && parentElement.assignedNodes().length > 0) {
      return NOT_RENDERED;
    }
    return parentElement;
  }
  function flatTreeChildren(element) {
    if (isSlot(element)) {
      return element.assignedNodes({ flatten: true });
    }
    if (element.shadowRoot) {
      return element.shadowRoot.childNodes;
    }
    return element.childNodes;
  }
  function isCollapsedDetailsContent(child, parent) {
    if (!isClosedDetails(parent)) {
      return false;
    }
    for (let sibling = parent.firstElementChild; sibling; sibling = sibling.nextElementSibling) {
      if (sibling.localName === "summary") {
        return sibling !== child;
      }
    }
    return true;
  }
  function hiddenState(element, context) {
    let state = context.hidden.get(element);
    if (state === void 0) {
      state = computeHiddenState(element, context);
      context.hidden.set(element, state);
    }
    return state;
  }
  function computeHiddenState(element, context) {
    if (isAriaHidden(element) || element.hasAttribute("inert")) {
      return "subtree";
    }
    if (element.localName === "noscript") {
      return "subtree";
    }
    if (element.localName === "area") {
      return areaState(element, context);
    }
    const style = styleOf(element, context);
    if (!style || style.display === "" || style.display === "none") {
      return "subtree";
    }
    const visibility = style.visibility;
    const invisible = visibility === "hidden" || visibility === "collapse";
    const contentsSkipped = style.getPropertyValue("content-visibility") === "hidden";
    if (invisible && contentsSkipped) {
      return "subtree";
    }
    if (contentsSkipped) {
      return "contents";
    }
    if (invisible) {
      return "self";
    }
    return "rendered";
  }
  function isHiddenByAncestor(element, context) {
    let child = element;
    for (; ; ) {
      const parent = flatTreeParent(child);
      if (parent === NOT_RENDERED) {
        return true;
      }
      if (parent === null) {
        return false;
      }
      const state = hiddenState(parent, context);
      if (isCollapsedDetailsContent(child, parent) || state === "subtree" || state === "contents") {
        return true;
      }
      child = parent;
    }
  }
  function isHidden(element, context) {
    const own = hiddenState(element, context);
    if (own === "self" || own === "subtree") {
      return true;
    }
    return isHiddenByAncestor(element, context);
  }

  // javascript/atoms/typescript/core/accessibility/value.ts
  var TEXT_ROLES = /* @__PURE__ */ new Set(["textbox", "searchbox"]);
  var SELECTION_ROLES = /* @__PURE__ */ new Set(["combobox", "listbox"]);
  var RANGE_ROLES = /* @__PURE__ */ new Set(["meter", "progressbar", "scrollbar", "slider", "spinbutton"]);
  function isEmbeddedControl(role) {
    return TEXT_ROLES.has(role) || SELECTION_ROLES.has(role) || RANGE_ROLES.has(role);
  }
  function selectedOptionsText(select) {
    const texts = [];
    for (let i = 0; i < select.options.length; i++) {
      const option = select.options[i];
      if (option.selected) {
        texts.push(option.label || option.text);
      }
    }
    return texts.join(" ");
  }
  function renderedText(element) {
    const text = element.innerText;
    return typeof text === "string" ? text : element.textContent || "";
  }
  function selectedAriaOptions(listbox) {
    const selected2 = listbox.querySelectorAll('[aria-selected="true"]');
    const texts = [];
    for (let i = 0; i < selected2.length; i++) {
      texts.push(renderedText(selected2[i]));
    }
    return texts.join(" ");
  }
  function embeddedValue(element, role) {
    if (RANGE_ROLES.has(role)) {
      const text = element.getAttribute("aria-valuetext");
      if (text !== null && text.trim() !== "") {
        return text.trim();
      }
      const now = element.getAttribute("aria-valuenow");
      if (now !== null) {
        return now.trim();
      }
      return "value" in element ? String(element.value) : null;
    }
    if (TEXT_ROLES.has(role) || SELECTION_ROLES.has(role)) {
      if (element.localName === "select") {
        return selectedOptionsText(element);
      }
      if ("value" in element && typeof element.value === "string") {
        const value = element.value;
        return element.localName === "input" && element.type === "password" ? "\u2022".repeat(value.length) : value;
      }
      if (role === "listbox") {
        return selectedAriaOptions(element);
      }
      return renderedText(element);
    }
    return null;
  }

  // javascript/atoms/typescript/core/accessibility/accname.ts
  var TEXT_NODE = 3;
  var ELEMENT_NODE = 1;
  var NAME_FROM_CONTENT = /* @__PURE__ */ new Set([
    "button",
    "cell",
    "checkbox",
    "columnheader",
    "gridcell",
    "heading",
    "link",
    "menuitem",
    "menuitemcheckbox",
    "menuitemradio",
    "option",
    "radio",
    "row",
    "rowheader",
    "switch",
    "tab",
    "tooltip",
    "treeitem"
  ]);
  var TEXT_INPUT_TYPES = /* @__PURE__ */ new Set(["email", "number", "password", "search", "tel", "text", "url"]);
  var INLINE_DISPLAYS = /* @__PURE__ */ new Set([
    "inline",
    "inline-block",
    "inline-flex",
    "inline-grid",
    "inline-table",
    "contents",
    "ruby",
    "ruby-base",
    "ruby-text",
    ""
  ]);
  function normalize(text) {
    return text.replace(/\s+/g, " ").trim();
  }
  function attribute(element, name) {
    const value = element.getAttribute(name);
    return value !== null && value.trim() !== "" ? value : null;
  }
  function rootNodeOf(element) {
    return element.getRootNode();
  }
  function referencedElements(element, attributeName) {
    const ids = element.getAttribute(attributeName);
    if (!ids) {
      return [];
    }
    const root = rootNodeOf(element);
    const found = [];
    for (const id of ids.trim().split(/\s+/)) {
      const target = root.getElementById(id);
      if (target) {
        found.push(target);
      }
    }
    return found;
  }
  function fromReferences(element, attributeName, t) {
    const parts = [];
    const listed = /* @__PURE__ */ new Set();
    for (const target of referencedElements(element, attributeName)) {
      if (listed.has(target)) {
        continue;
      }
      listed.add(target);
      let text = t.context.referenceTexts.get(target);
      if (text === void 0) {
        text = textAlternative(target, __spreadProps(__spreadValues({}, t), {
          inReference: true,
          recursive: false,
          includeHidden: isHidden(target, t.context),
          skip: null
        }));
        t.context.referenceTexts.set(target, text);
      }
      parts.push(text);
    }
    return normalize(parts.join(" "));
  }
  var GENERATED_CONTENT_SELECTOR = /::?(before|after)\b/i;
  function sheetDefinesGeneratedContent(sheet) {
    let rules;
    try {
      rules = sheet.cssRules;
    } catch (e) {
      return true;
    }
    return rulesDefineGeneratedContent(rules);
  }
  function rulesDefineGeneratedContent(rules) {
    for (let i = 0; i < rules.length; i++) {
      const rule = rules[i];
      if (typeof rule.selectorText === "string" && GENERATED_CONTENT_SELECTOR.test(rule.selectorText)) {
        return true;
      }
      if (rule.styleSheet && sheetDefinesGeneratedContent(rule.styleSheet)) {
        return true;
      }
      if (rule.cssRules && rulesDefineGeneratedContent(rule.cssRules)) {
        return true;
      }
    }
    return false;
  }
  function scopeDefinesGeneratedContent(scope, t) {
    let defines = t.context.generatedScopes.get(scope);
    if (defines === void 0) {
      defines = false;
      const sheets = scope.styleSheets;
      for (let i = 0; i < sheets.length && !defines; i++) {
        defines = sheetDefinesGeneratedContent(sheets[i]);
      }
      const adopted = scope.adoptedStyleSheets;
      if (adopted) {
        for (let i = 0; i < adopted.length && !defines; i++) {
          defines = sheetDefinesGeneratedContent(adopted[i]);
        }
      }
      t.context.generatedScopes.set(scope, defines);
    }
    return defines;
  }
  function mayHaveGeneratedContent(element, t) {
    if (scopeDefinesGeneratedContent(rootNodeOf(element), t)) {
      return true;
    }
    if (element.shadowRoot && scopeDefinesGeneratedContent(element.shadowRoot, t)) {
      return true;
    }
    const slot = element.assignedSlot;
    if (slot && scopeDefinesGeneratedContent(rootNodeOf(slot), t)) {
      return true;
    }
    if (element.hasAttribute("part")) {
      for (let host = rootNodeOf(element).host; host; host = rootNodeOf(host).host) {
        if (scopeDefinesGeneratedContent(rootNodeOf(host), t)) {
          return true;
        }
      }
    }
    return false;
  }
  function pseudoContent(element, pseudo, t) {
    let texts = t.context.generated.get(element);
    if (texts === void 0) {
      texts = mayHaveGeneratedContent(element, t) ? [readPseudoContent(element, "::before", t), readPseudoContent(element, "::after", t)] : ["", ""];
      t.context.generated.set(element, texts);
    }
    return pseudo === "::before" ? texts[0] : texts[1];
  }
  function endOfString(content, start) {
    const quote = content[start];
    let i = start + 1;
    while (i < content.length && content[i] !== quote) {
      if (content[i] === "\\" && i + 1 < content.length) {
        i++;
      }
      i++;
    }
    return i + 1;
  }
  function endOfFunction(content, start) {
    let depth = 0;
    let i = start;
    while (i < content.length) {
      const char = content[i];
      if (char === '"' || char === "'") {
        i = endOfString(content, i);
        continue;
      }
      if (char === "(") {
        depth++;
      } else if (char === ")" && --depth === 0) {
        return i + 1;
      }
      i++;
    }
    return i;
  }
  function readAttrToken(element, token2) {
    const match = /^attr\(\s*([^\s,)]+)/.exec(token2);
    return match ? element.getAttribute(match[1]) || "" : "";
  }
  function readPseudoContent(element, pseudo, t) {
    const style = styleOf(element, t.context, pseudo);
    if (!style || style.display === "none" || style.visibility === "hidden" || style.visibility === "collapse") {
      return "";
    }
    const content = style.content;
    if (!content || content === "none" || content === "normal") {
      return "";
    }
    let text = "";
    let i = 0;
    while (i < content.length) {
      const char = content[i];
      if (char === '"' || char === "'") {
        const end = endOfString(content, i);
        text += content.slice(i + 1, end - 1).replace(/\\(.)/g, "$1");
        i = end;
      } else if (char === "(") {
        const end = endOfFunction(content, i);
        const start = content.lastIndexOf(" ", i) + 1;
        text += readAttrToken(element, content.slice(start, end));
        i = end;
      } else if (char === "/") {
        text = "";
        i++;
      } else {
        i++;
      }
    }
    return text;
  }
  function isInline(element, t) {
    const style = styleOf(element, t.context);
    return !style || INLINE_DISPLAYS.has(style.display);
  }
  function fromContent(element, t) {
    const cacheable = !t.inReference && !t.includeHidden && t.skip === null && !t.describing;
    if (!cacheable) {
      return computeContentText(element, t);
    }
    let text = t.context.contentTexts.get(element);
    if (text === void 0) {
      text = computeContentText(element, t);
      t.context.contentTexts.set(element, text);
    }
    return text;
  }
  function computeContentText(element, t) {
    const ownTextHidden = !t.includeHidden && hiddenState(element, t.context) === "self";
    let text = ownTextHidden ? "" : pseudoContent(element, "::before", t);
    const textCollapsed = isClosedDetails(element);
    const children = flatTreeChildren(element);
    for (let i = 0; i < children.length; i++) {
      const child = children[i];
      if (child.nodeType === TEXT_NODE) {
        if (!ownTextHidden && !textCollapsed) {
          text += child.nodeValue || "";
        }
        continue;
      }
      if (child.nodeType !== ELEMENT_NODE) {
        continue;
      }
      const childElement = child;
      if (childElement === t.skip || isCollapsedDetailsContent(childElement, childElement.parentElement || element)) {
        continue;
      }
      if (childElement.localName === "br") {
        text += " ";
        continue;
      }
      const childState = t.includeHidden ? "rendered" : hiddenState(childElement, t.context);
      if (childState === "subtree" || childState === "contents") {
        continue;
      }
      const childText = childState === "self" ? fromContent(childElement, __spreadProps(__spreadValues({}, t), { recursive: true })) : textAlternative(childElement, __spreadProps(__spreadValues({}, t), { recursive: true }));
      text += isInline(childElement, t) ? childText : ` ${childText} `;
    }
    return text + (ownTextHidden ? "" : pseudoContent(element, "::after", t));
  }
  function firstChildNamed(element, localName) {
    for (let child = element.firstElementChild; child; child = child.nextElementSibling) {
      if (child.localName === localName) {
        return child;
      }
    }
    return null;
  }
  function fromLabels(element, t) {
    const labels = element.labels;
    if (!labels || labels.length === 0) {
      return null;
    }
    const parts = [];
    for (let i = 0; i < labels.length; i++) {
      const label = labels[i];
      parts.push(fromContent(label, __spreadProps(__spreadValues({}, t), { recursive: true, includeHidden: isHidden(label, t.context), skip: element })));
    }
    const text = normalize(parts.join(" "));
    return text !== "" ? text : null;
  }
  function inputNativeName(input, t) {
    switch (input.type) {
      case "button":
      case "reset":
      case "submit": {
        const label = fromLabels(input, t);
        if (label !== null) {
          return label;
        }
        const value = attribute(input, "value");
        if (value !== null) {
          return value;
        }
        return input.type === "submit" ? "Submit" : input.type === "reset" ? "Reset" : null;
      }
      case "image":
        return attribute(input, "alt") || fromLabels(input, t) || attribute(input, "value");
      default:
        return fromLabels(input, t);
    }
  }
  function nativeName(element, t) {
    switch (element.localName) {
      case "html":
        return (element.ownerDocument.title || "").trim() || null;
      case "input":
        return inputNativeName(element, t);
      case "button":
      case "meter":
      case "output":
      case "progress":
      case "select":
      case "textarea":
        return fromLabels(element, t);
      case "fieldset": {
        const legend = firstChildNamed(element, "legend");
        return legend ? normalize(fromContent(legend, __spreadProps(__spreadValues({}, t), { recursive: true }))) || null : null;
      }
      case "figure": {
        const caption = firstChildNamed(element, "figcaption");
        return caption ? normalize(fromContent(caption, __spreadProps(__spreadValues({}, t), { recursive: true }))) || null : null;
      }
      case "table": {
        const caption = firstChildNamed(element, "caption");
        return caption ? normalize(fromContent(caption, __spreadProps(__spreadValues({}, t), { recursive: true }))) || null : null;
      }
      case "img":
      case "area":
        return attribute(element, "alt");
      case "optgroup":
        return attribute(element, "label");
      case "option":
        return attribute(element, "label");
      case "svg": {
        const title = firstChildNamed(element, "title");
        return title ? normalize(title.textContent || "") || null : null;
      }
      default:
        return null;
    }
  }
  function placeholder(element) {
    if (element.localName === "textarea") {
      return attribute(element, "placeholder");
    }
    if (element.localName === "input" && TEXT_INPUT_TYPES.has(element.type)) {
      return attribute(element, "placeholder");
    }
    return null;
  }
  function isStandardDescendantTraversal(t) {
    return t.recursive && !t.inReference && !t.includeHidden && t.skip === null && !t.describing;
  }
  function textAlternative(node, t) {
    if (node.nodeType === TEXT_NODE) {
      return node.nodeValue || "";
    }
    if (node.nodeType !== ELEMENT_NODE) {
      return "";
    }
    const element = node;
    if (!isStandardDescendantTraversal(t)) {
      return computeTextAlternative(element, t).text;
    }
    let text = t.context.descendantTexts.get(element);
    if (text === void 0) {
      text = computeTextAlternative(element, t).text;
      t.context.descendantTexts.set(element, text);
    }
    return text;
  }
  function computeTextAlternative(element, t) {
    const role = roleOf(element, t.context);
    const embedded = (t.recursive || t.inReference) && isEmbeddedControl(role);
    if (!t.inReference) {
      const referenced = fromReferences(element, t.describing ? "aria-describedby" : "aria-labelledby", t);
      if (referenced !== "") {
        return { text: referenced, source: "reference" };
      }
    }
    if (!t.describing || t.inReference) {
      const label = attribute(element, "aria-label");
      if (label !== null && !embedded) {
        return { text: normalize(label), source: "label" };
      }
    }
    if (embedded) {
      const value = embeddedValue(element, role);
      if (value !== null) {
        return { text: normalize(value), source: "native" };
      }
    }
    if ((element.localName === "img" || element.localName === "area") && element.hasAttribute("alt")) {
      return { text: normalize(element.getAttribute("alt") || ""), source: "native" };
    }
    const native = nativeName(element, t);
    if (native !== null && normalize(native) !== "") {
      return { text: normalize(native), source: "native" };
    }
    if (NAME_FROM_CONTENT.has(role) || t.recursive || t.inReference) {
      const content = normalize(fromContent(element, t));
      if (content !== "") {
        return { text: content, source: "content" };
      }
    }
    const title = attribute(element, "title");
    if (title !== null) {
      return { text: normalize(title), source: "title" };
    }
    const hint = placeholder(element);
    if (hint !== null) {
      return { text: normalize(hint), source: "placeholder" };
    }
    return { text: "", source: "none" };
  }
  function traversal(context, describing) {
    return { context, describing, inReference: false, recursive: false, includeHidden: false, skip: null };
  }
  function computeName(element, context) {
    let result = context.names.get(element);
    if (result === void 0) {
      result = computeTextAlternative(element, traversal(context, false));
      context.names.set(element, result);
    }
    return result;
  }
  function computeDescription(element, context) {
    let description = context.descriptions.get(element);
    if (description === void 0) {
      description = fromReferences(element, "aria-describedby", traversal(context, true));
      if (description === "") {
        const inline = attribute(element, "aria-description");
        if (inline !== null) {
          description = normalize(inline);
        } else {
          const title = attribute(element, "title");
          description = title !== null && computeName(element, context).source !== "title" ? normalize(title) : "";
        }
      }
      context.descriptions.set(element, description);
    }
    return description;
  }

  // javascript/atoms/typescript/core/enabled.ts
  var DISABLED_ATTRIBUTE_SUPPORTED = ["BUTTON", "INPUT", "OPTGROUP", "OPTION", "SELECT", "TEXTAREA"];
  function getPreviousElementSibling(node) {
    let sibling = node.previousSibling;
    while (sibling && sibling.nodeType !== 1) {
      sibling = sibling.previousSibling;
    }
    return sibling;
  }
  function isInsideDisabledFieldset(element) {
    let node = element;
    while (node) {
      const parent = node.parentNode;
      if (parent && isElement(parent, "FIELDSET") && getProperty(parent, "disabled")) {
        if (!isElement(node, "LEGEND")) {
          return true;
        }
        let sibling = getPreviousElementSibling(node);
        while (sibling) {
          if (isElement(sibling, "LEGEND")) {
            return true;
          }
          sibling = getPreviousElementSibling(sibling);
        }
      }
      node = parent;
    }
    return false;
  }
  function isEnabled(element) {
    const isSupported = DISABLED_ATTRIBUTE_SUPPORTED.some((tagName) => isElement(element, tagName));
    if (!isSupported) {
      return true;
    }
    if (getProperty(element, "disabled")) {
      return false;
    }
    const parent = element.parentNode;
    if (parent && parent.nodeType === 1 && isElement(element, "OPTGROUP") || isElement(element, "OPTION")) {
      return isEnabled(parent);
    }
    return !isInsideDisabledFieldset(element);
  }

  // javascript/atoms/typescript/core/accessibility/states.ts
  var CHECKED_ROLES = /* @__PURE__ */ new Set(["checkbox", "menuitemcheckbox", "menuitemradio", "radio", "switch"]);
  var MIXED_ALLOWED = /* @__PURE__ */ new Set(["checkbox", "menuitemcheckbox"]);
  var ALWAYS_SELECTED_ROLES = /* @__PURE__ */ new Set(["option", "tab", "treeitem"]);
  var SELECTABLE_ROLES = /* @__PURE__ */ new Set(["columnheader", "gridcell", "row", "rowheader"]);
  var LEVEL_ROLES = /* @__PURE__ */ new Set(["comment", "listitem", "row", "tablist", "treeitem"]);
  var VALUE_ROLES = /* @__PURE__ */ new Set([
    "combobox",
    "meter",
    "progressbar",
    "scrollbar",
    "searchbox",
    "slider",
    "spinbutton",
    "textbox"
  ]);
  var DISABLEABLE_ELEMENTS = /* @__PURE__ */ new Set(["button", "input", "optgroup", "option", "select", "textarea"]);
  function token(element, name) {
    const value = element.getAttribute(name);
    return value === null ? null : value.trim().toLowerCase();
  }
  function optionalToken(element, name) {
    const value = token(element, name);
    return value === "" || value === "undefined" ? null : value;
  }
  function tristate(element, name, allowMixed) {
    const value = token(element, name);
    if (value === "true") {
      return true;
    }
    if (value === "mixed" && allowMixed) {
      return "mixed";
    }
    return false;
  }
  function checked(element, role) {
    if (element.localName === "input") {
      const input = element;
      if (input.type === "checkbox" || input.type === "radio") {
        return input.indeterminate && MIXED_ALLOWED.has(role) ? "mixed" : input.checked;
      }
    }
    return tristate(element, "aria-checked", MIXED_ALLOWED.has(role));
  }
  function expanded(element) {
    const value = optionalToken(element, "aria-expanded");
    if (value !== null) {
      return value === "true";
    }
    if (element.localName === "summary") {
      const details = element.parentElement;
      if (details && details.localName === "details") {
        return details.hasAttribute("open");
      }
    }
    return null;
  }
  function selected(element, role) {
    if (element.localName === "option" && role === "option") {
      return element.selected;
    }
    if (ALWAYS_SELECTED_ROLES.has(role)) {
      return token(element, "aria-selected") === "true";
    }
    if (SELECTABLE_ROLES.has(role)) {
      const value = optionalToken(element, "aria-selected");
      return value === null ? null : value === "true";
    }
    return null;
  }
  function ariaLevel(element) {
    const value = element.getAttribute("aria-level");
    if (value === null || !/^\s*\d+\s*$/.test(value)) {
      return null;
    }
    const level2 = parseInt(value, 10);
    return level2 >= 1 ? level2 : null;
  }
  function level(element, role) {
    if (role === "heading") {
      const explicit = ariaLevel(element);
      if (explicit !== null) {
        return explicit;
      }
      const tag = /^h([1-6])$/.exec(element.localName);
      return tag ? Number(tag[1]) : 2;
    }
    return LEVEL_ROLES.has(role) ? ariaLevel(element) : null;
  }
  function setsAriaDisabled(element) {
    return token(element, "aria-disabled") === "true";
  }
  function parentOrHost(element) {
    if (element.parentElement) {
      return element.parentElement;
    }
    return element.getRootNode().host || null;
  }
  function isDisabledByAncestor(element) {
    for (let current = parentOrHost(element); current; current = parentOrHost(current)) {
      if (setsAriaDisabled(current)) {
        return true;
      }
    }
    return false;
  }
  function disabled(element, disabledByAncestor) {
    if (setsAriaDisabled(element) || disabledByAncestor && canTakeFocus(element)) {
      return true;
    }
    return DISABLEABLE_ELEMENTS.has(element.localName) && !isEnabled(element);
  }
  function focused(element) {
    const doc = element.ownerDocument;
    if (element === doc.body || element === doc.documentElement) {
      return false;
    }
    const root = element.getRootNode();
    if (root.activeElement !== element) {
      return false;
    }
    return !(element.shadowRoot && element.shadowRoot.activeElement);
  }
  function computeStates(element, role, disabledByAncestor) {
    const states = {};
    if (CHECKED_ROLES.has(role)) {
      states.checked = checked(element, role);
    }
    if (role === "button") {
      const pressed = optionalToken(element, "aria-pressed");
      if (pressed !== null) {
        states.pressed = tristate(element, "aria-pressed", true);
      }
    }
    const isExpanded = expanded(element);
    if (isExpanded !== null) {
      states.expanded = isExpanded;
    }
    const isSelected = selected(element, role);
    if (isSelected !== null) {
      states.selected = isSelected;
    }
    const headingLevel = level(element, role);
    if (headingLevel !== null) {
      states.level = headingLevel;
    }
    if (disabled(element, disabledByAncestor)) {
      states.disabled = true;
    }
    if (focused(element)) {
      states.focused = true;
    }
    return states;
  }
  function computeValue(element, role) {
    return VALUE_ROLES.has(role) ? embeddedValue(element, role) : null;
  }

  // javascript/atoms/typescript/core/accessibility/tree.ts
  var ELEMENT_NODE2 = 1;
  var TEXT_NODE2 = 3;
  var CHILDREN_PRESENTATIONAL = /* @__PURE__ */ new Set([
    "button",
    "checkbox",
    "graphics-symbol",
    "img",
    "menuitemcheckbox",
    "menuitemradio",
    "meter",
    "option",
    "progressbar",
    "radio",
    "scrollbar",
    "separator",
    "slider",
    "switch",
    "tab"
  ]);
  var LEAF_ELEMENTS = /* @__PURE__ */ new Set(["audio", "frame", "iframe", "textarea", "video"]);
  function textLeaf(text) {
    return { role: "text", name: text, description: "", states: {}, children: [] };
  }
  function elementNode(element, role, name, context, disabledByAncestor) {
    const node = {
      role,
      name,
      description: computeDescription(element, context),
      states: computeStates(element, role, disabledByAncestor),
      element,
      children: []
    };
    const value = computeValue(element, role);
    if (value !== null) {
      node.value = value;
    }
    const url = linkUrl(element, role);
    if (url !== null) {
      node.url = url;
    }
    return node;
  }
  var HTML_NAMESPACE = "http://www.w3.org/1999/xhtml";
  function linkUrl(element, role) {
    if (role !== "link" || element.namespaceURI !== HTML_NAMESPACE) {
      return null;
    }
    const local = element.localName;
    if (local !== "a" && local !== "area" || !element.hasAttribute("href")) {
      return null;
    }
    return element.href;
  }
  function normalizeText(text) {
    return text.replace(/\s+/g, " ").trim();
  }
  function producesNode(role, name, context) {
    return !context.interestingOnly || !(role === "generic" || isPresentational(role)) || name !== "";
  }
  function isLeaf(element, role) {
    return LEAF_ELEMENTS.has(element.localName) || CHILDREN_PRESENTATIONAL.has(role);
  }
  function visitElement(element, context, above, out) {
    if (context.placed.has(element)) {
      return;
    }
    context.placed.add(element);
    const inherited = above.disabled || !setsAriaDisabled(element) ? above : __spreadProps(__spreadValues({}, above), { disabled: true });
    const domParent = element.parentElement;
    if (domParent && isCollapsedDetailsContent(element, domParent)) {
      return;
    }
    const hidden = hiddenState(element, context);
    if (hidden === "subtree") {
      return;
    }
    if (hidden === "self") {
      collectChildren(element, context, __spreadProps(__spreadValues({}, inherited), { textHidden: true }), out);
      return;
    }
    const role = roleOf(element, context);
    const name = computeName(element, context);
    const descend = hidden !== "contents" && !isLeaf(element, role);
    if (!producesNode(role, name.text, context)) {
      if (descend) {
        collectChildren(element, context, __spreadProps(__spreadValues({}, inherited), { textHidden: false }), out);
      }
      return;
    }
    const node = elementNode(element, role, name.text, context, above.disabled);
    if (descend) {
      collectChildren(
        element,
        context,
        __spreadProps(__spreadValues({}, inherited), { textHidden: false, textConsumed: inherited.textConsumed || name.source === "content" }),
        node.children
      );
    }
    out.push(node);
  }
  function collectChildren(parent, context, inherited, out) {
    const textCollapsed = isClosedDetails(parent);
    const children = flatTreeChildren(parent);
    for (let i = 0; i < children.length; i++) {
      const child = children[i];
      if (child.nodeType === TEXT_NODE2) {
        if (!inherited.textHidden && !inherited.textConsumed && !textCollapsed) {
          const text = normalizeText(child.nodeValue || "");
          if (text !== "") {
            out.push(textLeaf(text));
          }
        }
        continue;
      }
      if (child.nodeType === ELEMENT_NODE2 && !context.claimed.has(child)) {
        visitElement(child, context, inherited, out);
      }
    }
    const owned = context.owned.get(parent);
    if (owned) {
      for (const element of owned) {
        if (isHiddenByAncestor(element, context)) {
          continue;
        }
        visitElement(element, context, __spreadProps(__spreadValues({}, inherited), { disabled: isDisabledByAncestor(element) }), out);
      }
    }
  }
  function wouldCycle(target, owner, ownerOf) {
    for (let current = owner; current; current = ownerOf.get(current) || current.parentElement) {
      if (target.contains(current)) {
        return true;
      }
    }
    return false;
  }
  function collectOwners(element, out) {
    if (element.hasAttribute("aria-owns")) {
      out.push(element);
    }
    const children = flatTreeChildren(element);
    for (let i = 0; i < children.length; i++) {
      const child = children[i];
      if (child.nodeType === ELEMENT_NODE2) {
        collectOwners(child, out);
      }
    }
  }
  function recordOwnership(root, context) {
    const owners = [];
    collectOwners(root, owners);
    const ownerOf = /* @__PURE__ */ new Map();
    for (const owner of owners) {
      if (isLeaf(owner, roleOf(owner, context))) {
        continue;
      }
      const scope = owner.getRootNode();
      const targets = [];
      for (const id of (owner.getAttribute("aria-owns") || "").trim().split(/\s+/)) {
        const target = id ? scope.getElementById(id) : null;
        if (target && !context.claimed.has(target) && !wouldCycle(target, owner, ownerOf)) {
          targets.push(target);
          context.claimed.add(target);
          ownerOf.set(target, owner);
        }
      }
      if (targets.length) {
        context.owned.set(owner, targets);
      }
    }
  }
  function buildTree(root, context) {
    recordOwnership(root, context);
    context.placed.add(root);
    const role = roleOf(root, context);
    const name = computeName(root, context);
    const disabledByAncestor = isDisabledByAncestor(root);
    const node = elementNode(root, role, name.text, context, disabledByAncestor);
    const hidden = hiddenState(root, context);
    const descend = hidden !== "subtree" && hidden !== "contents" && !isLeaf(root, role) && !isHiddenByAncestor(root, context);
    if (descend) {
      collectChildren(
        root,
        context,
        {
          textHidden: hidden === "self",
          textConsumed: name.source === "content",
          disabled: disabledByAncestor || setsAriaDisabled(root)
        },
        node.children
      );
    }
    return node;
  }

  // javascript/atoms/typescript/core/accessibility/snapshot.ts
  var DOCUMENT_NODE2 = 9;
  function isDocument(node) {
    return !!node && typeof node === "object" && node.nodeType === DOCUMENT_NODE2;
  }
  function resolveRoot(root) {
    if (root === void 0 || root === null) {
      return document.documentElement;
    }
    if (isDocument(root)) {
      return root.documentElement;
    }
    if (!isElement(root)) {
      throw new Error("accessibilitySnapshot: root must be an Element or a Document");
    }
    if (!root.isConnected) {
      throw new Error("accessibilitySnapshot: root is detached from its document");
    }
    return root;
  }
  function accessibilitySnapshot(root, options) {
    return buildTree(resolveRoot(root), createContext(options));
  }
  var snapshot_default = accessibilitySnapshot;

  // javascript/atoms/typescript/core/accessibility/wire.ts
  function encodeWire(tree) {
    const elements = [];
    const windows = [];
    function encode(node) {
      const out = { role: node.role, name: node.name, description: node.description, states: node.states, children: [] };
      if (node.value !== void 0) {
        out.value = node.value;
      }
      if (node.url !== void 0) {
        out.url = node.url;
      }
      if (node.element) {
        out.element = elements.push(node.element) - 1;
        const window = node.role === "iframe" ? node.element.contentWindow : null;
        if (window) {
          out.frame = windows.push(window) - 1;
        }
      }
      out.children = node.children.map(encode);
      return out;
    }
    return { node: encode(tree), elements, windows };
  }
  function accessibilitySnapshotWire(root, options) {
    if (root === null) {
      return null;
    }
    if (root !== void 0) {
      if (!isElement(root)) {
        throw new Error("accessibilitySnapshotWire: root must be an Element");
      }
      if (root.ownerDocument !== document) {
        return null;
      }
      if (!root.isConnected) {
        return { error: "detached" };
      }
    }
    const { node, elements, windows } = encodeWire(snapshot_default(root, options));
    return { json: JSON.stringify(node), elements, windows };
  }
  var wire_default = accessibilitySnapshotWire;
  return __toCommonJS(accessibility_snapshot_wire_exports);
})();
return __seleniumAtom.default;
})()
