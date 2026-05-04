import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from "react";

export const HOME_TAB_ID = "home";

export type WorkspaceTabKind = "home" | "inventory" | "sales" | "purchase" | "production" | "finance" | "warehouse";

export type WorkspaceTab = {
  id: string;
  label: string;
  kind: WorkspaceTabKind;
  /** Last path from menu (for sidebar highlight). */
  navPath?: string;
  moduleId?: string;
  salesModuleId?: string;
  purchaseModuleId?: string;
  productionModuleId?: string;
  financeModuleId?: string;
  warehouseModuleId?: string;
};

export type TabActions = {
  find?: () => void;
  newDoc?: () => void;
  first?: () => void;
  prev?: () => void;
  next?: () => void;
  last?: () => void;
  print?: () => void;
};

type WorkspaceContextValue = {
  tabs: WorkspaceTab[];
  activeTabId: string;
  activeNavPath: string | null;
  switchTab: (id: string) => void;
  closeTab: (id: string) => void;
  /** Each menu click opens a new tab (multi-window style). */
  openInventoryModule: (moduleId: string, label: string, navPath: string) => void;
  openSalesModule: (salesModuleId: string, label: string, navPath: string) => void;
  openPurchaseModule: (purchaseModuleId: string, label: string, navPath: string) => void;
  openProductionModule: (productionModuleId: string, label: string, navPath: string) => void;
  openFinanceModule: (financeModuleId: string, label: string, navPath: string) => void;
  openWarehouseModule: (warehouseModuleId: string, label: string, navPath: string) => void;
  goHome: () => void;
  registerTabActions: (tabId: string, actions: TabActions | null) => void;
  runFind: () => void;
  runNew: () => void;
  runFirst: () => void;
  runPrev: () => void;
  runNext: () => void;
  runLast: () => void;
  runPrint: () => void;
  /** Right-hand User-Defined Fields column on document windows (SAP-style). */
  udfSidebarVisible: boolean;
  setUdfSidebarVisible: (visible: boolean) => void;
  toggleUdfSidebar: () => void;
};

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

const UDF_SIDEBAR_STORAGE_KEY = "ez_udf_sidebar_visible";

function readUdfSidebarVisible(): boolean {
  try {
    const s = localStorage.getItem(UDF_SIDEBAR_STORAGE_KEY);
    if (s === "0") return false;
    if (s === "1") return true;
  } catch {
    /* ignore */
  }
  return true;
}

