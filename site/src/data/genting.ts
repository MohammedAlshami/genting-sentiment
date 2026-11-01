export type SentimentPoint = {
  date: string;
  sentiment: number;
  genting: number;
  genm: number;
};

export const sentimentSeries = [
  { date: "Nov 24", sentiment: 0.114, genting: 3.74, genm: 2.16 },
  { date: "Dec 24", sentiment: 0.105, genting: 3.86, genm: 2.26 },
  { date: "Jan 25", sentiment: 0.066, genting: 3.63, genm: 2.23 },
  { date: "Feb 25", sentiment: 0.052, genting: 3.29, genm: 1.90 },
  { date: "Mar 25", sentiment: 0.120, genting: 3.25, genm: 1.66 },
  { date: "Apr 25", sentiment: 0.081, genting: 3.20, genm: 1.71 },
  { date: "May 25", sentiment: 0.168, genting: 3.00, genm: 1.82 },
  { date: "Jun 25", sentiment: 0.185, genting: 3.05, genm: 1.93 },
  { date: "Jul 25", sentiment: 0.187, genting: 3.13, genm: 1.96 },
  { date: "Aug 25", sentiment: 0.172, genting: 2.86, genm: 2.04 },
  { date: "Sep 25", sentiment: 0.163, genting: 2.92, genm: 2.10 },
  { date: "Oct 25", sentiment: 0.155, genting: 3.38, genm: 2.33 },
  { date: "Nov 25", sentiment: 0.142, genting: 3.27, genm: 2.35 },
  { date: "Dec 25", sentiment: 0.130, genting: 3.02, genm: 2.04 },
  { date: "Jan 26", sentiment: 0.150, genting: 2.86, genm: 1.98 },
  { date: "Feb 26", sentiment: 0.116, genting: 2.83, genm: 2.10 },
  { date: "Mar 26", sentiment: 0.073, genting: 2.23, genm: 1.78 },
  { date: "Apr 26", sentiment: 0.134, genting: 2.57, genm: 1.98 },
  { date: "May 26", sentiment: 0.132, genting: 2.32, genm: 1.93 },
  { date: "Jun 26", sentiment: 0.079, genting: 2.16, genm: 1.87 },
  { date: "Jul 26", sentiment: 0.118, genting: 2.12, genm: 1.75 },
  { date: "Aug 26", sentiment: 0.127, genting: 2.06, genm: 1.70 },
  { date: "Sep 26", sentiment: 0.068, genting: 1.89, genm: 1.47 },
  { date: "Oct 26", sentiment: 0.051, genting: 1.54, genm: 1.25 },
];

export const debtSeries = [
  { period: "4Q24", genting: 39.23, genm: 12.22, net: 16.83 },
  { period: "1Q25", genting: 39.00, genm: 12.19, net: 17.47 },
  { period: "2Q25", genting: 38.87, genm: 13.06, net: 18.01 },
  { period: "3Q25", genting: 38.88, genm: 13.16, net: 18.91 },
  { period: "4Q25", genting: 40.81, genm: 12.72, net: 22.81 },
  { period: "1Q26", genting: 43.50, genm: 15.67, net: 26.14 },
  { period: "2Q26", genting: 45.25, genm: 15.70, net: 27.61 },
];

export const events = [
  {
    date: "Oct 2025",
    title: "The RM2.35 offer",
    body: "On 13 Oct, Genting Berhad launches a RM6.7b takeover bid for the GENM shares it does not own, aiming past the 75% delisting threshold.",
    tag: "Privatisation",
  },
  {
    date: "Dec 2025",
    title: "The bid fails",
    body: "The offer closes on 1 Dec short of 75%. Genting's stake settles at 73.13%, then rises to 73.888% by April 2026 through open-market purchases.",
    tag: "Ownership",
  },
  {
    date: "Dec 2025",
    title: "New York licence secured",
    body: "RWNYC is recommended on 1 Dec and awarded the full licence on 16 Dec — a US$5.5b capex project with a US$600m upfront commitment.",
    tag: "New York",
  },
  {
    date: "May 2026",
    title: "Earnings soften",
    body: "1Q26 revenue rises, but higher finance costs and a weaker leisure mix drag profit. The market starts pricing a cash call.",
    tag: "Earnings",
  },
  {
    date: "Aug 2026",
    title: "1H26 profit halves",
    body: "Core profit falls 47.7% year on year to RM167.5m. Analysts cut target prices; the debt conversation gets louder.",
    tag: "Earnings",
  },
  {
    date: "Oct 2026",
    title: "The RM1.25b rights issue",
    body: "Genting proposes a RM1.25b cash call: RM800m debt repayment, RM429.5m working capital (including RM280m interest) and RM20.5m expenses.",
    tag: "Dilution",
  },
  {
    date: "Oct 2026",
    title: "A 22.87% single-day fall",
    body: "The stock drops to RM1.45, its lowest since 2007. Maybank cuts to Sell with a RM1.49 target; Affin cuts both counters to Sell.",
    tag: "Market",
  },
  {
    date: "Oct 2026",
    title: "Kien Huat buys the dip",
    body: "The Lim family vehicle buys 6m GENT shares at RM1.494 on 12 Oct — the day of the rights-issue crash.",
    tag: "Ownership",
  },
];

export const facts = [
  { label: "Genting stake in GENM", value: "73.888%", note: "just below the 75% delisting line" },
  { label: "Rights issue", value: "RM1.25b", note: "RM800m debt · RM429.5m working capital" },
  { label: "Group debt", value: "RM45.3b", note: "as at end-June 2026" },
  { label: "Annual interest", value: "RM2.1b", note: "the rights issue covers ~7 months" },
  { label: "2027 maturities", value: "US$617.5m", note: "plus RM2.35b of ringgit paper" },
  { label: "GENM market cap", value: "RM7.4b", note: "at RM1.25 per share" },
];

export const forecast = [
  { date: "Nov 26", base: 1.25, bull: 1.25, bear: 1.25 },
  { date: "Dec 26", base: 1.26, bull: 1.3, bear: 1.21 },
  { date: "Jan 27", base: 1.28, bull: 1.36, bear: 1.16 },
  { date: "Feb 27", base: 1.29, bull: 1.42, bear: 1.1 },
  { date: "Mar 27", base: 1.31, bull: 1.48, bear: 1.02 },
  { date: "Apr 27", base: 1.32, bull: 1.55, bear: 0.95 },
];

export const quotes = [
  "Tactic to delist. Want to buy back shares at cheap cheap price.",
  "Take private at RM0.20 per share. 5 years later relist back at 3.50.",
  "The whole RM1.25b covers barely 7 months of interest.",
  "Don't pay up, your stake shrinks from 100 to 80.",
  "Is this just some fresh new FUD or?",
  "Only thing going for it is it's dirt cheap vs book value.",
];

export const methodNotes = [
  { label: "Coverage", value: "24 months", body: "2 Nov 2024 → 2 Nov 2026. GENTING (3182) and GENM (4715)." },
  { label: "Corpus", value: "75,629", body: "Posts and comments across nine public sources." },
  { label: "Scoring", value: "Multilingual", body: "English, Malay and Chinese, with source and timestamp confidence." },
  { label: "Caveat", value: "Not advice", body: "Sentiment is sampled and noisy. Projections are scenarios, not forecasts." },
];
