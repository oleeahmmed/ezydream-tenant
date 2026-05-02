/** Purchase A/P admin: line Item + Whs autocomplete (+ Dscription on PRQ1). */
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
