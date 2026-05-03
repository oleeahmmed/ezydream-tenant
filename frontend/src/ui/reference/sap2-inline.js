/** Extracted from frontend/ui/sap2.html (<script> block) for reference — not imported by the app. */
   /* ══════════════════════════════════════════
         Tab switching
      ══════════════════════════════════════════ */
      function switchTab(el, tabId) {
        document.querySelectorAll('.sap-tab').forEach(function(t){ t.classList.remove('active'); });
        el.classList.add('active');
        var panels = ['contents','logistics','accounting','edocs','attachments'];
        panels.forEach(function(id) {
          var p = document.getElementById('panel-' + id);
          if (p) { p.classList.remove('active'); p.style.display = 'none'; }
        });
        var target = document.getElementById('panel-' + tabId);
        if (target) {
          target.classList.add('active');
          target.style.display = (tabId === 'contents') ? 'flex' : 'block';
          target.style.flexDirection = (tabId === 'contents') ? 'column' : '';
        }
      }

      /* ══════════════════════════════════════════
         Grid row selection
      ══════════════════════════════════════════ */
      function selectRow(row) {
        document.querySelectorAll('#gridBody tr').forEach(function(r){ r.classList.remove('selected'); });
        row.classList.add('selected');
      }

      /* ══════════════════════════════════════════
         Context Menu
      ══════════════════════════════════════════ */
      var ctxMenu = document.getElementById('ctxMenu');
      var activeRow = null;

      function showCtxMenu(e) {
        e.preventDefault();
        ctxMenu.style.left = Math.min(e.clientX, window.innerWidth - 230) + 'px';
        ctxMenu.style.top  = Math.min(e.clientY, window.innerHeight - 420) + 'px';
        ctxMenu.classList.add('visible');
        activeRow = e.target.closest('tr');
      }

      document.addEventListener('click', function(e) {
        if (!ctxMenu.contains(e.target)) ctxMenu.classList.remove('visible');
      });

      var rowCounter = 2;
      function ctxAction(action) {
        ctxMenu.classList.remove('visible');
        var tbody = document.getElementById('gridBody');
        if (action === 'addRow') {
          rowCounter++;
          var tr = document.createElement('tr');
          tr.className = 'sap-grid-row';
          tr.setAttribute('onclick', 'selectRow(this)');
          tr.innerHTML = '<td class="row-num">' + rowCounter + '</td>' +
            '<td class="cell-blue" onclick="openItemSearch(this)" style="cursor:pointer;"></td>' +
            '<td><input class="cell-input" type="text" value="" /></td>' +
            '<td><input class="cell-input" type="text" value="" /></td>' +
            '<td><input class="cell-input" type="text" value="" /></td>' +
            '<td><input class="cell-input" type="text" value="" /></td>' +
            '<td></td><td></td><td></td><td></td>';
          tbody.appendChild(tr);
        } else if (action === 'deleteRow') {
          if (activeRow && tbody.rows.length > 1) activeRow.remove();
        } else if (action === 'duplicateRow') {
          if (activeRow) {
            rowCounter++;
            var clone = activeRow.cloneNode(true);
            clone.cells[0].textContent = rowCounter;
            clone.setAttribute('onclick', 'selectRow(this)');
            activeRow.parentNode.insertBefore(clone, activeRow.nextSibling);
          }
        } else if (action === 'calculator') {
          alert('Calculator – Feature available in full SAP B1');
        } else if (action === 'rowDetails') {
          openRowDetails(activeRow);
        } else if (action === 'paymentMeans') {
          alert('Payment Means – Opens payment allocation dialog');
        } else if (action === 'grossProfit') {
          alert('Gross Profit – Opens GP analysis dialog');
        } else if (action === 'batchSerial') {
          alert('Batch/Serial Numbers – Opens batch tracking dialog');
        } else if (action === 'volumeWeight') {
          alert('Volume and Weight Calculation – Feature available in SAP B1');
        } else if (action === 'newActivity') {
          alert('New Activity – Opens activity / task dialog');
        } else if (action === 'cut') {
          document.execCommand('cut');
        } else if (action === 'copy') {
          document.execCommand('copy');
        } else if (action === 'paste') {
          alert('Paste – Use Ctrl+V to paste');
        }
      }

      /* ══════════════════════════════════════════
         Toolbar Actions
      ══════════════════════════════════════════ */
      function toolbarAction(action) {
        var labels = {
          'new': 'New Sales Order form opened.',
          'open': 'Open document dialog – Browse existing Sales Orders.',
          'save': 'Document saved successfully.',
          'print': 'Sending document to printer...',
          'printPreview': 'Opening print preview...',
          'email': 'Compose email with document attached.',
          'workflow': 'Workflow manager opened.',
          'approval': 'Approval status dialog opened.',
          'attachments': 'Switch to Attachments tab.',
          'docRemarks': 'Remarks field is at the bottom of the Contents tab.',
          'paymentMeans': 'Payment Means – Opens payment allocation dialog.',
          'grossProfit': 'Gross Profit – Opens GP analysis dialog.'
        };
        if (action === 'attachments') {
          var tab = document.querySelector('.sap-tab:nth-child(5)');
          if (tab) tab.click();
        } else {
          alert(labels[action] || action);
        }
      }

      /* ══════════════════════════════════════════
         Modal helpers
      ══════════════════════════════════════════ */
      function openModal(id) { document.getElementById(id).classList.add('visible'); }
      function closeModal(id) { document.getElementById(id).classList.remove('visible'); }

      /* ══════════════════════════════════════════
         Copy To Flow
      ══════════════════════════════════════════ */
      function openCopyToDialog() { openModal('copyToModal'); }

      function doCopyTo() {
        var type = document.querySelector('input[name="copyToType"]:checked').value;
        var date = document.getElementById('copyToDate').value || '27.04.21';
        var delivDate = document.getElementById('copyToDelivDate').value || date;
        var labels = { delivery: 'Delivery', invoice: 'A/R Invoice', reserve: 'Reserve Invoice' };
        var docNum = Math.floor(10000 + Math.random() * 89999);

        closeModal('copyToModal');

        document.getElementById('copyDoneTitle').textContent = labels[type] + ' Created';
        document.getElementById('copyDoneBody').innerHTML =
          '<p style="margin-bottom:8px;">Sales Order <strong>#1229</strong> was successfully copied to:</p>' +
          '<table style="font-size:11px; border-collapse:collapse; width:100%;">' +
          '<tr><td style="padding:3px 8px 3px 0; color:#555; width:130px;">Document Type</td><td><strong>' + labels[type] + '</strong></td></tr>' +
          '<tr><td style="padding:3px 8px 3px 0; color:#555;">Document No.</td><td><strong>' + docNum + '</strong></td></tr>' +
          '<tr><td style="padding:3px 8px 3px 0; color:#555;">Customer</td><td>C20000 – Maxi-Teq</td></tr>' +
          '<tr><td style="padding:3px 8px 3px 0; color:#555;">Posting Date</td><td>' + date + '</td></tr>' +
          '<tr><td style="padding:3px 8px 3px 0; color:#555;">Delivery Date</td><td>' + delivDate + '</td></tr>' +
          '<tr><td style="padding:3px 8px 3px 0; color:#555;">Total (LC)</td><td>GBP 300.00</td></tr>' +
          '</table>' +
          '<p style="margin-top:10px; color:#2a5a90; font-weight:600;">&#10003; Status: Open &nbsp;|&nbsp; Based On: Sales Order 1229</p>';

        openModal('copyDoneModal');
      }

      /* ══════════════════════════════════════════
         Item Search Popup
      ══════════════════════════════════════════ */
      var inventoryItems = [
        { code: 'A00001', name: 'Product A – Standard Unit',   stock: '42',   price: '300.00', group: 'General' },
        { code: 'A00002', name: 'Product B – Premium Pack',    stock: '18',   price: '450.00', group: 'General' },
        { code: 'C10001', name: 'Component X – Steel Bracket', stock: '200',  price: '12.50',  group: 'Components' },
        { code: 'C10002', name: 'Component Y – Rubber Seal',   stock: '500',  price: '4.75',   group: 'Components' },
        { code: 'S20001', name: 'Service – Installation',      stock: 'N/A',  price: '150.00', group: 'Services' },
        { code: 'S20002', name: 'Service – Consultation',      stock: 'N/A',  price: '200.00', group: 'Services' },
        { code: 'P30001', name: 'Package – Starter Bundle',    stock: '15',   price: '850.00', group: 'Packages' },
        { code: 'P30002', name: 'Package – Enterprise Suite',  stock: '5',    price: '2400.00',group: 'Packages' },
        { code: 'R40001', name: 'Raw Material – Aluminium',    stock: '1200', price: '3.20',   group: 'Raw Materials' },
        { code: 'R40002', name: 'Raw Material – Carbon Fibre', stock: '340',  price: '28.60',  group: 'Raw Materials' }
      ];

      var _itemTargetCell = null;
      var _itemSelectedRow = null;

      function openItemSearch(cell) {
        _itemTargetCell = cell;
        _itemSelectedRow = null;
        document.getElementById('itemSearchInput').value = '';
        renderItemRows(inventoryItems);
        openModal('itemSearchModal');
        setTimeout(function(){ document.getElementById('itemSearchInput').focus(); }, 80);
      }

      function renderItemRows(items) {
        var tbody = document.getElementById('itemSearchBody');
        tbody.innerHTML = '';
        items.forEach(function(item) {
          var tr = document.createElement('tr');
          tr.innerHTML = '<td>' + item.code + '</td><td>' + item.name + '</td>' +
            '<td style="text-align:right;">' + item.stock + '</td>' +
            '<td style="text-align:right;">' + item.price + '</td>' +
            '<td>' + item.group + '</td>';
          tr.addEventListener('click', function() {
            document.querySelectorAll('#itemSearchBody tr').forEach(function(r){ r.classList.remove('sel'); });
            tr.classList.add('sel');
            _itemSelectedRow = item;
          });
          tr.addEventListener('dblclick', function() {
            _itemSelectedRow = item;
            confirmItemSelect();
          });
          tbody.appendChild(tr);
        });
      }

      function filterItems() {
        var val = document.getElementById('itemSearchInput').value.toLowerCase();
        var field = document.getElementById('itemSearchField').value;
        var filtered = inventoryItems.filter(function(i) {
          var src = field === 'code' ? i.code : field === 'name' ? i.name : i.group;
          return src.toLowerCase().indexOf(val) !== -1;
        });
        renderItemRows(filtered);
      }

      function confirmItemSelect() {
        if (!_itemSelectedRow) {
          alert('Please select an item first.');
          return;
        }
        var item = _itemSelectedRow;
        if (_itemTargetCell) {
          _itemTargetCell.innerHTML = '<span style="color:#e67c00;margin-right:2px;">&#8594;</span>' + item.code;
          _itemTargetCell.setAttribute('data-item', item.code);
          var row = _itemTargetCell.closest('tr');
          if (row) {
            var inputs = row.querySelectorAll('.cell-input');
            if (inputs[0]) inputs[0].value = '1.000';
            if (inputs[1]) inputs[1].value = item.price;
            var totalCell = row.cells[6];
            if (totalCell) totalCell.textContent = 'GBP ' + parseFloat(item.price).toFixed(2);
            var uomCell = row.cells[7];
            if (uomCell) uomCell.textContent = item.group === 'Services' ? 'Manual' : 'EA';
            var numCell = row.cells[0];
            if (numCell && !numCell.textContent.trim()) {
              rowCounter++;
              numCell.textContent = rowCounter;
            }
          }
        }
        closeModal('itemSearchModal');
      }

      /* ══════════════════════════════════════════
         Row Details Popup
      ══════════════════════════════════════════ */
      var _rdTargetRow = null;

      function openRowDetails(row) {
        if (!row) {
          var sel = document.querySelector('#gridBody tr.selected');
          row = sel || document.querySelector('#gridBody tr');
        }
        _rdTargetRow = row;
        if (row) {
          var itemCell = row.cells[1];
          var txt = itemCell ? itemCell.textContent.replace('→','').trim() : '';
          var qtyInput = row.querySelector('.cell-input');
          var qty = qtyInput ? qtyInput.value : '1.000';
          var priceInputs = row.querySelectorAll('.cell-input');
          var price = priceInputs[1] ? priceInputs[1].value : '';
          var disc = priceInputs[2] ? priceInputs[2].value : '';
          var tax = priceInputs[3] ? priceInputs[3].value : '';
          var totalCell = row.cells[6];
          var total = totalCell ? totalCell.textContent.trim() : '';

          document.getElementById('rd_itemNo').value = txt || '';
          document.getElementById('rd_qty').value = qty || '1.000';
          document.getElementById('rd_unitPrice').value = price || '';
          document.getElementById('rd_disc').value = disc || '0';
          document.getElementById('rd_totalLC').value = total || '';
          document.getElementById('rd_freeText').value = '';
          document.getElementById('rd_rowRemarks').value = '';

          var lineNum = row.cells[0] ? row.cells[0].textContent.trim() : '?';
          document.querySelector('#rowDetailsModal .modal-titlebar span:first-child').textContent = 'Row Details – Line ' + lineNum;
        }
        openModal('rowDetailsModal');
      }

      function applyRowDetails() {
        if (_rdTargetRow) {
          var row = _rdTargetRow;
          var itemNo = document.getElementById('rd_itemNo').value.trim();
          var qty = document.getElementById('rd_qty').value.trim();
          var price = document.getElementById('rd_unitPrice').value.trim();
          var disc = document.getElementById('rd_disc').value.trim();
          var uom = document.getElementById('rd_uom').value;

          if (itemNo) {
            row.cells[1].innerHTML = '<span style="color:#e67c00;margin-right:2px;">&#8594;</span>' + itemNo;
            row.cells[1].setAttribute('data-item', itemNo);
          }
          var inputs = row.querySelectorAll('.cell-input');
          if (inputs[0] && qty) inputs[0].value = qty;
          if (inputs[1] && price) inputs[1].value = price;
          if (inputs[2] && disc !== '') inputs[2].value = disc;
          if (row.cells[7]) row.cells[7].textContent = uom;

          var qtyNum = parseFloat(qty) || 1;
          var priceNum = parseFloat(price) || 0;
          var discNum = parseFloat(disc) || 0;
          var total = qtyNum * priceNum * (1 - discNum / 100);
          if (row.cells[6] && priceNum) {
            row.cells[6].textContent = 'GBP ' + total.toFixed(2);
          }

          if (!row.cells[0].textContent.trim()) {
            rowCounter++;
            row.cells[0].textContent = rowCounter;
          }
        }
        closeModal('rowDetailsModal');
      }

      /* ══════════════════════════════════════════
         Close modals on overlay click
      ══════════════════════════════════════════ */
      document.querySelectorAll('.modal-overlay').forEach(function(overlay) {
        overlay.addEventListener('click', function(e) {
          if (e.target === overlay) overlay.classList.remove('visible');
        });
      });

      /* ══════════════════════════════════════════
         Item search – Enter key
      ══════════════════════════════════════════ */
      document.getElementById('itemSearchInput').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') filterItems();
      });
