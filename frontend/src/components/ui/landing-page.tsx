import {
  useEffect,
  useRef,
  useState,
  useCallback,
  useMemo,
} from "react";
import Globe from "./globe";
import { cn } from "../../lib/utils";
import { ArrowDown, ArrowUpRight, type LucideIcon } from "lucide-react";

function EditorialIconButton({
  label,
  icon: Icon,
  variant,
  onClick,
}: {
  label: string;
  icon: LucideIcon;
  variant: "primary" | "secondary";
  onClick?: () => void;
}) {
  const isPrimary = variant === "primary";

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "group relative inline-flex h-14 w-full min-w-0 max-w-full items-center overflow-hidden rounded-full border px-2 text-left text-sm font-medium tracking-[-0.01em] transition-colors duration-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#1a1a1a] focus-visible:ring-offset-4 sm:w-auto sm:min-w-[220px]",
        isPrimary
          ? "border-[#1a1a1a] bg-[#1a1a1a] text-[#fdf9f0] hover:bg-[#252525]"
          : "border-[#1a1a1a]/25 bg-[#fdf9f0]/80 text-[#1a1a1a] backdrop-blur-sm hover:border-[#1a1a1a]/50 hover:bg-[#f7f3ea]"
      )}
    >
      <span
        className={cn(
          "absolute inset-y-0 z-10 flex items-center whitespace-nowrap transition-[left,right] duration-500 ease-[cubic-bezier(0.23,1,0.32,1)]",
          isPrimary
            ? "left-14 right-2 group-hover:left-2 group-hover:right-14"
            : "left-2 right-14 group-hover:left-14 group-hover:right-2"
        )}
      >
        {label}
      </span>
      <span
        className={cn(
          "absolute z-10 flex h-10 w-10 items-center justify-center rounded-full transition-[left,right] duration-500 ease-[cubic-bezier(0.23,1,0.32,1)]",
          isPrimary
            ? "left-2 bg-[#fdf9f0] text-[#1a1a1a] group-hover:left-auto group-hover:right-2"
            : "right-2 bg-[#1a1a1a] text-[#fdf9f0] group-hover:left-2 group-hover:right-auto"
        )}
      >
        <Icon
          size={17}
          strokeWidth={1.8}
          aria-hidden="true"
          className={cn(
            "transition-transform duration-500 ease-[cubic-bezier(0.23,1,0.32,1)]",
            isPrimary && "group-hover:rotate-45"
          )}
        />
      </span>
    </button>
  );
}

interface ScrollGlobeProps {
  sections: {
    id: string;
    badge?: string;
    eyebrow?: string;
    title: string;
    subtitle?: string;
    description: string;
    align?: "left" | "center" | "right";
    features?: {
      title: string;
      description: string;
    }[];
    actions?: {
      label: string;
      variant: "primary" | "secondary";
      onClick?: () => void;
    }[];
  }[];
  globeConfig?: {
    positions: {
      top: string;
      left: string;
      scale: number;
    }[];
  };
  className?: string;
}

const defaultGlobeConfig = {
  positions: [
    { top: "50%", left: "75%", scale: 1.4 },
    { top: "25%", left: "50%", scale: 0.9 },
    { top: "15%", left: "90%", scale: 2 },
    { top: "50%", left: "50%", scale: 1.8 },
  ],
};

const parsePercent = (str: string): number => {
  return parseFloat(str.replace("%", ""));
};

