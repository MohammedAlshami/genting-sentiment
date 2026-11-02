# LLM sentiment classification

## Coverage
- Replies in the corpus: **293,601**
- Replies classified by the LLM: **9,015** (3.1%)
- Months covered: **2016-11 → 2026-11** (119 months)
- Labels: bullish 2,504, bearish 2,586, neutral 3,925
- Confidence: high 4,805, medium 3,950, low 260

## Model
- `opencode-go/deepseek-v4.1-flash#low`: 9,015 replies

Method: each reply was sent with its ticker, date, thread title and parent comment. The model assigned an integer level 0–10 (0 = maximally bearish, 5 = neutral, 10 = maximally bullish), stored as score/10. Labels: 0–4 bearish, 5 neutral, 6–10 bullish. Full rubric in `scripts/llm_classify.py` (v3).

## Latest month
- 2026-11: mean +0.471, bullish 4.9%, bearish 19.5%, neutral 75.6% (n=41)

## Agreement with the lexicon method
- Overlap months: **25**
- Pearson correlation with the lexicon score: **0.471**
- Mean difference (LLM rescaled to −1…+1, minus lexicon): **-0.164**
- Largest gap: **2025-08**

## Caveats
- This is a model annotation, not a human-labelled gold set. A 200-item hand audit is recommended.
- YouTube/TikTok comments are often about the video rather than the stock; the prompt scores those neutral.
- Channel-level ticker is used where a reply does not name a stock.
- Confidence is the model's own; it is not calibrated.

## Files
- `analysis/12_llm_sentiment_monthly.csv`
- `analysis/12b_llm_sentiment_monthly_by_ticker.csv`
- `analysis/12c_llm_sentiment_by_source.csv`
- `analysis/14_llm_sentiment_examples.md`
