/** Sales A/R admin: line Item + Whs autocomplete (+ Dscription fill). */
(function () {
  "use strict";
  if (window.ErpAdminAc && window.ErpAdminAc.mount) {
    window.ErpAdminAc.mount({
      itemInline: true,
      whsInline: true,
      fillDscription: true,
    });
  }
})();