function ScrollGlobe({
  sections,
  globeConfig = defaultGlobeConfig,
  className,
}: ScrollGlobeProps) {
  const [activeSection, setActiveSection] = useState(0);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [globeTransform, setGlobeTransform] = useState("");

  const containerRef = useRef<HTMLDivElement>(null);
  const sectionRefs = useRef<(HTMLElement | null)[]>([]);
  const animationFrameId = useRef<number | undefined>(undefined);

  const calculatedPositions = useMemo(() => {
    return globeConfig.positions.map((pos) => ({
      top: parsePercent(pos.top),
      left: parsePercent(pos.left),
      scale: pos.scale,
    }));
  }, [globeConfig.positions]);

  const updateScrollPosition = useCallback(() => {
    const scrollTop = window.pageYOffset;

    const docHeight =
      document.documentElement.scrollHeight - window.innerHeight;

    const progress =
      docHeight > 0
        ? Math.min(Math.max(scrollTop / docHeight, 0), 1)
        : 0;

    setScrollProgress(progress);

    const viewportCenter = window.innerHeight / 2;

    let newActiveSection = 0;
    let minDistance = Infinity;

    sectionRefs.current.forEach((ref, index) => {
      if (!ref) return;

      const rect = ref.getBoundingClientRect();
      const sectionCenter = rect.top + rect.height / 2;
      const distance = Math.abs(
        sectionCenter - viewportCenter
      );

      if (distance < minDistance) {
        minDistance = distance;
        newActiveSection = index;
      }
    });

    const currentPos =
      calculatedPositions[newActiveSection] ??
      calculatedPositions[0];

    if (currentPos) {
      const transform = `translate3d(${currentPos.left}vw, ${currentPos.top}vh, 0) translate3d(-50%, -50%, 0) scale3d(${currentPos.scale}, ${currentPos.scale}, 1)`;

      setGlobeTransform(transform);
    }

    setActiveSection(newActiveSection);
  }, [calculatedPositions]);

  useEffect(() => {
    let ticking = false;

    const handleScroll = () => {
      if (ticking) return;

      animationFrameId.current = requestAnimationFrame(() => {
        updateScrollPosition();
        ticking = false;
      });

      ticking = true;
    };

    window.addEventListener("scroll", handleScroll, {
      passive: true,
    });

    updateScrollPosition();

    return () => {
      window.removeEventListener("scroll", handleScroll);

      if (animationFrameId.current !== undefined) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [updateScrollPosition]);

  useEffect(() => {
    const initialPos = calculatedPositions[0];

    if (!initialPos) return;

    const initialTransform = `translate3d(${initialPos.left}vw, ${initialPos.top}vh, 0) translate3d(-50%, -50%, 0) scale3d(${initialPos.scale}, ${initialPos.scale}, 1)`;

    setGlobeTransform(initialTransform);
  }, [calculatedPositions]);

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative w-full max-w-screen overflow-x-hidden min-h-screen bg-background text-foreground",
        className
      )}
    >
      {/* Progress Bar */}
      <div className="fixed top-0 left-0 w-full h-0.5 bg-gradient-to-r from-border/20 via-border/40 to-border/20 z-50">
        <div
          className="h-full bg-gradient-to-r from-primary via-blue-600 to-blue-900 will-change-transform shadow-sm"
          style={{
            transform: `scaleX(${scrollProgress})`,
            transformOrigin: "left center",
            transition: "transform 0.15s ease-out",
            filter:
              "drop-shadow(0 0 2px rgba(59, 130, 246, 0.3))",
          }}
        />
      </div>

      {/* Section Navigation */}
      <div className="hidden sm:flex fixed right-2 sm:right-4 lg:right-8 top-1/2 -translate-y-1/2 z-40">
        <div className="space-y-3 sm:space-y-4 lg:space-y-6">
          {sections.map((section, index) => (
            <div
              key={section.id}
              className="relative group"
            >
              {/* Section Label */}
              <div
                className={cn(
                  "nav-label absolute right-6 sm:right-8 lg:right-10 top-1/2 -translate-y-1/2",
                  "px-2 sm:px-3 lg:px-4 py-1 sm:py-1.5 lg:py-2",
                  "rounded-md sm:rounded-lg",
                  "text-xs sm:text-sm font-medium whitespace-nowrap",
                  "bg-background/95 backdrop-blur-md",
                  "border border-border/60 shadow-xl z-50",
                  activeSection === index
                    ? "animate-fadeOut"
                    : "opacity-0"
                )}
              >
                <div className="flex items-center gap-1 sm:gap-1.5 lg:gap-2">
                  <div className="w-1 sm:w-1.5 lg:w-2 h-1 sm:h-1.5 lg:h-2 rounded-full bg-primary animate-pulse" />

                  <span className="text-xs sm:text-sm lg:text-base">
                    {section.badge ||
                      `Section ${index + 1}`}
                  </span>
                </div>
              </div>

              {/* Navigation Dot */}
              <button
                type="button"
                onClick={() => {
                  sectionRefs.current[index]?.scrollIntoView({
                    behavior: "smooth",
                    block: "center",
                  });
                }}
                className={cn(
                  "relative w-2 h-2 sm:w-2.5 sm:h-2.5 lg:w-3 lg:h-3 rounded-full border-2 transition-all duration-300 hover:scale-125 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-4",
                  "before:absolute before:inset-0 before:rounded-full before:transition-all before:duration-300",
                  activeSection === index
                    ? "bg-primary border-primary shadow-lg before:animate-ping before:bg-primary/20"
                    : "bg-transparent border-muted-foreground/40 hover:border-primary/60 hover:bg-primary/10"
                )}
                aria-current={activeSection === index ? "step" : undefined}
                aria-label={`Go to ${
                  section.badge ||
                  `section ${index + 1}`
                }`}
              />
            </div>
          ))}
        </div>

        {/* Navigation Line */}
        <div className="absolute left-1/2 top-0 bottom-0 w-0.5 lg:w-px bg-gradient-to-b from-transparent via-primary/20 to-transparent -translate-x-1/2 -z-10" />
      </div>

      {/* Fixed Globe */}
      <div
        className="fixed z-10 pointer-events-none will-change-transform transition-all duration-[1400ms] ease-[cubic-bezier(0.23,1,0.32,1)]"
        style={{
          transform: globeTransform,
          filter: `opacity(${
            activeSection === 3 ? 0.4 : 0.85
          })`,
        }}
      >
        <div className="scale-75 sm:scale-90 lg:scale-100">
          <Globe />
        </div>
      </div>

      {/* Sections */}
      {sections.map((section, index) => (
        <section
          key={section.id}
          ref={(element) => {
            sectionRefs.current[index] = element;
          }}
          className={cn(
            "relative min-h-screen flex flex-col justify-center",
            "px-4 sm:px-6 md:px-8 lg:px-12",
            "z-20 py-12 sm:py-16 lg:py-20",
            "w-full max-w-full overflow-hidden",
            section.align === "center" &&
              "items-center text-center",
            section.align === "right" &&
              "items-end text-right",
            section.align !== "center" &&
              section.align !== "right" &&
              "items-start text-left"
          )}
        >
          <div
            className={cn(
              "w-full max-w-sm sm:max-w-lg md:max-w-2xl",
              "lg:max-w-4xl xl:max-w-5xl",
              "will-change-transform transition-all duration-700",
              "opacity-100 translate-y-0"
            )}
          >
            {section.badge && (
              <div className="mb-4 flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[10px] font-medium uppercase tracking-[0.18em] text-muted-foreground/70">
                <span className="text-primary">{section.badge}</span>
                {section.eyebrow && <span>{section.eyebrow}</span>}
              </div>
            )}

            {/* Heading */}
            <h1
              className={cn(
                "font-bold mb-6 sm:mb-8",
                "leading-[1.1] tracking-tight",
                index === 0
                  ? "text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl 2xl:text-8xl"
                  : "text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl 2xl:text-7xl"
              )}
            >
              {section.subtitle ? (
                <div className="space-y-1 sm:space-y-2">
                  <div className="landing-reveal bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
                    {section.title}
                  </div>

                  <div className="landing-reveal landing-reveal-delay text-muted-foreground/90 text-[0.6em] sm:text-[0.7em] font-medium tracking-wider">
                    {section.subtitle}
                  </div>
                </div>
              ) : (
                <div className="landing-reveal bg-gradient-to-r from-foreground via-foreground to-foreground/80 bg-clip-text text-transparent">
                  {section.title}
                </div>
              )}
            </h1>

            {/* Description */}
            <div
              className={cn(
                "text-muted-foreground/80",
                "leading-relaxed mb-8 sm:mb-10",
                "text-base sm:text-lg lg:text-xl",
                "font-light",
                section.align === "center"
                  ? "max-w-full mx-auto text-center"
                  : "max-w-full"
              )}
            >
              <p className="mb-3 sm:mb-4">
                {section.description}
              </p>

              {index === 0 && (
                <div className="flex flex-wrap items-center gap-3 sm:gap-4 text-xs sm:text-sm text-muted-foreground/60 mt-4 sm:mt-6">
                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <div className="w-1 h-1 rounded-full bg-primary animate-pulse" />
                    <span>Interactive Experience</span>
                  </div>

                  <div className="flex items-center gap-1.5 sm:gap-2">
                    <div
                      className="w-1 h-1 rounded-full bg-primary animate-pulse"
                      style={{
                        animationDelay: "0.5s",
                      }}
                    />
                    <span>Scroll to Explore</span>
                  </div>
                </div>
              )}
            </div>

            {/* Features */}
            {section.features && (
              <div className="grid gap-3 sm:gap-4 mb-8 sm:mb-10">
                {section.features.map(
                  (feature, featureIndex) => (
                    <div
                      key={feature.title}
                      className={cn(
                        "group p-4 sm:p-5 lg:p-6",
                        "rounded-lg sm:rounded-xl",
                        "border bg-card/50 backdrop-blur-sm",
                        "hover:bg-card/80",
                        "transition-all duration-300",
                        "hover:shadow-lg hover:shadow-primary/5",
                        "hover:border-primary/20",
                        "hover:-translate-y-1"
                      )}
                      style={{
                        animationDelay: `${
                          featureIndex * 0.1
                        }s`,
                      }}
                    >
                      <div className="flex items-start gap-3 sm:gap-4">
                        <div className="w-1.5 sm:w-2 h-1.5 sm:h-2 rounded-full bg-primary/60 mt-1.5 sm:mt-2 group-hover:bg-primary transition-colors flex-shrink-0" />

                        <div className="flex-1 space-y-1.5 sm:space-y-2 min-w-0">
                          <h3 className="font-semibold text-card-foreground text-base sm:text-lg">
                            {feature.title}
                          </h3>

                          <p className="text-muted-foreground/80 leading-relaxed text-sm sm:text-base">
                            {feature.description}
                          </p>
                        </div>
                      </div>
                    </div>
                  )
                )}
              </div>
            )}

            {/* Actions */}
            {section.actions && (
              <div className={cn(section.id === "methodology" && "border border-border/60 bg-background/30 p-4 sm:p-6", "space-y-3 sm:space-y-4")}>
              <div
                className={cn(
                  "flex w-full min-w-0 flex-col flex-wrap gap-3 sm:flex-row sm:gap-4",
                  section.align === "center" &&
                    "justify-center",
                  section.align === "right" &&
                    "justify-end",
                  (!section.align ||
                    section.align === "left") &&
                    "justify-start"
                )}
              >
                {section.actions.map((action) => (
                  <EditorialIconButton
                    key={action.label}
                    label={action.label}
                    icon={
                      action.variant === "primary"
                        ? ArrowUpRight
                        : ArrowDown
                    }
                    variant={action.variant}
                    onClick={action.onClick}
                  />
                ))}
              </div>
              </div>
            )}
          </div>
        </section>
      ))}
    </div>
  );
}

