// Placeholder opinion sentences for the cloud.
// Tone + weight are illustrative for now (user-approved); the real
// 10-year sentence extraction will replace this file.

export type OpinionSentence = {
  text: string;
  weight: number;
  tone: 'pos' | 'neg' | 'neutral';
};

export const opinionSentences: OpinionSentence[] = [
  { text: 'No lowest, only lower.', weight: 56, tone: 'neg' },
  { text: '2.35 is not fair value.', weight: 46, tone: 'neg' },
  { text: 'Hold. The dividend will come back.', weight: 38, tone: 'pos' },
  { text: 'They are dumping all the debt into Genting.', weight: 34, tone: 'neg' },
  { text: 'Buy the dip. This is the bottom.', weight: 40, tone: 'pos' },
  { text: 'Rights issue is pure dilution.', weight: 36, tone: 'neg' },
  { text: 'New York will print money.', weight: 42, tone: 'pos' },
  { text: 'Will Genting take GENM private?', weight: 34, tone: 'neutral' },
  { text: 'Long term, the casino is worth more.', weight: 30, tone: 'pos' },
  { text: 'Empire Resorts is a bottomless pit.', weight: 32, tone: 'neg' },
  { text: 'Waiting for the New York licence.', weight: 30, tone: 'neutral' },
  { text: 'The family will privatise it eventually.', weight: 28, tone: 'neutral' },
  { text: 'Undervalued at book value.', weight: 36, tone: 'pos' },
  { text: 'Dead money for six years.', weight: 34, tone: 'neg' },
  { text: 'What happens to the 73% stake?', weight: 28, tone: 'neutral' },
  { text: 'The theme park finally opened.', weight: 30, tone: 'pos' },
  { text: 'Goreng until the last retailer leaves.', weight: 26, tone: 'neg' },
  { text: 'When is the next dividend?', weight: 32, tone: 'neutral' },
];
