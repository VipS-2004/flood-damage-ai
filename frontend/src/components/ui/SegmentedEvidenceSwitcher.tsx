import type { KeyboardEvent } from "react";

type EvidenceMode = "impact" | "sar" | "drainage" | "beforeAfter";

type EvidenceOption = {
  value: EvidenceMode;
  label: string;
};

type SegmentedEvidenceSwitcherProps = {
  value: EvidenceMode;
  options: EvidenceOption[];
  onChange: (value: EvidenceMode) => void;
};

export default function SegmentedEvidenceSwitcher({
  value,
  options,
  onChange,
}: SegmentedEvidenceSwitcherProps) {
  const handleKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    const currentIndex = options.findIndex((option) => option.value === value);
    let nextIndex = currentIndex;

    if (event.key === "ArrowRight" || event.key === "ArrowDown") {
      nextIndex = (currentIndex + 1) % options.length;
    } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
      nextIndex = (currentIndex - 1 + options.length) % options.length;
    } else if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = options.length - 1;
    } else {
      return;
    }

    event.preventDefault();
    const nextOption = options[nextIndex];
    onChange(nextOption.value);
    requestAnimationFrame(() => {
      document.getElementById(`evidence-mode-${nextOption.value}`)?.focus();
    });
  };

  return (
    <div
      aria-label="Evidence layer"
      className="flex flex-wrap gap-1.5"
      role="radiogroup"
    >
      {options.map((option) => {
        const isActive = option.value === value;

        return (
          <button
            key={option.value}
            id={`evidence-mode-${option.value}`}
            aria-checked={isActive}
            className={`border px-3 py-1.5 font-mono text-[9px] uppercase tracking-[0.04em] transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2c5282] focus-visible:ring-offset-1 focus-visible:ring-offset-[#ebe8df] ${
              isActive
                ? "border-[#1a1a1a] bg-[#1a1a1a] text-white"
                : "border-[#d8d5cc] bg-[#fdf9f0] text-[#4a4a4a] hover:border-[#2c5282] hover:text-[#2c5282]"
            }`}
            onClick={() => onChange(option.value)}
            onKeyDown={handleKeyDown}
            role="radio"
            tabIndex={isActive ? 0 : -1}
            type="button"
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}

