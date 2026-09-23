"use client";

import { useId, useRef, useState, type ReactNode } from "react";

export interface TabItem { id: string; label: string; content: ReactNode }
export function Tabs({ items, label }: { items: TabItem[]; label: string }) {
  const [active, setActive] = useState(items[0]?.id ?? "");
  const id = useId();
  const refs = useRef<(HTMLButtonElement | null)[]>([]);
  const selected = items.find((item) => item.id === active) ?? items[0];
  return <div>
    <div aria-label={label} className="evalio-tabs" role="tablist">
      {items.map((item, index) => <button
        aria-controls={`${id}-panel-${item.id}`} aria-selected={item.id === selected?.id}
        id={`${id}-tab-${item.id}`} key={item.id} role="tab" type="button"
        tabIndex={item.id === selected?.id ? 0 : -1}
        ref={(element) => { refs.current[index] = element; }}
        onClick={() => setActive(item.id)}
        onKeyDown={(event) => {
          let next = index;
          if (event.key === "ArrowRight") next = (index + 1) % items.length;
          else if (event.key === "ArrowLeft") next = (index - 1 + items.length) % items.length;
          else if (event.key === "Home") next = 0;
          else if (event.key === "End") next = items.length - 1;
          else return;
          event.preventDefault();
          setActive(items[next].id);
          refs.current[next]?.focus();
        }}
      >{item.label}</button>)}
    </div>
    {selected && <div aria-labelledby={`${id}-tab-${selected.id}`} className="evalio-tab-panel" id={`${id}-panel-${selected.id}`} role="tabpanel" tabIndex={0} key={selected.id}>{selected.content}</div>}
  </div>;
}
