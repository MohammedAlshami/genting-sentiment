"use client";

import React from "react";
import { ReactLenis } from "lenis/react";
import { OpeningSection } from "@/data/components/Genting/OpeningSection";
import { StorySections } from "@/data/components/Genting/StorySections";
import { KeyboardNav } from "@/data/components/Genting/KeyboardNav";

export function LandingPage() {
  return (
    <div className="landing-page min-h-screen bg-white text-[#0E100F]">
      <ReactLenis root options={{ lerp: 0.05 }}>
        <OpeningSection />
        <StorySections />
        <KeyboardNav />
      </ReactLenis>
    </div>
  );
}
