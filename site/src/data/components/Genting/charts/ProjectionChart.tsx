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
import { forecast } from '@/data/genting';
import { INK, MUTED, axisTick, tooltipStyle } from './theme';

export function ProjectionChart() {
  return (
    <div className="h-[300px] w-full sm:h-[340px]">
      <ResponsiveContainer
        width="100%"
        height="100%"
        minWidth={0}
        initialDimension={{ width: 900, height: 320 }}
      >
        <ComposedChart
          data={forecast}
          margin={{ top: 16, right: 8, bottom: 8, left: 0 }}
        >
          <CartesianGrid stroke="rgba(14,16,15,0.04)" vertical={false} />
          <XAxis
            dataKey="date"
            axisLine={false}
            tickLine={false}
            tick={axisTick}
          />
          <YAxis
            domain={[0.8, 1.7]}
            axisLine={false}
            tickLine={false}
            tick={axisTick}
            tickFormatter={(v) => `RM${Number(v).toFixed(2)}`}
          />
          <Tooltip
            contentStyle={tooltipStyle}
            labelStyle={{ color: MUTED, fontSize: 11 }}
            itemStyle={{ color: INK }}
            formatter={(value, name) => [
              `RM${Number(value).toFixed(2)}`,
              String(name).toUpperCase(),
            ]}
          />
          <Line
            type="monotone"
            dataKey="bull"
            stroke="rgba(14,16,15,0.25)"
            strokeWidth={1}
            strokeDasharray="3 4"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="bear"
            stroke="rgba(14,16,15,0.25)"
            strokeWidth={1}
            strokeDasharray="3 4"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="base"
            stroke={INK}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 3, fill: INK, stroke: '#FFFFFF' }}
            isAnimationActive
            animationDuration={1600}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
