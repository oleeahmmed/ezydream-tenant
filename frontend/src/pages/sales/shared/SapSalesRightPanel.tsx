/** Right column fields — layout from ``frontend/ui/sap2.html`` (UDF-style; not wired to sales API yet). */
export function SapSalesRightPanel() {
  return (
    <aside className="right-panel" aria-label="Additional fields">
      <div className="rp-titlebar">
        <div className="rp-nav-btn" aria-hidden>
          ◀
        </div>
        <div className="rp-nav-btn" style={{ marginRight: 4 }} aria-hidden>
          ▶
        </div>
        <select className="rp-select" aria-label="Category" defaultValue="all">
          <option value="all">All Categories</option>
        </select>
        <span className="rp-close" aria-hidden>
          ✕
        </span>
      </div>
      <div className="rp-body">
        <div className="rp-row">
          <span className="rp-label">Doc. Approval Status</span>
          <select className="rp-field-select" defaultValue="Pending">
            <option>Pending</option>
            <option>Approved</option>
            <option>Not Required</option>
          </select>
        </div>
        <div className="rp-row">
          <span className="rp-label">Payment Date</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Received Amount</span>
          <input className="rp-input" type="text" defaultValue="0.00" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Payment Mode</span>
          <select className="rp-field-select" defaultValue="Online NEFT">
            <option>Online NEFT</option>
            <option>Cash</option>
            <option>Cheque</option>
          </select>
        </div>
        <div className="rp-row" style={{ alignItems: "flex-start", paddingTop: 2 }}>
          <span className="rp-label" style={{ paddingTop: 2 }}>
            Payment Remark
          </span>
          <textarea className="rp-textarea" readOnly defaultValue="" />
        </div>
        <div className="rp-spacer" />
        <div className="rp-row">
          <span className="rp-label">Payment Status</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Order Source</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Vehicle No.</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Vehicle Temp.</span>
          <input className="rp-input" type="text" defaultValue="0.00" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Driver Name</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-spacer" />
        <div className="rp-row">
          <span className="rp-label">Driver Mobile</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Route</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Zone</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Delivery Priority</span>
          <select className="rp-field-select" defaultValue="">
            <option value="" />
            <option>High</option>
            <option>Normal</option>
            <option>Low</option>
          </select>
        </div>
        <div className="rp-row">
          <span className="rp-label">Vehicle Temp. ID</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Gift Wrap</span>
          <select className="rp-field-select" defaultValue="">
            <option value="" />
            <option>Yes</option>
            <option>No</option>
          </select>
        </div>
        <div className="rp-row">
          <span className="rp-label">Gift Message</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-spacer" />
        <div className="rp-row">
          <span className="rp-label">Shift Id</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Shift Name</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Payment Ref. Number</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-spacer" />
        <div className="rp-row">
          <span className="rp-label">Instruction Type</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">CRM Order ID</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Transporter</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Trans Inv. No.</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-spacer" />
        <div className="rp-row">
          <span className="rp-label">LR No</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-spacer" />
        <div className="rp-row">
          <span className="rp-label">Trans Remarks</span>
          <input className="rp-input" type="text" defaultValue="" readOnly />
        </div>
        <div className="rp-spacer" />
        <div className="rp-row">
          <span className="rp-label">Freight 1</span>
          <input className="rp-input" type="text" defaultValue="0.00" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Freight 2</span>
          <input className="rp-input" type="text" defaultValue="0.00" readOnly />
        </div>
        <div className="rp-row">
          <span className="rp-label">Freight 3</span>
          <input className="rp-input" type="text" defaultValue="0.00" readOnly />
        </div>
        <div className="rp-spacer" />
      </div>
    </aside>
  );
}
