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
import { debtSeries } from '@/data/genting';
import { INK, MUTED, axisTick, tooltipStyle } from './theme';

export function DebtChart() {
  return (
    <div className="h-[280px] w-full sm:h-[330px]">
      <ResponsiveContainer
        width="100%"
        height="100%"
        minWidth={0}
        initialDimension={{ width: 900, height: 300 }}
      >
        <ComposedChart
          data={debtSeries}
          margin={{ top: 10, right: 8, bottom: 8, left: -8 }}
        >
          <CartesianGrid stroke="rgba(14,16,15,0.04)" vertical={false} />
          <XAxis
            dataKey="period"
            axisLine={false}
            tickLine={false}
            tick={axisTick}
          />
          <YAxis
            domain={[0, 50]}
            axisLine={false}
            tickLine={false}
            tick={axisTick}
            tickFormatter={(v) => `RM${Number(v).toFixed(0)}b`}
          />
          <Tooltip
            contentStyle={tooltipStyle}
            labelStyle={{ color: MUTED, fontSize: 11 }}
            itemStyle={{ color: INK }}
            formatter={(value, name) => [
              `RM${Number(value).toFixed(1)}b`,
              name === 'genting'
                ? 'GENTING debt'
                : name === 'genm'
                  ? 'GENM debt'
                  : 'Net debt',
            ]}
          />
          <Line
            type="monotone"
            dataKey="genting"
            stroke={INK}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 3, fill: INK, stroke: '#FFFFFF' }}
            isAnimationActive
          />
          <Line
            type="monotone"
            dataKey="genm"
            stroke="rgba(14,16,15,0.45)"
            strokeWidth={1.4}
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="net"
            stroke="rgba(14,16,15,0.25)"
            strokeWidth={1.2}
            strokeDasharray="3 4"
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
