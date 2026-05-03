/** Extracted from frontend/ui/sap-dash.html (<script> block) for reference — not imported by the app. */
   // ── Utilities ──────────────────────────────────────────────
      function updateClocks() {
        var d = new Date();
        var s = d.toLocaleDateString() + '  ' + d.toLocaleTimeString();
        var el1 = document.getElementById('bar-datetime');
        var el2 = document.getElementById('sb-datetime');
        if (el1) el1.textContent = s;
        if (el2) el2.textContent = s;
      }
      updateClocks();
      setInterval(updateClocks, 1000);

      // ── Login ───────────────────────────────────────────────────
      document.getElementById('login-form').addEventListener('submit', function(e) {
        e.preventDefault();
        var uid = document.getElementById('user-id').value.trim() || 'manager';
        document.getElementById('bar-user').textContent = uid;
        document.getElementById('sb-user').textContent = uid;
        document.getElementById('login-screen').style.display = 'none';
        var ms = document.getElementById('main-screen');
        ms.classList.add('visible');
        renderDashboard();
      });

      document.getElementById('btn-cancel').addEventListener('click', function() {
        document.getElementById('user-id').value = '';
        document.getElementById('password').value = '';
        document.getElementById('user-id').focus();
      });

      // logout
      function doLogout() {
        document.getElementById('main-screen').classList.remove('visible');
        document.getElementById('login-screen').style.display = 'flex';
        document.getElementById('password').value = '';
        document.getElementById('user-id').focus();
      }
      document.getElementById('btn-logout').addEventListener('click', doLogout);
      document.getElementById('menu-logout').addEventListener('click', doLogout);

      // ── Left menu tree ──────────────────────────────────────────
      function toggleGroup(header) {
        var arrow = header.querySelector('.tree-arrow');
        var children = header.nextElementSibling;
        var isOpen = children.classList.contains('open');
        // close all
        document.querySelectorAll('.module-group-header').forEach(function(h) {
          h.classList.remove('active');
          h.querySelector('.tree-arrow').classList.remove('open');
          h.nextElementSibling.classList.remove('open');
        });
        if (!isOpen) {
          header.classList.add('active');
          arrow.classList.add('open');
          children.classList.add('open');
        }
      }

      // ── Tabs ────────────────────────────────────────────────────
      var openTabs = ['dashboard'];

      function openTab(id, label) {
        // deselect all children
        document.querySelectorAll('.module-child').forEach(function(c) { c.classList.remove('selected'); });
        // find and select clicked child
        document.querySelectorAll('.module-child').forEach(function(c) {
          if (c.getAttribute('onclick') && c.getAttribute('onclick').includes("'" + id + "'")) {
            c.classList.add('selected');
          }
        });
        if (openTabs.indexOf(id) === -1) {
          openTabs.push(id);
          var tabs = document.getElementById('content-tabs');
          var tab = document.createElement('div');
          tab.className = 'content-tab';
          tab.setAttribute('data-tab', id);
          tab.innerHTML = label + ' <span class="tab-close" onclick="closeTab(event,\'' + id + '\')">✕</span>';
          tab.addEventListener('click', function(){ switchTab(id); });
          tabs.appendChild(tab);
        }
        switchTab(id);
      }

      function switchTab(id) {
        openTabs.forEach(function(t) {
          var el = document.querySelector('.content-tab[data-tab="' + t + '"]');
          if (el) el.classList.remove('active');
        });
        var active = document.querySelector('.content-tab[data-tab="' + id + '"]');
        if (active) active.classList.add('active');
        if (id === 'dashboard') {
          renderDashboard();
        } else {
          renderPlaceholder(id);
        }
      }

      function closeTab(e, id) {
        e.stopPropagation();
        if (id === 'dashboard') return;
        var idx = openTabs.indexOf(id);
        if (idx > -1) openTabs.splice(idx, 1);
        var el = document.querySelector('.content-tab[data-tab="' + id + '"]');
        if (el) el.remove();
        switchTab(openTabs[openTabs.length - 1]);
      }

      // ── Render Dashboard ────────────────────────────────────────
      function renderDashboard() {
        var pane = document.getElementById('content-pane');
        pane.innerHTML = '<div class="dashboard-wrap">' +
          '<div class="dash-welcome-bar">' +
            '<span class="dash-welcome-text">Welcome to SAP Business One</span>' +
            '<span class="dash-welcome-sub">&nbsp;| Company: SBODemoUS &nbsp;| User: ' + document.getElementById('sb-user').textContent + ' &nbsp;| Today: ' + new Date().toLocaleDateString() + '</span>' +
          '</div>' +
          // KPI row
          '<div class="dash-kpi-row">' +
            kpiCard('Open Sales Orders', '142', '+8 today', true) +
            kpiCard('A/R Overdue', '$34,820', '12 invoices', false) +
            kpiCard('Stock Value', '$1,248,500', '+2.3%', true) +
            kpiCard('Open POs', '56', '-3 today', true) +
            kpiCard('Net Revenue MTD', '$482,300', '+11.4%', true) +
            kpiCard('Cash &amp; Bank', '$245,100', 'Updated now', true) +
          '</div>' +
          // Row 1
          '<div class="dash-row">' +
            '<div class="dash-panel" style="flex:2">' +
              '<div class="dash-panel-header"><span class="dash-panel-title">📋 Recent Sales Orders</span></div>' +
              '<div class="dash-panel-body">' +
                '<table class="dash-table"><thead><tr><th>Doc No.</th><th>Customer</th><th>Date</th><th>Amount</th><th>Status</th></tr></thead><tbody>' +
                  salesRows() +
                '</tbody></table>' +
              '</div>' +
            '</div>' +
            '<div class="dash-panel" style="flex:1">' +
              '<div class="dash-panel-header"><span class="dash-panel-title">📊 Monthly Sales</span></div>' +
              '<div class="dash-panel-body">' + salesChart() + '</div>' +
            '</div>' +
          '</div>' +
          // Row 2
          '<div class="dash-row">' +
            '<div class="dash-panel" style="flex:1">' +
              '<div class="dash-panel-header"><span class="dash-panel-title">⚡ Quick Launch</span></div>' +
              '<div class="dash-panel-body">' + quickLaunch() + '</div>' +
            '</div>' +
            '<div class="dash-panel" style="flex:1">' +
              '<div class="dash-panel-header"><span class="dash-panel-title">📬 Alerts &amp; Activities</span></div>' +
              '<div class="dash-panel-body">' + activityList() + '</div>' +
            '</div>' +
            '<div class="dash-panel" style="flex:1">' +
              '<div class="dash-panel-header"><span class="dash-panel-title">📦 Low Stock Items</span></div>' +
              '<div class="dash-panel-body">' +
                '<table class="dash-table"><thead><tr><th>Item</th><th>In Stock</th><th>Min</th></tr></thead><tbody>' +
                  stockRows() +
                '</tbody></table>' +
              '</div>' +
            '</div>' +
          '</div>' +
        '</div>';
      }

      function kpiCard(label, value, change, pos) {
        return '<div class="kpi-card">' +
          '<div class="kpi-label">' + label + '</div>' +
          '<div class="kpi-value">' + value + '</div>' +
          '<div class="kpi-change ' + (pos ? 'kpi-pos' : 'kpi-neg') + '">' + (pos ? '▲ ' : '▼ ') + change + '</div>' +
        '</div>';
      }

      function salesRows() {
        var rows = [
          ['SO-10042', 'American Computers', '05/01/2026', '$12,450', '🟡 Open'],
          ['SO-10041', 'Maxi-Teq', '05/01/2026', '$8,300', '🟢 Delivered'],
          ['SO-10040', 'One Time Customer', '04/30/2026', '$450', '🔵 Invoiced'],
          ['SO-10039', 'Parameter Technology', '04/30/2026', '$23,600', '🟡 Open'],
          ['SO-10038', 'Earthshaker Corp', '04/29/2026', '$5,100', '🔵 Invoiced'],
          ['SO-10037', 'American Computers', '04/28/2026', '$9,820', '🟢 Delivered'],
        ];
        return rows.map(function(r) {
          return '<tr><td>' + r[0] + '</td><td>' + r[1] + '</td><td>' + r[2] + '</td><td>' + r[3] + '</td><td>' + r[4] + '</td></tr>';
        }).join('');
      }

      function salesChart() {
        var months = ['Nov','Dec','Jan','Feb','Mar','Apr'];
        var vals = [65, 80, 55, 90, 72, 100];
        var max = 100;
        var html = '<div class="chart-bar-wrap">';
        for (var i = 0; i < months.length; i++) {
          var h = Math.round((vals[i] / max) * 82);
          html += '<div class="chart-bar-col">' +
            '<div class="chart-bar' + (i === 5 ? ' highlight' : '') + '" style="height:' + h + 'px"></div>' +
            '<div class="chart-bar-label">' + months[i] + '</div>' +
          '</div>';
        }
        html += '</div>';
        html += '<div style="font-size:10px;color:#888;text-align:center;margin-top:2px;">Revenue in $K (last 6 months)</div>';
        return html;
      }

      function quickLaunch() {
        var items = [
          ['📄','Sales Quotation','quotation'],
          ['📦','Sales Order','order'],
          ['🧾','A/R Invoice','ar-inv'],
          ['🏪','Purchase Order','po'],
          ['📥','Goods Receipt','goods-receipt'],
          ['📇','BP Master Data','bpmaster'],
          ['🔖','Item Master','item-master'],
          ['📊','Financial Reports','financial-reports'],
        ];
        var html = '<div class="shortcut-grid">';
        items.forEach(function(it) {
          html += '<div class="shortcut-btn" onclick="openTab(\'' + it[2] + '\',\'' + it[1] + '\')">' +
            '<span class="shortcut-icon">' + it[0] + '</span>' + it[1] + '</div>';
        });
        html += '</div>';
        return html;
      }

      function activityList() {
        var items = [
          ['dot-red','10:32 AM','A/R Invoice overdue: $4,200 - Earthshaker'],
          ['dot-orange','09:18 AM','Approval required: PO-3381 ($18,000)'],
          ['dot-blue','09:05 AM','New Sales Order from American Computers'],
          ['dot-green','08:50 AM','Delivery confirmed: SO-10038'],
          ['dot-blue','08:30 AM','Bank statement imported successfully'],
          ['dot-orange','Yesterday','Stock alert: Item A00001 below min qty'],
        ];
        return items.map(function(it) {
          return '<div class="activity-item"><div class="activity-dot ' + it[0] + '"></div>' +
            '<span class="activity-time">' + it[1] + '</span>' +
            '<span class="activity-text">' + it[2] + '</span></div>';
        }).join('');
      }

      function stockRows() {
        var rows = [
          ['A00001 - PC Comp HD', '5', '10'],
          ['A00027 - Monitor 24"', '3', '8'],
          ['B10020 - USB Hub', '12', '15'],
          ['C00045 - Printer Ink', '2', '20'],
          ['D00012 - Keyboard', '7', '10'],
        ];
        return rows.map(function(r) {
          var low = parseInt(r[1]) < parseInt(r[2]);
          return '<tr><td>' + r[0] + '</td>' +
            '<td style="color:' + (low ? '#c03020' : '#1a7a30') + ';font-weight:bold">' + r[1] + '</td>' +
            '<td>' + r[2] + '</td></tr>';
        }).join('');
      }

      function renderPlaceholder(id) {
        var labels = {
          'system-init':'System Initialization', 'users':'Users', 'auth':'Authorizations',
          'alerts':'Alert Management', 'coa':'Chart of Accounts', 'je':'Journal Entry',
          'je-report':'Journal Entry Report', 'budget':'Budget', 'cost-acc':'Cost Accounting',
          'quotation':'Sales Quotation', 'order':'Sales Order', 'delivery':'Delivery',
          'ar-inv':'A/R Invoice', 'ar-credit':'A/R Credit Memo', 'customers':'Customers',
          'po':'Purchase Order', 'grpo':'Goods Receipt PO', 'ap-inv':'A/P Invoice',
          'ap-credit':'A/P Credit Memo', 'vendors':'Vendors', 'bpmaster':'BP Master Data',
          'activities':'Activities', 'campaign':'Campaign', 'incoming':'Incoming Payments',
          'outgoing':'Outgoing Payments', 'bank-recon':'Bank Statement Processing',
          'item-master':'Item Master Data', 'goods-receipt':'Goods Receipt', 'goods-issue':'Goods Issue',
          'stock-count':'Stock Counting', 'warehouses':'Warehouses', 'mrp-wiz':'MRP Wizard',
          'order-rec':'Order Recommendation', 'bom':'Bill of Materials', 'wo':'Production Order',
          'service-call':'Service Call', 'contracts':'Service Contracts', 'equipment':'Equipment Card',
          'employees':'Employee Master Data', 'attendance':'Attendance',
          'financial-reports':'Financial Reports', 'sales-reports':'Sales Reports',
          'inventory-reports':'Inventory Reports', 'purchasing-reports':'Purchasing Reports',
        };
        var label = labels[id] || id;
        var pane = document.getElementById('content-pane');
        pane.innerHTML = '<div style="padding:8px;">' +
          '<div class="form-info-banner">ℹ &nbsp;<strong>' + label + '</strong> &nbsp;– Form area (no record selected)</div>' +
          '<div style="background:#f8f8f8;border:1px solid #b0c8e0;padding:0;">' +
            '<div style="height:28px;background:linear-gradient(180deg,#d8e8f8 0%,#bcd4f0 100%);border-bottom:1px solid #9ab8d8;display:flex;align-items:center;padding:0 8px;gap:8px;">' +
              '<span style="font-size:11px;font-weight:bold;color:#1a3a6a;">' + label + '</span>' +
              '<span style="font-size:10px;color:#5a7a9a;">| Find Mode</span>' +
            '</div>' +
            '<div style="padding:16px;font-size:11px;color:#777;'
            + 'display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:200px;gap:8px;">' +
              '<div style="font-size:32px;">📭</div>' +
              '<div>No record selected. Use the toolbar to <strong>Find</strong> or <strong>Add</strong> a record.</div>' +
              '<div style="display:flex;gap:6px;margin-top:10px;">' +
                '<button class="btn-sap" style="height:24px;padding:0 14px;font-size:11px;'
                + 'border:1px solid #7a9ab8;cursor:pointer;background:linear-gradient(180deg,#f5f5f5 0%,#dcdcdc 100%)">🔍 Find</button>' +
                '<button class="btn-sap primary" style="height:24px;padding:0 14px;font-size:11px;'
                + 'border:1px solid #b06000;cursor:pointer;background:linear-gradient(180deg,#f0a000 0%,#d48000 100%);color:#3a1800;font-weight:bold">➕ Add New</button>' +
              '</div>' +
            '</div>' +
          '</div>' +
        '</div>';
      }

      // ── Menu search ──────────────────────────────────────────────
      document.getElementById('menu-search').addEventListener('input', function() {
        var q = this.value.toLowerCase().trim();
        document.querySelectorAll('.module-child').forEach(function(c) {
          var txt = c.textContent.toLowerCase();
          c.style.display = (!q || txt.includes(q)) ? '' : 'none';
        });
        if (q) {
          document.querySelectorAll('.module-group-header').forEach(function(h) {
            h.classList.remove('active');
            h.querySelector('.tree-arrow').classList.remove('open');
            h.nextElementSibling.classList.remove('open');
          });
          document.querySelectorAll('.module-children').forEach(function(c) {
            var visible = Array.from(c.querySelectorAll('.module-child')).some(function(ch) {
              return ch.style.display !== 'none';
            });
            if (visible) { c.classList.add('open'); c.previousElementSibling.classList.add('active'); c.previousElementSibling.querySelector('.tree-arrow').classList.add('open'); }
          });
        }
