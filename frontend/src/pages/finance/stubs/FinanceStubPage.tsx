import { FINANCE_STUB_MODULES } from "./financeStubModules";

export function FinanceStubPage({ moduleId }: { moduleId: string }) {
  const meta = FINANCE_STUB_MODULES[moduleId];
  if (!meta) {
    return (
      <div className="workspace-home">
        <p>Unknown stub module: {moduleId}</p>
      </div>
    );
  }
  return (
    <div className="workspace-home">
      <h2>{meta.title}</h2>
      <p>
        <strong>{meta.sap}</strong> — database table is defined in the Finance app; UI/API wiring is pending.
      </p>
      {meta.hint ? <p>{meta.hint}</p> : null}
    </div>
  );
}
