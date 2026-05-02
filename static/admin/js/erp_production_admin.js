/** Production admin: BOM / order lines Item + Whs autocomplete. */
(function () {
  "use strict";
  if (window.ErpAdminAc && window.ErpAdminAc.mount) {
    window.ErpAdminAc.mount({
      itemInline: true,
      whsInline: true,
      itemHeader: true,
      whsHeader: true,
    });
  }
})();
