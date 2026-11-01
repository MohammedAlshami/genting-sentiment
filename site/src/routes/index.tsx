import { createFileRoute } from "@tanstack/react-router";
import { LandingPage } from "@/pages/public/LandingPage";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Genting · Retail Sentiment, 2016—2026" },
      {
        name: "description",
        content:
          "Two years of Malaysian retail conversation about Genting Berhad and Genting Malaysia, aligned with the price, the debt and the events that moved the stock.",
      },
    ],
  }),
  component: LandingPage,
});
