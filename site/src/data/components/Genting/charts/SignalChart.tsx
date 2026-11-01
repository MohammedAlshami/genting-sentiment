'use client';

import {
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { sentimentSeries } from '@/data/genting';
import { INK, MUTED, axisTick, tooltipStyle } from './theme';

export function SignalChart() {
  return (
    <div className="h-[330px] w-full sm:h-[390px]">
      <ResponsiveContainer
        width="100%"
        height="100%"
        minWidth={0}
        initialDimension={{ width: 900, height: 360 }}
      >
        <ComposedChart
          data={sentimentSeries}
          margin={{ top: 16, right: 8, bottom: 8, left: -12 }}
        >
          <CartesianGrid stroke="rgba(14,16,15,0.04)" vertical={false} />
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={axisTick}
            interval={3}
          />
          <YAxis
            yAxisId="sentiment"
            domain={[-0.02, 0.22]}
            axisLine={false}
            tickLine={false}
            tick={axisTick}
            tickFormatter={(v) => Number(v).toFixed(2)}
          />
          <YAxis
            yAxisId="price"
            orientation="right"
            domain={[1, 4.5]}
            axisLine={false}
            tickLine={false}
            tick={axisTick}
            tickFormatter={(v) => `RM${Number(v).toFixed(1)}`}
          />
          <Tooltip
            contentStyle={tooltipStyle}
            labelStyle={{ color: MUTED, fontSize: 11 }}
            itemStyle={{ color: INK }}
            formatter={(value, name) => {
              const n = Number(value);
              return name === 'sentiment'
                ? [n.toFixed(3), 'Sentiment']
                : [`RM${n.toFixed(2)}`, 'GENM'];
            }}
          />
          <Line
            yAxisId="sentiment"
            type="monotone"
            dataKey="sentiment"
            stroke="#ED1C24"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 3, fill: '#ED1C24', stroke: '#FFFFFF' }}
            isAnimationActive
            animationDuration={1200}
          />
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="genm"
            stroke="rgba(14,16,15,0.32)"
            strokeWidth={1.2}
            strokeDasharray="3 4"
            dot={false}
            activeDot={false}
            isAnimationActive
            animationDuration={1600}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
