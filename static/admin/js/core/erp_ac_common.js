/**
 * Shared staff-session autocomplete for Django admin (Unfold).
 * Endpoints: /admin/erp-search/items | warehouses | gl-accounts
 * Per-app scripts call ErpAdminAc.mount({ ... }) after this file loads.
 */
(function () {
  "use strict";

  var DEBOUNCE_MS = 220;
  var ITEM_MIN = 1;
  var WHS_MIN = 0;
  var GL_MIN = 1;

  var merged = {
    itemInline: false,
    fillDscription: false,
    whsInline: false,
    fromWhsInline: false,
    glAccountFields: false,
    itemHeader: false,
    whsHeader: false,
  };
  var installed = false;

  function merge(opts) {
    Object.assign(merged, opts || {});
  }

  function debounce(fn, ms) {
    var t;
    return function () {
      var ctx = this;
      var args = arguments;
      clearTimeout(t);
      t = setTimeout(function () {
        fn.apply(ctx, args);
      }, ms);
    };
  }

  function fetchJSON(url) {
    return fetch(url, {
      credentials: "same-origin",
      headers: { Accept: "application/json" },
    }).then(function (r) {
      if (!r.ok) {
        throw new Error("HTTP " + r.status);
      }
      return r.json();
    });
  }

  function removePanel(panel) {
    if (panel && panel.parentNode) {
      panel.parentNode.removeChild(panel);
    }
  }

  function placePanel(panel, anchor) {
    var rect = anchor.getBoundingClientRect();
    panel.style.position = "fixed";
    panel.style.left = Math.max(8, rect.left) + "px";
    panel.style.top = rect.bottom + 4 + "px";
    panel.style.zIndex = "10000";
    panel.style.maxHeight = "220px";
    panel.style.overflow = "auto";
    panel.style.minWidth = "260px";
    panel.style.background = "var(--color-bg-base, var(--body-bg, #fff))";
    panel.style.border = "1px solid var(--color-border-base, #ccc)";
    panel.style.boxShadow = "0 4px 12px rgba(0,0,0,.12)";
    panel.style.borderRadius = "4px";
    panel.style.fontSize = "13px";
    document.body.appendChild(panel);
  }

  function isItemCodeName(name) {
    return /-ItemCode$/.test(name) && name.indexOf("__prefix__") === -1;
  }

  function isWhsName(name) {
    return /-WhsCode$/.test(name) && name.indexOf("__prefix__") === -1;
  }

  function isFromWhsName(name) {
    return /-FromWhsCod$/.test(name) && name.indexOf("__prefix__") === -1;
  }

  function isBareItemCode(name) {
    return name === "ItemCode";
  }

  function isBareWhsCode(name) {
    return name === "WhsCode";
  }

  function isGlAccountName(name) {
    if (name.indexOf("__prefix__") !== -1) {
      return false;
    }
    if (name === "CashAcct" || name === "CheckAcct" || name === "BankAcct" || name === "FatherNum") {
      return true;
    }
    if (name === "Account") {
      return true;
    }
    return /-Account$/.test(name);
  }

  function bindPicker(input, kind) {
    if (input.dataset.erpAcBound) {
      return;
    }
    input.dataset.erpAcBound = "1";

    var panel = null;
    var minLen =
      kind === "item" ? ITEM_MIN : kind === "gl" ? GL_MIN : WHS_MIN;

    function close() {
      removePanel(panel);
      panel = null;
    }

    document.addEventListener("click", function (ev) {
      if (panel && !panel.contains(ev.target) && ev.target !== input) {
        close();
      }
    });

    input.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") {
        close();
      }
    });

    var run = debounce(function () {
      close();
      var q = input.value.trim();
      if (kind === "item" && q.length < minLen) {
        return;
      }
      if (kind === "gl" && q.length < minLen) {
        return;
      }
      var url;
      if (kind === "item") {
        url = "/admin/erp-search/items?limit=25&q=" + encodeURIComponent(q);
      } else if (kind === "gl") {
        url = "/admin/erp-search/gl-accounts?limit=25&q=" + encodeURIComponent(q);
      } else {
        url = "/admin/erp-search/warehouses?limit=25&q=" + encodeURIComponent(q);
      }
      fetchJSON(url)
        .then(function (data) {
          close();
          var items = data.items || [];
          if (!items.length) {
            return;
          }
          panel = document.createElement("div");
          panel.className = "erp-ac-panel";
          items.forEach(function (row) {
            var btn = document.createElement("button");
            btn.type = "button";
            btn.style.display = "block";
            btn.style.width = "100%";
            btn.style.textAlign = "left";
            btn.style.padding = "6px 10px";
            btn.style.border = "none";
            btn.style.borderBottom = "1px solid var(--color-border-base, #eee)";
            btn.style.background = "transparent";
            btn.style.cursor = "pointer";
            if (kind === "item") {
              btn.textContent = row.ItemCode + " — " + (row.ItemName || "");
              btn.addEventListener("mousedown", function (e) {
                e.preventDefault();
                input.value = row.ItemCode;
                input.dispatchEvent(new Event("input", { bubbles: true }));
                input.dispatchEvent(new Event("change", { bubbles: true }));
                var tr = input.closest("tr");
                if (tr && merged.fillDscription) {
                  var desc = tr.querySelector('input[name$="-Dscription"]');
                  if (desc && row.ItemName) {
                    desc.value = row.ItemName;
                    desc.dispatchEvent(new Event("change", { bubbles: true }));
                  }
                }
                close();
                input.focus();
              });
            } else if (kind === "gl") {
              btn.textContent = row.AcctCode + " — " + (row.AcctName || "");
              btn.addEventListener("mousedown", function (e) {
                e.preventDefault();
                input.value = row.AcctCode;
                input.dispatchEvent(new Event("change", { bubbles: true }));
                close();
                input.focus();
              });
            } else {
              btn.textContent = row.WhsCode + " — " + (row.WhsName || "");
              btn.addEventListener("mousedown", function (e) {
                e.preventDefault();
                input.value = row.WhsCode;
                input.dispatchEvent(new Event("change", { bubbles: true }));
                close();
                input.focus();
              });
            }
            btn.addEventListener("mouseenter", function () {
              btn.style.background = "var(--color-bg-subtle, #f0f0f0)";
            });
            btn.addEventListener("mouseleave", function () {
              btn.style.background = "transparent";
            });
            panel.appendChild(btn);
          });
          placePanel(panel, input);
        })
        .catch(function () {
          close();
        });
    }, DEBOUNCE_MS);

    input.addEventListener("input", run);
    input.addEventListener("focus", run);
  }

  function onFocusIn(ev) {
    var t = ev.target;
    if (!t || t.tagName !== "INPUT") {
      return;
    }
    var name = t.getAttribute("name") || "";
    if (merged.itemInline && isItemCodeName(name)) {
      bindPicker(t, "item");
    }
    if (merged.itemHeader && isBareItemCode(name)) {
      bindPicker(t, "item");
    }
    if (merged.whsInline && isWhsName(name)) {
      bindPicker(t, "whs");
    }
    if (merged.whsHeader && isBareWhsCode(name)) {
      bindPicker(t, "whs");
    }
    if (merged.fromWhsInline && isFromWhsName(name)) {
      bindPicker(t, "whs");
    }
    if (merged.glAccountFields && isGlAccountName(name)) {
      bindPicker(t, "gl");
    }
  }

  window.ErpAdminAc = {
    mount: function (opts) {
      merge(opts);
      if (!installed) {
        installed = true;
        document.addEventListener("focusin", onFocusIn, true);
      }
    },
  };
})();