function newWorkspaceTabId(prefix: string): string {
  return `${prefix}:${Date.now().toString(36)}:${Math.random().toString(36).slice(2, 10)}`;
}

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [tabs, setTabs] = useState<WorkspaceTab[]>([
    { id: HOME_TAB_ID, label: "🏠 Home", kind: "home", navPath: "/" },
  ]);
  const [activeTabId, setActiveTabId] = useState(HOME_TAB_ID);
  const [udfSidebarVisible, setUdfSidebarVisible] = useState(readUdfSidebarVisible);
  const actionsRef = useRef<Record<string, TabActions>>({});

  const activeNavPath = useMemo(() => {
    const t = tabs.find((x) => x.id === activeTabId);
    return t?.navPath ?? null;
  }, [tabs, activeTabId]);

  const switchTab = useCallback((id: string) => {
    setActiveTabId(id);
  }, []);

  const goHome = useCallback(() => {
    setActiveTabId(HOME_TAB_ID);
  }, []);

  const openInventoryModule = useCallback((moduleId: string, label: string, navPath: string) => {
    const id = newWorkspaceTabId("inv");
    setTabs((prev) => [
      ...prev,
      {
        id,
        label,
        kind: "inventory" as const,
        moduleId,
        navPath,
      },
    ]);
    setActiveTabId(id);
  }, []);

  const openSalesModule = useCallback((salesModuleId: string, label: string, navPath: string) => {
    const id = newWorkspaceTabId("sal");
    setTabs((prev) => [
      ...prev,
      {
        id,
        label,
        kind: "sales" as const,
        salesModuleId,
        navPath,
      },
    ]);
    setActiveTabId(id);
  }, []);

  const openPurchaseModule = useCallback((purchaseModuleId: string, label: string, navPath: string) => {
    const id = newWorkspaceTabId("pur");
    setTabs((prev) => [
      ...prev,
      {
        id,
        label,
        kind: "purchase" as const,
        purchaseModuleId,
        navPath,
      },
    ]);
    setActiveTabId(id);
  }, []);

  const openProductionModule = useCallback((productionModuleId: string, label: string, navPath: string) => {
    const id = newWorkspaceTabId("prd");
    setTabs((prev) => [
      ...prev,
      {
        id,
        label,
        kind: "production" as const,
        productionModuleId,
        navPath,
      },
    ]);
    setActiveTabId(id);
  }, []);

  const openFinanceModule = useCallback((financeModuleId: string, label: string, navPath: string) => {
    const id = newWorkspaceTabId("fin");
    setTabs((prev) => [
      ...prev,
      {
        id,
        label,
        kind: "finance" as const,
        financeModuleId,
        navPath,
      },
    ]);
    setActiveTabId(id);
  }, []);

  const openWarehouseModule = useCallback((warehouseModuleId: string, label: string, navPath: string) => {
    const id = newWorkspaceTabId("whs");
    setTabs((prev) => [
      ...prev,
      {
        id,
        label,
        kind: "warehouse" as const,
        warehouseModuleId,
        navPath,
      },
    ]);
    setActiveTabId(id);
  }, []);

  const closeTab = useCallback((id: string) => {
    if (id === HOME_TAB_ID) return;
    setTabs((prev) => {
      const next = prev.filter((t) => t.id !== id);
      delete actionsRef.current[id];
      return next.length ? next : [{ id: HOME_TAB_ID, label: "🏠 Home", kind: "home", navPath: "/" }];
    });
    setActiveTabId((cur) => {
      if (cur !== id) return cur;
      return HOME_TAB_ID;
    });
  }, []);

  const registerTabActions = useCallback((tabId: string, actions: TabActions | null) => {
    if (actions) actionsRef.current[tabId] = actions;
    else delete actionsRef.current[tabId];
  }, []);

  const runFind = useCallback(() => {
    actionsRef.current[activeTabId]?.find?.();
  }, [activeTabId]);

  const runNew = useCallback(() => {
    actionsRef.current[activeTabId]?.newDoc?.();
  }, [activeTabId]);

  const runFirst = useCallback(() => {
    actionsRef.current[activeTabId]?.first?.();
  }, [activeTabId]);

  const runPrev = useCallback(() => {
    actionsRef.current[activeTabId]?.prev?.();
  }, [activeTabId]);

  const runNext = useCallback(() => {
    actionsRef.current[activeTabId]?.next?.();
  }, [activeTabId]);

  const runLast = useCallback(() => {
    actionsRef.current[activeTabId]?.last?.();
  }, [activeTabId]);

  const runPrint = useCallback(() => {
    actionsRef.current[activeTabId]?.print?.();
  }, [activeTabId]);

  const persistUdf = useCallback((visible: boolean) => {
    try {
      localStorage.setItem(UDF_SIDEBAR_STORAGE_KEY, visible ? "1" : "0");
    } catch {
      /* ignore */
    }
  }, []);

  const setUdfSidebarVisibleWrapped = useCallback(
    (visible: boolean) => {
      setUdfSidebarVisible(visible);
      persistUdf(visible);
    },
    [persistUdf],
  );

  const toggleUdfSidebar = useCallback(() => {
    setUdfSidebarVisible((prev) => {
      const next = !prev;
      persistUdf(next);
      return next;
    });
  }, [persistUdf]);

  const value = useMemo<WorkspaceContextValue>(
    () => ({
      tabs,
      activeTabId,
      activeNavPath,
      switchTab,
      closeTab,
      openInventoryModule,
      openSalesModule,
      openPurchaseModule,
      openProductionModule,
      openFinanceModule,
      openWarehouseModule,
      goHome,
      registerTabActions,
      runFind,
      runNew,
      runFirst,
      runPrev,
      runNext,
      runLast,
      runPrint,
      udfSidebarVisible,
      setUdfSidebarVisible: setUdfSidebarVisibleWrapped,
      toggleUdfSidebar,
    }),
    [
      tabs,
      activeTabId,
      activeNavPath,
      switchTab,
      closeTab,
      openInventoryModule,
      openSalesModule,
      openPurchaseModule,
      openProductionModule,
      openFinanceModule,
      openWarehouseModule,
      goHome,
      registerTabActions,
      runFind,
      runNew,
      runFirst,
      runPrev,
      runNext,
      runLast,
      runPrint,
      udfSidebarVisible,
      setUdfSidebarVisibleWrapped,
      toggleUdfSidebar,
    ],
  );

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>;
}

export function useWorkspace(): WorkspaceContextValue {
  const v = useContext(WorkspaceContext);
  if (!v) throw new Error("useWorkspace must be used within WorkspaceProvider");
  return v;
}
