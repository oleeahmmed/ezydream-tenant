/** Inventory docs admin: Item, Whs, From warehouse, G/L on issue lines. */
(function () {
  "use strict";
  if (window.ErpAdminAc && window.ErpAdminAc.mount) {
    window.ErpAdminAc.mount({
      itemInline: true,
      whsInline: true,
      fromWhsInline: true,
      glAccountFields: true,
      itemHeader: true,
    });
  }
})();