export default function GlobeScrollDemo() {
  const demoSections = [
    {
      id: "hero",
      badge: "Flood Intelligence",
      eyebrow: "Earth Observation · Northern Nepal · 2026",
      title: "Understand the Ground",
      description:
        "Satellite intelligence for mapping flood pathways, infrastructure exposure, and accessibility across northern Nepal.",
      align: "left" as const,
      actions: [
        {
          label: "Explore the Analysis",
          variant: "primary" as const,
          onClick: () => {
            window.location.href = "/dashboard";
          },
        },
        {
          label: "How It Works",
          variant: "secondary" as const,
          onClick: () => {
            document
              .getElementById("trace")
              ?.scrollIntoView({
                behavior: "smooth",
                block: "center",
              });
          },
        },
      ],
    },

    {
      id: "observe",
      badge: "Observe",
      title: "Observe",
      subtitle: "From Orbit",
      description:
        "Sentinel-1 radar imagery reveals surface change even when clouds obscure the landscape.",
      align: "center" as const,
    },

    {
      id: "trace",
      badge: "Trace",
      title: "Trace",
      subtitle: "Through Terrain",
      description:
        "Elevation and hydrological analysis help identify drainage corridors and the terrain structures that shape flood movement.",
      align: "left" as const,
      features: [
        {
          title: "Sentinel-1",
          description:
            "Before-and-after radar observations for surface change detection.",
        },
        {
          title: "Copernicus DEM",
          description:
            "Terrain and drainage analysis for understanding flood pathways.",
        },
        {
          title: "OpenStreetMap",
          description:
            "Pre-event buildings, roads, bridges, settlements, and hospitals for exposure and accessibility analysis.",
        },
      ],
    },

    {
      id: "methodology",
      badge: "Assess",
      title: "Assess",
      subtitle: "Impact on the Ground",
      description:
        "Combine satellite evidence, terrain, infrastructure, and road-network analysis into a transparent disaster intelligence workflow.",
      align: "center" as const,
      actions: [
        {
          label: "Open Dashboard",
          variant: "primary" as const,
          onClick: () => {
            window.location.href = "/dashboard";
          },
        },
        {
          label: "View Methodology",
          variant: "secondary" as const,
          onClick: () => {
            document
              .getElementById("methodology")
              ?.scrollIntoView({
                behavior: "smooth",
                block: "center",
              });
          },
        },
      ],
    },
  ];

  return (
    <ScrollGlobe
      sections={demoSections}
      className="bg-gradient-to-br from-background via-muted/20 to-background"
    />
  );
}
